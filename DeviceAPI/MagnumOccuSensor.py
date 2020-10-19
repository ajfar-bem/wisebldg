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

TRANSLATOR = {BEMOSS_ONTOLOGY.OCCUPIED.POSSIBLE_VALUES.ON: 1,
                   BEMOSS_ONTOLOGY.OCCUPIED.POSSIBLE_VALUES.OFF: 2}

class API(baseAPI_Magnum):

    def __init__(self, parent=None,**kwargs):

        baseAPI_Magnum.__init__(self, converter=TRANSLATOR, parent=parent, **kwargs)


    def API_info(self):
        return [{'device_model': 'M9E0SW Occupancy Sensor', 'vendor_name': 'eBox BACnet/IP', 'communication': 'BACnet',
                 'device_type_id': 4, 'api_name': 'API_MagnumOccuSensor', 'html_template': 'sensors/sensors.html',
                 'agent_type': 'BasicAgent', 'identifiable': False,'authorizable': False, 'is_cloud_device': False,
                 'schedule_weekday_period': 4, 'schedule_weekend_period': 4, 'allow_schedule_period_delete': True,
                 'chart_template': 'charts/charts_occupancy.html'},
                ]

    def dashboard_view(self):

                  return {"top": None, "center": {"type": "number", "value": BEMOSS_ONTOLOGY.OCCUPIED.NAME},
            "bottom": None
                    }

    def ontology(self):
        return {"PIR Status":BEMOSS_ONTOLOGY.OCCUPIED}



    '''
        Attributes:
        ------------------------------------------------------------------------------------------
        Status          GET              Current status of occupancy sensor
        Illumination    GET              current irradiation in the room
        ------------------------------------------------------------------------------------------
    '''
    # converter = {BEMOSS_ONTOLOGY.OCCUPIED.POSSIBLE_VALUES.ON: 1,
    #           BEMOSS_ONTOLOGY.OCCUPIED.POSSIBLE_VALUES.OFF: 2}
    # def getDataFromDevice(self):
    #
    #     try:
    #
    #         bacnetread= self.Bacnet_read()
    #         if bacnetread["0x0194F5BF [0] (2) PIR Status"]==1:
    #             bacnetread["PIR Status"]=BEMOSS_ONTOLOGY.OCCUPIED.POSSIBLE_VALUES.ON
    #         else:
    #             bacnetread["PIR Status"]=BEMOSS_ONTOLOGY.OCCUPIED.POSSIBLE_VALUES.OFF
    #         print bacnetread
    #         return bacnetread
    #     except Exception as e:
    #         print e
    #         return None

