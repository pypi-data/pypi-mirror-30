# cf_email.py
__authors__ = ["tsalazar"]
__version__ = "0.1"

import logging
import smtplib
import re
import os.path
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders


class Email:
    """Send an Email with optional attachments."""

    def __init__(self, recipients=None, host='127.0.0.1', port='25', username=None, password=None, 
                 sender='noreply@change.me', subject='No Subject', body='No Body', use_tls=False, attachments=None, 
                 barracuda_tag=None):
        """Initialize an instance of the Email class.

        Args:
            recipients (list[str]): List of Email recipients.
            host (str): Email server hostname or IP.
            port (str): Email server port.
            username (str): Email server account username.
            password (str): Email server account password.
            sender (str): Email sender.
            subject (str): Email subject line.
            body (str): Body of Email.
            use_tls (bool): Connect to the Email server using TLS?
            attachments (list): Email attachments
            barracuda_tag (str): An Email header tag value that forces the Barracuda to encrypt the Email.
        """

        self.__logger = logging.getLogger(__name__)
        self.__logger.debug('Initializing Email class object')

        self.__host = host                   # Email server hostname/IP
        self.__port = port                   # Email server port number
        self.__username = username           # Username for server authentication
        self.__password = password           # Password for server authentication
        self.__sender = sender               # Sender Email address
        self.__recipients = [] if recipients is None else recipients  # Recipient Email addresses
        self.__subject = subject             # Email subject
        self.__body = body                   # Email body
        self.__use_tls = use_tls             # Use TLS?
        self.__attachments = attachments     # Full path and filename of attachment
        self.__barracuda_tag = barracuda_tag  # Meta tag to ensure a Barracuda grabs the message for secure delivery

        self.__sanity_check()
        self.__send()

    def __sanity_check(self):
        """Are we crazy?"""

        # Email recipients
        assert isinstance(self.__recipients, list), self.__logger.critical('email_recipients needs to be a list.')

        if len(self.__recipients) > 0:
            for recipient in self.__recipients:
                assert re.match('[^@]+@[^@]+\.[^@]+', recipient), \
                    self.__logger.critical('Bad Email format found in email_recipients: ' + recipient)
        else:
            self.__logger.critical('No recipients defined!')

        # Hostname
        assert len(self.__host) > 0, self.__logger.critical('No hostname defined!')

        # Port
        try:
            if 1 > int(self.__port) > 65000:
                self.__logger.critical('Port out of range')
                quit(0)
        except ValueError:
            self.__logger.critical('Port needs to be an integer presented as a string.')
            quit(0)

        # Sender Email
        if re.match('[^@]+@[^@]+\.[^@]+', self.__sender) is None:
            self.__logger.warning('No valid sender address set.')

        # Subject
        if self.__subject is None or self.__subject == '':
            self.__logger.warning('subject is empty')

        # Body
        if self.__body is None or self.__body == '':
            self.__logger.warning('body is empty')

        # Attachment
        if self.__attachments is not None:
            for attachment in self.__attachments:
                assert os.path.isfile(attachment), self.__logger.critical('Attachment does not exist!')

        self.__logger.debug('Sanity check passed.')
        # self.logger.debug(__dict__)

    def __send(self):
        """Deliver an Email to the mail server."""

        self.__logger.debug('Sending Email.')

        message = MIMEMultipart()
        message['Subject'] = self.__subject
        message['From'] = self.__sender
        message['To'] = ', '.join(self.__recipients)
        if self.__barracuda_tag is not None:
            message['X-Barracuda-Encrypted'] = self.__barracuda_tag
        # message['X-Barracuda-Encrypted'] = 'ECDHE-RSA-AES256-SHA'
        message.attach(MIMEText(self.__body))

        if self.__attachments is not None:

            self.__logger.debug('Attachments: ' + str(self.__attachments))

            for attachment_item in self.__attachments:
                attachment = MIMEBase('application', 'octet-stream')
                attachment.set_payload(open(attachment_item, 'rb').read())
                encoders.encode_base64(attachment)
                attachment.add_header(
                    'Content-Disposition',
                    'attachment; filename="' + os.path.basename(attachment_item) + '"'
                )
                message.attach(attachment)

        # Establish connection to Email server
        email_server = smtplib.SMTP(self.__host, self.__port)

        # debuglevel 1=messages, 2=timestamped messages
        if self.__logger.level == logging.DEBUG:
            email_server.set_debuglevel(2)

        if self.__use_tls is True:
            email_server.starttls()

        if self.__username is not None and self.__password is not None:
            email_server.login(self.__username, self.__password)

        # Send Email
        try:
            email_server.send_message(message)

        except ValueError as value_error:
            self.__logger.critical(f'Email send_message error {format(value_error)}')
            exit(1)

        # Close connection to Email server
        email_server.quit()

        self.__logger.debug('Email sent')
