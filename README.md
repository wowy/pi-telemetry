# pi-telemetry
Gathers telemetry via CAN BUS, and sends over APRS

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

- Waveshare [documentation and sample project](https://www.waveshare.com/wiki/RS485_CAN_HAT) (the basis for this repo).