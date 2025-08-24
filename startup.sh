#!/bin/bash

sudo ip link set can0 down
sudo ip link set can0 type can bitrate 1000000
sudo ip link set can0 up

python3 src/pi-telemetry/receive.py