# df_excel.py
__authors__ = ["tsalazar"]
__version__ = "0.2"

import logging
import pandas as pd
from .cf_excel import Excel


class DfExcel(Excel):

    def __init__(self, output_file):
        """Initialize an instance of the DfExcel class

        Args:
            output_file (str): Name of the Excel workbook file.
        """

        self.__logger = logging.getLogger(__name__)
        self.__logger.debug('Initializing DfExcel class object')

        super().__init__(output_file=output_file)

        # Create writer and workbook
        self.__logger.debug(f'Creating workbook: {self._output_file}')
        self.__writer = pd.ExcelWriter(self._output_file, engine='xlsxwriter')
        self.workbook = self.__writer.book

        self.__logger.debug('DfExcel class object initialized')

    def create_worksheet(self, worksheet_name='Worksheet', content=None):
        """Add a worksheet to the workbook

        Args:
            worksheet_name (str): Excel worksheet name.
            content (pd.DataFrame): Worksheet content.
        """
        assert content is not None, self.__logger.critical('content is missing.')

        self.__logger.debug('Creating worksheet: ' + worksheet_name)

        # Define cell formats
        self.__logger.debug('header_format:')
        self.__logger.debug(self.header_format_definition)
        header_format = self.workbook.add_format(self.header_format_definition)

        self.__logger.debug('body_row_format:')
        self.__logger.debug(self.row_format_definition)
        # row_format = self.workbook.add_format(self.row_format_definition)

        self.__logger.debug('alternate_row_format:')
        self.__logger.debug(self.alternate_row_format_definition)
        # alternate_row_format = self.workbook.add_format(self.alternate_row_format_definition)

        # Create the worksheet and keep the name <= 31 characters
        content.to_excel(self.__writer, index=False, sheet_name=worksheet_name[:30])
        worksheet = self.__writer.sheets[worksheet_name[:30]]

        worksheet.freeze_panes(1, 0)  # Freeze the top row
        # worksheet.autofilter('A1:Z1')  # Add filter buttons to the top row

        column_widths = []
        column_number = 0

        # Draws header
        for column_number, value in enumerate(content.columns.values):
            worksheet.write(0, column_number, value, header_format)

        worksheet.autofilter(0, 0, 0, column_number)  # Add filter buttons to the top row

        # Find column widths
        for column_name in content.columns:
            column_widths.append(content[column_name].map(lambda x: len(str(x))).max())

        # Adjust the column width.
        column_number = 0
        for column_width in column_widths:
            # print('set column ' + str(column) + ' to ' + str(column_width + 4))
            worksheet.set_column(column_number, column_number, column_width + 6)
            column_number += 1

    def close_workbook(self):
        """Gracefully wrap up the workbook"""

        self.__writer.save()
        self.__logger.debug('Workbook created.')
