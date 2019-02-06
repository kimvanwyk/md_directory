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
from string import ascii_uppercase
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
import common_modules.models as models
# -----------------------------------------------------------------------------------------------------
# Permission handlers
# -----------------------------------------------------------------------------------------------------

HANDLE_EXC = False

def can_edit_club(user, club_id, in_club_item='club'):
    ''' Return a tuple of (permission to edit club specified in 'club_id', response to provide if such permission not granted)
    Permission is determined by examining the profile of the user
    'in_club_item' specifies the item in the club being checked for. Leave 'club' for club iself, or use "member"
    '''
    try:
        p = user.get_profile()
        # check for superuser
        if p.all_access:
            return (True, '')

        if in_club_item != 'club':
            in_club = '%ss in' % in_club_item
        else:
            in_club = ''

        # if user is a club user, check it is for the current club_id
        if p.is_club:
            try:
                user_club = models.Club.objects.get(id=p.club_id)
            except:
                if not HANDLE_EXC: raise
                return (False, 'Could not look up the club with which your user name is associated. Please contact the MDC for IT or the Directory Compiler should this problem persist')

                # check match
            if str(p.club_id) != str(club_id):
                return (False, 'You may only edit the details of %s your own club, %s' % (in_club, user_club))
            
            # permission granted
            return (True, '')

        # user is not a club user, pass off to dist or md handler
        match_club = models.Club.objects.get(id=club_id) 
        if p.is_dist:
            return can_edit_dist(user, match_club.struct_id, in_club_item)
        if p.is_md:
            return can_edit_md(user, match_club.struct.parent_id, in_club_item)
        return (False, 'You may only edit the details of %s your own club, %s' % (in_club, user_club))
    except:
        if not HANDLE_EXC: raise
        return (False, 'Could not retrieve your user profile to check your permissions. Please contact the MDC for IT or the Directory Compiler should this problem persist')

def can_edit_dist(user, dist_id, in_dist_item='district'):
    ''' Return a tuple of (permission to edit item specified in 'dist_id', response to provide if such permission not granted)
    Permission is determined by examining the profile of the user
    'in_dist_item' specifies the item in the dist being checked for. Leave None for district iself, or use "region", "zone", "club" etc
    '''
    try:
        p = user.get_profile()
        # check for superuser
        if p.all_access:
            return (True, '')
        if in_dist_item != 'district':
            in_dist = '%ss in' % in_dist_item
        else:
            in_dist = ''

        print in_dist_item
        if p.is_dist:
            try:
                user_dist = models.Struct.objects.get(pk=p.struct_id)
            except:
                if not HANDLE_EXC: raise
                return (False, 'Could not look up the district with which your user name is associated. Please contact the MDC for IT or the Directory Compiler should this problem persist')

            # check match
            if str(p.struct_id) != str(dist_id):
                return (False, 'You may only edit the details of %s your own district, %s' % (in_dist, user_dist))
            
            # permission granted
            return (True, '')

        # user is not a dist user, pass off to md handler
        match_dist = models.Struct.objects.get(id=dist_id)        
        if match_dist.parent_id and p.is_md:
            return can_edit_md(user, match_dist.parent_id, in_dist_item)
        return (False, 'You may only edit the details of %s your own district, %s' % (in_dist, user_dist))
    except:
        if not HANDLE_EXC: raise
        return (False, 'Could not retrieve your user profile to check your permissions. Please contact the MDC for IT or the Directory Compiler should this problem persist')

def can_edit_md(user, parent_id, in_md_item='MD'):
    ''' Return a tuple of (permission to edit item specified in 'parent_id', response to provide if such permission not granted)
    Permission is determined by examining the profile of the user
    'in_md_item' specifies the item in the md being checked for. Leave None for MD iself, or use "merch_centre" etc
    '''
    try:
        p = user.get_profile()
        # check for superuser
        if p.all_access:
            return (True, '')
        if in_md_item != 'MD':
            in_md = '%ss in' % in_md_item
        else:
            in_md = ''

        if p.is_md:
            try:
                if in_md_item:
                    in_md = 'MD with which the specified %s is associated' % in_md_item
                else:
                    in_md = 'specified MD'
                user_md = models.Struct.objects.get(id=p.struct_id)
            except:
                if not HANDLE_EXC: raise
                return (False, 'Could not look up the MD with which your user name is associated. Please contact the MDC for IT or the Directory Compiler should this problem persist')

            # check match
            if str(p.struct_id) != str(parent_id):
                return (False, 'You may only edit the details of %s your own MD, %s' % (in_md, user_md))
            
            # permission granted
            return (True, '')

        # user doesn't match anything, return False
        return (False, 'You may only edit the details of %s your own MD, %s' % (in_md, user_md))
    except:
        if not HANDLE_EXC: raise
        return (False, 'Could not retrieve your user profile to check your permissions. Please contact the MDC for IT or the Directory Compiler should this problem persist')

