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
from django.db import models
import datetime

club_types = [i for i in enumerate(['Lions Club', 'Branch Club', 'Lioness Club', 'Leos Club', 'Lion Ladies Club'])]
# weekdays are  1-based
weekdays = [i for i in enumerate(['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'], 1)]
weeks = [i for i in enumerate(['Each', 'First', 'Second', 'Third', 'Fourth', 'Fifth', 'Last'])]
phone_help_text = \
'''Any or all of the phone numbers may be left blank. 
Please enter phone numbers as "+27 (031) 123 4567", for eg'''

class OfficerTitle(models.Model):
    id = models.IntegerField(primary_key=True)    
    title = models.CharField('Title', max_length=100)    
    ip = models.ForeignKey('self', null=True, help_text = 'If this entry is for an Immediate Past Officer, this field holds the id of the actual officer to look up')

    class Meta:
        app_label = 'md_directory'
    
    def __unicode__(self):
        return self.title

class StructType(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.CharField('Type of struct', max_length=40)

    class Meta:
        app_label = 'md_directory'
        ordering = ['id']
        
    def __unicode__(self):
        return self.type

class Struct(models.Model):
    name = models.CharField('Structure Name', max_length=100)    
    parent = models.ForeignKey('self', null=True, blank=True, 
                               help_text = 'Set to name of parent Multiple District. Leave blank if this is already a Multiple District')
    website = models.URLField(blank=True)
    type = models.ForeignKey(StructType, verbose_name="Type of district", null=True, blank=True)
    in_use_b = models.BooleanField('Is struct in use?', blank=True)


    class Meta:
        app_label = 'md_directory'
        ordering = ['id']

    def __unicode__(self):
        if self.parent_id:
            try:
                i = self.parent.name
            except:
                i = ''
        else:
            i = ''
        n = '%s %s%s' % (self.type.type, i, self.name)            
        return n

class Region(models.Model):
    ''' Represent a region
    '''
    # id's of regions, starting at 1000
    id = models.IntegerField(primary_key=True)    
    name = models.CharField('Region Name', max_length=100)    
    struct = models.ForeignKey(Struct, verbose_name="Parent district")

    class Meta:
        app_label = 'md_directory'
        ordering = ['name']

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.struct)

class Zone(models.Model):
    ''' Represent a zone
    '''
    # id's of Zones, starting at 0
    id = models.IntegerField(primary_key=True)    
    # False if zone is not in a region
    in_region_b = models.BooleanField('Is zone in a region?', blank=True)
    region = models.ForeignKey(Region, null=True, blank=True, verbose_name="Region")
    name = models.CharField('Zone Name', max_length=100)    
    struct = models.ForeignKey(Struct, verbose_name="Parent district")

    class Meta:
        app_label = 'md_directory'
        ordering = ['struct', 'name']

    def __unicode__(self):
        return '%s %s' % (str(self.struct).split(' ')[1], self.name)
        # return self.name

class Club(models.Model):
    id = models.IntegerField(primary_key=True)
    parent = models.ForeignKey('self', verbose_name="Parent club", null=True, blank=True, help_text='Leave this blank if this is a regular Lions Club')
    struct = models.ForeignKey(Struct, verbose_name="Parent district")
    name = models.CharField('Club Name', max_length=100)
    type = models.IntegerField('Type of Club', choices=club_types)
    meet_time = models.CharField('Meeting time(s) and date(s)', blank=True, max_length=200,
                                 help_text='e.g. First Thursday 20:00; Tuesday after First Monday 19:30; Contact Secretary')
    add1 = models.CharField('First line of meeting venue or instruction', blank=True, max_length=200, 
                            help_text='e.g. 1 Victoria Street; Lions Clubhouse; Contact Secretary')
    add2 = models.CharField('Second line of meeting venue or instruction', blank=True, max_length=200) 
    add3 = models.CharField('Third line of meeting venue or instruction', blank=True, max_length=200) 
    add4 = models.CharField('Fourth line of meeting venue or instruction', blank=True, max_length=200) 
    add5 = models.CharField('Fifth line of meeting venue or instruction', blank=True, max_length=200) 
    postal1 = models.CharField('Postal Address 1', blank=True, max_length=200)
    postal2 = models.CharField('Postal Address 2', blank=True, max_length=200) 
    postal3 = models.CharField('Postal Address 3', blank=True, max_length=200) 
    postal4 = models.CharField('Postal Address 4', blank=True, max_length=200) 
    postal5 = models.CharField('Postal Address 5', blank=True, max_length=200) 
    po_code = models.CharField('Postal code', blank=True, max_length=20) 
    charter_year = models.IntegerField('Charter Year', blank=True, null=True) 
    website = models.URLField(blank=True, max_length=200)
    suspended_b = models.BooleanField('Is club under suspension?', blank=True)
    zone = models.ForeignKey(Zone, verbose_name="Zone", blank=True, null=True)
    closed_b = models.BooleanField('Is club closed?', blank=True)

    class Meta:
        ordering = ['name']
        app_label = 'md_directory'

    def __unicode__(self):
        name = self.name
        if self.type > 0:
            name += ' (%s)' % (club_types[self.type][1])
        return name

class ClubMerge(models.Model):
    id = models.IntegerField(primary_key=True)
    club = models.ForeignKey(Club, verbose_name="Club")
    new_struct = models.ForeignKey(Struct, verbose_name="New Struct")

class ClubType(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.CharField('Type of club', max_length=40)

    class Meta:
        ordering = ['type']
        app_label = 'md_directory'

class Meetings(models.Model):
    club = models.ForeignKey(Club)
    day = models.IntegerField('Meeting day', choices=weekdays)
    week = models.IntegerField('Week of month', choices=weeks)
    time = models.TimeField('Time of meeting')
    spec_ins = models.CharField('Special instructions', max_length=200, blank=True, help_text='ie Contact secretary for meeting details')

    class Meta:
        app_label = 'md_directory'

class Member(models.Model):
    id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    deceased_b = models.BooleanField('Has member been called to higher service?')
    resigned_b = models.BooleanField('Has member resigned?')
    partner = models.CharField(max_length=100, blank=True)
    partner_lion_b = models.BooleanField('Is partner a Lion?')
    join_date = models.IntegerField('Year of becoming a member', null=True, blank=True)
    home_ph = models.CharField('Home phone', max_length=50, blank=True)
    bus_ph = models.CharField('Business phone', max_length=50, blank=True)
    fax = models.CharField(max_length=50, blank=True)
    cell_ph = models.CharField('Cell phone', max_length=50, blank=True)
    email = models.EmailField(blank=True)
    club = models.ForeignKey(Club, null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        app_label = 'md_directory'

    def __unicode__(self):
        try:
            if not self.club_id:
                raise
            club = self.club
        except:
            club = "No club name"
        return '%s, %s%s (%s/%s)' % (self.last_name, self.first_name, '*' if self.deceased_b else '', club, self.id)

class MerchCentre(models.Model):
    struct = models.ForeignKey(Struct, verbose_name="District/MD")
    add1 = models.CharField('Address 1', blank=True, max_length=200)
    add2 = models.CharField('Address 2', blank=True, max_length=200) 
    add3 = models.CharField('Address 3', blank=True, max_length=200) 
    add4 = models.CharField('Address 4', blank=True, max_length=200) 
    add5 = models.CharField('Address 5', blank=True, max_length=200) 
    po_code = models.CharField('Postal code', blank=True, max_length=20) 
    tel = models.CharField('Phone', max_length=35, blank=True)
    fax = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    manager = models.ForeignKey(Member, null=True)
    fin_advisor = models.ForeignKey(Member, related_name='fin_advisor_set', null=True, verbose_name='Financial Advisor')
    contact_person = models.CharField('Contact Person', max_length=200) 
    website = models.URLField(blank=True)

    class Meta:
        ordering = ['struct']
        app_label = 'md_directory'

    def __unicode__(self):
        return '%s Merch Centre' % self.struct

class BrightSightOffice(models.Model):
    struct = models.ForeignKey(Struct, verbose_name="District/MD")
    add1 = models.CharField('Address 1', blank=True, max_length=200)
    add2 = models.CharField('Address 2', blank=True, max_length=200) 
    add3 = models.CharField('Address 3', blank=True, max_length=200) 
    add4 = models.CharField('Address 4', blank=True, max_length=200) 
    add5 = models.CharField('Address 5', blank=True, max_length=200) 
    po_code = models.CharField('Postal code', blank=True, max_length=20) 
    postal1 = models.CharField('Postal Address 1', blank=True, max_length=200)
    postal2 = models.CharField('Postal Address 2', blank=True, max_length=200) 
    postal3 = models.CharField('Postal Address 3', blank=True, max_length=200) 
    postal4 = models.CharField('Postal Address 4', blank=True, max_length=200) 
    postal5 = models.CharField('Postal Address 5', blank=True, max_length=200) 
    contact_person = models.CharField('Contact Person', max_length=200) 
    tel = models.CharField('Phone', max_length=35, blank=True)
    fax = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    manager = models.CharField('Manager', max_length=200) 
    manager_cell_ph = models.CharField('Manager cell phone', max_length=50, blank=True)
    manager_email = models.EmailField(blank=True)
    website = models.URLField(blank=True)

    class Meta:
        ordering = ['struct']
        app_label = 'md_directory'

    def __unicode__(self):
        return '%s Lions Operation Brightsight Office' % self.struct
 
class DistrictOffice(models.Model):
    struct = models.ForeignKey(Struct, verbose_name="District/MD")
    add1 = models.CharField('Address 1', blank=True, max_length=200)
    add2 = models.CharField('Address 2', blank=True, max_length=200) 
    add3 = models.CharField('Address 3', blank=True, max_length=200) 
    add4 = models.CharField('Address 4', blank=True, max_length=200) 
    add5 = models.CharField('Address 5', blank=True, max_length=200) 
    po_code = models.CharField('Postal code', blank=True, max_length=20) 
    postal1 = models.CharField('Postal Address 1', blank=True, max_length=200)
    postal2 = models.CharField('Postal Address 2', blank=True, max_length=200) 
    postal3 = models.CharField('Postal Address 3', blank=True, max_length=200) 
    postal4 = models.CharField('Postal Address 4', blank=True, max_length=200) 
    postal5 = models.CharField('Postal Address 5', blank=True, max_length=200) 
    tel = models.CharField('Phone', max_length=35, blank=True)
    fax = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    contact_person = models.CharField('Contact Person', max_length=200) 
    # the operating hours, free-form text
    hours = models.CharField('Operating hours', blank=True, max_length=200) 
    website = models.URLField(blank=True)
 
    class Meta:
        ordering = ['struct']
        app_label = 'md_directory'

    def __unicode__(self):
        return '%s District Office' % self.struct
 
class MerlCoordinators(models.Model):
    struct = models.ForeignKey(Struct)    
    year = models.IntegerField('Lionistic Year')
    member = models.ForeignKey(Member, null=True)
    class Meta:
        app_label = 'md_directory'

class Mentor(models.Model):
    struct = models.ForeignKey(Struct)    
    year = models.IntegerField('Lionistic Year')
    member = models.ForeignKey(Member, null=True)
    email = models.EmailField(blank=True, help_text='Specific email for this office. Leave blank if N/A')    
    class Meta:
        app_label = 'md_directory'
        
class ClubOfficer(models.Model):
    club = models.ForeignKey(Club)
    year = models.IntegerField('Lionistic Year')
    # Set initial choice limitation to prevent long load time finding all members when subsequent model choice will limit members anyhow
    member = models.ForeignKey(Member, null=True)
    email = models.EmailField(max_length=200, blank=True, help_text='Specific email for club office. Leave blank if N/A')    
    office = models.ForeignKey(OfficerTitle)
    po_code = models.CharField('Postal code', blank=True, max_length=20, help_text='Specific address for club office. Leave blank if N/A') 
    add1 = models.CharField('Postal Address 1', blank=True, max_length=200, help_text='Specific address for club office. Leave blank if N/A')
    add2 = models.CharField('Postal Address 2', blank=True, max_length=200, help_text='Specific address for club office. Leave blank if N/A') 
    add3 = models.CharField('Postal Address 3', blank=True, max_length=200, help_text='Specific address for club office. Leave blank if N/A') 
    add4 = models.CharField('Postal Address 4', blank=True, max_length=200, help_text='Specific address for club office. Leave blank if N/A') 
    phone = models.CharField('Club phone', max_length=25, blank=True)
    fax = models.CharField('Club Fax', max_length=25, blank=True)

    class Meta:
        ordering = ['office__id']
        app_label = 'md_directory'

    def __unicode__(self):
        return self.member_id

class StructOfficer(models.Model):
    struct = models.ForeignKey(Struct)
    year = models.IntegerField('Lionistic Year')
    member = models.ForeignKey(Member, null=True)
    end_month = models.IntegerField('Last month of office holding')
    email = models.EmailField(blank=True, help_text='Specific email for this office. Leave blank if N/A')    
    office = models.ForeignKey(OfficerTitle)

    class Meta:
        ordering = ['office__id']
        app_label = 'md_directory'

    def __unicode__(self):
        return '%d: %s --> %s' % (self.year, self.office, self.member)

class StructChair(models.Model):
    struct = models.ForeignKey(Struct)
    year = models.IntegerField('Lionistic Year')
    member = models.ForeignKey(Member, null=True)
    email = models.EmailField(blank=True, help_text='Specific email for this office. Leave blank if N/A')    
    committee_members = models.CharField("Committee Members", blank=True, max_length=200, help_text="Members of the office's committee. Leave blank if N/A")
    office = models.CharField(max_length=150)

    class Meta:
        ordering = ['office']
        app_label = 'md_directory'

    def __unicode__(self):
        return self.member_id

class RegionChair(models.Model):
    ''' Chairs of regions
    '''
    # the region of which the member is the chair
    parent = models.ForeignKey(Region, verbose_name="Region")
    member = models.ForeignKey(Member, null=True, limit_choices_to = {'club': 29189})
    year = models.IntegerField('Lionistic Year')
    email = models.EmailField(blank=True, help_text='Specific email for this office. Leave blank if N/A')    

    class Meta:
        app_label = 'md_directory'
        
class ZoneChair(models.Model):
    ''' Chairs of zones
    '''
    # the zone of which the member is the chair
    parent = models.ForeignKey(Zone, verbose_name="Zone")
    member = models.ForeignKey(Member, null=True, limit_choices_to = {'club': 29189})
    year = models.IntegerField('Lionistic Year')
    email = models.EmailField(blank=True, help_text='Specific email for this office. Leave blank if N/A')
    assistant = models.ForeignKey(Member, null=True, related_name='assistant_set', limit_choices_to = {'club': 29189})

    class Meta:
        app_label = 'md_directory'

class EventAttendance(models.Model):
    ''' Member attendance at various events
    '''
    event = models.CharField("Event", max_length=200)
    member = models.ForeignKey(Member, null=True, limit_choices_to = {'club': 29189})    

    class Meta:
        app_label = 'md_directory'

try:        
    import django.contrib.auth as auth
    ### User profile models managed here ###
    class Profile(models.Model):
        ''' Profile for user management, to set whether the user is a club (and which club)
        or a district/md and which one or a superuser.
        '''
        # whether user is a club
        is_club = models.BooleanField('Is user a club user?', blank=True)
        # Which club user is from. Use NULL if not a club user
        club = models.ForeignKey(Club, null=True)
        # whether user is a struct
        is_dist = models.BooleanField('Is user a District user?', blank=True)
        is_md = models.BooleanField('Is user a MD user?', blank=True)
        struct = models.ForeignKey(Struct, null=True)
        all_access = models.BooleanField('Can user access all records?', blank=True)
        user = models.OneToOneField(auth.models.User)

        class Meta:
            app_label = 'md_directory'

        def __unicode__(self):
            out = []
            for i in ['club', 'dist', 'md']:
                out.append('is_%s: %s (ID: %s)' % (i, getattr(self, 'is_%s' % i), self.struct_id))
            out.append('User: %s' % self.user)
            return '\n'.join(out)
except AttributeError:
    # ignore Profile errors as models file may be called without auth module being set up
    pass
