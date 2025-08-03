import struct
import time
import logging
from can.typechecking import CanFilter

class CANParser:
    """
    Class for parsing CAN bus messages for vehicle telemetry.
    Handles messages for coolant temperature, oil temperature, fuel level,
    ABS error, and check engine light.
    """
    
    def __init__(self, can_interface, logger=None):
        """
        Initialize the CANParser with a CAN interface and logger.
        
        Args:
            can_interface: The CAN bus interface to receive messages from
            logger: Logger instance for logging messages (optional)
        """
        self.can_interface = can_interface
        self.logger = logger or logging.getLogger(__name__)
        
        # Constants for conversions
        self.LITERS_TO_GALLONS = 0.264172  # 1 Liter = 0.264172 US Gallons
        self.CELSIUS_TO_FAHRENHEIT = lambda c: (c * 9 / 5) + 32  # Convert Celsius to Fahrenheit
        
        # Variables to store the parsed values
        self.coolant_temp_celsius = None
        self.coolant_temp_fahrenheit = None
        self.oil_temp_celsius = None
        self.oil_temp_fahrenheit = None
        self.fuel_level_gallons = None
        self.abs_error = None
        self.check_engine = None
    
    def parse_messages(self, timeout=10.0):
        """
        Main method to continuously parse CAN messages.
        
        Args:
            timeout: Timeout in seconds for receiving messages
            
        Returns:
            Dictionary containing the latest parsed values
        """
        try:
            msg = self.can_interface.recv(timeout)
            if msg is None:
                self.logger.info("Timeout occurred, no message received")
                return self.get_current_values()
            
            self.logger.info(f"Received message ID: 0x{msg.arbitration_id:X}")
            
            # Process message based on arbitration ID
            if msg.arbitration_id == 0x3E0:
                self._process_temperature_message(msg)
            elif msg.arbitration_id == 0x3E2:
                self._process_fuel_level_message(msg)
            elif msg.arbitration_id == 0x3E4:
                self._process_error_message(msg)
            
            # Display all current values
            self._log_current_values()
            
            return self.get_current_values()
            
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            time.sleep(1)  # Prevent tight error loop
            return self.get_current_values()
    
    def _process_temperature_message(self, msg):
        """Process coolant and oil temperature message (ID: 0x3E0)"""
        try:
            # Extract the full byte for coolant temperature
            self.coolant_temp_celsius = (struct.unpack(">H", msg.data[0:2])[0] / 10.0) - 273.15
            self.coolant_temp_fahrenheit = self.CELSIUS_TO_FAHRENHEIT(self.coolant_temp_celsius)
            
            self.logger.info(f"Coolant Temperature: {self.coolant_temp_celsius:.2f}°C / {self.coolant_temp_fahrenheit:.2f}°F")
            
            # Extract the full byte for oil temperature
            self.oil_temp_celsius = (struct.unpack(">H", msg.data[6:8])[0] / 10.0) - 273.15
            self.oil_temp_fahrenheit = self.CELSIUS_TO_FAHRENHEIT(self.oil_temp_celsius)
            
            self.logger.info(f"Oil Temperature: {self.oil_temp_celsius:.2f}°C / {self.oil_temp_fahrenheit:.2f}°F")
        except Exception as e:
            self.logger.error(f"Error processing coolant & oil temperature: {e}")
    
    def _process_fuel_level_message(self, msg):
        """Process fuel level message (ID: 0x3E2)"""
        try:
            # Extract bytes 0-1 for fuel level in liters
            fuel_level_liters = struct.unpack(">H", msg.data[0:2])[0] / 10.0
            self.fuel_level_gallons = fuel_level_liters * self.LITERS_TO_GALLONS
            
            self.logger.info(f"Fuel Level: {fuel_level_liters}L / {self.fuel_level_gallons:.2f} gallons")
        except Exception as e:
            self.logger.error(f"Error processing fuel level: {e}")
    
    def _process_error_message(self, msg):
        """Process ABS Error and Check Engine Light message (ID: 0x3E4)"""
        try:
            # Extract bit 0 for ABS Error
            self.abs_error = bool((msg.data[7] & 0b10000000) >> 7)
            
            # Extract bit 1 for Check Engine Light
            self.check_engine = bool((msg.data[7] & 0b01000000) >> 6)
            
            self.logger.info(f"ABS Error: {self.abs_error}")
            self.logger.info(f"Check Engine Light: {self.check_engine}")
        except Exception as e:
            self.logger.error(f"Error processing ABS/Check Engine status: {e}")
    
    def _log_current_values(self):
        """Log all current values"""
        self.logger.info("\nCurrent Values:")
        self.logger.info(
            f"Coolant Temperature: {self.coolant_temp_fahrenheit:.2f}°F"
            if self.coolant_temp_fahrenheit is not None
            else "Coolant Temperature: Not received"
        )
        self.logger.info(
            f"Oil Temperature: {self.oil_temp_fahrenheit:.2f}°F"
            if self.oil_temp_fahrenheit is not None
            else "Oil Temperature: Not received"
        )
        self.logger.info(
            f"Fuel Level: {self.fuel_level_gallons:.2f} gallons"
            if self.fuel_level_gallons is not None
            else "Fuel Level: Not received"
        )
        self.logger.info(f"ABS Error: {self.abs_error}" if self.abs_error is not None else "ABS Error: Not received")
        self.logger.info(
            f"Check Engine Light: {self.check_engine}"
            if self.check_engine is not None
            else "Check Engine Light: Not received"
        )
        self.logger.info("-" * 50)
    
    def get_current_values(self):
        """
        Get the current parsed values.
        
        Returns:
            Dictionary containing all the parsed values
        """
        return {
            "coolant_temp_celsius": self.coolant_temp_celsius,
            "coolant_temp_fahrenheit": self.coolant_temp_fahrenheit,
            "oil_temp_celsius": self.oil_temp_celsius,
            "oil_temp_fahrenheit": self.oil_temp_fahrenheit,
            "fuel_level_gallons": self.fuel_level_gallons,
            "abs_error": self.abs_error,
            "check_engine": self.check_engine
        }