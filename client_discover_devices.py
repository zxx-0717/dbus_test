from gi.repository import GLib

import dbus
import dbus.mainloop.glib
import bluetooth_utils
import bluetooth_constants
import sys
sys.path.insert(0, '.')

adapter_interface = None
mainloop = None
timer_id = None

devices = {}
managed_objects_found = 0

def get_known_devices(bus):
    global managed_objects_found
    global devices
    object_manager = dbus.Interface(bus.get_object(bluetooth_constants.BLUEZ_SERVICE_NAME, "/"), bluetooth_constants.DBUS_OM_IFACE)
    managed_objects = object_manager.GetManagedObjects()

    for path, ifaces in managed_objects.items():
        for iface_name in ifaces:
            if iface_name == bluetooth_constants.DEVICE_INTERFACE:
                managed_objects_found += 1
                print("EXI path: ", path)
                devices_properties = ifaces[bluetooth_constants.DEVICE_INTERFACE]
                devices[path] = devices_properties
                if "Address" in devices_properties:
                    print("EXI bdaddr: ", bluetooth_utils.dbus_to_python(devices_properties['Address']))
                print('-------------------------------------------')


def properties_changed(interface, changed, invalidated, path):
    # print('interface: ', interface)
    if interface != bluetooth_constants.DEVICE_INTERFACE:
        return
    if path in devices:
        devices[path] = dict(devices[path].items())
        devices[path].update(changed.items())
    else:
        devices[path] = changed
    
    dev = devices[path]
    print("CHG path: ", path)
    if 'Address' in dev:
        print("CHG bdaddr: ", bluetooth_utils.dbus_to_python(dev['Address']))
    if 'Name' in dev:
        print("CHG name: ", bluetooth_utils.dbus_to_python(dev['Name']))
    if 'RSSI' in dev:
        print('CHG RSSI: ', bluetooth_utils.dbus_to_python(dev['RSSI']))
    print('-------------------------------------------')


def interfaces_removed(path, interfaces):
    # print('path: ', path)
    # print('interfaces: ', interfaces)
    if not bluetooth_constants.DEVICE_INTERFACE in interfaces:
        return
    if path in devices:
        dev = devices[path]
        if 'Address' in dev:
            print('DEL bdaddr: ', bluetooth_utils.dbus_to_python(dev['Address']))
        else:
            print("DEL path: ", path)
        print('-------------------------------------------')
        del devices[path]

def list_devices_found():
    print("Full list of devices", len(devices), " discovered:")
    print('-------------------------------------------')
    for path in devices:
        dev = devices[path]
        name = ""
        RSSI = ""
        if "Name" in dev:
            name = dev['Name']
        if "RSSI" in dev:
            RSSI = dev['RSSI']
        print(bluetooth_utils.dbus_to_python(dev['Address']), name.rjust(12, " "), RSSI)
        # for attribute in dev.keys():
        #     print(attribute)

def interfaces_added(path, interfaces):
    # print('path: ', path)
    # print('interfaces: ', interfaces)
    if bluetooth_constants.DEVICE_INTERFACE not in interfaces:
        return
    devices_properties = interfaces[bluetooth_constants.DEVICE_INTERFACE]
    if path not in devices:
        print("NEW path: ", path)
        devices[path] = devices_properties
        dev = devices[path]
        if 'Address' in dev:
            print("NEW bdaddr: ", bluetooth_utils.dbus_to_python(dev['Address']))
        if 'Name' in dev:
            print("NEW name: ", bluetooth_utils.dbus_to_python(dev['Name']))
        if 'RSSI' in dev:
            print('NEW RSSI: ', bluetooth_utils.dbus_to_python(dev['RSSI']))
        print('-------------------------------------------')

def discovery_timeout():
    global adapter_interface
    global mainloop
    global timer_id
    GLib.source_remove(timer_id)
    mainloop.quit()
    adapter_interface.StopDiscovery()
    bus = dbus.SessionBus()
    bus.remove_signal_receiver(interfaces_added, "InterfacesAdded")
    bus.remove_signal_receiver(interfaces_removed, "InterfacesRemoved")
    bus.remove_signal_receiver(properties_changed, "PropertiesChanged")
    list_devices_found()
    return True

def discover_devices(bus, timeout):
    global adapter_interface
    global mainloop
    global timer_id
    adapter_path = bluetooth_constants.BLUEZ_NAMESPACE + "hci1"
    adapter_path = bluetooth_constants.BLUEZ_NAMESPACE + bluetooth_constants.ADAPTER_NAME
    adapter_object = bus.get_object(bluetooth_constants.BLUEZ_SERVICE_NAME, adapter_path)
    adapter_interface = dbus.Interface(adapter_object, bluetooth_constants.ADAPTER_INTERFACE)
    bus.add_signal_receiver(interfaces_added, dbus_interface = bluetooth_constants.DBUS_OM_IFACE,
                            signal_name = "InterfacesAdded")
    bus.add_signal_receiver(interfaces_removed, dbus_interface = bluetooth_constants.DBUS_OM_IFACE,
                            signal_name = "InterfacesRemoved")
    bus.add_signal_receiver(properties_changed, dbus_interface = bluetooth_constants.DBUS_PROPERTIES,
                            signal_name = 'PropertiesChanged',
                            path_keyword = "path")
    mainloop = GLib.MainLoop()
    timer_id = GLib.timeout_add(timeout, discovery_timeout)
    adapter_interface.StartDiscovery(byte_arrays=True)
    mainloop.run()

if (len(sys.argv) != 2):
    print("usage: python3 clinet_discover_devices.py [scantime (secs) ]")
    sys.exit(1)
scantime = int(sys.argv[1]) * 1000

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()

print("Listing devices already known to BlueZ: ")
get_known_devices(bus)

print("Scanning ......")
discover_devices(bus, scantime)



