# pi-telemetry
Gathers telemetry via CAN BUS from a Haltech ECU and writes to a file.

Eventually, this data will be transmitted via APRS using [Direwolf](https://github.com/wb2osz/direwolf).

## Requirements

### Hardware
- Raspberry Pi Zero 2W (with headers)
- [Waveshare CAN Hat](https://www.waveshare.com/rs485-can-hat.htm)

### Software
- Python 3.9+
- Python dependencies are declared in pyproject.toml. To install runtime dependencies:
  - Using pip:
    - Runtime only: `pip install .`
    - Development (adds Black): `pip install -e .[dev]`
- Add the following lines to your Raspberry Pi boot config:
  ```
  dtparam=spi=on
  dtoverlay=mcp2515-can0,oscillator=12000000,interrupt=25,spimaxfrequency=1000000
  ```

## Usage

`sudo ./startup.sh`

This will write the data to a file, `telemetry_data.csv`, with a single line of values.
Feel free to modify this to suit your needs; I only want the latest values for parsing using
[Direwolf](https://github.com/wb2osz/direwolf) to send via [APRS](https://en.wikipedia.org/wiki/Automatic_Packet_Reporting_System).

## Resources

- [Waveshare documentation and sample project](https://www.waveshare.com/wiki/RS485_CAN_HAT) (the basis for this repo).
- [Haltech ECU CAN broadcast protocol](https://support.haltech.com/portal/en/kb/articles/haltech-can-ecu-broadcast-protocol)
- [Haltech CAN protocol specification](https://support.haltech.com/portal/en/kb/articles/haltech-can-protocol-specification)