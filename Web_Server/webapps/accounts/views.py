# -*- coding: utf-8 -*-


# Create your views here.
'''
Copyright (c) 2016, Virginia Tech
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
 following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the authors and should not be
interpreted as representing official policies, either expressed or implied, of the FreeBSD Project.

This material was prepared as an account of work sponsored by an agency of the United States Government. Neither the
United States Government nor the United States Department of Energy, nor Virginia Tech, nor any of their employees,
nor any jurisdiction or organization that has cooperated in the development of these materials, makes any warranty,
express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness or
any information, apparatus, product, software, or process disclosed, or represents that its use would not infringe
privately owned rights.

Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer, or
otherwise does not necessarily constitute or imply its endorsement, recommendation, favoring by the United States
Government or any agency thereof, or Virginia Tech - Advanced Research Institute. The views and opinions of authors
expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof.

VIRGINIA TECH – ADVANCED RESEARCH INSTITUTE
under Contract DE-EE0006352

#__author__ = "BEMOSS Team"
#__credits__ = ""
#__version__ = "2.0"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2014-09-12 12:04:50"
#__lastUpdated__ = "2016-03-14 11:23:33"
'''
from django.shortcuts import render
from bemoss_lib.communication.Email import EmailService
from django.db import transaction
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, QueryDict
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from _utils.lockout import LockedOut
from _utils.device_list_utils import get_device_list_and_count
from webapps.buildinginfos.models import ZoneInfo

from webapps.deviceinfos.models import DeviceType
from webapps.bemoss_applications.models import ApplicationRegistered
from webapps.bemoss_accounts.models import BemossAccount, BemossToken
from webapps.buildinginfos.models import BuildingInfo

from webapps.multinode.models import NodeInfo, NodeDeviceStatus
from forms import RegistrationForm, RegistrationForm1, ResetpasswordForm
import logging
import _utils.messages as _
import json
from django.views.decorators.csrf import ensure_csrf_cookie
from webapps.accounts.models import UserProfile, UserRegistrationRequests
from bemoss_lib.communication.Email import EmailService
import settings
emailservie = EmailService()
logger = logging.getLogger("views")

from datetime import datetime, timedelta
import uuid

from _utils.authentication import authorize_request
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@ensure_csrf_cookie
def login_user(request):
    print "User login request"
    # Obtain the context for the user's request.
    context = RequestContext(request)

    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']
        user = None
        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        try:
            user = authenticate(username=username, password=password)
        except LockedOut:
            messages.warning(request, 'Your account has been locked out because of too many failed login attempts.')

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user is not None:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                request.session['zipcode'] = '22204'
                logger.info("Login of user : %s", user.username)
                redirect_to = str(request.META.get('HTTP_REFERER', '/'))
                if redirect_to.__contains__('next='):
                    redirect_to = str(redirect_to).split('=')
                    redirect_to = redirect_to[1]
                    return HttpResponseRedirect(redirect_to)
                else:
                    return HttpResponseRedirect('/home/')
            else:
                # An inactive account was used - no logging in!
                messages.error(request, _.INACTIVE_USER)
                return HttpResponseRedirect('/login/')

        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            messages.error(request, _.INCORRECT_USER_PASSWORD)
            # return HttpResponse("Invalid login details supplied.")
            return HttpResponseRedirect('/login/')

    else:
        print request
        if request.user.is_authenticated():
            return HttpResponseRedirect('/home/')
        else:
            # The request is not a HTTP POST, so display the login form.
            # This scenario would most likely be a HTTP GET.
            return render(request,'accounts/login.html', {})


# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required(login_url='/login/')
def logout_user(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return HttpResponseRedirect('/login/')

@ensure_csrf_cookie
def register(request):
    if request.method == "POST":
        form = RegistrationForm1(request.POST)

        if form.is_valid():
            token = uuid.UUID(form["token"].value())
            try:
                usertoken = BemossToken.objects.get(token=token)

                if form["password1"].value() == form["password2"].value():
                    if usertoken.email == form["email"].value():

                        kwargs = form.cleaned_data

                        new_user = create_user(request, usertoken, **kwargs)

                        messages.success(request, "Thanks for creating an BEMOSS account!  Your login id is %s. "%
                                         kwargs['username'])
                        # return HttpResponseRedirect(reverse('registration_complete'))
                        BemossToken.objects.filter(token=token).delete()

                        try:
                            email = form["email"].value()
                            name = form["last_name"].value()+' '+form["first_name"].value()
                            emailService = EmailService()
                            email_fromaddr = settings.NOTIFICATION['email']['fromaddr']
                            email_username = settings.NOTIFICATION['email']['username']
                            email_password = settings.NOTIFICATION['email']['password']
                            email_mailServer = settings.NOTIFICATION['email']['mailServer']
                            emailService.sendEmail(email_fromaddr, email, email_username, email_password,
                                                   _.EMAIL_USER_APPROVED_SUBJECT,
                                                   _.EMAIL_USER_MESSAGE.format(name), email_mailServer,
                                                   html=True)

                        except Exception as er:
                            print er

                        return HttpResponseRedirect('register')
                    else:
                        error = 'Email address doesn\'t match with the token, please try again.'
                        messages.error(request, error)
                        return HttpResponseRedirect('register')
                else:
                    error = 'Passwords doesn\'t match, please try again.'
                    messages.error(request, error)
                    return HttpResponseRedirect('register')

            except BemossToken.DoesNotExist:
                error = 'The Token you provided is invalid, please try again.'
                messages.error(request, error)
                return HttpResponseRedirect('register')



        else:
            errors = json.dumps(form.errors)
            errors = json.loads(errors)
            for error in errors:
                print error
                message = ""
                for mesg in errors[error]:
                    message = message + "," + error + ":" + mesg
                message = message[:-1]
                message = message[1:]
                messages.error(request, message)

            return HttpResponseRedirect('register')

    else:
        return render(request,'accounts/registration_form.html', {})


@ensure_csrf_cookie
def forgotpassword_email(request):
    if request.method != "POST":
        return render(request,'accounts/forgot_password_email.html',{})

def change_password(request):
    if request.method == "POST":
        _data = request.body
        _data = json.loads(_data)
        username = _data['id_user_name']
        password = _data['old_password']
        password_new = _data['id_password_new_1']
        user = authenticate(username=username, password=password)
        if user is not None:
            json_text = {
                "status": "success"
            }
            u = User.objects.get(username=username)
            u.set_password(password_new)
            u.save()
            print "Password changed successfully"
            return HttpResponse(json.dumps(json_text), content_type='text/plain')  # This works

def email_password(request):
    if request.method == "POST":
        token_reset = uuid.uuid4()
        _data = request.body
        _data = json.loads(_data)
        email = _data['id_email_']
        u = User.objects.get(email=email)

        token = uuid.uuid4()
        new_token = BemossToken(token=token_reset, expiration_date=datetime.now() + timedelta(days=2))
        new_token.account = u.userprofile.account
        new_token.auth_user_group = u.userprofile.group
        new_token.email = email
        new_token.building = u.userprofile.building
        new_token.save()

        emailService = EmailService()
        # email settings
        email_fromaddr = settings.NOTIFICATION['email']['fromaddr']
        email_username = settings.NOTIFICATION['email']['username']
        email_password = settings.NOTIFICATION['email']['password']
        email_mailServer = settings.NOTIFICATION['email']['mailServer']
        emailService.sendEmail(email_fromaddr,email,email_username,email_password,_.EMAIL_USER_PASSWORD_CHANGE,
                              _.EMAIL_USER_PASSWORD_MESSAGE.format(u.username, token_reset),email_mailServer,html=True)
        json_text = {
                "status": "success"
        }
        return HttpResponse(json.dumps(json_text), content_type='text/plain')

def update_user_groups(new_user):
    user_role = new_user.userprofile.group.name
    new_user.groups = list()
    if user_role in ["Owner"]:
        new_user.groups.add(Group.objects.get(name="Owner"))
    if user_role in ["Admin","Owner"]:
        new_user.groups.add(Group.objects.get(name="Admin"))
    if user_role in ["Zone Manager","Admin","Owner"]:
        new_user.groups.add(Group.objects.get(name="Zone Manager"))
    if user_role in ["Tenant","Zone Manager","Admin","Owner"]:
        new_user.groups.add(Group.objects.get(name="Tenant"))

@transaction.atomic
def create_user(request, usertoken, *args, **kwargs):
    new_user = User.objects.create_user(kwargs['username'], kwargs['email'], kwargs['password1'])
    new_user.save()
    new_user.is_active = True
    new_user.first_name = kwargs['first_name']
    new_user.last_name = kwargs['last_name']
    

    newUserProfile = new_user.userprofile
    newUserProfile.account = usertoken.account
    newUserProfile.building = usertoken.building
    newUserProfile.zone = usertoken.zone
    newUserProfile.group = Group.objects.get(name=usertoken.auth_user_group.name)
    update_user_groups(new_user)
    newUserProfile.save()
    new_user.save()
    return new_user


@login_required(login_url='/login/')
def user_manager(request):

    isAdmin = request.user.groups.filter(name='Admin')
    if request.user.is_superuser or not isAdmin:
        return HttpResponse('Unauthorized',status=401)

    context = RequestContext(request)
    zones = ZoneInfo.objects.all()
    device_list_side_nav = get_device_list_and_count(request)
    context.update(device_list_side_nav)

    if request.user.groups.filter(name='Admin').exists():
        _users = User.objects.filter(userprofile__account=request.user.userprofile.account)
        authorized_buildings = request.user.userprofile.authorized_buildings()
        coworker_users = list() #Users who are also allowed to control one of the building you control
        for user in _users:
            if user.userprofile.building == None or user.userprofile.building in authorized_buildings:
                if user.groups.filter(name='Owner').exists() and not request.user.groups.filter(name='Owner').exists():
                    pass #if the user is a Owner, and you are not, then don't add that user
                else:
                    coworker_users.append(user)

        groups = Group.objects.all()
        data = {"users": coworker_users, 'zones': zones, 'groups': groups}
        data.update(get_device_list_and_count(request))
        print _users
        return render(request, 'accounts/user_manager_new.html', data)

    else:
        return HttpResponseRedirect('/home/')


@login_required(login_url='/login/')
def add_user(request):
    if request.method == "POST":
        _data = request.body
        _data = json.loads(_data)
        role = _data['data']['role'].strip()
        email = _data['data']['email'].strip()
        building = _data['data']['building'].strip()
        name = _data['data']['name'].strip()

        token = uuid.uuid4()
        new_token = BemossToken(token=token, expiration_date=datetime.now() + timedelta(days=2))
        new_token.account = request.user.userprofile.account
        new_token.email = email
        new_token.auth_user_group = Group.objects.get(name=role)
        if building == '':
            new_token.building = None
        else:
            new_token.building = BuildingInfo.objects.get(name=building,account=request.user.userprofile.account)
        new_token.save()
        try:

            emailService = EmailService()
            email_fromaddr = settings.NOTIFICATION['email']['fromaddr']
            email_username = settings.NOTIFICATION['email']['username']
            email_password = settings.NOTIFICATION['email']['password']
            email_mailServer = settings.NOTIFICATION['email']['mailServer']
            emailService.sendEmail(email_fromaddr, email, email_username, email_password,
                                   _.EMAIL_USER_TOKEN,
                                   _.EMAIL_USER_TOKEN_MESSAGE.format(name, token), email_mailServer,
                                   html=True)

        except Exception as er:
            print er

        print "user accounts activated"
        json_text = {
            "status": "success"
        }

        return HttpResponse(json.dumps(json_text), content_type='text/plain')


@login_required(login_url='/login/')
def modify_user_permissions(request):
    if request.method == "POST":
        _data = request.body
        _data = json.loads(_data)
        print _data

        for row in _data['data']:
            user = User.objects.get(id=row[0].strip())
            if user.is_superuser:
                continue #ignore changes to super-user
            user_role = Group.objects.get(name=row[1].strip())
            zone = row[2].strip().split()
            user.userprofile.zone = None #TODO zones are not implemented
            
            user.userprofile.group = user_role
            update_user_groups(user)
            user.userprofile.save()
            user.save()

        print "user accounts permissions modified"
        json_text = {
            "status": "success"
        }

        return HttpResponse(json.dumps(json_text), content_type='text/plain')


@login_required(login_url='/login/')
def delete_user(request):
    if request.method == "POST":
        _data = request.body
        _data = json.loads(_data)
        print _data

        user_id = _data['id']
        usr = User.objects.get(id=user_id)
        usr.delete()

        print "user account removed"
        json_text = {
            "status": "success"
        }

        return HttpResponse(json.dumps(json_text), content_type='text/plain')

def processAddAccount(data_dict):
    contract_id = data_dict['contract_id'][0]
    account_name = data_dict['account_name'][0]
    owner_name = data_dict['owner_name'][0]
    owner_email = data_dict['owner_email'][0]
    device_limit = int(data_dict['device_limit'][0])
    devicechecks = data_dict['devicechecks']
    applicationchecks = data_dict['applicationchecks']
    buildinglist = data_dict['buildinglist']

    new_account = BemossAccount(account_id=contract_id, account_name=account_name, device_limit=device_limit)
    new_account.save()
    for type in devicechecks:
        new_account.device_type_allowed.add(DeviceType.objects.get(device_type__iexact=type))
    for application in applicationchecks:
        new_account.applications_allowed.add(ApplicationRegistered.objects.get(app_name=application.lower()))

    for building in buildinglist:
        new_building = BuildingInfo(name=building)
        new_building.account = new_account
        new_building.save()

    token = uuid.uuid4()
    new_token = BemossToken(token=token, expiration_date=datetime.now() + timedelta(days=2))
    new_token.account = new_account
    new_token.email = owner_email
    new_token.auth_user_group = Group.objects.filter(name__iexact='Owner')[0]
    new_token.save()

    emailService = EmailService()
    email_fromaddr = settings.NOTIFICATION['email']['fromaddr']
    email_username = settings.NOTIFICATION['email']['username']
    email_password = settings.NOTIFICATION['email']['password']
    email_mailServer = settings.NOTIFICATION['email']['mailServer']
    emailService.sendEmail(email_fromaddr, owner_email, email_username, email_password,
                           _.EMAIL_USER_TOKEN,
                           _.EMAIL_USER_TOKEN_MESSAGE.format(owner_name, token), email_mailServer,
                           html=True)

@api_view(['GET', 'POST'])
def add_account_api(request):
    valid, response, user = authorize_request(request)
    if not valid:
        return response

    authorized_buildings = user.userprofile.authorized_buildings()
    return_data = {}
    try:
        return_data = processAddAccount(data_dict=request.data)

        return Response(return_data)
    except Exception as er:
        print er
        return Response({"message":"Internal failure"}, status=status.HTTP_400_BAD_REQUEST)


@login_required(login_url='/login/')
def add_account(request):
    if not request.user.is_superuser:
        return HttpResponse('Unauthorized',status=401)
    if request.method == "POST":

        if 'contract_id' in request.POST and 'account_name' in request.POST and 'device_limit' in request.POST\
                and 'devicechecks' in request.POST and 'applicationchecks' in request.POST and 'buildinglist' in request.POST:
            try:
                data_dict = dict(QueryDict.iterlists(request.POST))
                processAddAccount(data_dict)

                messages.success(request, "Thanks for creating an account!  ")
                return HttpResponseRedirect('add_account')
            except Exception as er:
                messages.error(request, er)
                return HttpResponseRedirect('add_account')

        else:
            error = 'Please fill all the required entries.'
            messages.error(request, error)
            return HttpResponseRedirect('add_account')
    else:
        Device_type = [ob.as_json() for ob in DeviceType.objects.all()]
        Application_type = [ob.as_json() for ob in ApplicationRegistered.objects.all()]
        return_data = {'device_type': Device_type, 'application_type': Application_type}
        return_data.update(get_device_list_and_count(request))
        return render(request, 'accounts/add_account.html', return_data)


@ensure_csrf_cookie
def reset_password(request):
    if request.method == "POST":
        form = ResetpasswordForm(request.POST)
        token = uuid.UUID(form["token"].value())
        try:
            usertoken = BemossToken.objects.get(token=token)

            if form["password1"].value() == form["password2"].value():
                if usertoken.email == form["email"].value():
                    target_user = User.objects.get(email=form["email"].value())
                    target_user.set_password(form["password1"].value())
                    target_user.save()
                    messages.success(request, "Your BEMOSS password has been reset")
                    # return HttpResponseRedirect(reverse('registration_complete'))
                    BemossToken.objects.filter(token=token).delete()
                    try:
                        email = form["email"].value()
                        name = target_user.first_name + ' ' + target_user.last_name
                        emailService = EmailService()
                        email_fromaddr = settings.NOTIFICATION['email']['fromaddr']
                        email_username = settings.NOTIFICATION['email']['username']
                        email_password = settings.NOTIFICATION['email']['password']
                        email_mailServer = settings.NOTIFICATION['email']['mailServer']
                        emailService.sendEmail(email_fromaddr, email, email_username, email_password,
                                               _.EMAIL_USER_PASSWORD_CHANGE,
                                               _.EMAIL_PASSWORD_RESET.format(name), email_mailServer,
                                               html=True)

                    except Exception as er:
                        print er

                    return HttpResponseRedirect('resetpassword')
                else:
                    error = 'Email address doesn\'t match with the token, please try again.'
                    messages.error(request, error)
                    return HttpResponseRedirect('resetpassword')

            else:
                error = 'Passwords doesn\'t match, please try again.'
                messages.error(request, error)
                return HttpResponseRedirect('resetpassword')

        except BemossToken.DoesNotExist:
            error = 'The Token you provided is invalid, please try again.'
            messages.error(request, error)
            return HttpResponseRedirect('resetpassword')

    else:
        return render(request,'accounts/reset_password.html', {})