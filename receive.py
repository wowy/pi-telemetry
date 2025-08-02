import os
import can
from can.typechecking import CanFilter
import time
import struct
import logging
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Constants for conversions
LITERS_TO_GALLONS = 0.264172  # 1 Liter = 0.264172 US Gallons

# Initialize CAN interface
try:
    logger.info("Initializing CAN interface...")
    os.system("sudo ip link set can0 type can bitrate 100000")
    os.system("sudo ifconfig can0 up")

    can0 = can.interface.Bus(
        channel="can0", interface="socketcan"
    )  # Updated to use 'interface' instead of deprecated 'bustype'
    logger.info("CAN interface initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize CAN interface: {e}")
    sys.exit(1)

# Define constants
CAN_MASK_STANDARD = 0x7FF

# CAN filter definitions - using proper CanFilter objects
CAN_FILTERS = [
    CanFilter(can_id=0x3E0, can_mask=CAN_MASK_STANDARD),  # Coolant Temperature
    CanFilter(can_id=0x3E1, can_mask=CAN_MASK_STANDARD),  # Oil Temperature
    CanFilter(can_id=0x3E9, can_mask=CAN_MASK_STANDARD),  # Fuel Level
    CanFilter(
        can_id=0x3EB, can_mask=CAN_MASK_STANDARD
    ),  # ABS Error and Check Engine Light
]

try:
    if can0 is None:
        raise ValueError("CAN interface not initialized")

    can0.set_filters(CAN_FILTERS)

    logger.info("CAN filters set up successfully")

except (AttributeError, ValueError, RuntimeError) as e:
    logger.error(f"Failed to set up CAN filters: {e}")
    os.system("sudo ifconfig can0 down")
    sys.exit(1)

try:
    logger.info("Waiting for CAN messages...")

    # Variables to store the parsed values
    coolant_temp_celsius = None
    oil_temp_celsius = None
    fuel_level_gallons = None
    abs_error = None
    check_engine = None

    while True:
        try:
            msg = can0.recv(10.0)
            if msg is None:
                logger.info("Timeout occurred, no message received")
                continue

            logger.info(f"Received message ID: 0x{msg.arbitration_id:X}")

            # Process Coolant Temperature (ID: 0x3E0)
            if msg.arbitration_id == 0x3E0:
                try:
                    # Extract the full byte for coolant temperature
                    coolant_temp_kelvin = msg.data[0]
                    coolant_temp_celsius = coolant_temp_kelvin - 273.15

                    logger.info(
                        f"Coolant Temperature: {coolant_temp_kelvin}K / {coolant_temp_celsius:.2f}°C"
                    )
                except Exception as e:
                    logger.error(f"Error processing coolant temperature: {e}")

            # Process Oil Temperature (ID: 0x3E1)
            elif msg.arbitration_id == 0x3E1:
                try:
                    # Extract the full byte for oil temperature
                    oil_temp_kelvin = msg.data[0]
                    oil_temp_celsius = oil_temp_kelvin - 273.15

                    logger.info(
                        f"Oil Temperature: {oil_temp_kelvin}K / {oil_temp_celsius:.2f}°C"
                    )
                except Exception as e:
                    logger.error(f"Error processing oil temperature: {e}")

            # Process Fuel Level (ID: 0x3E9)
            elif msg.arbitration_id == 0x3E9:
                try:
                    # Extract bytes 0-1 for fuel level in liters
                    fuel_level_liters = struct.unpack("<H", msg.data[0:2])[0]
                    fuel_level_gallons = fuel_level_liters * LITERS_TO_GALLONS

                    logger.info(
                        f"Fuel Level: {fuel_level_liters}L / {fuel_level_gallons:.2f} gallons"
                    )
                except Exception as e:
                    logger.error(f"Error processing fuel level: {e}")

            # Process ABS Error and Check Engine Light (ID: 0x3EB)
            elif msg.arbitration_id == 0x3EB:
                try:
                    # Extract bit 0 for ABS Error
                    abs_error = bool(msg.data[0] & 0b00000001)

                    # Extract bit 1 for Check Engine Light
                    check_engine = bool((msg.data[0] & 0b00000010) >> 1)

                    logger.info(f"ABS Error: {abs_error}")
                    logger.info(f"Check Engine Light: {check_engine}")
                except Exception as e:
                    logger.error(f"Error processing ABS/Check Engine status: {e}")

            # Display all current values
            logger.info("\nCurrent Values:")
            logger.info(
                f"Coolant Temperature: {coolant_temp_celsius:.2f}°C"
                if coolant_temp_celsius is not None
                else "Coolant Temperature: Not received"
            )
            logger.info(
                f"Oil Temperature: {oil_temp_celsius:.2f}°C"
                if oil_temp_celsius is not None
                else "Oil Temperature: Not received"
            )
            logger.info(
                f"Fuel Level: {fuel_level_gallons:.2f} gallons"
                if fuel_level_gallons is not None
                else "Fuel Level: Not received"
            )
            logger.info(
                f"ABS Error: {abs_error}"
                if abs_error is not None
                else "ABS Error: Not received"
            )
            logger.info(
                f"Check Engine Light: {check_engine}"
                if check_engine is not None
                else "Check Engine Light: Not received"
            )
            logger.info("-" * 50)

        except can.CanError as e:
            logger.error(f"CAN error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(1)  # Prevent tight error loop

except KeyboardInterrupt:
    logger.info("Program terminated by user")
except Exception as e:
    logger.error(f"Program terminated due to error: {e}")
finally:
    try:
        logger.info("Shutting down CAN interface...")
        os.system("sudo ifconfig can0 down")
        logger.info("CAN interface shut down successfully")
    except Exception as e:
        logger.error(f"Error shutting down CAN interface: {e}")
    logger.info("Program exited")
