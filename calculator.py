import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib

mainloop = None

class Calculator(dbus.service.Object):
    def __init__(self, bus):
        self.path = '/com/example/calculator'
        dbus.service.Object.__init__(self, bus, self.path)

    @dbus.service.method("com.example.calculator_interface",
                         in_signature='dd',
                         out_signature='d')
    def Add(self, a1, a2):
        sum = a1 + a2
        print(a1, " + ", a2, " = ", sum)
        return sum
    

    @dbus.service.method("com.example.calculator_interface",
                         in_signature='dd',
                         out_signature='d')
    def Mul(self, a1, a2):
        result = a1 * a2
        print(a1, " * ", a2, " = ", result)
        return result

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()


calc = Calculator(bus)

mainloop = GLib.MainLoop()
print("waiting for some calculations to do ...")
mainloop.run()











