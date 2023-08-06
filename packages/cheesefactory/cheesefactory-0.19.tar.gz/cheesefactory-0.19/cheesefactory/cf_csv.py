# cf_csv.py
__authors__ = ["tsalazar"]
__version__ = "0.1"

import logging
import csv


class CSV:
    """Create and append to CSV files."""

    def __init__(self, output_file=None, header=None, content=None, delimeter=',', mode='create', dictwriter=True):
        """Initialize an instance of the CSV class.

        Args:
            output_file (str): File to write.
            header (list[str]): List of file header column names.
            content: CSV file content to write or append.
            delimeter (str): Character to use for delimiting CSV records.
            mode (str): "append" to, "create", or "read" a CSV file.
            dictwriter (bool): Is the content being provided as a dictionary?
        """

        self.__logger = logging.getLogger(__name__)
        self.__logger.debug('Initializing CSV class object')

        self.__output_file = output_file     # Output file name
        self.__header = header         # Table header
        self.__content = content                  # Table content
        self.__delimiter = delimeter
        self.__mode = mode                        # 'create' or 'append'
        self.__dictwriter = dictwriter

        self.__logger.debug('Performing sanity check.')
        self.__sanity_check()

        if mode == 'create':
            self.__create_csv_file()
        elif mode == 'append':
            self.__append_csv_file()
        # TODO (tsalazar): Build out the 'read' mode for CSV
        elif mode == 'read':
            self.__read_csv_file()
        else:
            self.__logger.critical('No valid CSV mode selected.  Use "create", "append", or "read".')

    def __sanity_check(self):
        """Are we crazy?"""

        assert self.__output_file is not None, self.__logger.critical('No output file defined.')
        assert self.__content is not None, self.__logger.critical('No content defined.')

    def __create_csv_file(self):
        """Create a CSV file."""

        self.__logger.debug('Creating CSV file: ' + self.__output_file)

        with open(self.__output_file, 'w', newline='\n') as csv_file:

            if self.__dictwriter is True:
                csv_writer = csv.DictWriter(
                    csv_file,
                    fieldnames=self.__header,
                    delimiter=self.__delimiter,
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL
                )
                # Write header
                csv_writer.writeheader()

            else:
                csv_writer = csv.writer(
                    csv_file,
                    delimiter=self.__delimiter,
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL
                )
                # Write header
                self.__logger.debug('Writing header: ' + str(self.__header))
                csv_writer.writerow(self.__header)

            # Write body
            for row in self.__content:
                self.__logger.debug('Writing row: ' + str(row))
                csv_writer.writerow(row)

    def __append_csv_file(self):
        """Append to an existing CSV file."""

        self.__logger.debug('Appending CSV file: ' + self.__output_file)

        with open(self.__output_file, 'a', newline='\n') as csv_file:
            if self.__dictwriter is True:
                csv_writer = csv.DictWriter(
                    csv_file,
                    fieldnames=self.__header,
                    delimiter=self.__delimiter,
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL
                )
            else:
                csv_writer = csv.writer(
                    csv_file,
                    delimiter=self.__delimiter,
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL
                )

            # Write body
            for row in self.__content:
                self.__logger.debug('Writing row: ' + str(row))
                csv_writer.writerow(row)

    def __read_csv_file(self):
        """Read a CSV file"""
        pass
