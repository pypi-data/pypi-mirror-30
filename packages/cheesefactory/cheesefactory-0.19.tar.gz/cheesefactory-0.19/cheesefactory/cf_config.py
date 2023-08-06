# cf_config.py
__authors__ = ["tsalazar"]
__version__ = "0.2"

# 0.2 -- Removed pprint from debug logger.

import logging
import ast
from os import environ


class Config:
    """Grab a configuration file and make it available to the program.

    The file's locations is provided by an environment variable.

    Attributes:
        cfg (dict): A dictionary representation of the configuration settings.
    """

    def __init__(self, config_location_env=None):
        """Initialize an instance of the Config class.

        Config will use the environment variable provided during initialization to find the configuration file. It will
        then open the file and provide access to the configuration variables.

        Args:
            config_location_env (str): Environment variable that provides the full path to the config file.

        Examples:
            config = Config('APP_CONFIG')
        """

        self.__logger = logging.getLogger(__name__)
        self.__logger.debug('Initializing Config class object')

        assert config_location_env is not None, self.__logger.critical('No config_location_env defined.')

        with open(environ.get(config_location_env)) as config_file:
            # read() will return a string.  ast.literal_eval() converts it to a dictionary.
            self.cfg = ast.literal_eval(config_file.read())

        self.__logger.debug('Config type converted to: ' + str(type(self.cfg)))
        self.__logger.debug(self.cfg)
