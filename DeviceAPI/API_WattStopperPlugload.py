# -*- coding: utf-8 -*-
from __future__ import division
'''
Copyright (C) 2014 by Virginia Polytechnic Institute and State University
All rights reserved
Virginia Polytechnic Institute and State University (Virginia Tech) owns the copyright for the BEMOSS software and its
associated documentation (“Software”) and retains rights to grant research rights under patents related to
the BEMOSS software to other academic institutions or non-profit research institutions.
You should carefully read the following terms and conditions before using this software.
Your use of this Software indicates your acceptance of this license agreement and all terms and conditions.
You are hereby licensed to use the Software for Non-Commercial Purpose only.  Non-Commercial Purpose means the
use of the Software solely for research.  Non-Commercial Purpose excludes, without limitation, any use of
the Software, as part of, or in any way in connection with a product or service which is sold, offered for sale,
licensed, leased, loaned, or rented.  Permission to use, copy, modify, and distribute this compilation
for Non-Commercial Purpose to other academic institutions or non-profit research institutions is hereby granted
without fee, subject to the following terms of this license.
Commercial Use If you desire to use the software for profit-making or commercial purposes,
you agree to negotiate in good faith a license with Virginia Tech prior to such profit-making or commercial use.
Virginia Tech shall have no obligation to grant such license to you, and may grant exclusive or non-exclusive
licenses to others. You may contact the following by email to discuss commercial use: vtippatents@vtip.org
Limitation of Liability IN NO EVENT WILL VIRGINIA TECH, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR REDISTRIBUTE
THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR
CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO
LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR A FAILURE
OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF VIRGINIA TECH OR OTHER PARTY HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGES.
For full terms and conditions, please visit https://bitbucket.org/bemoss/bemoss_os.
Address all correspondence regarding this license to Virginia Tech’s electronic mail address: vtippatents@vtip.org
__author__ =  "BEMOSS Team"
__credits__ = ""
__version__ = "3.5"
__maintainer__ = "BEMOSS Team""
__email__ = "aribemoss@gmail.com"
__website__ = ""
__status__ = "Prototype"
__created__ = "2016-10-24 16:12:00"
__lastUpdated__ = "2016-10-25 13:25:00"
'''

from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
from DeviceAPI.BaseAPI_WattStopper import baseAPI_Wattstopper
debug = True

TRANSLATOR = {"RELAY":{BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.ON:'active',
            BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.OFF:'inactive',
            }}

class API(baseAPI_Wattstopper):

    def __init__(self, parent=None,**kwargs):

        baseAPI_Wattstopper.__init__(self, converter=TRANSLATOR, parent=parent, **kwargs)

    def API_info(self):
        return [
            {'device_model': 'LMPL-201', 'vendor_name': 'WattStopper', 'communication': 'BACnet', 'support_oauth': False,
             'device_type_id': 3, 'api_name': 'API_WattStopperPlugload', 'html_template': 'plugload/plugload.html',
             'agent_type': 'BasicAgent', 'identifiable': True, 'authorizable': False, 'is_cloud_device': False,
             'schedule_weekday_period': 4, 'schedule_weekend_period': 4, 'allow_schedule_period_delete': True,
             'chart_template': 'charts/charts_plugload.html'}


                ]

    def dashboard_view(self):

        if self.get_variable(BEMOSS_ONTOLOGY.STATUS.NAME) == BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.ON:
            return {"top": None, "center": {"type": "image", "value": 'wattstopper_on.png'},
                    "bottom": BEMOSS_ONTOLOGY.STATUS.NAME, "image":"wattstopper_on.png"}
        else:
            return {"top": None, "center": {"type": "image", "value": 'wattstopper_off.png'},
                    "bottom": BEMOSS_ONTOLOGY.STATUS.NAME, "image":"wattstopper_off.png"}

    def ontology(self):
        return { "RELAY":BEMOSS_ONTOLOGY.STATUS}

    def identifyDevice(self):
        identifyDeviceResult = False
        postmsg=dict()

        result=False
        bacnetread = self.Bacnet_read()
        if bacnetread:
            value = bacnetread.get("RELAY")
        else:
            return identifyDeviceResult

        if value== BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.OFF:
            postmsg[BEMOSS_ONTOLOGY.STATUS.NAME] =  BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.ON
            result = self.sendcommand(postmsg)
        elif value== BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.ON:
             postmsg[BEMOSS_ONTOLOGY.STATUS.NAME] =  BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.OFF
             result = self.sendcommand(postmsg)
        else:
            return identifyDeviceResult

        if result:
            self.timeDelay(5)
            postmsg = {BEMOSS_ONTOLOGY.STATUS.NAME: value}
            status=self.sendcommand(postmsg)
            if status:
                identifyDeviceResult = True

        return identifyDeviceResult

    def preidentify_message(self):
        identifyDeviceResult = False
        # print(" {0}Agent for {1} is identifying itself by doing colorloop. Please observe your lights"
        #       .format(self.variables.get('agent_id', None), self.variables.get('model', None)))
        self.devicewasoff = 0
        if self.get_variable('status') == "OFF":
            self.devicewasoff = 1
            message={"status": "ON"}
            return message
        else:
            return {"status": "OFF"}


    def postidentify_message(self):
        if self.devicewasoff:
            return {"status": "OFF"}
        else:
            message = {"status": "ON"}
            return message