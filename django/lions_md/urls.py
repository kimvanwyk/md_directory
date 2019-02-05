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
from django.conf.urls import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
                       # to INSTALLED_APPS to enable admin documentation:
#                           (r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                           (r'^admin/', include(admin.site.urls)),

                       # login page
                       (r'^login/$', 'django.contrib.auth.views.login'),
                       (r'^logout/$', 'django.contrib.auth.views.logout'),

                       # base index
                       (r'^$', 'lions_md.md_directory.views.index'),

                       # find a member
                       (r'^member/$', 'lions_md.md_directory.views_find.find_member'),

                       # Add 2011 Training Weekend Event
                       (r'^member/(?P<event>-?[^a0-9]\w+)/', 'lions_md.md_directory.views_find.find_member'),

                       # edit the officers of a club by year and officer title number
                       (r'^club/officers/(?P<year>-?\d+)/(?P<club_id>-?\d+)/$', 'lions_md.md_directory.views.club_officers'),
                       
                       # list the officers of a struct for supplied  year and struct id                       
                       (r'^struct/officers/(?P<year>-?\d+)/(?P<id>-?\d+)/$', 'lions_md.md_directory.views.struct_officers'),

                       # list the chairs of a struct for supplied  year and struct id                       
                       (r'^struct/chairs/(?P<year>-?\d+)/(?P<id>-?\d+)/$', 'lions_md.md_directory.views.struct_chairs_mentors'),

                       # list the mentors of a struct for supplied  year and struct id                       
                       (r'^struct/mentors/(?P<year>-?\d+)/(?P<id>-?\d+)/$', 'lions_md.md_directory.views.struct_chairs_mentors', {'off_type': 'mentor'}),

                       # list the addresses of a club for a given struct
                       (r'^club_addresses/(?P<struct_id>-?\d+)/$', 'lions_md.md_directory.views.club_addresses'),

                       # edit the zones of each club or regions of each zone for a given district
                       (r'^struct/(?P<group_type>-?\w+)list/(?P<struct_id>-?\d+)/$', 'lions_md.md_directory.views.club_zones'),

                       # edit the details of an officer or chair of a struct for supplied year, struct id and either the officer title number or the chair id
                       (r'^struct/(?P<office_type>-?\w+)s/(?P<year>-?\d+)/(?P<struct_id>-?\d+)/(?P<office_id>-?\d+)/$', 
                        'lions_md.md_directory.views.struct_officeholder_edit'),

                       # add a new chair of a struct for supplied year and struct id
                       (r'^struct/chairs/(?P<year>-?\d+)/(?P<struct_id>-?\d+)/add/$', 
                        'lions_md.md_directory.views.struct_officeholder_edit', {'office_type':'chair'}),

                       # add a new mentor of a struct for supplied year and struct id
                       (r'^struct/mentors/(?P<year>-?\d+)/(?P<struct_id>-?\d+)/add/$', 
                        'lions_md.md_directory.views.struct_officeholder_edit', {'office_type':'mentor'}),

                       # edit the chair of a zone or region selected by year and zone id
                       (r'^(?P<obj>-?\w+)/chair/(?P<year>-?\d+)/(?P<id>-?\d+)/$', 
                        'lions_md.md_directory.views.region_zone_chair_edit'),

                       # find a struct, region, zone or club to edit its details
                       (r'^(?P<obj>-?\w+)/$', 'lions_md.md_directory.views_find.find_s_mc_lobs_do_r_z_c'),

                       # edit the details of a struct, region, zone, club or member selected by struct id
                       (r'^(?P<obj>-?\w+)/(?P<id>-?\d+)/$', 
                        'lions_md.md_directory.views.s_mc_lobs_do_r_z_c_m'),

                       # add a struct, region, zone, club or member
                       (r'^(?P<obj>-?\w+)/add/$', 'lions_md.md_directory.views.s_mc_lobs_do_r_z_c_m'),

                       # find a struct, region, zone or club to edit its officers or chair(s) for a selected year
                       (r'^(?P<obj>[a-z]+)/(?P<dest>[a-z]+)/$', 'lions_md.md_directory.views_find.find_s_mc_lobs_do_r_z_c'),

                       # Provide a specified struct, region, zone or club to edit its officers or chair(s) for a selected year
                       (r'^(?P<obj>-?\w+)/(?P<dest>-?\w+)/(?P<item_id>-?\w+)/$', 'lions_md.md_directory.views_find.find_s_mc_lobs_do_r_z_c'),
)
