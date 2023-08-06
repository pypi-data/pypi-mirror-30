# cf_database.py
__authors__ = ["tsalazar"]
__version__ = "1.3"

# v1.2 (tsalazar) -- Disabled debug logging in fetch_all().
# v1.3 (tsalazar) -- Added MongoDB support.

import logging
import psycopg2
import psycopg2.extras
import pyodbc
import pymongo


class Database:
    """A wrapper for PostgreSQL and MSSQL connections"""

    def __init__(self, host=None, port=None, database=None, username=None,  password=None, autocommit=True,
                 dictionary_cursor=True, encoding='utf8', driver=None):
        """Initialize an instace of the Database class
        
        Args:
            host (str): Database server hostname or IP.
            port (str): Database server port.
            database (str): Database name.
            username (str): Database server account username.
            password (str): Database server account password.
            autocommit (bool): Use autocommit on changes?
            dictionary_cursor (bool): Return the results as a dictionary?
            encoding (str): Database client encoding ("utf8", "latin1", "usascii")
            driver (str): Database client driver ("postgres", "{MSSQLSERVER}", "FreeTDS", etc.).
        """

        self.__logger = logging.getLogger(__name__)
        self.__logger.debug('Initializing Database class object.')

        # Default Settings
        self.__host = host
        self.__port = port
        self.__database = database
        self.__username = username
        self.__password = password
        self.__autocommit = autocommit
        self.dictionary_cursor = dictionary_cursor
        self.__encoding = encoding
        self.__driver = driver
        self._connection = None  # Used by pandas (DfDatabase)

        self.__sanity_check()

        # Establish a database connection
        self.cursor = self.__connect()

        self.__logger.debug('Database class object initialized.')

    def __sanity_check(self):
        """Are we crazy?"""

        assert self.__host is not None, self.__logger.critical('No database hostname set.')
        assert self.__port is not None, self.__logger.critical('No database port set.')
        assert self.__database is not None, self.__logger.critical('No database name set.')
        assert self.__username is not None, self.__logger.critical('No database username set.')
        assert self.__password is not None, self.__logger.critical('No database password set.')
        assert self.__driver is not None, \
            self.__logger.critical('No database driver set. Use sql_server, freetds, postgres')

        self.__logger.debug('Sanity check passed.')

    def __connect(self):
        """Connect to the database"""

        self.__logger.debug('Establishing connection to the database.')

        if self.__driver == 'postgres':
            return self.__connect_postgresql()

        elif self.__driver == '{MSSQLSERVER}' \
                or self.__driver == '{SQL Native Client} ' \
                or self.__driver == '{SQL Server Native Client 10.0}' \
                or self.__driver == '{SQL Server Native Client 11.0}' \
                or self.__driver == '{ODBC Driver 11 for SQL Server}' \
                or self.__driver == '{ODBC Driver 13 for SQL Server}' \
                or self.__driver == 'FreeTDS' \
                or self.__driver == '{SQL Server}':
            return self.__connect_mssql()

        elif self.__driver == 'mongodb':
            return self.__connect_mongodb()

        else:
            self.__logger.critical('No driver defined!')
            quit(1)

    def __connect_postgresql(self):
        """Connect to a PostgreSQL database"""

        # Try a connection to the database.  If it fails, then log the error and exit
        try:
            self._connection = psycopg2.connect(
                host=self.__host,
                port=self.__port,
                database=self.__database,
                user=self.__username,
                password=self.__password,
                client_encoding=self.__encoding,
            )

            # If autocommit is set to True, then set it on the connection
            if self.__autocommit:
                self._connection.autocommit = True

            # If we want to use a DictCursor, then set it.
            if self.dictionary_cursor:
                return self._connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            else:
                return self._connection.cursor()

        except psycopg2.Error as e:
            self.__logger.critical('PostgreSQL: error {}'.format(e.pgerror))
            exit(1)

        self.__logger.debug('PostgreSQL database connection established.')

    def __connect_mssql(self):
        """Connect to a MSSQL database."""

        # Try a connection to the database.  If it fails, then log the error and exit
        try:
            connection_string = f'DRIVER={self.__driver};SERVER={self.__host};DATABASE={self.__database};' \
                                f'UID={self.__username};PWD={self.__password}'

            self.__logger.debug('connection_string: ' + connection_string)

            self._connection = pyodbc.connect(connection_string)
            return self._connection.cursor()

        except ValueError:
            self.__logger.error('MSSQL connection error.')
            exit(1)

        self.__logger.debug('MSSQL database connection established.')

    def __connect_mongodb(self):
        """Connect to a MongoDB database."""

        # Try a connection to the database.  If it fails, then log the error and exit
        try:
            connection_string = \
                f'mongodb://{self.__username}:{self.__password}@{self.__host}:{self.__port}/{self.__database}'

            self.__logger.debug('connection_string: ' + connection_string)

            self._connection = pymongo.MongoClient(connection_string)
            return self._connection

        except ValueError:
            self.__logger.error('MongoDB connection error.')
            exit(1)

        self.__logger.debug('MSSQL database connection established.')

    def execute(self, sql_query):
        """Execute a SQL query

        Args:
            sql_query (str): SQL query to execute.
        """

        self.__logger.debug('Executing query.')
        assert sql_query is not None, self.__logger.critical('sql_query is missing!')

        self.__logger.debug('sql_query:')
        self.__logger.debug(sql_query)

        self.cursor.execute(sql_query)

    def fetch_all(self):
        """Return all rows of the query results"""

        self.__logger.debug('Fetching all results.')

        results = self.cursor.fetchall()

        # self.__logger.debug('results: ')
        # self.__logger.debug(results)

        return results

    def fetch_one(self):
        """Return one row of the query results"""

        self.__logger.debug('Fetching one result.')

        results = self.cursor.fetchone()

        self.__logger.debug('results:')
        self.__logger.debug(results)

        return results

    def get_header(self):
        """Return the column headers"""

        self.__logger.debug('Getting headers from results.')

        # header = [column[0].replace('_', ' ').title() for column in self.cursor.description]
        header = [column[0] for column in self.cursor.description]

        self.__logger.debug('header:')
        self.__logger.debug(header)

        return header
