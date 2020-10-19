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

Commercial Use If you desire to use the software for profit-making or commercial purposes,
you agree to negotiate in good faith a license with Virginia Tech prior to such profit-making or commercial use.
Virginia Tech shall have no obligation to grant such license to you, and may grant exclusive or non-exclusive
licenses to others. You may contact the following by email to discuss commercial use: vtippatents@vtip.org

Limitation of Liability IN NO EVENT WILL VIRGINIA TECH, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR REDISTRIBUTE
THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR
CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO
LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR A FAILURE
OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF VIRGINIA TECH OR OTHER PARTY HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGES.

For full terms and conditions, please visit https://bitbucket.org/bemoss/bemoss_os.

Address all correspondence regarding this license to Virginia Tech’s electronic mail address: vtippatents@vtip.org

__author__ = "Aditya Nugur"
__credits__ = ""
__version__ = "3.5"
__maintainer__ = "Aditya Nugur""
__email__ = "aditya32@vt.edu"
__website__ = ""
__status__ = "Prototype"
__created__ = "2016-10-24 16:12:00"
__lastUpdated__ = "2016-10-25 13:25:00"
'''

from DeviceAPI.BACnetAPI import BACnetAPI
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
debug = True

CONFIG_FILE = "/Bacnetdata/Wattnode_config.csv"

SCALE={"power_sum":1,"power_a":1,"power_b":1,"power_c":1,"power_reactive_sum":1,"power_reactive_a":1,"power_reactive_b":1,"power_reactive_c":1}
class API(BACnetAPI):

    def __init__(self, parent=None,**kwargs):

        BACnetAPI.__init__(self, parent=parent, scale=SCALE, **kwargs)
        self.config_file=CONFIG_FILE

    def API_info(self):
        return [
            {'device_model': 'WNC-3Y-208-BN', 'vendor_name': 'Continental Control Systems, LLC', 'communication': 'BACnet',
             'device_type_id': 5, 'api_name': 'API_WattnodePM', 'html_template': 'powermeter/powermeter.html', 'support_oauth': False,
             'agent_type': 'BasicAgent', 'identifiable': False, 'authorizable': False, 'is_cloud_device': False,
             'schedule_weekday_period': 4, 'schedule_weekend_period': 4, 'allow_schedule_period_delete': True,
             'chart_template': 'charts/charts_powermeter.html'},

        ]

    def dashboard_view(self):
        return {"top": BEMOSS_ONTOLOGY.ENERGY.NAME,
                "center": {"type": "number", "value": BEMOSS_ONTOLOGY.POWER.NAME},
                "bottom": None,"image":"powermeter.png"}

    def ontology(self):
        return {"energy_sum":BEMOSS_ONTOLOGY.ENERGY,"power_sum":BEMOSS_ONTOLOGY.POWER,"power_a":BEMOSS_ONTOLOGY.POWER_L1,"power_b":BEMOSS_ONTOLOGY.POWER_L2,"power_c":BEMOSS_ONTOLOGY.POWER_L3,
                "voltage_avg":BEMOSS_ONTOLOGY.VOLTAGE,"voltage_a":BEMOSS_ONTOLOGY.VOLTAGE_L1,"voltage_b":BEMOSS_ONTOLOGY.VOLTAGE_L2,"voltage_c":BEMOSS_ONTOLOGY.VOLTAGE_L3,
                "frequency":BEMOSS_ONTOLOGY.FREQUENCY,"power_factor_avg":BEMOSS_ONTOLOGY.POWERFACTOR,"power_factor_a":BEMOSS_ONTOLOGY.POWERFACTOR_L1,
                "power_factor_b":BEMOSS_ONTOLOGY.POWERFACTOR_L2,"power_factor_c":BEMOSS_ONTOLOGY.POWERFACTOR_L3,"power_reactive_sum":BEMOSS_ONTOLOGY.REACTIVE_POWER,
                "current_a":BEMOSS_ONTOLOGY.CURRENT_L1,"current_b":BEMOSS_ONTOLOGY.CURRENT_L2,"current_c":BEMOSS_ONTOLOGY.CURRENT_L3 }

    def discover(self):
        device_list = super(API,self).discover()
        #override the vendor and model of base discover because for watt-node they are not accurate
        for device in device_list:
            device['model'] = self.API_info()[0]['device_model']
            device['vendor'] = self.API_info()[0]['vendor_name']

        return device_list
