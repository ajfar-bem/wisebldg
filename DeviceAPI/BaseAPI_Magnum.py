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
from DeviceAPI.BACnetAPI import BACnetAPI

CONFIG_FILE = "/Bacnetdata/Magnum.csv"
class baseAPI_Magnum(BACnetAPI):

    def __init__(self, parent=None,**kwargs):

        BACnetAPI.__init__(self, parent=parent,CONFIG_FILE=CONFIG_FILE, **kwargs)
        self.device_supports_auto = True
        if 'agent_id' in kwargs.keys():
            decode=kwargs["agent_id"]
            agent= decode.split('n')[0]
            number=decode.split('n')[1]
            self.agent=agent
            self.number=number


    def discover(self):

        try:
            devicelist=list()
            maclist = list()
            modellist = list()
            vendorlist=list()
            deviceinfo = self.broadcast()
            addresslist = list()
            if deviceinfo:
                for device in deviceinfo:
                    address = device["address"]
                    device_id = int(device["mac"])
                    vendor = device["vendor"]
                    model=device["model"]
                    if vendor == 'eBox BACnet/IP':
                        deviceinfo.remove(device)
                        try:
                                data=self.readcsv()
                                if data:
                                    device_count = data["Device number"]
                                    device_map=self.duplicates_indices(device_count)
                                    for device,value in device_map.iteritems():
                                        if device!="":
                                            for each_value in value:
                                                if data['Reference Point Name'][each_value].find("Signal")>0:
                                                    instance=int(data['Index'][each_value])
                                                    obj_type=data['BACnet Object Type'][each_value]
                                                    result = self.rpc(self.proxy_address, 'simple_read', address, instance,
                                                                              ["presentValue"], obj_type=obj_type,timeout=30)
                                                    result = result[0]
                                                    if result=="active":
                                                          maclist.append(str(device_id)+"n"+device)
                                                          modellist.append(data['Model Name'][each_value])
                                                          addresslist.append(address)
                                                          vendorlist.append(vendor)
                        except Exception as e:
                            print e
                            continue
                        except self.RPCTimeout:
                            print "Magnum discovery call timeout"
                            return None
                        devicelist = zip(maclist, modellist,addresslist,vendorlist)
                if devicelist:
                    for mac,model,add,Vendor in devicelist:
                        deviceinfo.append({'address': add, 'mac': mac,
                                               'model': model, 'vendor': Vendor, })
                return deviceinfo

        except Exception as e:
            print e
            return deviceinfo


