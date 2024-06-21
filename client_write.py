import dbus.mainloop
import dbus.mainloop.glib
from gi.repository import GLib
import bluetooth_constants
import bluetooth_utils
import dbus
import sys
sys.path.insert(0, '.')
import time

bus = None
device_proxy = None
device_interface = None
mainloop = None

device_path = None
found_service0025 = False # service0025 => device information service
found_characteristic0026 = False  # mn  => model number string characteristic
service0025_path = None
characteristic0026_path = None
code = None

def write_value(code):
    global characteristic0026_path
    global bus
    char_proxy = bus.get_object(bluetooth_constants.BLUEZ_SERVICE_NAME, characteristic0026_path)
    char_interface = dbus.Interface(char_proxy, bluetooth_constants.GATT_CHARACTERISTIC_INTERFACE)
    try:
        rt = char_interface.WriteValue(code, {dbus.String('type'): dbus.String('request')})
    except Exception as e:
        print("Failed to write code")
        print(e.get_dbus_name())
        print(e.get_dbus_message())
        return bluetooth_constants.RESULT_EXCEPTION
    else:
        print("written OK") 

def service_discovery_completed():
    global found_service0025
    global found_characteristic0026
    global service0025_path
    global characteristic0026_path
    global bus
    global mainloop

    if found_service0025 and found_characteristic0026:
        print("Required service and characteristic found - device is OK")
        print("Service0025 path: ", service0025_path)
        print("Characteristic0026 path: ", characteristic0026_path)
        write_value(code)
    else:
        print("Required service and characteristic were not found - device is NOK")
        print("Device Information service found: ", str(found_service0025))
        print("Model Number String characteristic found: ", str(found_service0025))
    
    bus.remove_signal_receiver(interfaces_added, "InterfacesAdded")
    bus.remove_signal_receiver(properties_changed, "PropertiesChanged")
    mainloop.quit()

def properties_changed(interface, changed, invalidated, path):
    global device_path
    if path != device_path:
        return
    
    if 'ServicesResolved' in changed:
        sr = bluetooth_utils.dbus_to_python(changed['ServicesResolved'])
        print("\nServicesResolved: ", sr)
        if sr == True:
            service_discovery_completed()

def connect(bdaddr):
    global bus
    global device_proxy
    global device_interface
    global device_path

    adapter_path = bluetooth_constants.BLUEZ_NAMESPACE + bluetooth_constants.ADAPTER_NAME
    device_path = bluetooth_utils.device_address_to_path(bdaddr, adapter_path)
    device_proxy = bus.get_object(bluetooth_constants.BLUEZ_SERVICE_NAME, device_path)
    device_interface = dbus.Interface(device_proxy, bluetooth_constants.DEVICE_INTERFACE)

    try:
        time_start = time.time()
        device_interface.Connect()
        time_end = time.time()
        print(f'Connect() cost {"{:.2f}".format(time_end - time_start)} seconds.')
    except Exception as e:
        print("Failed to connect")
        print(e.get_dbus_name())
        print(e.get_dbus_message())
        if ("UnknownObject" in e.get_dbus_name()):
            print("Try scanning first to resolve this problem")
        return bluetooth_constants.RESULT_EXCEPTION
    else:
        print("Connected OK")
        return bluetooth_constants.RESULT_OK

def interfaces_added(path, interfaces):
    global found_service0025
    global found_characteristic0026
    global service0025_path
    global characteristic0026_path

    if bluetooth_constants.GATT_SERVICE_INTERFACE in interfaces:
        properties = interfaces[bluetooth_constants.GATT_SERVICE_INTERFACE]
        print("-----------------------------------------------------")
        print("SVC path: ", path)
        if 'UUID' in properties:
            uuid = properties['UUID']
            if uuid == "55535343-fe7d-4ae5-8fa9-9fafd205e455":
                found_service0025 = True
                service0025_path = path
            print("SVC UUID: ", bluetooth_utils.dbus_to_python(uuid))
            print("SVC name: ", bluetooth_utils.get_name_from_uuid(uuid))
        return
    
    if bluetooth_constants.GATT_CHARACTERISTIC_INTERFACE in interfaces:
        properties = interfaces[bluetooth_constants.GATT_CHARACTERISTIC_INTERFACE]
        print("CHR path: ", path)
        if "UUID" in properties:
            uuid = properties['UUID']
            if uuid == "49535343-8841-43f4-a8d4-ecbe34729bb3":
                found_characteristic0026 = True
                characteristic0026_path = path
            print("CHR UUID: ", bluetooth_utils.dbus_to_python(uuid))
            print("CHR name: ", bluetooth_utils.get_name_from_uuid(uuid))
            flags = ""
            for flag in properties['Flags']:
                flags = flags + flag + ","
            print("CHR Flags: ", flags)
        return
    
    if bluetooth_constants.GATT_DESCRIPTOR_INTERFACE in interfaces:
        properties = interfaces[bluetooth_constants.GATT_DESCRIPTOR_INTERFACE]
        print("DSC path: ", path)
        if "UUID" in properties:
            uuid = properties['UUID']
            print("DSC UUID: ", bluetooth_utils.dbus_to_python(uuid))
            print("DSC name: ", bluetooth_utils.get_name_from_uuid(uuid))
        return
    

if (len(sys.argv) != 3):
    print("usage: python3 ", sys.argv[0], " [bdaddr] [code]")
    sys.exit(1)

bdaddr = sys.argv[1]
code   = sys.argv[2].split(',')
code = [int(e) for e in code]
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()

print("Connecting to "+ bdaddr)
rt_code = connect(bdaddr)
if rt_code != 0:
    print('Connect() Failed')
else:
    print("Discovering  services++")
    print("Registering to receive InterfacesAdded signals")
    bus.add_signal_receiver(interfaces_added, dbus_interface= bluetooth_constants.DBUS_OM_IFACE,
                            signal_name="InterfacesAdded")
    print("Registering to receive ProptertiesChanged signals")
    bus.add_signal_receiver(properties_changed,
                            dbus_interface=bluetooth_constants.DBUS_PROPERTIES,
                            signal_name='PropertiesChanged',
                            path_keyword="path")
    mainloop = GLib.MainLoop()
    mainloop.run()
    print("Finished")









