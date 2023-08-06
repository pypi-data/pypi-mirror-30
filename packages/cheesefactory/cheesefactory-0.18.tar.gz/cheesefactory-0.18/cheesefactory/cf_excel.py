# cf_excel.py
__authors__ = ["tsalazar"]
__version__ = "0.2"

import logging
import xlsxwriter


class Excel:
    """Create an Excel workbook with worksheets.

    Attributes:
        workbook: Excel workbook object.
        header_format_definition (dict): Cell and font format settings for the worksheet header.
        row_format_definition (dict): Cell and font format settings for worksheet rows.
        alternate_row_format_definition (dict): Cell and font format settings for alternating worksheet rows.
    """

    def __init__(self, output_file=None):
        """Initialize an instance of the Excel class

        Args:
            output_file (str): Name of the Excel workbook file.
        """

        self.__logger = logging.getLogger(__name__)
        self.__logger.debug('Initializing Excel class object')

        self._output_file = output_file  # Output file name

        self.header_format_definition = {
            # == Font ==
            'font_name': 'Calibri',  # Font type (i.e. 'Consolas', 'Times New Roman', 'Calibri', 'Courier New')
            'font_size': 10,  # Font size
            'font_color': 'black',  # Font color
            'bold': True,  # Bold
            'italic': False,  # Italic
            'underline': 0,  # Underline (0, 1 = Single, 2 = Double, 33 = Single Accounting, 34 = Double Accounting)
            'font_strikeout': False,  # Strikeout
            'font_script': 0,  # Super/Subscript (0 = Off, 1 = Superscript, 2 = Subscript)

            # == Number ==
            # 'num_format': '',  # Numeric/Date format and Conditional formatting

            # == Protection ==
            'locked': False,  # Lock cells
            'hidden': False,  # Hide formulas

            # == Alignment ==
            'align': 'center',  # Horizontal align ('center', 'right', 'fill', 'justify', 'center_across')
            'valign': 'vcenter',  # Vertical align ('top', 'vcenter', 'bottom', 'vjustify')
            'rotation': 0,  # Rotation
            'text_wrap': False,  # Text wrap
            # 'text_justlast': False,  # Justify last. For Eastern languages
            # 'center_across': False,  # Center across
            'indent': 0,  # Indentation
            'shrink': False,  # Shrink to fit

            # == Pattern ==
            'pattern': 1,  # Cell Pattern (1 = solid fill of bg_color)
            'bg_color': '#D7E4BC',  # Background color
            # 'fg_color': '#D7E4BC',  # Foreground color

            # == Border ==
            'border': 1,  # Cell border
            # 'bottom': '',  # Bottom border
            # 'top': '',  # Top border
            # 'left': '',  # Left border
            # 'right': '',  # Right border
            'border_color': 'white',  # Border color
            # 'bottom_color': '',  # Bottom color
            # 'top_color': '',  # Top color
            # 'left_color': '',  # Left color
            # 'right_color': '',  # Right color
        }

        self.row_format_definition = {
            # == Font ==
            'font_name': 'Calibri Light',  # Font type (i.e. 'Consolas', 'Times New Roman', 'Calibri', 'Courier New')
            'font_size': 11,  # Font size
            'font_color': 'black',  # Font color
            'bold': False,  # Bold
            'italic': False,  # Italic
            'underline': 0,  # Underline (0, 1 = Single, 2 = Double, 33 = Single Accounting, 34 = Double Accounting)
            'font_strikeout': False,  # Strikeout
            'font_script': 0,  # Super/Subscript (0 = Off, 1 = Superscript, 2 = Subscript)

            # == Number ==
            # 'num_format': '',  # Numeric/Date format and Conditional formatting

            # == Protection ==
            'locked': False,  # Lock cells
            'hidden': False,  # Hide formulas

            # == Alignment ==
            # 'align': 'left',  # Horizontal align ('center', 'right', 'fill', 'justify', 'center_across')
            # 'valign': 'vcenter',  # Vertical align ('top', 'vcenter', 'bottom', 'vjustify')
            # 'rotation': 0,  # Rotation
            'text_wrap': False,  # Text wrap
            # 'text_justlast': False,  # Justify last. For Eastern languages
            # 'center_across': False,  # Center across
            'indent': 0,  # Indentation
            'shrink': False,  # Shrink to fit

            # == Pattern ==
            'pattern': 1,  # Cell Pattern (1 = solid fill of bg_color)
            'bg_color': '#FFFFFF',  # Background color
            'fg_color': 'black',  # Foreground color

            # == Border ==
            'border': 1,  # Cell border
            # 'bottom': '',  # Bottom border
            # 'top': '',  # Top border
            # 'left': '',  # Left border
            # 'right': '',  # Right border
            'border_color': '080851',  # Border color
            # 'bottom_color': '',  # Bottom color
            # 'top_color': '',  # Top color
            # 'left_color': '',  # Left color
            # 'right_color': '',  # Right color
        }

        self.alternate_row_format_definition = {
            # == Font ==
            'font_name': 'Consolas',  # Font type (i.e. 'Consolas', 'Times New Roman', 'Calibri', 'Courier New')
            'font_size': 11,  # Font size
            'font_color': 'black',  # Font color
            'bold': False,  # Bold
            'italic': False,  # Italic
            'underline': 0,  # Underline (0, 1 = Single, 2 = Double, 33 = Single Accounting, 34 = Double Accounting)
            'font_strikeout': False,  # Strikeout
            'font_script': 0,  # Super/Subscript (0 = Off, 1 = Superscript, 2 = Subscript)

            # == Number ==
            # 'num_format': '',  # Numeric/Date format and Conditional formatting

            # == Protection ==
            'locked': False,  # Lock cells
            'hidden': False,  # Hide formulas

            # == Alignment ==
            # 'align': 'left',  # Horizontal align ('center', 'right', 'fill', 'justify', 'center_across')
            # 'valign': 'vcenter',  # Vertical align ('top', 'vcenter', 'bottom', 'vjustify')
            # 'rotation': 0,  # Rotation
            'text_wrap': False,  # Text wrap
            # 'text_justlast': False,  # Justify last. For Eastern languages
            # 'center_across': False,  # Center across
            'indent': 0,  # Indentation
            'shrink': False,  # Shrink to fit

            # == Pattern ==
            'pattern': 1,  # Cell Pattern (1 = solid fill of bg_color)
            'bg_color': '#D4D3FF',  # Background color
            'fg_color': 'black',  # Foreground color

            # == Border ==
            'border': 1,  # Cell border
            # 'bottom': '',  # Bottom border
            # 'top': '',  # Top border
            # 'left': '',  # Left border
            # 'right': '',  # Right border
            'border_color': '080851',  # Border color
            # 'bottom_color': '',  # Bottom color
            # 'top_color': '',  # Top color
            # 'left_color': '',  # Left color
            # 'right_color': '',  # Right color
        }

        self.workbook = None

        self.__logger.debug('Excel class object initialized')

    def __sanity_check(self):
        """Are we crazy?"""

        assert self._output_file is not None, self.__logger.critical('No output file defined.')

    def __open_workbook(self):
        """Open the workbook and prep it for worksheets

        Returns:
            workbook: An XlsxWriter workbook.
        """

        # Create a workbook.
        self.__logger.debug(f'Creating workbook: {self._output_file}')
        self.workbook = xlsxwriter.Workbook(self._output_file)

        # Define cell formats
        self.__logger.debug('header_format:')
        self.__logger.debug(self.header_format_definition)
        self._header_format = self.workbook.add_format(self.header_format_definition)

        self.__logger.debug('body_row_format:')
        self.__logger.debug(self.row_format_definition)
        self._row_format = self.workbook.add_format(self.row_format_definition)

        self.__logger.debug('alternate_row_format:')
        self.__logger.debug(self.alternate_row_format_definition)
        self._alternate_row_format = self.workbook.add_format(self.alternate_row_format_definition)

    def create_worksheet(self, worksheet_name='Worksheet', content=None, header=None):
        """Add a worksheet to the workbook

        Args:
            worksheet_name (str): Excel worksheet name.
            content: Worksheet content.
            header: Worksheet header.
        """

        # Start a workbook if it doesn't yet exist
        if self.workbook is None:
            self.__open_workbook()

        self.__logger.debug('Creating worksheet: ' + worksheet_name)

        if content is None:
            self.__logger.warning('No worksheet content defined')
        if header is None:
            self.__logger.warning('No worksheet header defined')

        # Stay under 31 character limit
        worksheet_name = worksheet_name[:30]

        worksheet = self.workbook.add_worksheet(worksheet_name)

        # Assign formatting
        header_format = self.workbook.add_format(self.header_format_definition)
        row_format = self.workbook.add_format(self.row_format_definition)
        # alternate_row_format = self.workbook.add_format(self.alternate_row_format_definition)

        column_widths = []
        column = 0

        # Output header
        if header is not None:
            for header_item in header:
                self.__logger.debug(f'Writing row: column={column}, header_item={header_item}')
                worksheet.write(0, column, header_item, header_format)
                column_widths.append(len(header_item))
                column += 1

            worksheet.autofilter(0, 0, 0, column-1)  # Add filter buttons to the top row

        # Start from the first cell. Rows and columns are zero indexed.
        if header is not None:
            row = 1
        else:
            row = 0

        column = 0

        # Iterate over the data and write it out row by row.
        if content is not None:

            if header is None:
                column_widths = [5] * len(content[0])

            for result in content:

                for key, data in result.items():

                    if type(data) is int or type(data) is float:
                        worksheet.write(row, column, data, row_format)
                    else:
                        worksheet.write(row, column, str(data), row_format)

                    if len(str(data)) > column_widths[column]:
                        column_widths[column] = len(str(data))

                    column += 1

                # Move to next row and reset to first column
                row += 1
                column = 0

        # Adjust the column width.
        for column_width in column_widths:
            worksheet.set_column(column, column, column_width + 6)
            column += 1

        # Freeze the first row
        worksheet.freeze_panes(1, 0)

        # Adds Filters
        # worksheet.autofilter('A1:Z1')

    def close_workbook(self):
        """Gracefully wrap up the workbook"""

        self.__logger.debug('Workbook created.')
        self.workbook.close()

    # def __del__(self):
    #    """Wrap it all up."""

    #    if self.workbook is not None:
    #        self.close_workbook()
