from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from webapps.deviceinfos.models import DeviceMetadata
from webapps.device.models import Devicedata
from webapps.bemoss_accounts.models import BemossAccount, BemossToken
from webapps.alerts.models import Alerts, AlertTypes, PossibleEvents, Notification, NotificationChannelAddresses,\
    NotificationChannels, PriorityLevels
from webapps.bemoss_applications.models import ApplicationRegistered, ApplicationRunning
from webapps.buildinginfos.models import BuildingInfo, IOTGateway, ZoneInfo, GlobalSetting
from webapps.device.models import Devicedata
from webapps.deviceinfos.models import DeviceMetadata, DeviceType, SupportedDevices, Miscellaneous
from webapps.discovery.models import PasswordsManager
from django.contrib.auth.models import User, Group, Permission
from webapps.accounts.models import UserProfile
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from _utils.authentication import authorize_request, get_token, get_user

from bemoss_lib.utils.VIP_helper import vip_publish, vip_publish_bulk
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
from django.core.exceptions import ObjectDoesNotExist
import json
import settings
import uuid

import time
import settings
from webapps.charts.views import export_time_series_data_spreadsheet
from _utils.device_list_utils import get_device_list_and_count
from rest_framework.authentication import SessionAuthentication as OriginalSessionAuthentication

class SessionAuthentication(OriginalSessionAuthentication):
    def enforce_csrf(self, request):
        return


#Table to Model (t2m)
t2m = {
    "bemoss_account": BemossAccount,
    "bemoss_token": BemossToken,
    "building_info": BuildingInfo,
    "building_zone": ZoneInfo,
    "IOT_gateway": IOTGateway,
    "devicedata" : Devicedata,
    "device_info" : DeviceMetadata,
    "device_type": DeviceType,
    "supported_devices": SupportedDevices,
    "miscellaneous" : Miscellaneous,
    "password_manager": PasswordsManager,
    "auth_user": User,
    "auth_permission": Permission,
    "accounts_userprofile": UserProfile

}



@api_view(['GET', 'POST'])
def api_login(request):

    if 'username' in request.query_params:
        username = request.query_params['username']
    else:
        username = request.data['username']
    if 'password' in request.query_params:
        password = request.query_params['password']
    else:
        password = request.data['password']

    user = authenticate(username=username, password=password)

    if user is not None and user.is_active:
        # If the account is valid and active, we will send a JSON webtoken back that has the user id
        token, expiry_time = get_token(user)
        return Response({"user_id":user.id,"token":str(token),"expires_in":expiry_time})
    else:
        return Response({"message":"Invalid username or password"},status=status.HTTP_401_UNAUTHORIZED)






@api_view(['GET', 'POST'])
def get_list(request):

    valid, response, user = authorize_request(request)
    if not valid:
        return response

    authorized_buildings = user.userprofile.authorized_buildings()
    return_data = {}
    try:
        for building in authorized_buildings:
            return_data[building.name] = dict()
            return_data[building.name]['zipcode'] = building.zip_code
            return_data[building.name]['location'] = building.building_settings.get('location','')
            devices = Devicedata.objects.filter(agent__building=building,agent__approval_status="APR")
            for device in devices:
                if device.agent.device_type.device_type not in return_data[building.name]:
                    return_data[building.name][device.agent.device_type.device_type] = list()
                return_data[building.name][device.agent.device_type.device_type].append(device.as_json())

        return Response(return_data)
    except Exception as er:
        print er
        return Response({"message":"Internal failure"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def get_better_list(request):

    valid, response, user = authorize_request(request)
    if not valid:
        return response

    authorized_buildings = user.userprofile.authorized_buildings()
    return_data = {}
    try:
        for building in authorized_buildings:
            return_data[building.name] = dict()
            return_data[building.name]['zipcode'] = building.zip_code
            return_data[building.name]['settings'] = building.building_settings
            return_data[building.name]['description'] = building.description
            return_data[building.name]['devices'] = dict()
            devices = Devicedata.objects.filter(agent__building=building,agent__approval_status="APR")
            for device in devices:
                if device.agent.device_type.device_type not in return_data[building.name]['devices']:
                    return_data[building.name]['devices'][device.agent.device_type.device_type] = list()
                return_data[building.name]['devices'][device.agent.device_type.device_type].append(device.as_json())

        return Response(return_data)
    except Exception as er:
        print er
        return Response({"message":"Internal failure"}, status=status.HTTP_400_BAD_REQUEST)


def get_all_devices_list(request,approval_type):
    valid, response, user = authorize_request(request)
    if not valid:
        return response

    authorized_buildings = user.userprofile.authorized_buildings()
    return_data = {}
    try:
        for building in authorized_buildings:
            return_data[building.name] = dict()
            return_data[building.name]['zipcode'] = building.zip_code
            return_data[building.name]['settings'] = building.building_settings
            return_data[building.name]['description'] = building.description
            return_data[building.name]['devices'] = dict()
            devices = DeviceMetadata.objects.filter(approval_status=approval_type)
            for device in devices:
                if device.device_type.device_type not in return_data[building.name]['devices']:
                    return_data[building.name]['devices'][device.device_type.device_type] = list()
                return_data[building.name]['devices'][device.device_type.device_type].append(device.as_json())

        return Response(return_data)
    except Exception as er:
        print er
        return Response({"message": "Internal failure"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def get_pending_devices_list(request):
    return get_all_devices_list(request,"PND")

@api_view(['GET', 'POST'])
def get_approved_devices_list(request):
    return get_all_devices_list(request,"APR")


# @api_view(['GET', 'POST'])
# def get_full_info(request):
#
#     valid, response, user = validate_data(request, mode="retrieve")
#     if not valid:
#         return response
#
#     info = get_device_list_and_count(request,get_devices=True,user=user)
#
#     return Response(info)




@api_view(['POST'])
def get_data(request):
    valid, response, user = authorize_request(request)
    if not valid:
        return response
    data = request.data
    mac = data['mac']
    return_data = export_time_series_data_spreadsheet(request,mac,body=data)
    return return_data







@api_view(['GET', 'POST'])
def api_register(request):
    data = request.data
    token = uuid.UUID(data['token'])
    first_name = data['first_name']
    last_name = data['last_name']
    username = data['username']
    password = data['password']
    password_check = data['password_check']
    email = data['email']


    try:
            usertoken = BemossToken.objects.get(token=token)

            if password == password_check:
                if usertoken.email == email:


                        kwargs = data

                        new_user = create_user(request, usertoken, **kwargs)
                        BemossToken.objects.filter(token=token).delete()


                        try:
                            email = email
                            name = last_name+' '+first_name
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

                        return Response({"message": "User Successfully Registered"}, status=status.HTTP_200_OK)
                else:

                    return Response({"message": "Email address doesn\'t match with the token, please try again."}, status=status.HTTP_401_UNAUTHORIZED)
            else:

                return Response({"message": "Passwords doesn\'t match, please try again."}, status=status.HTTP_401_UNAUTHORIZED)


    except BemossToken.DoesNotExist:

        return Response({"message": "The Token you provided is invalid, please try again."}, status=status.HTTP_401_UNAUTHORIZED)

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
    new_user = User.objects.create_user(kwargs['username'], kwargs['email'], kwargs['password'])
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



@api_view(['GET', 'POST'])
def api_add_account(request):

    if 'contract_id' in request.data and 'account_name' in request.data and 'device_limit' in request.data \
            and 'devicechecks' in request.data and 'applicationchecks' in request.data and 'buildinglist' in request.data:
            try:
                data_dict = request.data
                contract_id = data_dict['contract_id'][0]
                account_name = data_dict['account_name'][0]
                owner_name = data_dict['owner_name'][0]
                owner_email = data_dict['owner_email'][0]
                device_limit = int(data_dict['device_limit'][0])
                devicechecks = data_dict['devicechecks']
                applicationchecks = data_dict['applicationchecks']
                buildinglist = data_dict['buildinglist']
                address=data_dict['address']

                new_account = BemossAccount(account_id=contract_id, account_name=account_name, device_limit=device_limit)
                new_account.save()
                for type in devicechecks:
                    new_account.device_type_allowed.add(DeviceType.objects.get(device_type__iexact=type))
                for application in applicationchecks:
                    new_account.applications_allowed.add(ApplicationRegistered.objects.get(app_name=application.lower()))
                i=0
                for building in buildinglist:

                    new_building = BuildingInfo(name=building,description=address[i])
                    i=i+1
                    new_building.account = new_account
                    new_building.save()

                token = uuid.uuid4()
                new_token = BemossToken(token = token, expiration_date= datetime.now()+timedelta(days=2))
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

                messages.success(request, "Thanks for creating an account!  ")
                return Response({"message": "New Account Successfully Created"}, status=status.HTTP_200_OK)
            except Exception as er:
                return Response({"message": "Failed to create new account"}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response({"message": "Please fill out all the information"}, status=status.HTTP_400_BAD_REQUEST)








