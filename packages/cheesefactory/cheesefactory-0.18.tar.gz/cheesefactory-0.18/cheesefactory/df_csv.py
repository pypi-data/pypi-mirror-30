# df_csv.py
__authors__ = ["tsalazar"]
__version__ = "0.1"

import logging


class DfCSV:
    """Create and append a dataframe to CSV files."""

    def __init__(self, output_file=None, content=None, delimeter=',', mode='create'):
        """Initialize an instance of the DfCSV class.

        Args:
            output_file (str): File to write.
            content (pandas.Dataframe): CSV file content to write or append.
            delimeter (str): Character to use for delimiting CSV records.
            mode (str): "append" to, "create", or "read" a CSV file.
        """

        self.__logger = logging.getLogger(__name__)
        self.__logger.debug('Initializing DfCSV class object')

        self.__output_file = output_file
        self.__content = content
        self.__delimiter = delimeter
        self.__mode = mode

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
        self.__content.to_csv(path_or_buf=self.__output_file, sep=self.__delimiter, index=False)

    def __append_csv_file(self):
        """Append to an existing CSV file."""

        self.__logger.debug('Appending CSV file: ' + self.__output_file)

        with open(self.__output_file, 'a', newline='\n') as csv_file:
            self.__content.to_csv(csv_file, header=False)

    def __read_csv_file(self):
        """Read a CSV file"""
        pass
