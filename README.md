# pi-telemetry
Gathers telemetry via CAN BUS from a Haltech ECU, and writes to a file.

Eventually, this data will be transmitted via APRS using [Direwolf](https://github.com/wb2osz/direwolf).

## Requirements

### Hardware
- Raspberry Pi Zero 2W (with headers)
- [Waveshare CAN Hat](https://www.waveshare.com/rs485-can-hat.htm)

### Software
- Python 3.9
  - python3-black
  - python3-can

## Usage

`sudo python3 receive.py`

## Resources

- [Waveshare documentation and sample project](https://www.waveshare.com/wiki/RS485_CAN_HAT) (the basis for this repo).
- [Haltech ECU CAN broadcast protocol](https://support.haltech.com/portal/en/kb/articles/haltech-can-ecu-broadcast-protocol)
- [Haltech CAN protocol specification](https://support.haltech.com/portal/en/kb/articles/haltech-can-protocol-specification)