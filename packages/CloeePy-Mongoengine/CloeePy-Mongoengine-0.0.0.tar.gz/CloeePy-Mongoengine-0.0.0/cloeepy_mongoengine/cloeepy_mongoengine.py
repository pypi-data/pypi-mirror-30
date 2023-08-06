import os
import sys
from logging import Logger
import mongoengine

class CloeePyMongoengine(object):
    """
    Class representing the CloeePy Mongoengine plugin
    """
    def __init__(self, config:dict, log:Logger):
        # make a copy of the config so we're not messing with the original values
        info = config.copy()

        # set pluginNamespace
        self._namespace = None
        if "pluginNamespace" in info:
            self._namespace = info["pluginNamespace"]
            del info["pluginNamespace"]
        else:
            self._namespace = "mongoengine"

        # use environment variables for username and password if they exist
        if 'CLOEEPY_MONGOENGINE_USERNAME' in os.environ and 'CLOEEPY_MONGOENGINE_PASSWORD' in os.environ:
            log.info("CloeePy-Mongoengine: Using credentials defined in environment")
            info['username'] = os.environ['CLOEEPY_MONGOENGINE_USERNAME']
            info['password'] = os.environ['CLOEEPY_MONGOENGINE_PASSWORD']

        # HACK: can't pass name as kwarg, so have to save it off, remove it from
        # the dict, and pass as first positional argument
        name = info["name"]
        del info['name']
        self.conn = mongoengine.connect(name, **info)

        # verify connection
        try:
            # The ismaster command is cheap and does not require auth.
            self.conn.admin.command('ismaster')
        except ConnectionFailure:
            msg = "Failed to connect to MongoDB"
            log.error(msg)
            sys.exit(msg)
        else:
            log.info("Established connection to MongoDB")

    def get_namespace(self):
        return self._namespace

    def get_value(self):
        return self.conn
