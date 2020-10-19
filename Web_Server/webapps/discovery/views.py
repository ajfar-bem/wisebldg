from django.shortcuts import render


from webapps.deviceinfos.models import DeviceMetadata,SupportedDevices, Miscellaneous

import _utils.defaults as __
import ast

from django.forms.models import modelformset_factory
from webapps.discovery.forms import PasswordManagerForm

from _utils.encrypt import encrypt_value
import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from datetime import datetime
from _utils.device_list_utils import get_device_list_and_count
from webapps.discovery.models import PasswordsManager



from bemoss_lib.utils.VIP_helper import vip_publish, vip_publish_bulk
kwargs = {'subscribe_address': __.SUB_SOCKET,
          'publish_address': __.PUSH_SOCKET}

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from _utils.authentication import authorize_request
from bemoss_lib.utils.date_converter import tzNow









@login_required(login_url='/login')
def discover_devices(request):
    if request.user.groups.filter(name__iexact = 'admin').exists():
        context = RequestContext(request)
        try:
            discovery_status = Miscellaneous.objects.get(key='auto_discovery')
            print discovery_status.value
        except Miscellaneous.DoesNotExist:
            discovery_status = {'value':'not_started'}

        hvac = SupportedDevices.objects.filter(device_type_id=1)
        lt_loads = SupportedDevices.objects.filter(device_type_id=2)
        plugloads = SupportedDevices.objects.filter(device_type_id=3)
        sensors = SupportedDevices.objects.filter(device_type_id=4)
        power_meters = SupportedDevices.objects.filter(device_type_id=5)
        DER=SupportedDevices.objects.filter(device_type_id=6)
        camera=SupportedDevices.objects.filter(device_type_id=7)
        print lt_loads
        print hvac
        print power_meters
        print plugloads
        print sensors
        print DER

        device_list_side_nav = get_device_list_and_count(request)
        return_data = dict()
        return_data.update(device_list_side_nav)
        devices = {'hvac': hvac, 'lt_loads':lt_loads, 'plugloads':plugloads, 'sensors':sensors, 'power_meters':power_meters, "DER": DER, "camera":camera}
        return_data.update(devices)
        return_data.update({'discovery_status':discovery_status})

        return render(request,'discovery/manual_discovery.html', return_data
                                  )
    else:
        return HttpResponseRedirect('/home/')


@api_view(['GET', 'POST'])
def discover_new_devices_api(request):
    valid, response, user = authorize_request(request)
    if not valid:
        return response
    if request.method == 'POST':
        if 'data' not in request.data:
            return Response({"message": "POST data dict missing 'data'"}, status=status.HTTP_400_BAD_REQUEST)
        _data = request.data['data']
        authorized_buildings = user.userprofile.authorized_buildings()
        try:
            publish_messages = list()
            for building in authorized_buildings:
                message = {'devices': _data, 'building_id': building.building_id,
                           'account_id': user.userprofile.account.account_id}
                publish_messages.append(('ui', 'devicediscoveryagent', 'discovery_request', message))

            vip_publish_bulk(publish_messages)
            return Response({"message": "success"})
        except Exception as er:
            print er
            return Response({"message": "Internal failure"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message": "GET not supported"}, status=status.HTTP_400_BAD_REQUEST)


def discover_new_devices(request):
    if request.POST:
        _data = request.body
        _data = json.loads(_data)
        _data = [x.encode('utf-8') for x in _data]
        print _data
        authorized_buildings = request.user.userprofile.authorized_buildings()
        publish_messages = list()
        for building in authorized_buildings:
            message = {'devices': _data, 'building_id':building.building_id, 'account_id':request.user.userprofile.account.account_id}
            publish_messages.append(('ui','devicediscoveryagent','discovery_request', message))

        print publish_messages
        vip_publish_bulk(publish_messages)
        if request.is_ajax():
            return HttpResponse(json.dumps("success"))

def authenticate_device(request):
    if  request.method == 'POST' and request.body:
        _data = request.body
        _data = ast.literal_eval(_data)
        print _data
        agent_id = _data['agent_id']
        message = {'agent_id': agent_id}
        print message
        print type(message)

        try:
            device = DeviceMetadata.objects.get(agent_id=agent_id)
        except DeviceMetadata.DoesNotExist:
            return HttpResponse('Invalid device_id', status=401)

        if device.building not in request.user.userprofile.authorized_buildings():
            return HttpResponse('Unauthorized ', status=401)

        vip_publish('ui','approvalhelperagent','get_device_username', message)

        if request.is_ajax():
            return HttpResponse(json.dumps("success"), 'application/json')


@api_view(['GET', 'POST'])
def add_password_api(request):
    valid, response, user = authorize_request(request)
    if not valid:
        return response
    if request.method=='POST':
        user_building = user.userprofile.authorized_buildings()[0]
        return_data = {}
        try:
            passwords_dict=request.data['data']
            passwords_dict['last_modified'] = tzNow()
            mm = SupportedDevices.objects.get(device_model=passwords_dict['device_model'])
            passwords_dict['device_model'] = mm
            passwords_dict['password'] = encrypt_value(passwords_dict['password']).encode('utf8')
            new_password = PasswordsManager(**passwords_dict)
            new_password.building = user_building
            new_password = new_password.save()
            return Response({"message":"success"})
        except Exception as er:
            print er
            return Response({"message":"Internal failure"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def get_password_api(request):
    valid, response, user = authorize_request(request)
    if not valid:
        return response

    user_buildings = user.userprofile.authorized_buildings()
    return_data = {}
    try:
        result = [ob.as_json() for ob in PasswordsManager.objects.filter(building__in=user_buildings)]
        return Response(result)
    except Exception as er:
        print er
        return Response({"message":"Internal failure"}, status=status.HTTP_400_BAD_REQUEST)



@login_required(login_url='/login')
def password_manager(request):
    context = RequestContext(request)
    PasswordManagerFormSet = modelformset_factory(PasswordsManager, PasswordManagerForm)
    user_building = request.user.userprofile.authorized_buildings()[0] #use the first building as assigned building. #TODO add a building dropdown in the UI to let the user chose the building
    if request.method == 'POST':
        formset = PasswordManagerFormSet(request.POST)
        for form in formset:
            if form.is_valid():
                if form.cleaned_data:
                        form.cleaned_data['password'] = encrypt_value(form.cleaned_data['password']).encode('utf8')
                        password_data = form.save(commit=False)
                        password_data.last_modified = datetime.now()
                        password_data.building = user_building
                        password_data.save()
        password_manager_data = [ob.data_passwords_manager() for ob in PasswordsManager.objects.filter(building__in=request.user.userprofile.authorized_buildings())]
        formset = PasswordManagerFormSet(queryset=PasswordsManager.objects.filter(building__in=request.user.userprofile.authorized_buildings()))
    else:
        password_manager_data = [ob.data_passwords_manager() for ob in PasswordsManager.objects.filter(building__in=request.user.userprofile.authorized_buildings())]
        formset = PasswordManagerFormSet(queryset=PasswordsManager.objects.filter(building__in=request.user.userprofile.authorized_buildings()))
        # Allows initial pre-existing data to be rendered into the form.
        # When saving, previously saved data need to be treated as old data and ignored.
        # formset = PasswordManagerFormSet(initial=[ob.data_passwords_manager() for ob in
        # PasswordsManager.objects.all()])
    if request.user.is_superuser or request.user.groups.filter(name__iexact = 'admin'):
        data =  {'formset': formset, 'pwd_data': password_manager_data}
        data.update(get_device_list_and_count(request))
        return render(request,'discovery/password_manager.html',data)
    else:
        return HttpResponseRedirect('/home/')