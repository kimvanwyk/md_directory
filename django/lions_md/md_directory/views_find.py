'''
Copyright (c) 2011, Kim van Wyk 
All rights reserved.  

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer. 
Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.shortcuts import render_to_response, redirect
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from common_modules.utilities import get_years, get_current_year
from views_utility import get_model, get_label
from views import index
import common_modules.models as models

# -----------------------------------------------------------------------------------------------------
# Find views
# -----------------------------------------------------------------------------------------------------
@login_required
def find_member(request, event=None):
    ''' View to find a member by initial
    '''
    from django.forms import ModelForm

    # create a list of upper-case initials
    from string import ascii_uppercase
    inits = list(ascii_uppercase)

    from_str = ''
    p = request.user.get_profile()
    # if current user is a club user, don't use initial dropdown
    if p.is_club:
        use_initial = False
        club_id = p.club
        # set from_str to specify what the find page is limited to
        from_str = 'from the %s club' % models.Club.objects.get(pk=int(p.club_id))
    else:
        use_initial = True

    if request.method == 'POST':
        if use_initial:
            # find the letter which has been selected
            init = inits[int(request.POST['init'])]
            # find the last name of the member, then get the initial from that to find the letter heading the current name list
            # check that a valid 'member' member of the POST dict exists.
            # if not, the current member list was empty, so set name_init to 'a' to force change
            if 'member' not in request.POST:
                name_init = 'a'
            else:
                name_init = str(models.Member.objects.get(pk=int(request.POST['member'])).last_name.upper()[0])
            # check if the current init is the same as the member list - i.e. has a new init been chosen
            if init != name_init:
                current_initial = init
            else:
                current_initial = name_init
    else:
        # not a post, use the first initial
        current_initial = inits[0]
    # filter the members list for the names dropdown to be names which start with the initial, if use_initial is True
    if use_initial:
        source = models.Member.objects.filter(last_name__istartswith=current_initial)
        # add dist filter if needed
        if p.is_dist:
            source = source.filter(club__struct = int(p.struct_id))
    else:
        source = models.Member.objects.filter(club=club_id)        
    members = [(m.id,m.__unicode__()) for m in source]

    class Form(forms.Form):
        # create a initial selection dropdown, which submits the form when a new value is chosen
        if use_initial:
            init = forms.ChoiceField(choices=[(n,k) for n,k in enumerate(inits)], initial=ascii_uppercase[0], 
                                     widget=forms.Select(attrs={"onchange": "form_initial_submit()"}))
        member = forms.ChoiceField(choices=members)
    
    if request.method == 'POST':
        # build the form and validate
        form = Form(request.POST)
        if form.is_valid(): # All validation rules pass
            # direct to the appropriate member page
            if not event:
                return redirect('/member/%s' % (form.cleaned_data['member']))
            # event supplied, so set member event model
            obj = models.EventAttendance(event=event, member_id=form.cleaned_data['member'])
            obj.save()
            return redirect('/member/%s/' % event)
    else:
        # Not a POST, build an initial form
        form = Form()
    return render_to_response('md_directory/find_member.html', {'form':form, 'from':from_str, 'event':event})

@login_required
def find_s_mc_lobs_do_r_z_c(request, obj, dest=None, use_year=True, item_id=None):
    ''' locate a merch centre, district office, struct, region, zone or club to edit its chairs, its officers (where applicable for either) or its details
    'obj' is the type of object to find: merch centre, district office, struct, region, zone or club
    'dest' is an optional destination for the URL. If blank, the object is the destination - ie. the edit page for an object
         otherwise the destination is inserted between the object type and the specific id of the item to edit
    'item_id' is an optional id for the obj. If supplied, only the year is chosen. 
    'use_year' is an optional instruction, if dest is true, use_year governs whether the year is inserted between the dest and the specific id
    '''

    print 'starting find_s_mc_lobs_do_r_z_c'
    # a list of obj, dest pairs this function can process
    pairs = [('struct',None), ('merch_centre',None), ('brightsight', None), ('dist_office',None), ('region',None), ('zone',None), 
             ('struct','regionlist'), ('struct','zonelist'),('club',None), ('member',None),
             ('club','officers'), ('struct','officers'), ('struct','chairs'), ('struct','mentors'), ('region','chair'), ('zone','chair')]
    if (obj,dest) not in pairs:
        # not a valid pairing, return a tailored error message
        return HttpResponse("/%s%s is an invalid location" % (obj, dest and '/%s' % dest or ''))

    # if 'list' is in dest, do not use year
    if dest and ('list' in dest):
        use_year = False

    print 'looked up'
    # If user is a club user, redirect to suitable page for club objects, permission denied for others
    p = request.user.get_profile()
    if p.is_club:
        if obj == 'club':
            if not dest:
                # if club itself, go straight there
                return redirect('/%s/%s/' % (obj, p.club_id))
            elif not use_year:
                return redirect('/%s/%s/%s/' % (obj, dest, p.club_id))
            else:
                # ensure item_id is set the only club user can access
                item_id = int(p.club_id)
        else:
            # not a club, deny permission for anything else
            return render_to_response('md_directory/not_auth.html', {'response':'You do not have the necessary permission to access the requested area'})            

    print 'in find_s_mc_lobs_do_r_z_c'

    #create form to list item
    class Form(forms.Form):
        def __init__(self, *args, **kwargs):
            # inherit from parent Form
            super(Form, self).__init__(*args, **kwargs)
            # if item_id is not supplied, provide a selection dropdown
            self.no_entries = False
            if not item_id:
                # build a list of (item id, item) for the type of obj being found
                # determine if object should be filtered by district
                if p.is_dist:
                    source = get_model(obj).objects.filter(struct=p.struct).filter(struct__in_use_b=1)
                else:
                    try:
                        # don't do struct in_use filtering for clubs to avoid
                        # needing a complicated query for the club_merge table
                        if obj == 'club':
                            raise Exception
                        if obj == 'struct':
                            source = get_model(obj).objects.filter(in_use_b=1)
                        else:
                            source = get_model(obj).objects.filter(struct__in_use_b=1)
                            print 'used struct lookup'
                    except Exception as e:
                        source = get_model(obj).objects.all()
                        print 'no struct lookup'
                items = [(s.id, s) for s in source]
                if not items:
                    self.no_entries = True
                else:
                    self.fields[obj] = forms.ChoiceField(choices=items, initial=items[0][0], label=get_label(obj))
                    self.item = ''
                    self.label = ''
            else:
                # item id is supplied, use the name of the item instead of the dropdown
                self.item = get_model(obj).objects.get(pk=int(item_id))
                self.label = get_label(obj)
            # if there is a dest and a use_year, add a dropdown to pick the year of interest, as it is not the base object which will be edited
            if dest and use_year:
                (yl, initial) = get_years()
                # use the current year as the initial choice, as get_years will look one year into the future
                self.fields['year'] = forms.ChoiceField(choices=yl, initial=yl[initial][0], label='Year of interest')                

    if request.method == 'POST':
        form = Form(request.POST)       
        if form.is_valid():
            # redirect to the specific destination page if use_year is True, the object's details page otherwise
            if not item_id:
                item_id = form.cleaned_data[obj]
            if dest:
                if use_year:
                    year_str = '%s/' % form.cleaned_data['year']
                else:
                    year_str = ''
                return redirect('/%s/%s/%s%s/' % (obj, dest, year_str, item_id))
            else:
                return redirect('/%s/%s/' % (obj, item_id))
    else:
        # no POST, use an initial form
        form = Form()
    # determine if there are no entries, redirecting back to main page with a blurb if so
    if form.no_entries:
        return index(request, 'There are no %ss available' % get_label(obj), '')
    return render_to_response('md_directory/find_s_mc_lobs_do_r_z_c.html', {'form':form, 'dest':dest, 'type':obj, 'item_id':item_id,
                                                                            'title':get_label(obj), 'item':form.item, 'label':form.label})
 
