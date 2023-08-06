# cf_sftp.py
__authors__ = ["tsalazar"]
__version__ = "0.4"

# v0.2 (tsalazar) -- Now exits when walktree() fails.  Added docstring to walktree().
# v0.3 (tsalazar) -- Added asserts to walktree().
# v0.4 (tsalazar) -- Added local_directory to get_file()
# v0.5 (tsalazar) -- Changed get_file() from using local_directory to local_path.
# v0.6 (tsalazar) -- Added exists()
# v0.7 (tsalazar) -- Typecast port as an int
# v0.8 (tsalazar) -- Added self.confirm for put_file()

import logging
import pysftp


class SFTP:
    """A class that provides methods for interacting with an SFTP server."""

    def __init__(self, host=None, port='22', username=None, password=None, remote_directory='/', confirm=True):
        """Initialize an instance of the Report class.

        Args:
            host (str): SFTP server hostname or IP.
            port (str): SFTP server port.
            username (str): SFTP server account username.
            password (str): SFTP server account password.
            remote_directory (str): Remote SFTP directory.
            confirm (bool): Confirm that the transfer was successful using stat().
        """

        # Logging

        self.__logger = logging.getLogger(__name__)
        self.__logger.debug('Initializing CSV class object')

        # Initialize instance attributes

        self.sftp_connection = None

        self.host = host
        self.port = int(port)
        self.username = username
        self.password = password
        self.remote_directory = remote_directory
        self.confirm = confirm

        self.__logger.debug('SFTP class object initialized')
        self.__connect()

    def __sanity_check(self):
        """Are we sane?"""

        assert self.host is not None, self.__logger.critical('No host defined.')

        # Port
        try:
            if 1 > int(self.port) > 65000:
                self.__logger.critical('Port out of range')
                quit(0)
        except ValueError:
            self.__logger.critical('Port needs to be an integer presented as a string.')
            quit(0)

        assert self.username is not None, self.__logger.critical('No username defined')
        assert self.password is not None, self.__logger.critical('No password defined')

        self.__logger.debug('Sanity check passed.')
        self.__logger.debug(__dict__)

    def __connect(self):
        """Establish an SFTP connection with a server."""

        # Connect
        self.__logger.debug('Establishing a connection to the SFTP server.')

        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None

        self.sftp_connection = pysftp.Connection(
            self.host,
            port=int(self.port),
            username=self.username,
            password=self.password,
            cnopts=cnopts,
        )

        # Change directory
        self.__logger.debug('SFTP connection established.')

        self.sftp_connection.cd(self.remote_directory)

    def get_file(self, filename, local_path):
        """Download a file from an SFTP server.

        Args:
            filename (str): The name of the file to download.
            local_path (str): The local directory and filename to download the file into.
        """

        self.__logger.debug(f'Attempting to retrieve file: {filename}')

        try:
            self.sftp_connection.get(filename, localpath=local_path)
        except ValueError:
            self.__logger.critical('Problem encountered when retrieving file.')
            exit(1)

    def put_file(self, filename):
        """Upload a file to an SFTP server.

        Args:
            filename (str): The name of the file to download.
        """

        try:
            self.__logger.debug(f'Changing directory: {self.remote_directory}')
            with self.sftp_connection.cd(self.remote_directory):

                # self.logger.info(f'Directory changed to: {self.sftp_connection.cwd}')

                self.__logger.debug(f'Attempting to upload file: {filename}')

                if self.confirm is True:
                    self.sftp_connection.put(filename, confirm=True)
                else:
                    self.sftp_connection.put(filename, confirm=False)

        except ValueError:
            self.__logger.critical('Problem encountered when uploading file.')
            exit(1)

    def walktree(self, remotepath=None, file_callback=None, directory_callback=None, unknown_callback=None,
                 recurse=True):
        """Iterate through a remote directory and run a callback function on each file/directory

        Args:
            remotepath (str): The remote SFTP path to recursively traverse.
            file_callback (object): Function to apply on each file found in the directory.
            directory_callback (object): Function to apply on each directory found in the directory.
            unknown_callback (object): Function to apply on each unknown file found in the directory.
            recurse (bool): Recurse through the directory structure.
        """

        assert remotepath is not None, self.__logger.critical('Missing remote_path!')
        assert file_callback is not None, self.__logger.critical('Missing file_callback!')
        assert directory_callback is not None, self.__logger.critical('Missing directory_callback!')
        assert unknown_callback is not None, self.__logger.critical('Missing unknown_callback!')

        try:
            self.sftp_connection.walktree(remotepath, file_callback, directory_callback, unknown_callback, recurse)

        except ValueError:
            self.__logger.critical('Problem walking tree.')
            exit(1)

    def exists(self, filename):
        """Does a file exist?

        Args:
            filename (str): Name of file to test for.

        Returns:
            (bool)
        """

        return self.sftp_connection.exists(filename)

    def close(self):
        """Close a connection to an SFTP server."""

        try:
            self.sftp_connection.close
        except ValueError:
            print('Problem closing connection.')
            exit(1)

    def __del__(self):
        """Wrap it up."""

        try:
            self.sftp_connection.close
        except ValueError:
            self.__logger.critical('Problem closing connection.')
            exit(1)
