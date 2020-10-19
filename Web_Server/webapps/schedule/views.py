from django.shortcuts import render

import os
import shutil
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
# from _utils.page_load_utils import get_device_list_side_navigation
from _utils.device_list_utils import get_device_list_and_count
from webapps.deviceinfos.models import DeviceMetadata, DeviceType
from webapps.deviceinfos.models import SupportedDevices
from webapps.device.models import Devicedata
from webapps.schedule.models import schedule_data
from bemoss_lib.utils.BEMOSS_globals import *
from webapps.bemoss_applications.models import ApplicationRunning, ApplicationRegistered
from bemoss_lib.utils import  security
from django.contrib.auth.models import User
from _utils.authentication import authorize_request

import json
from _utils import config_helper

from bemoss_lib.utils.VIP_helper import vip_publish
from django_web_server import settings_tornado
from _utils import defaults as __

import  logging
logger = logging.getLogger("")



from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from _utils.authentication import authorize_request
from bemoss_lib.utils.date_converter import tzNow

@login_required(login_url='/login/')
def showSchedule(request,device_id):
    # return HttpResponse('No schedule yet for: ' + str(device_id) )

    user_group = request.user.groups.all().values_list('name', flat=True)
    if not ('Admin' in user_group or 'Zone Manager' in user_group):
        return HttpResponse("Need to be Admin or Zone-manager", status=401)

    mac = device_id.encode('ascii', 'ignore')
    device_info = DeviceMetadata.objects.get(mac_address=device_id)
    schedule_data, schedule_meta = get_schedule_data(device_id)
    device_list_side_nav = get_device_list_and_count(request, user=request.user)
    device_metadata = [ob.device_control_page_info() for ob in DeviceMetadata.objects.filter(mac_address=mac)]
    # print device_metadata
    device_id = device_metadata[0]['agent_id']
    device_model = device_metadata[0]['device_model']

    device_status = [ob.as_json() for ob in Devicedata.objects.filter(agent_id=device_id)]
    device_node = device_status[0]['node_id']
    device_nickname = device_status[0]['nickname']
    node_nickname = device_status[0]['node_nickname']

    disabled_range = get_disabled_date_ranges(schedule_data['schedulers'])
    schedule_json = json.dumps(schedule_data['schedulers'],encoding='ascii')
    schedule = schedule_data['schedulers']
    return_data = {'device_id': device_id, 'device_zone': device_node, 'zone_nickname': node_nickname,
                   'mac_address': mac,
                   'device_nickname': device_nickname, 'schedule': schedule,
                   'schedule_json': json.dumps(schedule),
                   'disabled_ranges': json.dumps(disabled_range), 'active_schedule': str(schedule_data['active']),
                   'schedule_meta': schedule_meta}
    return_data.update(device_list_side_nav)
    if device_info.device_type.device_type == 'HVAC':
        return render(request, 'schedule/thermostat_schedule.html', return_data)
    elif device_info.device_type.device_type == 'Lighting':
        return render(request, 'schedule/lighting_schedule.html', return_data)
    elif device_info.device_type.device_type == 'Plugload':
        return render(request, 'schedule/plugload_schedule.html', return_data)


device_id = ''



# @login_required(login_url='/login/')
def get_schedule_data(mac):

    #Check if schedule for this device exists
    device_metadata = [ob.device_control_page_info() for ob in DeviceMetadata.objects.filter(mac_address=mac)]
    device_id = device_metadata[0]['agent_id']
    device_model = device_metadata[0]['device_model']
    try:
        sch_data = schedule_data.objects.get(agent_id=device_id)
        device_schedule_data = sch_data.schedule
    except ObjectDoesNotExist:
        device_schedule_data = {"active": 'everyday',
                "schedulers": __.EMPTY_DEFAULT_SCHEDULES
            }

        schedule_data(agent_id=device_id, schedule=device_schedule_data).save()

    schedule_meta = [ob.get_schedule_info() for ob in SupportedDevices.objects.filter(device_model=device_model)]
    schedule_meta = json.dumps(schedule_meta[0])
    logger.debug(schedule_meta)

    return device_schedule_data, schedule_meta

@api_view(['POST', 'GET'])
def api_schedule_update(request):
    logger.debug("got api schedule update request")
    logger.debug(request.data)
    valid, response, user = authorize_request(request)
    if not valid:
        return response

    user_buildings = user.userprofile.authorized_buildings()
    try:
        if 'agent_id' in request.query_params:
            agent_id = request.query_params['agent_id']
        else:
            agent_id = request.data['agent_id']
    except:
        return Response({"message": "agent_id missing in query params"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        device_info = DeviceMetadata.objects.get(agent_id=agent_id)
    except DeviceMetadata.DoesNotExist:
        return Response({"message": "No such device exists"}, status=status.HTTP_400_BAD_REQUEST)

    if device_info.building not in user_buildings:
        return Response({"message": "User not authorized to control that"}, status=status.HTTP_400_BAD_REQUEST)

    if 'schedule_data' in request.data:
        schedule_data = request.data['schedule_data']
    else:
        schedule_data=request.data['data']

    schedule = {'everyday':schedule_data}
    schedule_type = 'everyday'
    logger.debug("Schedule sent:" +str(schedule_data))
    result = update_schedule(request,agent_id,schedule,schedule_type,user,rest_response=True)
    return result


@api_view(['POST', 'GET'])
def get_api_schedule(request):
    valid, response, user = authorize_request(request)
    if not valid:
        return response

    user_buildings = user.userprofile.authorized_buildings()
    try:
        if 'agent_id' in request.query_params:
            agent_id = request.query_params['agent_id']
        else:
            agent_id = request.data['agent_id']
    except:
        return Response({"message": "agent_id missing in query params"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        device = DeviceMetadata.objects.get(agent_id=agent_id)
    except DeviceMetadata.DoesNotExist:
        return Response({"message": "No such device exists"}, status=status.HTTP_400_BAD_REQUEST)

    if device.building not in user_buildings:
        return Response({"message": "User not authorized to control that"}, status=status.HTTP_400_BAD_REQUEST)

    device_mac = device.mac_address
    device_schedule_data, schedule_metadata = get_schedule_data(device_mac)
    schedule = device_schedule_data['schedulers']['everyday']
    return Response(schedule)

@login_required(login_url='/login/')
def update_device_schedule(request):

    _data = json.loads(request.body)
    print _data
    device_info = _data['device_info']
    device_info = device_info.split('/')
    device_id = device_info[2]
    device_type = device_info[1]
    device_zone = device_info[0]
    schedule_type = ''
    if 'everyday' in str(_data):
        schedule_type = 'everyday'
    elif 'weekdayweekend' in str(_data):
        schedule_type = 'weekdayweekend'
    elif 'holiday' in str(_data):
        schedule_type = 'holiday'

    user = request.user
    schedule=_data['schedule']
    result = update_schedule(request,device_id,schedule,schedule_type,user)
    return result



def update_schedule(request,device_id,schedule,schedule_type,user,rest_response=False):
    content = save_schedule(device_id, schedule, schedule_type, user)

    message_to_agent = {
        "user": user.get_full_name(),
        "scheduleData": content,
        "agent_id":device_id
    }

    device = DeviceMetadata.objects.get(agent_id=device_id)
    supported_device = SupportedDevices.objects.get(device_model=device.device_model)

    if supported_device.built_in_schedule_support:
        vip_publish('ui', 'basicagent', 'update', message_to_agent)
    else:
        vip_publish('ui', 'scheduleragent', 'triggerSchedule', message_to_agent)

    result = 'success'
    if rest_response:
        return Response({'success':1})
    else:
        return HttpResponse(json.dumps(result))


def save_schedule(device_id, _data, schedule_type, user):


    try:
        _json_data = schedule_data.objects.get(agent_id=device_id).schedule
    except ObjectDoesNotExist:
        _json_data = {"active": 'everyday',
                "schedulers": __.EMPTY_DEFAULT_SCHEDULES
            }

    _json_data['schedulers'][schedule_type] = _data[schedule_type]
    _json_data['user'] = user.get_full_name()
    _json_data['start_from'] = str(datetime.now())
    logger.debug(_json_data)
    schedule_file_content = _json_data
    sch_data = schedule_data(agent_id=device_id, schedule=schedule_file_content)
    sch_data.save()
    return schedule_file_content



def activate_schedule(device_type,device_id):
    #TODO: enable / disable schedules
    pass
    return {"Success":True}



@login_required(login_url='/login/')
def update_schedule_status_to_browser(request):
    print "device_schedule_update_message_to_browser"
    if request.method == 'POST':
        _data = request.raw_post_data
        device_info = _data
        device_info = device_info.split('/')
        device_type = device_info[1]
        device_id = device_info[2]
        topic = 'schedule_update_status'
        thermostat_update_schedule_status = config_helper.get_update_message(topic)
        print type(thermostat_update_schedule_status)
        data_split = str(thermostat_update_schedule_status).split("/")
        if data_split[0] == device_id:
            result = data_split[1]
        else:
            result = 'failure'
        json_result = {'status': result}
        #zmq_topics.reset_update_topic()
        print json.dumps(json_result)
        if request.is_ajax():
            return HttpResponse(json.dumps(json_result), content_type='application/json')


def get_disabled_date_ranges(_data):

    disabled_values = dict(__.EMPTY_DISABLED_VALUES)
    for sch_type in _data:
        if sch_type == 'holiday':
            for item in _data[sch_type]:
                value = []
                for _item in _data[sch_type]:
                    value.append(int(_item['at']))
                disabled_values[sch_type]['holiday'] = value
        else:
            for day in _data[sch_type]:
                for item in _data[sch_type][day]:
                    value = []
                    for _item in _data[sch_type][day]:
                        value.append(int(_item['at']))
                    disabled_values[sch_type][day] = value
    #print disabled_values
    return disabled_values

def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv


def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv
