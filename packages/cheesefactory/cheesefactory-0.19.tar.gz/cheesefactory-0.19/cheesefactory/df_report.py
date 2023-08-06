# df_report.py
__authors__ = ["tsalazar"]
__version__ = "0.4"

# v0.4 (tsalazar) -- Added def __del__()

import logging
import os

from .df_csv import DfCSV
from .cf_email import Email
from .df_database import DfDatabase
from .cf_sftp import SFTP
from .df_excel import DfExcel


class DfReport:

    def __init__(
            self, email_report=False, email_host=None, email_port=None, email_username=None, email_password=None,
            email_sender=None, email_recipients=None, email_subject=None, email_body=None, email_barracuda_tag=None,
            email_use_tls=False, db_host=None, db_port=None, db_database=None, db_username=None, db_password=None,
            db_encoding=None, db_driver=None, sftp_report=False, sftp_host=None, sftp_port='22', sftp_username=None,
            sftp_password=None, sftp_remote_directory=None, report_directory='/tmp', sql_query=None,
            dataframe_result=False
    ):
        """Initialize an instance of the Report class

        Args:
            email_report (bool): Email this report?
            email_host (str): Email server hostname or IP.
            email_port (str): Email server port.
            email_username (str): Email server account username.
            email_password (str): Email server account password.
            email_sender (str): Email sender.
            email_recipients (list[str]): List of Email recipients.
            email_subject (str): Email subject line.
            email_body (str): Body of Email.
            email_barracuda_tag (str): An Email header tag value that forces the Barracuda to encrypt the Email.
            email_use_tls (bool): Connect to the Email server using TLS?
            db_host (str): Database server hostname or IP.
            db_port (str): Database server port.
            db_database (str): Database name.
            db_username (str): Database server account username.
            db_password (str): Database server account password.
            db_encoding (str): Database server client encoding (utf-8, latin1, etc.).
            db_driver (str): Database driver (postgres, FreeTDS, {MSSQLSERVER}, etc.)
            sftp_report (bool): SFTP this report?
            sftp_host (str): SFTP server hostname or IP.
            sftp_port (str): SFTP server port.
            sftp_username (str): SFTP server account username.
            sftp_password (str): SFTP server account password.
            sftp_remote_directory (str): Remote SFTP directory.
            report_directory (str): Local report directory.
            sql_query (str): SQL query to execute.
        """

        self.__logger = logging.getLogger(__name__)
        self.__logger.debug('Starting report creation')

        self.email_report = email_report
        self.email_host = email_host
        self.email_port = email_port
        self.email_username = email_username
        self.email_password = email_password
        self.email_sender = email_sender
        self.email_recipients = email_recipients
        self.email_subject = email_subject
        self.email_body = email_body
        self.email_baracuda_tag = email_barracuda_tag
        self.email_use_tls = email_use_tls

        self.sftp_report = sftp_report
        self.sftp_host = sftp_host
        self.sftp_port = sftp_port
        self.sftp_username = sftp_username
        self.sftp_password = sftp_password
        self.sftp_remote_directory = sftp_remote_directory

        self.db_host = db_host
        self.db_port = db_port
        self.db_database = db_database
        self.db_username = db_username
        self.db_password = db_password
        self.db_encoding = db_encoding
        self.db_driver = db_driver
        self.dataframe_result = dataframe_result

        self.__sanity_check()

        self.db_connection = DfDatabase(
            host=self.db_host, port=self.db_port, database=self.db_database,
            username=self.db_username,
            password=self.db_password, encoding=self.db_encoding, driver=self.db_driver
        )

        assert sql_query is not None, self.__logger.critical('sql_query is missing!')
        self.query_results = self.db_connection.df_execute(sql_query)

        self.report_directory = report_directory
        self.file_list = []
        self.__sanity_check()

    def __sanity_check(self):
        """Are we crazy?"""

        # assert self.report_type in ('csv', 'excel'), self.__logger.critical("Report type must be 'csv' or 'excel'")
        # assert self.sql_query is not None, self.__logger.critical('sql_query is missing!')
        pass

    #
    # CSV
    #

    def create_csv(self, output_file=None, delimiter=','):
        """Create a new CSV file, overwriting if it exists

        Args:
            output_file (str): File to write.
            delimiter (str): Character to use for delimiting CSV records.
        """

        assert output_file is not None, self.__logger.critical('output_file is missing.')
        output_file = self.report_directory + output_file

        DfCSV(
            output_file=output_file,
            content=self.query_results,
            delimeter=delimiter,
            mode='create',
        )
        self.file_list.append(output_file)
        self.__logger.info('CSV created: ' + output_file)

    def append_csv(self, output_file=None, delimiter=','):
        """Append to an existing CSV file

        Args:
            output_file (str): File to append to.
            delimiter (str): Character to use for delimiting CSV records.
        """

        DfCSV(
            output_file=output_file,
            content=self.query_results,
            delimeter=delimiter,
            mode='append'
        )
        self.file_list.append(output_file)
        self.__logger.info('CSV appended: ' + output_file)

    #
    # Excel
    #

    def create_simple_excel_workbook(self, output_file=None, worksheet_name='worksheet'):
        """Create a one-worksheet Excel workbook from a dataframe

        Args:
            output_file (str): Name of Excel file to create.
            worksheet_name (str): Worksheet name.
        """

        assert output_file is not None, self.__logger.critical('output_file is missing.')
        output_file = self.report_directory + output_file
        excel = DfExcel(output_file=output_file)
        excel.create_worksheet(worksheet_name=worksheet_name, content=self.query_results)
        excel.close_workbook()

        self.file_list.append(output_file)
        self.__logger.info('Workbook created: ' + output_file)
        self.__logger.info('Worksheet(s) created: ' + worksheet_name)

    #
    # Email and SFTP
    #

    def send_report(self):
        """Email and SFTP the created report(s) as directed by class attributes."""

        if self.email_report is True:

            Email(recipients=self.email_recipients, host=self.email_host, port=self.email_port,
                  username=self.email_username, password=self.email_password,
                  sender=self.email_sender, subject=self.email_subject, body=self.email_body,
                  use_tls=self.email_use_tls, attachments=self.file_list)

            # Create a formated list of recipeints for logging output
            recipients = ''
            for recipient in self.email_recipients:
                recipients = recipients + recipient + ', '

            recipients = recipients[:-2]

            self.__logger.debug('self.email_recipients: ' + str(self.email_recipients))
            self.__logger.info('Email sent to: ' + recipients)

            # Create a formated list of files for logging output
            files = ''
            for file in self.file_list:
                files = files + os.path.basename(file) + ', '

            files = files[:-2]

            self.__logger.debug('self.file_list: ' + str(self.file_list))
            self.__logger.info('Email attachments: ' + files)

        if self.sftp_report is True:

            sftp = SFTP(host=self.sftp_host, port=self.sftp_port, username=self.sftp_username,
                        password=self.sftp_password, remote_directory=self.sftp_remote_directory)

            # Create a formated list of files for logging output while pushing files to SFTP server
            files = ''
            for file in self.file_list:
                sftp.put_file(file)
                files = file + ','

            files = files[:-1]

            sftp.close()

            self.__logger.info('Files sent to SFTP server: ' + files)

    def __del__(self):
        """Automatically send the report ."""
        self.send_report()
