import logging
import sys
import time

import can

from can_parser import CANParser, CAN_FILTERS
from csv_writer import CSVWriter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Initialize CAN interface
try:
    logger.info("Initializing CAN interface...")
    can0 = can.interface.Bus(channel="can0", interface="socketcan")
    logger.info("CAN interface initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize CAN interface: {e}")
    sys.exit(1)

try:
    if can0 is None:
        raise ValueError("CAN interface not initialized")

    can0.set_filters(CAN_FILTERS)

    logger.info("CAN filters set up successfully")

except (AttributeError, ValueError, RuntimeError) as e:
    logger.error(f"Failed to set up CAN filters: {e}")
    sys.exit(1)

try:
    logger.info("Waiting for CAN messages...")

    # Create an instance of the CANParser
    parser = CANParser(can_interface=can0, logger=logger)

    # Create an instance of the CSVWriter
    csv_writer = CSVWriter(filename="telemetry_data.csv", logger=logger)

    # Main loop to continuously parse CAN messages
    while True:
        try:
            # Parse messages and get the current values
            values = parser.parse_messages(timeout=10.0)

            # Write the values to the CSV file
            if values:
                csv_writer.write_values(values)

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
    logger.info("Program exited")
