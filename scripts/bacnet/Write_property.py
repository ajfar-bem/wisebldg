
import sys

from bacpypes.debugging import ModuleLogger
from bacpypes.app import LocalDeviceObject
from bacpypes.basetypes import PropertyIdentifier,ObjectTypesSupported
from bacpypes.task import TaskManager
# Make sure the TaskManager singleton exists...
from scripts.bacnet.grab_bacnet_config import get_iam, write_bacnet,read_prop,SynchronousApplication
from bemoss_lib.utils.find_own_ip import getIPs


task_manager = TaskManager()
_debug = 0
_log = ModuleLogger(globals())


def getObjectnProperty(object,property):
    return_object=""
    return_property=""
    for Specific_property, number in PropertyIdentifier.enumerations.iteritems():
        if number == property:
            return_property=Specific_property
    for Specific_object, another_number in ObjectTypesSupported.bitNames.iteritems():
        if another_number == object:
            return_object=Specific_object

    return return_object,return_property

def main():  # USage address, obj_type, obj_inst, prop_id--- 192.168.10.67 8 123 70 value

    arguments=sys.argv
    if(len(arguments) is not 6):
        print "Insufficient arguments please provide exactly 5 arguments with device address as 1st argument , object property as 2nd argument, property instance as 3rd argument and " \
              "property name as 4th argument and value to be written as 5th argument"
        return
    ips = getIPs()
    device_address = ips[0] + "/24"
    # make a device object
    this_device = LocalDeviceObject(
        objectName="BEMOSS-PLUS",
        objectIdentifier=int(599),
        maxApduLengthAccepted=int(1024),
        segmentationSupported="segmentedBoth",
        vendorIdentifier=int(15),
    )

    # make a simple application
    this_application = SynchronousApplication(this_device, device_address)

    _log.debug("starting build")
    address=arguments[1]
    obj_type=int(arguments[2])
    device_id=int(arguments[3])
    prop_id=int(arguments[4]) #convert to PropertyIdentifier
    value=int(arguments[5])
    result = get_iam(this_application, device_id, address)

    target_address = result.pduSource

    _log.debug('pduSource = ' + repr(result.pduSource))
    _log.debug('iAmDeviceIdentifier = ' + str(result.iAmDeviceIdentifier))
    _log.debug('maxAPDULengthAccepted = ' + str(result.maxAPDULengthAccepted))
    _log.debug('segmentationSupported = ' + str(result.segmentationSupported))
    _log.debug('vendorID = ' + str(result.vendorID))

    device_id = result.iAmDeviceIdentifier[1]
    Specific_object,Specific_property=getObjectnProperty(obj_type,prop_id)
    if Specific_object=="" or Specific_property=="":
        print "Incorrect object type or property instance"
        return
    try:

        Result =  write_bacnet(this_application, target_address, Specific_object, device_id,Specific_property, value)
        print Result
        return
    except Exception as e:
        print "Error during reading-- ",e
        exit(1)
    return


if __name__=='__main__':
    try:
        main()
    except Exception, e:
        _log.exception("an error has occurred: %s", e)
    finally:
        _log.debug("finally")