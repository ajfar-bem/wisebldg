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

#__author__ = "Ashraful Haque"
#__credits__ = ""
#__version__ = "Plus"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2018-04-24"
#__lastUpdated__ = "2018-04-24"
'''

'''This API class is for an agent that want to communicate/monitor/control
devices that compatible with WeMo Dimmer'''

from DeviceAPI.BaseAPI_WeMo import baseAPI_WeMo
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY


class API(baseAPI_WeMo):
    def __init__(self, **kwargs):
        super(API, self).__init__(**kwargs)


    def API_info(self):
        return [{'device_model': 'Dimmer', 'vendor_name': 'Belkin International Inc.', 'communication': 'WiFi',
                 'device_type_id': 2, 'api_name': 'API_WeMoDimmer', 'html_template': 'lighting/lighting.html', 'support_oauth': False,
                 'agent_type': 'BasicAgent', 'identifiable': True, 'authorizable': False, 'is_cloud_device': False,
                 'schedule_weekday_period': 4, 'schedule_weekend_period': 4, 'allow_schedule_period_delete': True,'chart_template': 'charts/charts_lighting.html'}]

    def dashboard_view(self):
        if self.get_variable(BEMOSS_ONTOLOGY.STATUS.NAME) == BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.ON:
            return {"top": None, "center": {"type": "image", "value": 'wemoon.jpg'},
                    "bottom": BEMOSS_ONTOLOGY.STATUS.NAME, "image":"wemoon.png"}
        else:
            return {"top": None, "center": {"type": "image", "value": 'wemooff.jpg'},
                    "bottom": BEMOSS_ONTOLOGY.STATUS.NAME, "image":"wemooff.png"}

    def ontology(self):
      return {  "brightness": BEMOSS_ONTOLOGY.BRIGHTNESS,"status": BEMOSS_ONTOLOGY.STATUS}

   

