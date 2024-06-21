#!/usr/bin/python3

import dbus
import dbus.mainloop.glib
from gi.repository import GLib


# ----------------- original example ----------------- 
# mainloop = None

# def greeting_signal_received(greeting):
#     print(greeting)

# dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

# bus = dbus.SystemBus()
# bus.add_signal_receiver(greeting_signal_received, dbus_interface='com.example.greeting', signal_name='GreetingSignal')

# mainloop = GLib.MainLoop()
# mainloop.run()

#  ----------------- read data received from bluetooth ----------------- 

mainloop_bluetooth = None

def bluetooth_signal_received(interface, dict, array):
    print("interface: ", interface)
    data = list(dict['Value'])
    data = ['{:02x}'.format(dbus_byte) for dbus_byte in data]
    print("value: ", data)
    # print("array: ", array)
    print('----------------------------------------')

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

bus_bluetooth = dbus.SystemBus()
bus_bluetooth.add_signal_receiver(bluetooth_signal_received, dbus_interface='org.freedesktop.DBus.Properties', signal_name='PropertiesChanged',
                                  bus_name='org.bluez', path='/org/bluez/hci0/dev_94_C9_60_43_BE_FD/service0025/char0028')

mainloop_bluetooth = GLib.MainLoop()
mainloop_bluetooth.run()


#  ----------------- read  data writed by user's bluetooth program ----------------- 

# mainloop_bluetooth = None

# def bluetooth_signal_received(array_byte, dict):
#     data = list(array_byte['Value'])
#     data = ['{:02x}'.format(dbus_byte) for dbus_byte in data]
#     print("value: ", data)
#     print('----------------------------------------')

# dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

# bus_bluetooth = dbus.SystemBus()
# bus_bluetooth.add_signal_receiver(bluetooth_signal_received, dbus_interface='org.freedesktop.DBus.Properties', signal_name='PropertiesChanged',
#                                   bus_name='org.bluez', path='/org/bluez/hci0/dev_94_C9_60_43_BE_FD/service0025/char0026')

# mainloop_bluetooth = GLib.MainLoop()
# mainloop_bluetooth.run()



