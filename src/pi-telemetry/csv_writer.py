import csv
import logging
import os
import tempfile


class CSVWriter:
    """
    Class for atomically writing telemetry data to a CSV file.
    The file will be overwritten each time data is written and will only contain one line.
    """

    def __init__(self, filename, logger=None):
        """
        Initialize the CSVWriter with a filename and logger.

        Args:
            filename: The path to the CSV file to write to
            logger: Logger instance for logging messages (optional)
        """
        self.filename = filename
        self.logger = logger or logging.getLogger(__name__)

    def write_values(self, values):
        """
        Atomically write the values dictionary to a CSV file.
        The file will be overwritten each time and will only contain one line.

        Args:
            values: Dictionary containing the values to write
        """
        try:
            # Create a temporary file in the same directory as the target file
            directory = os.path.dirname(self.filename)
            with tempfile.NamedTemporaryFile(mode="w", delete=False, dir=directory) as temp_file:
                # Get the field names from the values dictionary
                fieldnames = list(values.keys())

                # Create a CSV writer
                writer = csv.DictWriter(temp_file, fieldnames=fieldnames)

                # Write the header and the values
                writer.writeheader()

                # Format float values to two decimal places before writing
                formatted_values = {k: (f"{v:.2f}" if isinstance(v, float) else v) for k, v in values.items()}
                writer.writerow(formatted_values)

                # Ensure all data is written to disk
                temp_file.flush()
                os.fsync(temp_file.fileno())

                # Get the temporary filename
                temp_filename = temp_file.name

            # Atomically replace the target file with the temporary file
            os.replace(temp_filename, self.filename)

            self.logger.debug(f"Successfully wrote telemetry data to {self.filename}")

        except Exception as e:
            self.logger.error(f"Error writing telemetry data to CSV: {e}")
            # If the temporary file still exists, remove it
            if "temp_filename" in locals():
                try:
                    os.remove(temp_filename)
                except:
                    pass
