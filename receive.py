import os
import can
import time

os.system("sudo ip link set can0 type can bitrate 100000")
os.system("sudo ifconfig can0 up")

can0 = can.interface.Bus(channel="can0", bustype="socketcan")  # socketcan_native

# Set up a filter for messages with ID 0x3E0
can0.set_filters([{"can_id": 0x3E0, "can_mask": 0x7FF, "extended": False}])

try:
    print("Waiting for CAN message with ID 0x3E0...")
    while True:
        msg = can0.recv(10.0)
        if msg is None:
            print("Timeout occurred, no message.")
            continue

        if msg.arbitration_id == 0x3E0:
            print(f"Received message: {msg}")

            # Extract bits 0-1 from the first byte of data
            # This gets the 2 least significant bits (0 and 1)
            value = msg.data[0] & 0b00000011

            # Divide by 10
            kelvin = value / 10.0

            # Convert from Kelvin to Celsius
            celsius = kelvin - 273.15

            print(f"Extracted value (bits 0-1): {value}")
            print(f"Temperature in Kelvin: {kelvin}")
            print(f"Temperature in Celsius: {celsius}")
            break

except KeyboardInterrupt:
    print("Program terminated by user")
finally:
    os.system("sudo ifconfig can0 down")
