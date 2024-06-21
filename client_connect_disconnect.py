import bluetooth_constants
import bluetooth_utils
import dbus
import sys
sys.path.insert(0, '.')
import time

bus = None
device_proxy = None
device_interface = None

def connect(bdaddr):
    global bus
    global device_proxy
    global device_interface

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
    
def disconnect():
    global device_interface
    try:
        time_start = time.time()
        device_interface.Disconnect()
        time_end = time.time()
        print(f'Disconnect() cost {"{:.2f}".format(time_end - time_start)} seconds.')
    except Exception as e:
        print("Failed to disconnect")
        print(e.get_dbus_name())
        print(e.get_dbus_message())
        return bluetooth_constants.RESULT_EXCEPTION
    else:
        print("Disconnected OK")
        return bluetooth_constants.RESULT_OK
    

if (len(sys.argv) != 2):
    print("usage: python3 ", sys.argv[0], " [bdaddr]")
    sys.exit(1)

bdaddr = sys.argv[1]
bus = dbus.SystemBus()

test_number_index = 0

connect_max_number = 5
connect_number = 0

while True:
    test_number_index += 1
    print(f'\n---------------------- {test_number_index} ----------------------')
    while connect_number < connect_max_number:
        connect_number += 1
        print("Connecting to " + bdaddr + " {}".format(connect_number) + " time(s).") 
        rt_code = connect(bdaddr)
        if rt_code != 0:
            print('Connect() Failed, retry after 3 seconds......')
            time.sleep(3)
            continue
        else:
            connect_number = 0
            break
    if connect_number == connect_max_number:
        print(f"Connect() Failed after {connect_number} times.")
        break

    time.sleep(5)
    print("Disconnecting from " + bdaddr)
    rt_code = disconnect()
    if rt_code != 0:
        print('Disonnect() Failed, exit loop.')
        break

    time.sleep(5)







