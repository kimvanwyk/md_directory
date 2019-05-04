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
# Create your views here.
import views_permissions as permissions
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.shortcuts import render_to_response, redirect
from string import ascii_uppercase
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from views_utility import get_model, get_label
from common_modules.utilities import get_years, get_current_year
import common_modules.models as models

HANDLE_EXC = False

add_help_text = \
'''For each of the address lines, please include 1 piece of info per line.
E.g. 1 Made-up Complex
23 Pretend Road
Imaginary Suburb
Fake Town

Leave unneeded lines blank'''

phone_help_text = \
'''Any or all of the phone numbers may be left blank. 
Please enter phone numbers as "+27 (031) 123 4567", for eg'''

# -----------------------------------------------------------------------------------------------------
# Detail views
# -----------------------------------------------------------------------------------------------------

@login_required
def club_officers(request, club_id, year=None):
    ''' Pick club officers from drop-down list for President, Secretary, Treasurer and Membership Chair
    '''
    import django.forms
    # check if permitted to edit this club
    edit, response = permissions.can_edit_club(request.user, club_id)
    if not edit:
        return render_to_response('md_directory/not_auth.html', {'response':response})        

    if not year:
        year = get_current_year()
    #check if year is an int
    try:
        year = int(year)
    except:
        return HttpResponse("%d is not a valid year" % year)            
    
    try:
        club_id = int(club_id)
    except:
        # Could not obtain instance, report bad ID
        return HttpResponse("%s is an invalid club id" % club_id)    

    # obtain club model from id
    model = models.Club.objects.get(pk=club_id)
    # Limit members to live club members if current year
    from django.db.models import Q
    limit = Q(club=club_id)
    if year == get_current_year():
        limit = limit  & Q(deceased_b=False)

    if model.type > 0:
        # This is a child club, allow members from parent club to appear as well
        limit = limit | Q(club=int(model.parent_id))
    # apply limit to members model
    models.ClubOfficer.member.field.rel.limit_choices_to = limit
 
   # Get queryset for club officers with specified year
    q = models.ClubOfficer.objects.filter(year=year).filter(club=club_id)
    # get title based on club_type
    # 0: regular club; 1: branch; 2: Lioness club; 3: Leos; 4: Lion Ladies
    titles = {0:[1,2,3,4], 1:[16,1,2], 2:[1,2,3,4], 3:[20,1,2,3], 4:[1]}[model.type]

    fields = ['email', 'add1', 'add2', 'add3', 'add4', 'po_code', 'phone', 'fax']
    
    #create form to hold officers
    class OfficerForm(django.forms.Form):
        def __init__(self, model, members_list, title, index, *args, **kwargs):
            super(OfficerForm, self).__init__(*args, **kwargs)
            self.title = title
            # Determine the name of the office held
            self.office = models.OfficerTitle.objects.get(pk=title).title
            obj = model.filter(office=title)
            # Determine if this model and year combo has an entry for this office
            ini = {}
            if obj:
                self.obj = obj[0]
                if obj[0].member:
                    # extract the member id and set the email field
                    ini_member = obj[0].member.id
                else:
                    ini_member = 0
                for n in fields:
                    ini[n] = getattr(obj[0], n)
            else:
                # No office entry for this model/year combo, use blank data
                ini_member = 0
                for n in fields:
                    ini[n] = ''
                self.obj = None

            # create member and email fields
            self.fields['member'] = forms.ChoiceField(choices=members_list, required=None, initial=ini_member, widget=forms.Select(attrs={'tabindex':str(index)}))
            for n in fields:
                self.fields[n] = forms.CharField(required=None, initial=ini[n])

        def clean_member(self):
            data = self.cleaned_data['member']
            # ensure members set to 0 are changed to None for DB insertion
            try:
                if int(data) == 0:
                    data = None
            except:
                pass
            return data

    def get_form_list(titles, limit, POST=None):
        ''' Return a list of OfficerForms, one for each title 
        '''
        # obtain a members list of all club members
        member_filter = models.Member.objects.filter(limit)
        members = [(0, 'No office holder')] + [(m.id, m) for m in member_filter]
        l = []
        for (j,t) in enumerate(titles,1):
            if POST:
                # if this is a POSTed form, use the POST data in the form
                data = {}
                for n in fields:
                    data['%d-%s' % (t, n)] = POST['%d-%s' % (t, n)]
                data['%d-member' % t] = int(POST['%d-member' % t])
            else:
                data = None
            l.append(OfficerForm(q, members, t, j, data=data, prefix=str(t)))
        return l
                     

    if request.method == 'POST':
        form_list = get_form_list(titles, limit, request.POST)
        # check that all forms are validaed
        if all(form.is_valid() for form in form_list):
            # Store changes in DB and render confirmation page.
            changes = []
            for n,t in enumerate(titles):
                form = form_list[n]
                if form.has_changed():
                    # Form has new data, save it
                    if form.obj:
                        # Obect existed before, save its changes
                        form.obj.member_id = form.cleaned_data['member']
                        for n in fields:
                            setattr(form.obj, n, form.cleaned_data[n])
                        form.obj.save()
                    else:
                        # Object didn't exist, add a new one
                        obj = models.ClubOfficer(club_id=club_id, year=year, member_id=form.cleaned_data['member'], email=form.cleaned_data['email'], office_id=t)
                        obj.save()
                        
                    # pretty-print the changes for a confirmation page
                    if form.cleaned_data['member']:
                        m = models.Member.objects.get(pk=form.cleaned_data['member'])
                        member = '%s, %s' % (m.last_name, m.first_name)
                    else:
                        member = 'No office holder'
                    office = models.OfficerTitle.objects.get(pk=t).title
                    changes.append([office, member])
                    changes.extend(form.cleaned_data[n] for n in fields)
            # TODO: temp measure - going back to club finder
#            return render_to_response('md_directory/confirmation_officers.html', {'changes':changes, 'name':name})
            return redirect('/club/officers/')
    else:
        # Not a POST, build an initial form
        form_list = get_form_list(titles, limit)
        
    return render_to_response('md_directory/club_officers.html', {'form_list':form_list, 'name': model.name, 'id': club_id, 'year':year})

@login_required
def club_zones(request, struct_id, group_type='zone'):
    ''' Pick club zones or zone regions for each club or zone in the district
    group_type can either be "zone" or "region"
    '''
    import django.forms
    # check if permitted to edit this struct
    edit, response = permissions.can_edit_dist(request.user, struct_id)
    if not edit:
        return render_to_response('md_directory/not_auth.html', {'response':response})        

    base_types = {'zone': 'club',
                 'region': 'zone'}

    if group_type not in base_types.keys():
        return HttpResponse("%s is an invalid group type" % group_type)    

    group_model = getattr(models, group_type.capitalize())
    base_type = base_types[group_type]
    base_model = getattr(models, base_type.capitalize())
    try:
        struct_id = int(struct_id)
    except:
        # Could not obtain instance, report bad ID
        return HttpResponse("%s is an invalid struct id" % struct_id)    

    # obtain list of zones/regions for the club/zone
    group_items = [(z.id, z.__unicode__()) for z in group_model.objects.filter(struct=struct_id)]
    group_items.sort()
 
    # obtain a list of clubs/zones
    objs = base_model.objects.filter(struct=struct_id)
    if base_type == 'club':
        objs = objs.filter(closed_b=False)
    base_items = [(c.id, c.__unicode__()) for c in objs]
    base_items.sort(key=lambda s: s[1])

    #create form to hold zones
    class GroupForm(django.forms.Form):
        def __init__(self, base_id, group_list, *args, **kwargs):
            super(GroupForm, self).__init__(*args, **kwargs)
            base = base_model.objects.get(pk=base_id)
            self.base = base.__unicode__()
            try:
                ini_group = getattr(base, '%s_id' % group_type)
            except:
                ini_group = 0

            # create club and zone fields
            self.fields['group'] = forms.ChoiceField(choices=group_list, required=None, initial=ini_group)

            if base_type == 'zone':
                # add in next years zone chair
                zc = models.ZoneChair.objects.filter(parent=base_id).get(year=2015).member
                self.member = zc

        def clean_member(self):
            data = self.cleaned_data['group']
            # ensure members set to 0 are changed to None for DB insertion
            try:
                if int(data) == 0:
                    data = None
            except:
                pass
            return data

    def get_form_list(base_items, POST=None):
        ''' Return a list of GroupForms, one for each club
        '''
        l = []
        for c_id, name in base_items:
            if POST:
                # if this is a POSTed form, use the POST data in the form
                data = {'%d-group' % c_id:int(POST['%d-group' % c_id])}
            else:
                data = None
            l.append(GroupForm(c_id, group_items, data=data, prefix=str(c_id)))
        return l

    if request.method == 'POST':
        form_list = get_form_list(base_items, request.POST)
        # check that all forms are validaed
        if all(form.is_valid() for form in form_list):
            # Store changes in DB and render confirmation page.
            changes = []
            for n,(t,name) in enumerate(base_items):
                form = form_list[n]
                if form.has_changed():
                    base = base_model.objects.get(pk=t)
                    setattr(base, '%s_id' % group_type, int(form.cleaned_data['group']))
                    base.save()

            # TODO: temp measure - going back to club finder
#            return render_to_response('md_directory/confirmation_officers.html', {'changes':changes, 'name':name})
            return redirect('/')
    else:
        # Not a POST, build an initial form
        form_list = get_form_list(base_items)

        # base on club_officers.html
    return render_to_response('md_directory/struct_zones.html', {'form_list':form_list, 'name': models.Struct.objects.get(pk=struct_id), 
                                                          'base_type': base_type, 'group_type': group_type, 'id': struct_id})

@login_required
def club_addresses(request, struct_id):
    ''' Display addresses for the clubs in a District
    '''

    try:
        struct_id = int(struct_id)
    except:
        # Could not obtain instance, report bad ID
        return HttpResponse("%s is an invalid struct id" % struct_id)    

    # obtain a list of clubs

    clubs = [(c.id, ';'.join([c.meet_time] + [getattr(c, 'add%d' % i) for i in range(1,6)]), c.__unicode__()) for c in models.Club.objects.filter(struct=struct_id)]
    clubs.sort(key=lambda s: s[2])

    return render_to_response('md_directory/club_addresses.html', {'clubs':clubs, 'name':models.Struct.objects.get(id=struct_id).name})

@login_required
def struct_officers(request, id, year=None):
    ''' Obtain officers for district or MD
    '''
    # check if permitted to edit this struct
    edit, response = permissions.can_edit_dist(request.user, id)
    if not edit:
        return render_to_response('md_directory/not_auth.html', {'response':response})        

    if not year:
        year = get_current_year()
    #check if year is an int
    try:
        year = int(year)
    except:
        return HttpResponse("%d is not a valid year" % year)            
    try:
        id = int(id)
    except:
        # Could not obtain instance, report bad ID
        return HttpResponse("%d is an invalid district or multiple district id" % id)    

    struct = models.Struct.objects.get(id=id)
    md = struct.type_id == 1
    titles = {0:[5,7,8,9,10], 1:[11,13,14,15]}[md]

    #obtain queryset to limit chairs
    table = []
    for t in titles:
        q = models.StructOfficer.objects.filter(struct=id).filter(year=year).filter(office=str(t))
        if q:
            q = q[0]
            d = {'office':q.office, 'member':q.member, 'email':q.email, 'id':t}
        else:
            d = {'office': models.OfficerTitle.objects.get(pk=str(t)), 'member':'No office holder', 'email':'', 'id':t}
        table.append(d)

    return render_to_response('md_directory/struct_officers.html', {'table':table, 'name':struct.__unicode__(), 'year':year, 'id':id})

@login_required
def struct_chairs_mentors(request, id, year=None, off_type="chair"):
    # check if permitted to edit this struct
    edit, response = permissions.can_edit_dist(request.user, id)
    if not edit:
        return render_to_response('md_directory/not_auth.html', {'response':response})        

    if not year:
        year = get_current_year()
    #check if year is an int
    try:
        year = int(year)
    except:
        return HttpResponse("%d is not a valid year" % year)            
    try:
        id = int(id)
    except:
        # Could not obtain instance, report bad ID
        return HttpResponse("%d is an invalid district or multiple district id" % id)    

    types = {'chair': models.StructChair,
             'mentor': models.Mentor}
    struct = models.Struct.objects.get(id=id)
    md = struct.type_id == 1

    if off_type not in types:
        return HttpResponse("%s is an invalid type of district or multiple district officer" % off_type)    
    #obtain queryset to limit members
    
    q = types[off_type].objects.filter(struct=id).filter(year=year)

    table = []
    for obj in q:
        table.append({'member':obj.member, 'email':obj.email, 'id':obj.id})
        if hasattr(obj, 'office'):
            table[-1]['office'] = obj.office

    return render_to_response('md_directory/struct_chair_mentor.html', {'table':table, 'name':struct.__unicode__(), 'year':year, 'id':id, 'off_type': off_type})

@login_required
def struct_officeholder_edit(request, struct_id, year, office_id=None, office_type='chair', dg=False):
    from django.forms import ModelForm
    # check if permitted to edit this struct
    edit, response = permissions.can_edit_dist(request.user, struct_id)
    if not edit:
        return render_to_response('md_directory/not_auth.html', {'response':response})        

    model_dict = {'chair':models.StructChair, 'officer':models.StructOfficer, 'mentor': models.Mentor}
    if office_type not in model_dict.keys():
        return HttpResponse('%s is not a valid office_type' % office_type)            

    model = model_dict[office_type]
    if not year:
        year = get_current_year()
    #check if year is an int
    try:
        year = int(year)
    except:
        return HttpResponse("%d is not a valid year" % year)            

    try:
        struct = models.Struct.objects.get(pk=struct_id)
    except:
        # Could not obtain instance, report bad ID
        return HttpResponse("%s is an invalid struct id" % struct_id)    
    #only limit members if not an md
    from django.db.models import Q
    # Temporary removal to allow all members to be picked, as work-around
    # for club merging table requiring a more complicated Q field
    # than the expected short-term life span of this app can justify
    limit = Q()
    # if (struct.type_id == 1) or year < (get_current_year()):
    #     limit = Q()
    # else:
    #     limit = (Q(club__struct=struct_id)|Q(club=None))
    # exclude passed away people if current year
    if year == get_current_year():
        limit = limit & Q(deceased_b=False)
    # Set i to DB instance if an id is supplied, No otherwise
    if office_id:
        try:
            i = model.objects.filter(year=str(year)).filter(struct=struct)
            if office_type in ['chair', 'mentor']:
                i = i.filter(id=office_id)
            else:
                i = i.filter(office=office_id)                
            try:
                i = i[0]
            except:
                i = None
        except:
            # Could not obtain instance, report bad ID
            return HttpResponse("%s is an invalid id" % office_id)    
    else:
        i = None

    from string import ascii_uppercase
    inits = [(n,j) for n,j in enumerate(ascii_uppercase)]
    init_dict = dict([(v,k) for k,v in inits])

    if request.method == 'POST':
        init = inits[int(request.POST['init'])][1]
        if init != str(request.POST['member']).upper():
            initial = init
        else:
            initial = str(request.POST['member']).upper()
    else:
        if i and i.member:
            initial = str(i.member.last_name[0]).upper()
        else:
            initial = 'A'

    limit = limit & Q(last_name__istartswith=initial)
    model.member.field.rel.limit_choices_to = limit
 
    init_data = {'init':init_dict[initial]}
    class InitForm(forms.Form):
        init = forms.ChoiceField(choices=inits, initial=ascii_uppercase[0], widget=forms.Select(attrs={"onchange": "form_initial_submit()"}))
    
    # Create the form class.
    class Form(ModelForm):
        class Meta:
            model = model_dict[office_type]
            fields = []
            if office_type in ['chair']:
                fields.append('office')
                fields.append('committee_members')
                widgets={'office':forms.TextInput(attrs={'size':100}),
                         'committee_members':forms.TextInput(attrs={'size':100})}

            fields.extend(['member', 'email'])
 
        
    if office_type in ['officer']:
        title = models.OfficerTitle.objects.get(id=office_id)
    else:
        title = ''
    
    if request.method == 'POST':
        # if id exists, use it to retrieve the data
        form = Form(request.POST, instance=i)
        if form.is_valid(): # All validation rules pass
            if i:
                form.save()
            else:
                if office_type in ['mentor']:
                    obj = model(struct_id=struct_id, year=year, member=form.cleaned_data['member'], 
                                email=form.cleaned_data['email'])

                elif office_type in ['chair']:
                    office = office=form.cleaned_data['office']
                    obj = model(struct_id=struct_id, year=year, member=form.cleaned_data['member'], 
                                email=form.cleaned_data['email'], office=office, committee_members=form.cleaned_data['committee_members'])
                else:
                    office = title
                    obj = model(struct_id=struct_id, year=year, member=form.cleaned_data['member'], 
                                email=form.cleaned_data['email'], office=office, end_month=12)
                obj.save()
            if dg:
                return redirect('/struct/dgs/%s/' % (struct_id))
            return redirect('/struct/%ss/%d/%s/' % (office_type, year, struct_id))
    else:
        # Not a POST, build an initial form, using id if there is one
        form = Form(instance=i)
    initform = InitForm(init_data)
    context = {'form': form, 'struct_id': struct_id, 'year':year, 'office_id':office_id, 'name':struct, 'office_type':office_type, 'initform':initform}
    if dg:
        context['office_type'] = 'dg'
    if office_type in ['officer']:
        context['title'] = title
    return render_to_response('md_directory/struct_officeholder.html', context)

@login_required
def region_zone_chair_edit(request, id, year, obj):
    ''' Edit the details of the chair of a region or zone
    '''
    # get the model from the supplied obj
    model = getattr(models, obj.capitalize())
    model_chair = getattr(models, '%sChair' % obj.capitalize())
    # Set i to DB instance if an id is supplied, No otherwise
    try:
        item = model.objects.get(pk=id)
    except:
        # Could not obtain instance, report bad ID
        return HttpResponse("%s is an invalid %s" % (id, obj))    

    if not year:
        year = get_current_year()
    #check if year is an int
    try:
        year = int(year)
    except:
        return HttpResponse("%d is not a valid year" % year)            

    # check that obj is from the right list
    if obj not in ['region', 'zone']:
        return HttpResponse("%s is an invalid type" % obj)    

    # check if permitted to edit this zone or region
    edit, response = permissions.can_edit_dist(request.user, item.struct_id, obj)
    if not edit:
        return render_to_response('md_directory/not_auth.html', {'response':response})        

    # obtain instance
    i = model_chair.objects.filter(year=str(year)).filter(parent=id)
    if i:
        i = i[0]
    else:
        i = None

    # limit members to those from the item's district
    # Temporarily disabled to allow all members to be displayed -
    # as with other areas, complicated queries sufficient to handle
    # merging tables aren't justified by the expected lifespan of this app
    # limit = {'club__struct': item.struct_id}
    limit = {}

    # generate a drop-down list of initials and a dict to match the selected number against to get the correct initial
    from string import ascii_uppercase
    inits = [(n,j) for n,j in enumerate(ascii_uppercase)]
    init_dict = dict([(v,k) for k,v in inits])

    # if this is a POST, an initial will have been supplied
    if request.method == 'POST':
        # get the character submitted as the initial
        init = inits[int(request.POST['init'])][1]
        # determine if an initial was submitted which differs to the initial of the names in the member list
        if init != str(request.POST['member']).upper():
            # set new initial for the form
            initial = init
        else:
            # set the initial to what it currently is, as a new one hasn't been chosen
            initial = str(request.POST['member']).upper()
    else:
        # not a post, determine what initial should initially be
        if i:
            # there is an instance, use its initial
            initial = str(i.member.last_name[0]).upper()
        else:
            # no instance, use a default
            initial = 'A'

    # refine member limit to use only the initial and apply the limit
    limit['last_name__istartswith']=initial
    model_chair.member.field.rel.limit_choices_to = limit

    # A form to choose the initial. Applies a JS function if it is changed to prevent the need for a seperate submit button
    class InitForm(forms.Form):
        init = forms.ChoiceField(choices=inits, initial=ascii_uppercase[0], widget=forms.Select(attrs={"onchange": "form_initial_submit()"}))
    
    from django.forms import ModelForm
    class Form(ModelForm):
        class Meta:
            model = getattr(models, '%sChair' % obj.capitalize())
            fields = ['member', 'email']
    
    if request.method == 'POST':
        form = Form(request.POST, instance=i)
        if form.is_valid(): # All validation rules pass
            if i:
                form.save()
            else:
                # no instance, add a new item
                o = model_chair(parent=item, year=year, member=form.cleaned_data['member']) 
                o.save()
            return redirect('/%s/chair/' % obj)
    else:
        # Not a POST, build an initial form, using instance if there is one
        form = Form(instance=i)
    # create the init form, supplying the initial to use
    initform = InitForm({'init':init_dict[initial]})
    context = {'form': form, 'year':year, 'id':id, 'name':item.__unicode__(), 'initform':initform, 'type':obj}
    return render_to_response('md_directory/zone_region_chair.html', context)

@login_required
def s_mc_lobs_do_r_z_c_m(request, obj, id=0):
    ''' Edit the details of a struct, zone, club or region
    '''
    from django.forms import ModelForm

    print 'in s_mc_lobs_do_r_z_c_m'
    # check that obj is from the right list
    if obj not in ['struct', 'merch_centre', 'brightsight', 'dist_office', 'region', 'zone', 'club', 'member']:
        return HttpResponse("%s is an invalid type" % obj)    

    id = int(id)
    # get the model from the supplied obj
    model = get_model(obj)
    edit = True
    if id != 0:
        # try:
        if 1:
            i = model.objects.get(pk=id)
            # Determine if permission is available to edit this particular item:
            if obj == 'member':
                # Determine if club perms available
                edit, response = permissions.can_edit_club(request.user, i.club_id, obj)
            elif obj == 'club':
                # club user may edit their own club
                # Determine if club perms available
                edit, response = permissions.can_edit_club(request.user, i.id)
            elif obj == 'struct':
                # Determine if struct perms available
                edit, response = permissions.can_edit_dist(request.user, i.id)
            elif obj in ['merch_centre', 'brightsight', 'dist_office', 'region', 'zone']:
                # Determine if struct perms available
                edit, response = permissions.can_edit_dist(request.user, i.struct_id, obj)
            elif obj in ['merch_centre']:
                # Determine if struct perms available
                edit, response = permissions.can_edit_md(request.user, i.struct_id, obj)

            # check if one of the fields is from a list that should be limited by struct
            for a in ['zone', 'region', 'parent']:
                if hasattr(model, a) and hasattr(i, 'struct'):
                    getattr(model, a).field.rel.limit_choices_to = {'struct': i.struct}
        # except:
#     if not HANDLE_EXC: raise
        #     # Could not obtain instance, report bad id
        #     return HttpResponse("%s is an invalid %s id" % (id, obj))    
    else:
        i = None
        # Only dist users or above can add new clubs
        p = request.user.get_profile()
        if obj == 'club' and p.is_club:
            edit, response = (False, 'You do not have the necessary permissions to add new clubs to the system.')

    if not edit:
        return render_to_response('md_directory/not_auth.html', {'response':response})        

    # for forms which carry an id, if an id of 0 is input, calculate the next negative id to use
    import copy
    post =  copy.copy(request.POST)
    if ('id' in post) and (post['id'] == '0'):
        neg_id = str(int(model.objects.all().order_by('id')[0].id) - 1)
        post['id'] = neg_id

    # dict to hold preset form values, preset for various permission related reasons
    preset = {}

    class Form(ModelForm):
        class Meta:
            model = get_model(obj)
            exclude = []
            # if there is a real instance, exclude id as this should not be changed
            if id:
                exclude.append('id')
            # a dict keyed by objects which need altering, with the length as the value
            field_names = model._meta.get_all_field_names()
            wid = {'website':60, 'email':50, 'meet_time': 50, 'home_ph':50, 'cell_ph':50, 'bus_ph':50, 'fax':50, 
                   'tel':30, 'hours':60, 'manager_email':50, 'manager_cell_ph':50}
            for n in range(1,6):
                wid['add%d' % n] = 40
                wid['postal%d' % n] = 40                
            widgets = {}
            for w in wid.keys():
                if w in field_names:
                    widgets[w] = forms.TextInput(attrs={'size':wid[w]})

            # permission limitations
            p = request.user.get_profile()
            # if there is a club field, limit to a specific club if a club user, or clubs in the dist if a dist user
            if ('club' in field_names) and (obj == 'member'):
                if p.is_club:
                    # exclude club dropdown and set as a preset
                    exclude.append('club')
                    preset['club_id'] = p.club_id
                if p.is_dist:
                    # limit clubs to those in the district
                    model.club.field.rel.limit_choices_to = {'struct': p.struct}

            # if there is a zone field, limit to a specific zone if a club user, or zones in the dist if a dist user
            if ('zone' in field_names) and (obj == 'club'):
                if p.is_club:
                    # exclude zone dropdown and set as a preset
                    exclude.append('zone')
                    preset['zone_id'] = model.objects.get(pk=int(p.club_id)).zone_id
                if p.is_dist:
                    # limit zones to those in the district
                    model.zone.field.rel.limit_choices_to = {'struct': p.struct}

            if ('struct' in field_names) and (obj in ['club', 'zone', 'region', 'dist_office']):
                if p.is_club or p.is_dist:
                    # exclude zone dropdown and set as a preset
                    exclude.append('struct')
                    if p.is_club:
                        preset['struct_id'] = model.objects.get(pk=int(p.club_id)).struct_id
                    else:
                        preset['struct_id'] = p.struct_id
            
            # don't permit dist user to change MD of dist
            if ('md' in field_names) and (obj in ['struct']):
                if p.is_dist:
                    # exclude zone dropdown and set as a preset
                    exclude.append('md')
                    preset['md'] = model.objects.get(pk=int(p.struct_id)).md

    if request.method == 'POST':
        form = Form(post, instance=i)
        old = copy.copy(i)
        if form.is_valid(): # All validation rules pass
            table = []
            # How to determine the name of the object. The default of 'name' is used if no specific match is found
            if obj in ['member']:
                name = '%(first_name)s %(last_name)s' % form.cleaned_data
            elif obj in ['dist_office', 'brightsight']:
                name = obj
            else:
                name = '%(name)s' % form.cleaned_data

            if i:
                # Provide differing covering blurb depending on whether changes were made
                if form.has_changed():
                    blurb = 'The following details of %s have been changed:' % name
                else:
                    blurb = 'No changes were made to the details of %s' % name
                # Generate a list of changes made
                for c in form.changed_data:
                    try:
                        old_val = getattr(old, c)
                    except ObjectDoesNotExist:
                        old_val = None
                    # append label, old and new value to a list for table rendering
                    table.append((form.fields[c].label, old_val, form.cleaned_data[c]))
            # Store changes in DB and provide render confirmation page.
            else:
                blurb = '%s has been added to the system' % name
            # add presets to form
            save_obj = form.save(commit=False)
            for k,v in preset.items():
                setattr(save_obj, k, v)
            save_obj.save()
            
            # TODO: replace with confirmation and main menu return
            return index(request, blurb, table)
    else:
        # Not a POST, build an initial form, using instance if there is one
        form = Form(instance=i)

    return render_to_response('md_directory/s_mc_lobs_do_r_z_c_m.html', {'form': form, 'id': id, 'type':obj, 'title':get_label(obj)})

@login_required
def index(request, blurb='', table=''):
    ''' Show main index page
    '''
    # determine if user is a club user, showing correct page
    p = request.user.get_profile()
    if p.is_club:
        club = models.Club.objects.get(id=p.club_id)
        return render_to_response('md_directory/index_club.html', {'name':club.name, 'id':club.id, 'blurb':blurb, 'table':table})
    if p.is_dist:
        dist = models.Struct.objects.get(id=p.struct_id)
        return render_to_response('md_directory/index_dist.html', {'name':dist, 'id':dist.id, 'blurb':blurb, 'table':table})

    return render_to_response('md_directory/index.html')
