# -*- coding: utf-8 -*-
# Authors: Kruthika Rathinavel
# Version: 2.0
# Email: kruthika@vt.edu
# Created: "2014-10-13 18:45:40"
# Updated: "2015-02-13 15:06:41"


# Copyright © 2014 by Virginia Polytechnic Institute and State University
# All rights reserved
#
# Virginia Polytechnic Institute and State University (Virginia Tech) owns the copyright for the BEMOSS software and
# and its associated documentation ("Software") and retains rights to grant research rights under patents related to
# the BEMOSS software to other academic institutions or non-profit research institutions.
# You should carefully read the following terms and conditions before using this software.
# Your use of this Software indicates your acceptance of this license agreement and all terms and conditions.
#
# You are hereby licensed to use the Software for Non-Commercial Purpose only.  Non-Commercial Purpose means the
# use of the Software solely for research.  Non-Commercial Purpose excludes, without limitation, any use of
# the Software, as part of, or in any way in connection with a product or service which is sold, offered for sale,
# licensed, leased, loaned, or rented.  Permission to use, copy, modify, and distribute this compilation
# for Non-Commercial Purpose to other academic institutions or non-profit research institutions is hereby granted
# without fee, subject to the following terms of this license.
#
# Commercial Use: If you desire to use the software for profit-making or commercial purposes,
# you agree to negotiate in good faith a license with Virginia Tech prior to such profit-making or commercial use.
# Virginia Tech shall have no obligation to grant such license to you, and may grant exclusive or non-exclusive
# licenses to others. You may contact the following by email to discuss commercial use:: vtippatents@vtip.org
#
# Limitation of Liability: IN NO EVENT WILL VIRGINIA TECH, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR REDISTRIBUTE
# THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR
# CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO
# LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR A FAILURE
# OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF VIRGINIA TECH OR OTHER PARTY HAS BEEN ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGES.
#
# For full terms and conditions, please visit https://bitbucket.org/bemoss/bemoss_os.
#
# Address all correspondence regarding this license to Virginia Tech's electronic mail address: vtippatents@vtip.org
from webapps.multinode.models import NodeInfo, NodeDeviceStatus
from webapps.buildinginfos.models import ZoneInfo, IOTGateway
from webapps.device.models import Devicedata
from webapps.deviceinfos.models import DeviceType, DeviceMetadata
from bemoss_lib.utils.BEMOSS_globals import *
from collections import OrderedDict
from bemoss_lib.utils.BEMOSS_globals import *
from webapps.alerts.models import Notification
from webapps.buildinginfos.models import BuildingInfo

def get_device_list_and_count(request,get_devices = True,user=None):

    if not user:
        user = request.user

    buildings = BuildingInfo.objects.filter(account=user.userprofile.account).order_by('name')
    gateway_count=0
    gateways=IOTGateway.objects.filter(status="APR")



    for gateway in gateways:
        gateway_count += 1
    if user.userprofile.building is None:
        user_buildings = buildings
    else:
        user_buildings = user.userprofile.authorized_buildings()

    building_names = OrderedDict()
    building_list = OrderedDict()
    building_count = 0
    building_id_list = list()

    for building in user_buildings:
        building_names[building.building_id] = building.name
        building_count += 1
        building_list[building.building_id] = building
        building_id_list.append(building.building_id)

    deviceTypes = DeviceType.objects.all()

    device_type_list = list()

    for device in deviceTypes:
        device_type_list.append(device.device_type)


    all_devices = DeviceMetadata.objects.filter(building__in=user_buildings).order_by('nickname')

    device_list = OrderedDict()
    device_list['all'] = OrderedDict()
    device_list['PND'] = OrderedDict()
    device_list['APR'] = OrderedDict()
    device_list['NBD'] = OrderedDict()
    device_count = OrderedDict()
    device_count['all'] = OrderedDict()
    device_count['PND'] = OrderedDict()
    device_count['APR'] = OrderedDict()
    device_count['NBD'] = OrderedDict()

    approval_ordering = APPROVAL_STATUS.full_names.keys() + ['all']
    building_id_ordering = building_id_list + ['all']
    device_type_ordering = device_type_list + ['all']

    def fill(approval_status, building_id, device_type, value=None):
        if approval_status not in device_list:
            device_list[approval_status] = OrderedDict()
            device_count[approval_status] = OrderedDict()

        if building_id not in device_list[approval_status]:
            device_list[approval_status][building_id] = OrderedDict()
            device_count[approval_status][building_id] = OrderedDict()

        if device_type not in device_list[approval_status][building_id]:
            device_list[approval_status][building_id][device_type] = list()
            device_count[approval_status][building_id][device_type] = 0

        if value:
            if get_devices:
                device_list[approval_status][building_id][device_type].append(value)

            device_count[approval_status][building_id][device_type] += 1


    #basic fill first
    for apr in approval_ordering:
        for b_id in building_id_ordering:
            fill(apr,b_id,'all')


    for device in all_devices:
        approval_stat = device.approval_status
        building_id = device.building.building_id
        device_type = device.device_type.device_type

        fill('all','all','all',device)
        fill(approval_stat, 'all', 'all', device)
        fill('all', 'all', device_type, device)

        fill(approval_stat, building_id, 'all', device)
        fill('all', building_id, device_type, device)
        fill(approval_stat, building_id, device_type, device)


        fill(approval_stat, 'all', device_type, device)


    # Re-order the device list

    ordered_device_list = OrderedDict()

    #create new device_list ordered according to ordering of the list above
    for ao in approval_ordering:
        if ao in device_list:
            if type(device_list[ao]) is OrderedDict:
                if ao not in ordered_device_list:
                    ordered_device_list[ao] = OrderedDict()
            else:
                ordered_device_list[ao] = device_list[ao]

            for bo in building_id_ordering:
                if bo in device_list[ao]:
                    if type(device_list[ao][bo]) is OrderedDict:
                        if bo not in ordered_device_list[ao]:
                            ordered_device_list[ao][bo] = OrderedDict()
                    else:
                        ordered_device_list[ao][bo] = device_list[ao][bo]

                    for do in device_type_ordering:
                        if do in device_list[ao][bo]:
                            ordered_device_list[ao][bo][do] = device_list[ao][bo][do]

    unseen_notifications = Notification.objects.filter(seen=False,building__in=user_buildings).order_by('-dt_triggered')
    if get_devices:
        return { 'device_list':ordered_device_list, 'device_count': device_count,'building_names': building_names, 'building_list':building_list,
                 'building_count':building_count, 'approval_full_name': APPROVAL_STATUS.full_names, "unseen_notifications":unseen_notifications,"gateway_devices":gateway_count}
    else:
        return {'device_count': device_count, 'building_list': building_list, 'building_names': building_names, 'building_count':building_count, "unseen_notifications":unseen_notifications,
                "gateway_devices": gateway_count}


def get_page_load_data(agent_id):

    print 'Accessing database....'
    initials = agent_id[:4]
    data = Devicedata.objects.get(agent_id=agent_id)
    return data


#

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