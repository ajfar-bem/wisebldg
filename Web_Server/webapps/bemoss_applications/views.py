import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import redirect

import datetime

from django.core.urlresolvers import reverse

from webapps.bemoss_applications.models import ApplicationRunning, ApplicationRegistered
from webapps.deviceinfos.models import DeviceMetadata
from webapps.device.models import Devicedata

from _utils.device_list_utils import get_device_list_and_count
from bemoss_lib.utils.VIP_helper import vip_publish
from bemoss_lib.utils.BEMOSS_globals import *
from webapps.buildinginfos.models import BuildingInfo
# Create your views here.

@login_required(login_url='/login/')
def application_main(request):
    # Display the main page of bemoss applications
    user_building = request.user.userprofile.authorized_buildings()
    apps = ApplicationRunning.objects.filter(building__in=user_building)
    return_data = {'apps': apps, 'fault_detection_preinfo':fault_detection_preinfo(user_building),
                   'thermostat_control_preinfo':thermostat_control_preinfo(user_building)}
    return_data.update(get_device_list_and_count(request))
    return render(request, 'applications/applications.html', return_data)

def application_add(request):
    if request.POST:
        # 1. Save configuration data
        _data = request.body
        _data = json.loads(_data)

        user_building = request.user.userprofile.authorized_buildings()
        app_building = BuildingInfo.objects.get(building_id=_data['app_data']['building'])
        if app_building in user_building:
            registered_app = ApplicationRegistered.objects.get(app_name__iexact=_data['app_name'])
            if registered_app.app_name in ['fault_detection','thermostat_control']:
                thermostat = DeviceMetadata.objects.get(agent_id=_data['app_data']['thermostat'])
                data = {'thermostat':thermostat.agent_id,'description':"For: " + thermostat.nickname }
            elif registered_app.app_name in ['dr_test']:
                data = {'description': "For: " + app_building.name}
            else:
                data = {}
            if registered_app:
                no = ApplicationRunning.objects.filter(app_type=registered_app).count()+1
                new_app = ApplicationRunning(start_time=datetime.datetime.now(),status='stopped',
                                          app_type=registered_app, app_data=data, app_agent_id='some_name')
                new_app.building = app_building
                new_app.save()
                new_app.app_agent_id = registered_app.app_name + str(new_app.id)
                new_app.save()
                if request.is_ajax():
                    return HttpResponse(json.dumps("success"))


def application_remove(request,app_agent_id):
    running_app = ApplicationRunning.objects.get(app_agent_id=app_agent_id)
    user_building = request.user.userprofile.authorized_buildings()
    if running_app and running_app.building in user_building:
        running_app.delete()
        vip_publish('ui','platformmanager','stop', app_agent_id) #stop the app agent

    return redirect('application-main')

@login_required(login_url='/login/')
def application_individual(request, app_agent_id):
    user_building = request.user.userprofile.authorized_buildings()
    try:
        running_app = ApplicationRunning.objects.get(app_agent_id=app_agent_id)
        app_type = running_app.app_type
    except ApplicationRunning.DoesNotExist:
        print "Invalid application id"
        raise Http404
    if app_type.app_name == 'iblc':
        return_data = illuminance_based_control(user_building,app_agent_id)
        return_data.update(get_device_list_and_count(request))
        return render(request, 'applications/illuminance_light_control.html', return_data)
    elif app_type.app_name == 'dr_test':
        return_data = demand_response_test(app_agent_id)
        return_data.update(get_device_list_and_count(request))
        return render(request, 'applications/demand_response_test.html', return_data)
    elif app_type.app_name == 'fault_detection':
        return_data = fault_detection_info(app_agent_id)
        return_data.update(get_device_list_and_count(request))
        return render(request, 'applications/fault_detection.html', return_data)
    elif app_type.app_name == 'thermostat_control':
        return_data = thermostat_control_info(user_building,app_agent_id)
        return_data.update(get_device_list_and_count(request))
        return render(request, 'applications/thermostat_control.html', return_data)
    elif app_type.app_name in ['plugload_scheduler','lighting_scheduler']:
        app_data = running_app.app_data
        device_mac = app_data['device_agent_id'].split('_')[-1]
        return redirect('view-device-schedule',device_mac)



def fault_detection_info(app_agent_id):
    data = {}
    app_info = ApplicationRunning.objects.get(app_agent_id=app_agent_id)
    thermostat_agent_id = app_info.app_data['thermostat']
    thermostat = DeviceMetadata.objects.filter(agent_id=thermostat_agent_id)[0]
    data.update({'thermostat': thermostat,'app_info': app_info, 'app_id': app_agent_id})
    return data

def fault_detection_preinfo(user_buildings):
    hvac_fault_apps = ApplicationRunning.objects.filter(app_type__app_name='fault_detection',building__in=user_buildings)
    used_thermostat_ids = []
    for app in hvac_fault_apps:
        used_thermostat_ids.append(app.app_data['thermostat'])

    available_thermostats = DeviceMetadata.objects.filter(approval_status='APR', device_type_id=1, building__in=user_buildings).exclude(
        agent_id__in=used_thermostat_ids)

    return {'available_thermostats':available_thermostats}


def thermostat_control_preinfo(user_buildings):
    thermo_control_apps = ApplicationRunning.objects.filter(app_type__app_name='thermostat_control',building__in=user_buildings)
    used_thermostat_ids = []
    for app in thermo_control_apps:
        used_thermostat_ids.append(app.app_data['thermostat'])

    available_thermostats = DeviceMetadata.objects.filter(approval_status='APR', device_type_id=1, building__in=user_buildings).exclude(
        agent_id__in=used_thermostat_ids)

    return {'available_thermostats': available_thermostats}


def thermostat_control_info(user_buildings,app_agent_id):
    data = {}

    app_info = ApplicationRunning.objects.get(app_agent_id=app_agent_id)
    thermostat_agent_id = app_info.app_data['thermostat']
    thermostat = DeviceMetadata.objects.filter(agent_id=thermostat_agent_id)[0]
    all_devices = DeviceMetadata.objects.filter(building__in=user_buildings)
    sensors = list()
    for device in all_devices:
        try:
            devicedata = Devicedata.objects.get(agent_id=device.agent_id)
            if 'temperature' in devicedata.data:
                sensors.append(device)
        except Devicedata.DoesNotExist:
            continue

    data.update({'thermostat': thermostat, 'app_info': app_info, 'app_id': app_agent_id, 'sensors':sensors})
    return data

def demand_response_test(app_agent_id):
    data = {}
    app = ApplicationRunning.objects.get(app_agent_id=app_agent_id)
    app_building = app.building_id
    available_hvac = DeviceMetadata.objects.filter(approval_status='APR', device_type_id=1, building_id=app_building)
    available_light = DeviceMetadata.objects.filter(approval_status='APR', device_type_id=2, building_id=app_building)
    available_plugload = DeviceMetadata.objects.filter(approval_status='APR', device_type_id=3, building_id=app_building)

    if 'devSelected' in app.app_data.keys():
        data.update(app.app_data)
        nickname = {}
        devs = app.app_data['devSelected']['hvac'].keys() + app.app_data['devSelected']['lighting'].keys() \
                + app.app_data['devSelected']['plugload'].keys()
        for dev in devs:
            nick = DeviceMetadata.objects.get(agent_id=dev).nickname
            nickname[dev] = nick
        if 'start' in app.app_data.keys():
            data.update({'start': app.app_data['start'],
                         'end': app.app_data['end']})
        else:
            data.update({'start': None,
                         'end': None})
        data.update({'nickname': nickname})
        data.update({'lights': app.app_data['devSelected']['lighting'],
                     'plugs': app.app_data['devSelected']['plugload'], 'app_id': app_agent_id,
                     'hvacs': app.app_data['devSelected']['hvac']})
    else:
        data.update({'lights': available_light, 'plugs': available_plugload, 'app_id': app_agent_id,
                 'hvacs': available_hvac})
    return data


def register_dr_devices(request, app_agent_id):
    if request.POST:
        _data = request.body
        _data = json.loads(_data)
        _data = [x.encode('utf-8') for x in _data]
        devSelected = {'hvac':{}, 'lighting':{}, 'plugload':{}}
        for agent_id in _data:
            dev = DeviceMetadata.objects.get(agent_id=agent_id)
            devSelected[dev.device_type.device_type.lower()][agent_id]=None
        app = ApplicationRunning.objects.get(app_agent_id=app_agent_id)
        app.app_data.update({'devSelected': devSelected})
        app.save()
        if request.is_ajax():
            return HttpResponse(json.dumps("success"))

def save_dr_config(request, app_agent_id):
    if request.POST:
        _data = request.body
        _data = json.loads(_data)
        app = ApplicationRunning.objects.get(app_agent_id=app_agent_id)
        app_data = app.app_data
        all_dev = [x.agent_id for x in DeviceMetadata.objects.all()]
        for item in _data:
            if item[0] == 'start_in':
                app_data['start'] = datetime.datetime.now() + datetime.timedelta(minutes=int(item[1]))
            elif item[0] == 'dr_duration':
                app_data['end'] = app_data['start'] + datetime.timedelta(minutes=int(item[1]))
            else:
                if item[0] not in all_dev:
                    continue
                else:
                    for dtype in ['plugload', 'lighting', 'hvac']:
                        if item[0] in app_data['devSelected'][dtype].keys():
                            if dtype in ['lighting', 'hvac']:
                                control = int(item[1])
                            else:
                                control = item[1]
                            app_data['devSelected'][dtype][item[0]] = control
                            continue
        app_data['start'] = str(app_data['start']).split('.')[0]
        app_data['end'] = str(app_data['end']).split('.')[0]
        app.app_data = app_data
        app.save()

        if request.is_ajax():
            return HttpResponse(json.dumps("success"))

def illuminance_based_control(user_buildings,app_agent_id):
    data = {}
    available_lights = DeviceMetadata.objects.filter(approval_status='APR', device_type_id=2,building__in=user_buildings)
    controllable_lights = list()
    for light in available_lights:
        try:
            dev_data = Devicedata.objects.get(agent_id=light.agent_id)
            if 'brightness' in dev_data.data:
                controllable_lights.append(light)
        except Devicedata.DoesNotExist:
            pass


    #TODO: currently there is no flag for light sensor, device model should not be hardcoded, should be updated later.
    available_sensors = DeviceMetadata.objects.filter(approval_status='APR', device_type_id=4, device_model='LMLS-400',building__in=user_buildings)
    app_info = ApplicationRunning.objects.get(app_agent_id=app_agent_id)
    data.update({'lights':controllable_lights, 'sensors':available_sensors, 'app_id': app_agent_id,
                 'app_info':app_info})

    return data

@login_required(login_url='/login/')
def save_and_start(request):
    if request.POST:
        # 1. Save configuration data
        user_building = request.user.userprofile.authorized_buildings()
        _data = request.body
        _data = json.loads(_data)
        app_agent_id = _data['app_id']
        try:
            app = ApplicationRunning.objects.get(app_agent_id=app_agent_id)
        except ApplicationRunning.DoesNotExist:
            return HttpResponse("Invalid Appliation ID",status=401)

        if app.building not in user_building:
            return HttpResponse("Unauthorized",status=401)

        app.status = 'started'
        app.save()
        if 'app_data' in _data.keys():
            app_data = _data['app_data'] #TODO validate app data so that the application cannot control devices not authorized
            save_app_data(app_agent_id, app_data)
        # 2. Start application
        app_agent = app.app_type.app_agent

        vip_publish('ui','platformmanager','start', app_agent + ' ' + app_agent_id)

        if request.is_ajax():
            return HttpResponse(json.dumps("success"))

@login_required(login_url='/login/')
def update_target_illuminance(request):
    if request.POST:
        # 1. Save configuration data
        user_building = request.user.userprofile.authorized_buildings()

        _data = request.body
        _data = json.loads(_data)
        app_id = _data[0]
        target = _data[1]
        try:
            app = ApplicationRunning.objects.get(app_agent_id=app_id)
        except ApplicationRunning.DoesNotExist:
            return HttpResponse("Invalid App ID",status=401)

        if app.building not in user_building:
            return HttpResponse("Unauthorized",status=401)

        try:
            message_to_agent = {
                "auth_token": "bemoss",
                "target": int(target)
            }

            vip_publish('ui',app_id,'update_target',json.dumps(message_to_agent))

            if request.is_ajax():
                return HttpResponse(json.dumps("success"))
        except ValueError:
            if request.is_ajax():
                return HttpResponse(json.dumps("invalid target"))

@login_required(login_url='/login/')
def calibrate(request):
    if request.POST:
        user_building = request.user.userprofile.authorized_buildings()

        # 1. Save configuration data
        _data = request.body
        _data = json.loads(_data)
        app_id = _data
        # 2. Start application
        try:
            app = ApplicationRunning.objects.get(app_agent_id=app_id)
        except ApplicationRunning.DoesNotExist:
            return HttpResponse("Invalid App ID", status=401)

        if app.building not in user_building:
            return HttpResponse("Unauthorized", status=401)

        message_to_agent = {
            "auth_token": "bemoss"
        }
        vip_publish('ui', app_id, 'calibrate', json.dumps(message_to_agent))

        if request.is_ajax():
            return HttpResponse(json.dumps("success"))


def save_app_data(app_agent_id, app_data):
    app = ApplicationRunning.objects.get(app_agent_id=app_agent_id)
    for key, value in app_data.items():
        app.app_data[key] = value
    app.save()
