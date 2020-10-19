# -*- coding: utf-8 -*-
from __future__ import division
'''
Copyright © 2014 by Virginia Polytechnic Institute and State University
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

__author__ = "Aditya Nugur"
__credits__ = ""
__version__ = "3.5"
__maintainer__ = "Aditya Nugur""
__email__ = "aditya32@vt.edu"
__website__ = ""
__status__ = "Prototype"
__created__ = "2016-10-22 16:12:00"
__lastUpdated__ = "2016-10-25 13:25:00"
'''


from DeviceAPI.BaseAPI_Magnum import baseAPI_Magnum
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
debug = True


class API(baseAPI_Magnum):


    def API_info(self):
        return [{'device_model': 'M9TS1 Thermostat', 'vendor_name': 'eBox BACnet/IP', 'communication': 'BACnet',
                 'device_type_id': 1, 'api_name': 'API_MagnumThermostat', 'html_template': 'thermostat/magnum_thermostat.html',
                 'agent_type': 'BasicAgent', 'identifiable': False,'authorizable': False, 'is_cloud_device': False,
                 'schedule_weekday_period': 4, 'schedule_weekend_period': 4, 'allow_schedule_period_delete': True,
                 'chart_template': 'charts/charts_thermostat.html'},
                ]

    def dashboard_view(self):
        if self.get_variable(BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME) == BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.OFF:
            return {"top": BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME, "center": {"type": "number", "value": BEMOSS_ONTOLOGY.TEMPERATURE.NAME},
            "bottom": None}
        else:
            return {"top": BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME, "center": {"type": "number", "value": BEMOSS_ONTOLOGY.TEMPERATURE.NAME},
            "bottom": BEMOSS_ONTOLOGY.SETPOINT.NAME}

    def ontology(self):
        return {
"0x01A157DF [0] (14) Temperature (linear)": BEMOSS_ONTOLOGY.TEMPERATURE,
"0x01A157DF [0] (13) Turn-switch for fan": BEMOSS_ONTOLOGY.FAN_MODE ,
"0x01A157DF [0] (12) Rel. Humidity (linear)": BEMOSS_ONTOLOGY.RELATIVE_HUMIDITY,
"0x01A157DF [0] (11) Unoccupied Heating Limit": BEMOSS_ONTOLOGY.HEAT_SETPOINT,
"0x01A157DF [0] (10) Unoccupied Cooling Limit": BEMOSS_ONTOLOGY.COOL_SETPOINT,
"0x01A157DF [0] (7) Comfort Set point": BEMOSS_ONTOLOGY.SETPOINT,

}

    fmode_dict = {0: BEMOSS_ONTOLOGY.FAN_MODE.POSSIBLE_VALUES.AUTO,
                  1: BEMOSS_ONTOLOGY.FAN_MODE.POSSIBLE_VALUES.CIRCULATE,
                  2: BEMOSS_ONTOLOGY.FAN_MODE.POSSIBLE_VALUES.ON}

    # def getDataFromDevice(self):
    #
    #     returndata=dict()
    #
    #     bacnetread = self.Bacnet_read()
    #     for key, value in bacnetread.iteritems():
    #         if type(value)!= str and type(value)!= int:
    #             if key in ["0x01A157DF [0] (14) Temperature (linear)","0x01A157DF [0] (11) Unoccupied Heating Limit","0x01A157DF [0] (10) Unoccupied Cooling Limit","0x01A157DF [0] (7) Comfort Set point"]:
    #                 value=self.farenheitCon(value)
    #             bacnetread[key]=round(value,2)
    #     if "0x01A157DF [0] (13) Turn-switch for fan" in bacnetread.keys():
    #         bacnetread["0x01A157DF [0] (13) Turn-switch for fan"]=self.fmode_dict[bacnetread["0x01A157DF [0] (13) Turn-switch for fan"]]
    #     print bacnetread
    #     return bacnetread