# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python sw=4 ts=4 sts=4 et:
#
# Copyright (c) 2015, Battelle Memorial Institute
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of the FreeBSD Project.
#

# This material was prepared as an account of work sponsored by an
# agency of the United States Government.  Neither the United States
# Government nor the United States Department of Energy, nor Battelle,
# nor any of their employees, nor any jurisdiction or organization
# that has cooperated in the development of these materials, makes
# any warranty, express or implied, or assumes any legal liability
# or responsibility for the accuracy, completeness, or usefulness or
# any information, apparatus, product, software, or process disclosed,
# or represents that its use would not infringe privately owned rights.
#
# Reference herein to any specific commercial product, process, or
# service by trade name, trademark, manufacturer, or otherwise does
# not necessarily constitute or imply its endorsement, recommendation,
# r favoring by the United States Government or any agency thereof,
# or Battelle Memorial Institute. The views and opinions of authors
# expressed herein do not necessarily state or reflect those of the
# United States Government or any agency thereof.
#
# PACIFIC NORTHWEST NATIONAL LABORATORY
# operated by BATTELLE for the UNITED STATES DEPARTMENT OF ENERGY
# under Contract DE-AC05-76RL01830

#}}}


from bemoss_lib.platform.async import AsyncCall

__version__ = '0.1'

import os.path
import errno
from collections import defaultdict
from Queue import Queue, Empty
from bemoss_lib.utils.find_own_ip import getIPs
from bacpypes.task import RecurringTask
from bacpypes.apdu import ConfirmedRequestSequence, WhoIsRequest
import bacpypes.core

import threading

#Tweeks to BACpypes to make it play nice with Gevent.
bacpypes.core.enable_sleeping()
bacpypes.core.SPIN = 0.1
from bacpypes.errors import DecodingError
from bacpypes.pdu import Address, GlobalBroadcast
from bacpypes.app import BIPSimpleApplication
from bacpypes.service.device import LocalDeviceObject
from bacpypes.object import get_datatype

from bemoss_lib.platform.BEMOSSAgent import BEMOSSAgent

from bacpypes.apdu import (ReadPropertyRequest, 
                           WritePropertyRequest, IAmRequest,
                           Error, 
                           AbortPDU, 
                           ReadPropertyACK, 
                           SimpleAckPDU,
                           ReadPropertyMultipleRequest,
                           ReadPropertyMultipleACK,
                           PropertyReference,
                           ReadAccessSpecification,
                           )
from bacpypes.primitivedata import Null, Atomic, Enumerated, Integer, Unsigned, Real
from bacpypes.constructeddata import Array, Any, Choice
from bacpypes.basetypes import ServicesSupported
from bacpypes.task import TaskManager
from gevent.event import AsyncResult

path = os.path.dirname(os.path.abspath(__file__))
configFile = os.path.join(path, "bacnet_example_config.csv")

#Make sure the TaskManager singleton exists...
task_manager = TaskManager()
#import traceback
from bemoss_lib.utils.catcherror import getErrorInfo

#IO callback
class IOCB:

    def __init__(self, request, asynccall):
        # requests and responses
        self.ioRequest = request
        self.ioResult = AsyncResult()
        self.ioCall = asynccall

    def set(self, value):
        self.ioCall.send(None, self.ioResult.set, value)

    def set_exception(self, exception):
        self.ioCall.send(None, self.ioResult.set_exception, exception)

class BACnet_application(BIPSimpleApplication, RecurringTask):


    def __init__(self, *args):
        BIPSimpleApplication.__init__(self, *args)
        RecurringTask.__init__(self, 250)
        self.request_queue = Queue()
        self._request = None
        self.found_address=list()
       # self.found_deviceidentifier=list()
        # assigning invoke identifiers
        self.nextInvokeID = 1

        # keep track of requests to line up responses
        self.iocb = {}

        self.install_task()

    def process_task(self):
        while True:
            try:
                iocb = self.request_queue.get(False)
            except Empty:
                break

            self.handle_request(iocb)

    def submit_request(self, iocb):
        self.request_queue.put(iocb)

    def get_next_invoke_id(self, addr):
        """Called to get an unused invoke ID."""

        initialID = self.nextInvokeID
        while 1:
            invokeID = self.nextInvokeID
            self.nextInvokeID = (self.nextInvokeID + 1) % 256

            # see if we've checked for them all
            if initialID == self.nextInvokeID:
                raise RuntimeError("no available invoke ID")

            # see if this one is used
            if (addr, invokeID) not in self.iocb:
                break

        return invokeID

    def handle_request(self, iocb):
        apdu = iocb.ioRequest

        if isinstance(apdu, ConfirmedRequestSequence):
            # assign an invoke identifier
            apdu.apduInvokeID = self.get_next_invoke_id(apdu.pduDestination)

            # build a key to reference the IOCB when the response comes back
            invoke_key = (apdu.pduDestination, apdu.apduInvokeID)

            # keep track of the request
            self.iocb[invoke_key] = iocb

        try:
            self.request(apdu)
        except StandardError as e:
            iocb.set_exception(e)

    def confirmation(self, apdu):
        # build a key to look for the IOCB
        invoke_key = (apdu.pduSource, apdu.apduInvokeID)

        # find the request
        iocb = self.iocb.get(invoke_key, None)
        if iocb is None:
            iocb.set_exception(RuntimeError("no matching request for confirmation"))
            return
        del self.iocb[invoke_key]

        if isinstance(apdu, AbortPDU):
            iocb.set_exception(RuntimeError("Device communication aborted: " + str(apdu)))
            return

        if isinstance(apdu, Error):
            iocb.set_exception(RuntimeError("Error during device communication: " + str(apdu)))
            return

        elif (isinstance(iocb.ioRequest, ReadPropertyRequest) and
              isinstance(apdu, ReadPropertyACK)):
            # find the datatype
            datatype = get_datatype(apdu.objectIdentifier[0], apdu.propertyIdentifier)
            if not datatype:
                iocb.set_exception(TypeError("unknown datatype"))
                return

            # special case for array parts, others are managed by cast_out
            if issubclass(datatype, Array) and (apdu.propertyArrayIndex is not None):
                if apdu.propertyArrayIndex == 0:
                    value = apdu.propertyValue.cast_out(Unsigned)
                else:
                    value = apdu.propertyValue.cast_out(datatype.subtype)
            else:
                value = apdu.propertyValue.cast_out(datatype)
                if issubclass(datatype, Enumerated):
                    value = datatype(value).get_long()
            iocb.set(value)

        elif (isinstance(iocb.ioRequest, WritePropertyRequest) and
              isinstance(apdu, SimpleAckPDU)):
            iocb.set(apdu)
            return

        elif (isinstance(iocb.ioRequest, ReadPropertyMultipleRequest) and
              isinstance(apdu, ReadPropertyMultipleACK)):

            result_dict = {}
            for result in apdu.listOfReadAccessResults:
                # here is the object identifier
                objectIdentifier = result.objectIdentifier

                # now come the property values per object
                for element in result.listOfResults:
                    # get the property and array index
                    propertyIdentifier = element.propertyIdentifier
                    propertyArrayIndex = element.propertyArrayIndex

                    # here is the read result
                    readResult = element.readResult

                    # check for an error
                    if readResult.propertyAccessError is not None:
                        error_obj = readResult.propertyAccessError

                        msg = 'ERROR DURRING SCRAPE (Class: {0} Code: {1})'
                        #print msg.format(error_obj.errorClass, error_obj.errorCode)

                    else:
                        # here is the value
                        propertyValue = readResult.propertyValue

                        # find the datatype
                        datatype = get_datatype(objectIdentifier[0], propertyIdentifier)
                        if not datatype:
                            iocb.set_exception(TypeError("unknown datatype"))
                            return

                        # special case for array parts, others are managed by cast_out
                        if issubclass(datatype, Array) and (propertyArrayIndex is not None):
                            if propertyArrayIndex == 0:
                                value = propertyValue.cast_out(Unsigned)
                            else:
                                value = propertyValue.cast_out(datatype.subtype)
                        else:
                            value = propertyValue.cast_out(datatype)
                            if type(value)==int:
                                if issubclass(datatype, Enumerated):
                                    value = datatype(value).get_long()

                            if issubclass(datatype, Array):
                                if issubclass(datatype.subtype, Choice):
                                    new_value = []
                                    for item in value.value[1:]:
                                        result = item.dict_contents().values()
                                        if result[0] != ():
                                            new_value.append(result[0])
                                        else:
                                            new_value.append(None)
                                    value = new_value
                                else:
                                    pass
                                    #value = [x.cast_out(datatype.subtype) for x in value.value[1:]]

                        result_dict[objectIdentifier[0], objectIdentifier[1], propertyIdentifier] = value

            iocb.set(result_dict)

        else:
            iocb.set_exception(TypeError('Unsupported Request Type'))

    def indication(self,apdu):

        self.apdu = apdu
        device_type, device_instance = apdu.iAmDeviceIdentifier
        self.device_type=device_type
        self.device_instance=device_instance
        self.release=False
        self.update=True
        self.updator()


    def updator(self):

        if self.update==True:
            apdu=self.apdu
            Remotestation=str(apdu.pduSource)
            StationIdentifier=self.device_instance
            addresslist=(Remotestation, StationIdentifier)
            try:
                self.found_address.append(addresslist)
                #self.found_deviceidentifier.append(StationIdentifier)
            except Exception as e:
                #print e
                pass
        if self.release==True:
            return (self.found_address)



class BACnetAgent(BEMOSSAgent):
    '''This agent creates a virtual bacnet device that is used by
    the bacnet driver interface to communicate with devices.
    '''
    def __init__(self, *args, **kwargs):
        super(BACnetAgent, self).__init__(*args, **kwargs)
        ips = getIPs()
        print "found local ip as ", ips
        device_address = ips[0] + "/24"
        max_apdu_len =  1024
        seg_supported = "segmentedBoth"
        obj_id =  599
        obj_name = "BEMOSS BACnet driver"
        ven_id = 15
        self.async_call = AsyncCall()
        self.setup_device(device_address,
                         max_apdu_len, seg_supported,
                         obj_id, obj_name, ven_id)
        self.subscribe(topic="read_property",callback=self.processRead)
        self.subscribe(topic="write_property",callback=self.processWrite)
        self.subscribe(topic="broadcast", callback=self.broadcast)
        self.subscribe(topic="simple_read",callback=self.processSimpleRead)
        self.run()

    def extract_pipe(self,reduced_pipe):
        rebuild_func = reduced_pipe[0]
        return rebuild_func(*reduced_pipe[1])

    def processRead(self,dbcon, sender,topic,message):
        return_pipe = self.extract_pipe(message["reduced_return_pipe"])
        message = message["actual_message"]
        result = self.read_properties(*message)
        try:
            return_pipe.send(result)
        except IOError:
            self.infoLog(__name__,result,header='bacnetagent/pipeclosed',comments="Pipe Closed/ Data Abandoned")
            pass
        #self.bemoss_publish(target=sender,topic="read_response",message=result)

    def processSimpleRead(self,dbcon, sender,topic,message):
        return_pipe = self.extract_pipe(message["reduced_return_pipe"])
        message = message["actual_message"]

        result = self.simple_read(*message)
        try:
            return_pipe.send(result)
        except IOError as er:
            pass
        #self.bemoss_publish(target=sender,topic="read_response",message=result)

    def processWrite(self,dbcon, sender,topic,message):
        return_pipe = self.extract_pipe(message["reduced_return_pipe"])
        message = message['actual_message']
        result = self.write_property(*message)
        return_pipe.send(result)
        #self.bemoss_publish(target=sender,topic="write_response",message=result)
        #fill the temp Q


    def setup_device(self, address,
                     max_apdu_len=1024,
                     seg_supported='segmentedBoth',
                     obj_id=599,
                     obj_name='sMap BACnet driver',
                     ven_id=15):



        this_device = LocalDeviceObject(
            objectName=obj_name,
            objectIdentifier=obj_id,
            maxApduLengthAccepted=max_apdu_len,
            segmentationSupported=seg_supported,
            vendorIdentifier=ven_id,
            )

        # build a bit string that knows about the bit names and leave it empty. We respond to NOTHING.
        pss = ServicesSupported()

        # set the property value to be just the bits
        this_device.protocolServicesSupported = pss.value

        self.this_application = BACnet_application(this_device, address)

        server_thread = threading.Thread(target=bacpypes.core.run)
        # exit the BACnet App thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()


    def broadcast(self,dbcon, sender,topic,message):
        try:

            return_pipe = self.extract_pipe(message["reduced_return_pipe"])
            request = WhoIsRequest()
            request.pduDestination = GlobalBroadcast()
            self.this_application.request(request)
            self.this_application.release = True
            self.this_application.update = False
            addresslist = self.this_application.found_address
            addresslist=list(set(addresslist))
            #self.bemoss_publish(target=sender,topic='broadcast_response',message=addresslist)
            #print "Printing address"
            #print addresslist
            return_pipe.send(addresslist)

        except Exception as e:
            #print "an error has occurred during bacnet discovery: %s"
            return []

    def write_property(self, target_address, value, object_type, instance_number, property_name, priority=None, index=None):
        """Write to a property."""
        # target_address = IP or network address of device
        # setvalue = the value you want to set to
        # object_type =  protocol related object type: eg: Analog Input (AI), Analog Output etc
        # instance_number = the interger id of the property you want to change (brightness, state etc)
        # property = always set to "presentValue"
        # priority =  the priority of your settings. Higher priority settings takes over

        request = WritePropertyRequest(
            objectIdentifier=(object_type, instance_number),
            propertyIdentifier=property_name)

        datatype = get_datatype(object_type, property_name)
        bac_value = Null()
        if issubclass(datatype, Atomic):
            if datatype is Integer:
                value = int(value)
            elif datatype is Real:
                value = float(value)
            elif datatype is Unsigned:
                value = int(value)
            bac_value = datatype(value)
        elif issubclass(datatype, Array) and (index is not None):
            if index == 0:
                bac_value = Integer(value)
            elif issubclass(datatype.subtype, Atomic):
                bac_value = datatype.subtype(value)
            elif not isinstance(value, datatype.subtype):
                raise TypeError("invalid result datatype, expecting %s" % (datatype.subtype.__name__,))
        elif not isinstance(value, datatype):
            raise TypeError("invalid result datatype, expecting %s" % (datatype.__name__,))

        request.propertyValue = Any()
        request.propertyValue.cast_in(bac_value)

        request.pduDestination = Address(target_address)

        #Optional index
        if index is not None:
            request.propertyArrayIndex = index

        #Optional priority
        if priority is not None:
            request.priority = priority

        self.async_call = AsyncCall()
        iocb = IOCB(request, self.async_call)
        self.this_application.submit_request(iocb)
        result = iocb.ioResult.wait()
        if isinstance(result, SimpleAckPDU):
            return value
        return None #Failed to set proper value

    def simple_read(self, target_address,  obj_inst, propertylist, obj_type= "device", index=0):
        try:
            reverse_point_map = {}
            result_dict = []
            read_access_spec_list = []
            count = 0
            prop_ref_list = []
            for prop in propertylist:
                prop_ref = PropertyReference(propertyIdentifier=prop)
                prop_ref_list.append(prop_ref)
                count += 1

            read_access_spec = ReadAccessSpecification(objectIdentifier=(obj_type, obj_inst),
                                                       listOfPropertyReferences=prop_ref_list)

            read_access_spec_list.append(read_access_spec)
            if read_access_spec_list:
                request = ReadPropertyMultipleRequest(listOfReadAccessSpecs=read_access_spec_list)
                request.pduDestination = Address(target_address)
                self.async_call = AsyncCall()
                iocb = IOCB(request, self.async_call)
                self.this_application.submit_request(iocb)
                #print "bacnet request sent"
                bacnet_results=tuple
                bacnet_results = iocb.ioResult.get(True,timeout=10)
                #print"bacnet data fetched"
                for prop_tuple, value in bacnet_results.iteritems():

                    result_dict.append(value)
            #print result_dict
            return result_dict

        except Exception as e:
            self.infoLog(__name__, getErrorInfo(), header='bacnetagent/simplereadfail', comments="Simple Read failed")
            return None

    def read_properties(self, target_address, point_map, max_per_request=None):
        try:
            """Read a set of points and return the results"""

            #Set max_per_request really high if not set.
            if max_per_request is None:
                max_per_request = 1000000



            #This will be used to get the results mapped
            # back on the the names
            reverse_point_map = {}

            #TODO Support rading an index of an Array.

            #Used to group properties together for the request.
            object_property_map = defaultdict(list)

            for name, properties in point_map.iteritems():
                object_type, instance_number, property_name = properties
                reverse_point_map[object_type,
                                  instance_number,
                                  property_name] = name

                object_property_map[object_type,
                                    instance_number].append(property_name)

            result_dict={}
            finished = False

            while not finished:
                read_access_spec_list = []
                count = 0
                for _ in xrange(max_per_request):
                    try:
                        obj_data, properties = object_property_map.popitem()
                    except KeyError:
                        finished = True
                        break
                    obj_type, obj_inst = obj_data
                    prop_ref_list = []
                    for prop in properties:
                        prop_ref = PropertyReference(propertyIdentifier=prop)
                        prop_ref_list.append(prop_ref)
                        count += 1
                    read_access_spec = ReadAccessSpecification(objectIdentifier=(obj_type, obj_inst),
                                                               listOfPropertyReferences=prop_ref_list)
                    read_access_spec_list.append(read_access_spec)

                if read_access_spec_list:
                    request = ReadPropertyMultipleRequest(listOfReadAccessSpecs=read_access_spec_list)
                    request.pduDestination = Address(target_address)
                    self.async_call = AsyncCall()
                    iocb = IOCB(request, self.async_call)
                    self.this_application.submit_request(iocb)

                    bacnet_results = iocb.ioResult.get(True,10)

                    for prop_tuple, value in bacnet_results.iteritems():
                        name = reverse_point_map[prop_tuple]
                        result_dict[name] = value

            return result_dict
        except Exception as e:
            self.infoLog(__name__,getErrorInfo(),header='bacnetagent/readpropertyfail',comments="Read failed")
            return None
if __name__ == '__main__':
    # Entry point for script
    print "Can't run as script"