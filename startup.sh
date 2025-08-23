#!/bin/bash

#sudo ip link set can0 type can bitrate 100000
#sudo ifconfig can0 txqueuelen 65536
#sudo ifconfig can0 up

python3 src/pi-telemetry/receive.py