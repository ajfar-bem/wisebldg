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


from _utils.device_list_utils import get_device_list_and_count
from bemoss_lib.utils.security import decrypt_value
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from webapps.deviceinfos.models import DeviceMetadata, Miscellaneous, SupportedDevices
from _utils import config_helper
from _utils import device_list_utils as _helper
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from _utils.authentication import authorize_request
from bemoss_lib.utils.date_converter import tzNow

import httplib
import os
import time
import json
import urllib2
import logging
import settings
from django_web_server import settings_tornado
import _utils.defaults as __

from bemoss_lib.utils.VIP_helper import vip_publish

logger = logging.getLogger(__name__)
logger.level = logging.DEBUG

def get_zip_code():
    try:
        location_info = urllib2.urlopen('http://ipinfo.io/json').read()
        location_info_json = json.loads(location_info)
        zipcode = location_info_json['postal'].encode('ascii', 'ignore')
        return zipcode
    except urllib2.HTTPError, e:
        logger.error('HTTPError = ' + str(e.code))
    except urllib2.URLError, e:
        logger.error('URLError = ' + str(e.reason))
    except httplib.HTTPException, e:
        logger.error('HTTPException = ' + str(e.message))
    except Exception:
        import traceback
        logger.error('generic exception: ' + traceback.format_exc())

def get_weather_info(zipcode):
    # Get the zip according to your IP, if available:
    wu_key = settings.WUNDERGROUND_KEY

    try:
        # Get weather underground service key
        rs = urllib2.urlopen("http://api.wunderground.com/api/" + wu_key + "/conditions/q/" + zipcode + ".json")
    except urllib2.HTTPError, e:
        logger.error('HTTPError = ' + str(e.code))
    except urllib2.URLError, e:
        logger.error('URLError = ' + str(e.reason))
    except httplib.HTTPException, e:
        logger.error('HTTPException = ' + str(e.message))
    except Exception:
        import traceback
        logger.error('generic exception: ' + traceback.format_exc())

    ##print rs
    ##print zipcode

    ##json_string = rs.read() if rs != {} else {}
    try:
        location = 'Arlington, VA (Default, please update settings)'
        temp_f = '77'
        humidity = '10%'
        precip = '0.0'
        winds = '1.0'
        icon = 'mostlysunny'
        weather = 'Sunny'
    except Exception:
        location = 'Arlington, VA (Default, please update settings)'
        temp_f = '77'
        humidity = '10%'
        precip = '0.0'
        winds = '1.0'
        icon = 'mostlysunny'
        weather = 'Sunny'

    weather_icon = config_helper.get_weather_icon(icon)

    weather_info = {'location':location, 'temp_f':temp_f, 'humidity':humidity, 'precip':precip, 'winds':winds, 'weather':
        weather, 'weather_icon':weather_icon,'zip_code':22311}

    return weather_info

@login_required(login_url='/login/')
def devicedata_view(request, mac):
    if request.method == 'GET':

        try:
            device_info = DeviceMetadata.objects.get(mac_address=mac)
        except DeviceMetadata.DoesNotExist:
            return HttpResponse('Invalid Devices', status=404)
        if device_info.building not in request.user.userprofile.authorized_buildings():
            return HttpResponse('Unauthorized', status=401)

        template = SupportedDevices.objects.filter(device_model=device_info.device_model).values('html_template')[0]['html_template']
        context = RequestContext(request)
        username = request.session.get('user')
        agent_id = device_info.agent_id
        #Request a device monitor
        vip_publish(sender="ui",target='basicagent',topic='onDemandMonitor',message={'agent_id':agent_id})

        _data = _helper.get_page_load_data(agent_id)
        device_list_side_nav = get_device_list_and_count(request)
        if device_info.vendor_name=="Foscam":
            all_addresses=device_info.address
            local='http://'+all_addresses.split(",")[0]
            if local==all_addresses:
                remote=local
            else:
                remote = 'http://'+all_addresses.split(",")[1]

            device_info.local=local
            device_info.remote=remote
            device_info.comment=decrypt_value(device_info.config.get("password"))
        zip_code = device_info.building.zip_code
        weather_info = get_weather_info(zip_code)
        device_info.username = device_info.config.get("username") #put username and password directly into deviceinfo
        device_info.password = device_info.config.get("password")
        return_data = {'device_info': device_info, 'device_data': _data, 'weather_info':weather_info}
        return_data.update(device_list_side_nav)
        context.update({'return_data': return_data})
        return render(request, template, return_data)



@api_view(['GET', 'POST'])
def submit_devicedata_api(request):
    valid, response, user = authorize_request(request)
    if not valid:
        return response

    if request.method=='POST':
        try:
            user_buildings = user.userprofile.authorized_buildings()
            try:
                if 'agent_id' in request.query_params:
                    agent_id = request.query_params['agent_id']
                else:
                    agent_id = request.data['agent_id']
            except:
                return Response({"message":"agent_id missing in query params"},status=status.HTTP_400_BAD_REQUEST)

            try:
                device_info = DeviceMetadata.objects.get(agent_id=agent_id)
            except DeviceMetadata.DoesNotExist:
                return Response({"message":"No such device exists"},status=status.HTTP_400_BAD_REQUEST)

            if device_info.building not in user_buildings:
                return Response({"message": "User not authorized to control that"}, status=status.HTTP_400_BAD_REQUEST)


            post_data = request.data['data']
            post_data.update({"agent_id":agent_id})
            vip_publish('ui', "basicagent", 'update', post_data)
            logger.info("API Submiting Data to agent: " + str(post_data))
            return Response({"message":"success"})
        except Exception as er:
            print er
            return Response({"message":"Internal failure"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message":"Not a post request"})


@login_required(login_url='/login/')
def submit_devicedata(request):
    if request.method == 'POST':
        _data = request.body
        _data = json.loads(_data)
        agent_id = _data['agent_id']
        try:
            device_info = DeviceMetadata.objects.get(agent_id=agent_id)
        except DeviceMetadata.DoesNotExist:
            return HttpResponse('Invalid', status=401)

        if device_info.building not in request.user.userprofile.authorized_buildings():
            return HttpResponse('Unauthorized', status=401)

        vip_publish('ui',"basicagent",'update', _data)
        logger.info("Submiting Data: "+str(_data))


        if request.is_ajax():
            return HttpResponse(json.dumps(_data))

