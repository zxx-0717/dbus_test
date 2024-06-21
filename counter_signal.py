import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import time

mainloop = None

class Counter(dbus.service.Object):
    def __init__(self, bus):
        self.path = "/com/example/counter"
        self.c = 0
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

    @dbus.service.signal('com.example.Counter')
    def CounterSignal(self, counter):
        pass
    def emitCounterSignal(self):
        self.CounterSignal(self.c)

    def increment(self):
        self.c = self.c + 1
        print(self.c)

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()
counter = Counter(bus)

while True:
    counter.increment()
    counter.emitCounterSignal()
    time.sleep(1)
# to be catched in d-feet ,comment while True, uncomment the following codes.
# mainloop = GLib.MainLoop()
# mainloop.run()








