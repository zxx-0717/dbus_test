#!/usr/bin/python3

import dbus

bus = dbus.SystemBus()
proxy = bus.get_object('org.freedesktop.hostname1', '/org/freedesktop/hostname1')
interface = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')

print('---------------------------')
hostname = interface.Get('org.freedesktop.hostname1', 'Hostname')
print("The hostname is:".rjust(26,' '), hostname)

properties = interface.GetAll('org.freedesktop.hostname1')

for name, value in properties.items():
    name = name.rjust(25,' ')
    print(f"{name}: {value}")

print('---------------------------')
hci0_proxy = bus.get_object('org.bluez', '/org/bluez/hci0')
hci0_interface = dbus.Interface(hci0_proxy, 'org.freedesktop.DBus.Properties')
hci0_properties = hci0_interface.GetAll('org.bluez.Adapter1')
for name, value in hci0_properties.items():
    name = name.rjust(25,' ')
    print(f"{name}: {value}")

print('---------------------------')
bluetooth_charger_proxy = bus.get_object('org.bluez', '/org/bluez/hci0/dev_94_C9_60_43_BE_FD')
bluetooth_charger_interface = dbus.Interface(bluetooth_charger_proxy, 'org.freedesktop.DBus.Properties')
bluetooth_charger_properties = bluetooth_charger_interface.GetAll('org.bluez.Device1')
for name, value in bluetooth_charger_properties.items():
    name = name.rjust(25,' ')
    print(f"{name}: {value}")


