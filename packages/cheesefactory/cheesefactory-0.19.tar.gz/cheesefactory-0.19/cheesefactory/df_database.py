# df_database.py
__authors__ = ["tsalazar"]
__version__ = "1.0"

# v1.0 (tsalazar) -- Removed a redundant execute.

import logging
import pandas.io.sql as psql
from .cf_database import Database


class DfDatabase(Database):
    """A wrapper for DFDatabase that outputs a dataframe result."""

    def __init__(self, host=None, port=None, database=None, username=None,  password=None, autocommit=True,
                 dictionary_cursor=True, encoding='utf8', driver=None):
        """Initialize an instace of the DfDatabase class
        
        Args:
            host (str): Database server hostname or IP.
            port (str): Database server port.
            database (str): Database name.
            username (str): Database server account username.
            password (str): Database server account password.
            autocommit (bool): Use autocommit on changes?
            dictionary_cursor (bool): Return the results as a dictionary?
            encoding (str): Database client encoding ("utf8", "latin1")
            driver (str): Database client driver ("postgres", "{MSSQLSERVER}", "FreeTDS", etc.).
        """

        self.__logger = logging.getLogger(__name__)
        self.__logger.debug('Initializing DfDatabase class object.')

        super().__init__(
            host=host, port=port, database=database, username=username, password=password, autocommit=autocommit,
            dictionary_cursor=dictionary_cursor, encoding=encoding, driver=driver
        )

    def df_execute(self, sql_query):
        """Execute a SQL query and return the results in a dataframe

        Args:
            sql_query (str): SQL query to execute.

        Returns:
            pd.Dataframe: SQL query results.
        """

        self.__logger.debug('Executing query to dataframe.')
        assert sql_query is not None, self.__logger.critical('sql_query is missing!')

        self.__logger.debug('sql_query:')
        self.__logger.debug(sql_query)

        return psql.read_sql_query(sql_query, self._connection)
