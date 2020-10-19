# -*- coding: utf-8 -*-
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

import ast
import json
import tablib
import _utils.defaults as __
import re
from _utils.device_list_utils import get_device_list_and_count
from webapps.deviceinfos.models import Miscellaneous
import pytz
from webapps.deviceinfos.models import SupportedDevices
from webapps.multinode.models import NodeInfo, NodeDeviceStatus

from webapps.multinode.models import NodeInfo

from webapps.deviceinfos.models import DeviceMetadata
from webapps.buildinginfos.models import ZoneInfo, GlobalSetting, IOTGateway
from webapps.device.models import Devicedata
from bemoss_lib.utils.BEMOSS_globals import *
from bemoss_lib.utils.VIP_helper import vip_publish, vip_publish_bulk
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, Template, Context
from django.shortcuts import render
from django.db.models import ObjectDoesNotExist
from datetime import datetime
from django.template import loader as template_loader

from django_web_server import *
import django_web_server.settings_tornado
from webapps.device.models import Devicedata
from webapps.schedule.models import Holiday
from webapps.discovery.models import PasswordsManager
from webapps.multinode.models import NodeInfo, NodeDeviceStatus
from django.views.decorators.csrf import csrf_protect
from webapps.buildinginfos.models import BuildingInfo

import settings
import _utils.defaults as __
from _utils.encrypt import encrypt_value
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from _utils.authentication import authorize_request
from bemoss_lib.utils.date_converter import tzNow

kwargs = {'subscribe_address': __.SUB_SOCKET,
                    'publish_address': __.PUSH_SOCKET}



@login_required(login_url='/login/')
def add_new_zone(request):
    if request.POST:
        _data = request.raw_post_data
        zone_id = ""
        a = re.compile("^[A-Za-z0-9_]{6,15}$")
        if (a.match(_data)):
            p = ZoneInfo.objects.get_or_create(zone_nickname=str(_data))
            zone_id = ZoneInfo.objects.get(zone_nickname=str(_data)).zone_id
            global_settings = GlobalSetting(id=zone_id, heat_setpoint=70, cool_setpoint=72, illuminance=67, zone_id=zone_id)
            global_settings.save()
            message = "success"
            if request.is_ajax():
                return HttpResponse(str(zone_id), content_type='text/plain')
        else:
            message = "invalid"
            if request.is_ajax():
                return HttpResponse("invalid", content_type='text/plain')
    

@login_required(login_url='/login/')
def save_changes_modal(request):
    if request.POST:
        _data = request.raw_post_data
        a = re.compile("^[A-Za-z0-9_]{6,15}$")
        _data = ast.literal_eval(_data)
        if a.match(_data['nickname']):
            agent_id = _data['id']
            nickname = _data['nickname']
            device_type_id = _data['device_type']
            device_class = DEVICE_CLASS[agent_id[:4]]
            device = device_class.get(id=agent_id)
            device.nickname = nickname
            device.save()

            # if device_type_id == '1THE' or device_type_id == '1NST' or device_type_id == '1HWT':
            #     device = Thermostat.objects.get(agent_id=device_id)
            #     device.nickname = nickname
            #     device.save()
            # elif device_type_id == '1VAV':
            #     device = VAV.objects.get(agent_id=device_id)
            #     device.nickname = nickname
            #     device.save()

            message = {'status':'success',
                       'agent_id':agent_id,
                       'nickname':nickname}
            if request.is_ajax():
                return HttpResponse(json.dumps(message), content_type='application/json')
        else:
            message = "invalid"
            if request.is_ajax():
                return HttpResponse(json.dumps(message), content_type='application/json')


@api_view(['GET', 'POST'])
def save_zone_nickname_change_api(request):
    valid, response, user = authorize_request(request)
    if not valid:
        return response
    if request.method=='POST':
        user_building = user.userprofile.authorized_buildings()[0]
        post_data = request.data
        try:

            return Response({"message":"success"})
        except Exception as er:
            print er
            return Response({"message":"Internal failure"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message":"success"})


@login_required(login_url='/login/')
def save_zone_nickname_change(request):
    context = RequestContext(request)
    if request.method=='POST':
        _data = request.read()
        # _data = request.body
        a = re.compile("^[A-Za-z0-9_]{6,15}$")
        _data = ast.literal_eval(_data)
        if a.match(_data['nickname']):

            nickname = _data['nickname']
            agent_id = _data['id']
            message = {'status': 'success',
                       'agent_id': agent_id,
                       'nickname': nickname}
            device_instance = DeviceMetadata.objects.get(agent_id=agent_id)
            device_instance.nickname = nickname
            device_instance.save()
            if request.is_ajax():
                return HttpResponse(json.dumps(message), content_type='application/json')
        else:
            message = "invalid"
            if request.is_ajax():
                return HttpResponse(json.dumps(message), content_type='application/json')

@login_required(login_url='/login/')
def save_building_nickname_change(request):
    context = RequestContext(request)
    if request.method=='POST':
        _data = request.read()
        # _data = request.body
        a = re.compile("^[A-Za-z0-9_]{6,15}$")
        _data = ast.literal_eval(_data)
        if a.match(_data['nickname']):

            nickname = _data['nickname']
            node_id = _data['id']
            message = {'status': 'success',
                       'node_id': node_id,
                       'nickname': nickname}
            node_instance = NodeInfo.objects.get(node_id=node_id)
            node_instance.node_name = nickname
            node_instance.save()

            #modify multinode json file
            with open(settings.MULTINODE_DATA_PATH, "r") as jsonFile:
                content = json.load(jsonFile)
            tmp = content["known_nodes"]
            tmpnode = tmp[int(node_id)]
            if content["this_node"] == tmpnode["name"]:
                content["this_node"] = nickname
            tmpnode["name"] = nickname

            with open(settings.MULTINODE_DATA_PATH, "w") as jsonFile:
                json.dump(content, jsonFile)

            vip_publish('ui','multinodeagent','update_multinode_data',{})
            if request.is_ajax():
                return HttpResponse(json.dumps(message), content_type='application/json')
        else:
            message = "invalid"
            if request.is_ajax():
                return HttpResponse(json.dumps(message), content_type='application/json')

@login_required(login_url='/login/')
def identify_device(request):
    if request.method=='POST':
        _data = request.read()
        _data = json.loads(_data)
        agent_id = _data['agent_id']
        try:
            device_info = DeviceMetadata.objects.get(agent_id=agent_id)
        except DeviceMetadata.DoesNotExist:
            return HttpResponse('Invalid', status=401)

        if device_info.building not in request.user.userprofile.authorized_buildings():
            return HttpResponse('Unauthorized', status=401)

        vip_publish('ui', agent_id, 'identify', "Identify Device")

        if request.is_ajax():
            return HttpResponse(json.dumps("success"), content_type='application/json')


@login_required(login_url='/login/')
def add_device(request):
    if request.method=='POST':
        _data = request.read()
        _data = json.loads(_data)
        vendor_name = _data["vendor"]
        device_model = _data["model"]
        Device_exists=SupportedDevices.objects.filter(device_model=device_model).exists()
        if Device_exists:
            return HttpResponse(json.dumps("Wrong"), content_type='application/json')
        elif vendor_name=="Foscam":
            device_type_id=7
            api_name="Ipcam"
            html_template="others/ipcam.html"
            chart_template="others/ipcam.html"
            is_cloud=True
            address = _data["address"]

        elif vendor_name=="Fronius":
            device_type_id = 6
            api_name ="FroniusInverter"
            html_template = 'der/solar.html'
            chart_template = "charts/charts_solar.html"
            is_cloud = False
            address=_data["address"]

        elif vendor_name=="Egauge":
            device_type_id = 5
            api_name ="eGauge"
            html_template = 'powermeter/egauge.html'
            chart_template = "charts/charts_egauge.html"
            is_cloud = False
            address=_data["address"]

        device = SupportedDevices(device_model=device_model, vendor_name=vendor_name, communication="Wifi", device_type_id=device_type_id, api_name=api_name, html_template=html_template,agent_type='BasicAgent',
                                  identifiable=False, authorizable=False,  is_cloud_device=is_cloud, schedule_weekday_period=4, schedule_weekend_period=4, allow_schedule_period_delete=True,chart_template=chart_template,
                                  address=address)
        device.save()
        if request.is_ajax():
            return HttpResponse(json.dumps("success"), content_type='application/json')

@login_required(login_url='/login/')
def add_gateway(request):
    if request.method=='POST':
        _data = request.read()
        _data = json.loads(_data)
        unique_id = _data["unique_id"]
        name = _data["name"]
        building=int(_data["building_id"])
        gateway_exists = IOTGateway.objects.filter(gateway=unique_id).exists()
        if gateway_exists:
            return HttpResponse(json.dumps("wrong"), content_type='application/json')
        building_info = BuildingInfo.objects.get(building_id=building) # _data["building_id"]
        gateway_entry=IOTGateway(gateway=unique_id,gateway_name=name,date_attached=datetime.now(),gateway_settings={} ,account_id=building_info.account_id, building_id=building,status="PND")
        gateway_entry.save()
        if request.is_ajax():
            return HttpResponse(json.dumps("success"), content_type='application/json')



@login_required(login_url='/login/')
def change_address(request):
    if request.method=='POST':
        _data = request.read()
        _data = json.loads(_data)
        address = _data["address"]
        device_instance = DeviceMetadata.objects.get(vendor_name="foscam")
        if device_instance:
            device_instance.address=address
            device_instance.save()
        if request.is_ajax():
            return HttpResponse(json.dumps("success"), content_type='application/json')

@login_required(login_url='/login/')
def node_status(request):
    context = RequestContext(request)

    if True or request.user.get_profile().group.name.lower() == 'admin':

        return render(request,
            'dashboard/node_discovery.html',
            get_device_list_and_count(request))
    else:
        return HttpResponseRedirect('/home/')


#Version 2.2
#Change: Includes the new field 'approval_status' for manual approval process
#@login_required(login_url='/login/')


@login_required(login_url='/login/')
@csrf_protect
def discover(request):
    print "Discovering devices"

    if True or request.user.get_profile().group.name.lower() == 'admin':
        req_context = RequestContext(request)
        username = request.user
        # template_loader = template_loader.get_template('dashboard/dashboard.html')
        return render(request, 'dashboard/discovery.html', get_device_list_and_count(request))

    else:
        return HttpResponseRedirect('/home/')




@login_required(login_url='/login/')
@csrf_protect
def gateway_devices(request):
    context = RequestContext(request)
    buildings = request.user.userprofile.authorized_buildings()
    device_list_side_nav = get_device_list_and_count(request)
    context.update(device_list_side_nav)
    if request.user.groups.filter(name='Admin').exists():
        data = {"building_list": buildings}
        data.update(get_device_list_and_count(request))
        return render(request, 'dashboard/gateway_devices.html', data)

    else:
        return HttpResponseRedirect('/home/')

@login_required(login_url='/login/')
def gateway_status(request):
    context = RequestContext(request)
    buildings = request.user.userprofile.authorized_buildings()
    device_list_side_nav = get_device_list_and_count(request)
    context.update(device_list_side_nav)
    if request.user.groups.filter(name='Admin').exists():
        gateways = IOTGateway.objects.filter(building__in=buildings)
        data = {"gateways": gateways}
        data.update(get_device_list_and_count(request))
        print gateways
        return render(request, 'dashboard/gateway_status.html', data)

    else:
        return HttpResponseRedirect('/home/')


def processChangeZone(data):
    command_group = list()
    status_change = dict()
    gateway_devices = dict()
    for row in data:
        # row = 'agent_id, Node_name, 'Nickname', 'Approved/pending'
        agent_id = row[0]
        building = BuildingInfo.objects.get(name__iexact=row[1])
        device_instance = DeviceMetadata.objects.get(agent_id=row[0])
        gateway = device_instance.gateway
        updated_approval_status = row[3]
        device_instance.building = building  # change field
        device_instance.nickname = row[2]
        device_instance.approval_status = updated_approval_status
        device_instance.save()
        if gateway:  # gateway exists,meaning it is a gateway controlled device
            if gateway.gateway not in gateway_devices:
                gateway_devices[gateway.gateway] = []
            gateway_devices[gateway.gateway].append((agent_id, updated_approval_status))

        if updated_approval_status == APPROVAL_STATUS.APR:
            command_group.append(('ui', 'basicagent', 'onDemandMonitor', {'agent_id':agent_id}))
        else:
            # command_group.append(('ui', 'baicagent', 'stop', agent_id))
            pass  # nothing to be done/ the device will not be polled from now on

    if gateway_devices:
        for gateway, status_change_list in gateway_devices.items():
            vip_publish("ui", "gatewayagent", "gateway_device_status_update" + "_" + str(gateway), status_change_list)
    vip_publish_bulk(command_group)


@api_view(['GET', 'POST'])
def change_zones_api(request):
    valid, response, user = authorize_request(request)
    if not valid:
        return response
    if request.method=='POST':
        user_building = user.userprofile.authorized_buildings()[0]
        post_data = request.data['data']
        try:
            processChangeZone(post_data)
            return Response({"message":"success"})
        except Exception as er:
            print er
            return Response({"message":"Internal failure"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message":"success"})



@login_required(login_url='/login/')
@csrf_protect
def change_zones(request):
    if request.method == 'POST' and request.body:
        gateway_device_list = []
        _data = request.body
        _data = json.loads(_data)
        processChangeZone(_data['data'])
        if request.is_ajax():
            return HttpResponse(json.dumps("success"), 'application/json')

@login_required(login_url='/login/')
def bemoss_home(request):
    req_context = RequestContext(request)
    username = request.user

    #template_loader = template_loader.get_template('dashboard/dashboard.html')
    return render(request,'dashboard/dashboard.html', get_device_list_and_count(request))


@login_required(login_url='/login/')
def network_status(request):
    print 'Network status page load'
    context = RequestContext(request)

    if request.user.groups.all()[0].name.lower() == 'admin':
        return render(request, 'dashboard/network_status.html', get_device_list_and_count(request))
    else:
        return HttpResponseRedirect('/home/')


@login_required(login_url='/login/')
def device_status(request):
    print 'Device status page load'
    context = RequestContext(request)

    if request.user.groups.filter(name__iexact = 'admin').exists():
        return render(request, 'dashboard/device_status.html', get_device_list_and_count(request))
    else:
        return HttpResponseRedirect('/home/')


@login_required(login_url='/login/')
def change_global_settings(request):
    if request.POST:
        _data = request.body
        _data = json.loads(_data)

        zone_id = _data['zone_id']
        zone = ZoneInfo.objects.get(zone_id=zone_id)
        gsettings = GlobalSetting.objects.get(zone_id=zone)
        gsettings.heat_setpoint = _data['heat_setpoint']
        gsettings.cool_setpoint = _data['cool_setpoint']
        gsettings.illuminance = _data['illumination']
        gsettings.save()

        if request.is_ajax():
            return HttpResponse(json.dumps("success"), content_type='application/json')


@login_required(login_url='/login/')
def zone_device_listing(request, building_id, device_type):
    context = RequestContext(request)
    username = request.user
    dev_list = get_device_list_and_count(request)
    building_id = building_id.lower()
    device_type = device_type

    try:
        if building_id == 'all':
            request_building = 'ALL BUILDINGS'
        elif int(building_id) in dev_list['building_names']:
            request_building = dev_list['building_names'][int(building_id)]
        else:
            return HttpResponse('Bad building name')
    except TypeError: #because building_id is not integer or 'all'
        return HttpResponse('Bad building name')

    if device_type not in dev_list['device_list']['all']['all'].keys():
        return HttpResponse('No such device exists')

    data = {'request_building_id':int(building_id), 'request_deviceType':device_type, 'request_building':request_building}

    data.update(dev_list)
    return render(request,
        'dashboard/devices.html',
        data)


@login_required(login_url='/login/')
def change_approval_status(agent_id, app_status_updated):
    d_info = DeviceMetadata.objects.get(agent_id=agent_id)
    current_approval_status = d_info.approval_status
    print current_approval_status

    updated_approval_status = APPROVAL_SHORT_CODE[app_status_updated]

    if updated_approval_status != current_approval_status:
        d_info.approval_status = updated_approval_status
        d_info.save()
    return True


def bemoss_settings(request):
    print 'BEMOSS Settings page load'
    context = RequestContext(request)

    holidays = [ob.as_json() for ob in Holiday.objects.filter(building=request.user.userprofile.authorized_buildings()[0])]
    print holidays

    zip = Miscellaneous.objects.get(key='zipcode')
    b_location = zip.value

    device_list_side_nav = get_device_list_and_count(request)

    data = {'holidays': holidays, 'b_location': b_location}

    data.update(device_list_side_nav)

    if request.user.groups.filter(name__iexact='admin').exists():
        return render(request,'dashboard/bemoss_settings.html',data)
    else:
        return HttpResponseRedirect('/home/')


@login_required(login_url='/login/')
def delete_holiday(request):
    if request.method == 'POST':
        _data = request.body
        _data = json.loads(_data)

        if _data['id']:
            h_date = _data['id']
            Holiday.objects.filter(date=h_date).delete()

        json_text = {"status": "success"}

        if request.is_ajax():
            return HttpResponse(json.dumps(json_text), content_type='application/json')


@login_required(login_url='/login/')
def add_holiday(request):

    if request.method == 'POST':
        _data = request.body
        _data = json.loads(_data)
        print _data

        _date = _data['date']
        if _date:
            _date = _date.split("T")
            _date = _date[0]
            _date = _date.split("-")
            year = int(_date[0])
            month = int(_date[1])
            day = int(_date[2])
            h_date = datetime(year, month, day).date()
            print _date
            if _data['desc'] == '':
                _data['desc'] = 'No Description'
            new_holiday = Holiday(date=h_date, description=_data['desc'])
            new_holiday.save()

            json_text = {"status": "success"}

            if request.is_ajax():
                return HttpResponse(json.dumps(json_text), content_type='application/json')
        else:
            json_text = {"status": "no date"}

            if request.is_ajax():
                return HttpResponse(json.dumps(json_text), content_type='application/json')


@login_required(login_url='/login/')
def update_zip(request):

    if request.body:
        message = json.loads(request.body)
        zip_code = message['b_loc']

        try:
            saved_zip = Miscellaneous.objects.get(key='zipcode')
            if saved_zip:
                saved_zip.value = zip_code
                saved_zip.save()
        except ObjectDoesNotExist:
            Miscellaneous(key='zipcode', value=str(zip_code)).save()

    json_text = "success"

    if request.is_ajax():
        return HttpResponse(json.dumps(json_text), content_type='application/json')

@login_required(login_url='/login/')
def export_all_device_information(request):
    _data_hvac = [ob.device_status() for ob in DeviceMetadata.objects.filter(approval_status='APR',device_type_id=1)]
    _data_hvac = data_this([_data_hvac], "Thermostat Devices")
    _data_lt = [ob.device_status() for ob in DeviceMetadata.objects.filter(approval_status='APR',device_type_id=2)]
    _data_lt = data_this([_data_lt], "lighting Devices")
    _data_pl= [ob.device_status() for ob in DeviceMetadata.objects.filter(approval_status='APR', device_type_id=3)]
    _data_pl = data_this([_data_pl], "Plugload Devices")
    _data_pm = [ob.device_status() for ob in DeviceMetadata.objects.filter(approval_status='APR', device_type_id=4)]
    _data_pm = data_this([_data_pm], "PowerMeter Devices")
    _data_ss = [ob.device_status() for ob in DeviceMetadata.objects.filter(approval_status='APR', device_type_id=5)]
    _data_ss = data_this([_data_ss], "Sensors Devices")
    _data_der = [ob.device_status() for ob in DeviceMetadata.objects.filter(approval_status='APR', device_type_id=6)]
    _data_der = data_this([_data_der], "DER Devices")
    devices = tablib.Databook((_data_hvac, _data_lt,_data_pl,_data_pm, _data_ss, _data_der))
    with open('bemoss_devices.xls', 'wb') as f:
        f.write(devices.xls)
    response = HttpResponse(devices.xls, content_type='application/vnd.ms-excel;charset=utf-8')
    response['Content-Disposition'] = "attachment; filename=bemoss_devices.xls"
    return response


def data_this(__data, sheetname):
    headers = ('Device Nickname', 'Zone', 'Device Model', 'Device Added On', 'Network Status', 'Last Scanned Time',
               'Last Offline Time')
    data = []
    data = tablib.Dataset(*data, headers=headers,  title=sheetname)
    for _data in __data:
        for device in _data:
            data.append((device['nickname'], device['mac'], device['device_model'],
                        str(device['date_added']),
                        device['network_status'],
                        str(device['last_scanned']),
                         str(device['last_offline'])))
    return data