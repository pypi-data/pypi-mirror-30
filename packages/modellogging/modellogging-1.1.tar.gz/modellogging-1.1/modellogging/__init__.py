"""Logger"""

import errno
import os
import copy
import logging
from logging import getLogger, StreamHandler
from logging.handlers import TimedRotatingFileHandler
from pythonjsonlogger import jsonlogger
import inspect

RESET_SEQ = "\033[0m"
BOLD_SEQ = "\033[1m"

NO_EFFECT = "0"
BOLD = "1"
FAINT = "2"
ITALIC = "3"
UNDERLINE = "4"
SLOW_BLINK = "5"
RAPID_BLINK = "6"
REVERSE = "7"
FRAMED = "51"
ENCIRCLED = "52"

FG_BLACK = "30"
FG_RED = "31"
FG_GREEN = "32"
FG_YELLOW = "33"
FG_BLUE = "34"
FG_PURPLE = "35"
FG_CYAN = "36"
FG_WHITE = "37"

BG_BLACK = "40"
BG_RED = "41"
BG_GREEN = "42"
BG_YELLOW = "43"
BG_BLUE = "44"
BG_PURPLE = "45"
BG_CYAN = "46"
BG_WHITE = "47"

class SimpleFormatter(logging.Formatter):
    """ A simple class to format log output
    """
    def __init__(self, app_name):
        self.app_name = app_name
        self.msg_format = ('%(asctime)s - %(app_name)s:%(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d') #pylint: disable=C0301
        msg = self.msg_format
        logging.Formatter.__init__(self, msg)

    def format(self, record):
        record.app_name = self.app_name
        return logging.Formatter.format(self, record)


class ColorFormatter(logging.Formatter):
    """ A simple class to color log output
    """

    COLORS = {}
    COLORS['WARNING'] = "\033[%sm" % (";".join([BOLD, FG_YELLOW]))
    COLORS['INFO'] = "\033[%sm" % (";".join([NO_EFFECT, FG_GREEN]))
    COLORS['DEBUG'] = "\033[%sm" % (";".join([NO_EFFECT, FG_BLUE]))
    COLORS['CRITICAL'] = "\033[%sm" % (";".join([BOLD, FG_RED]))
    COLORS['ERROR'] = "\033[%sm" % (";".join([NO_EFFECT, FG_RED]))
    COLORS['NAME'] = "\033[%sm" % (";".join(FAINT))

    def __init__(self, app_name):
        self.msg_format = ("[$NAME%(app_name)-10s$RESET][$NAME%(name)-30s$RESET][%(levelname)19s] "
                           "%(message)s "
                           "(%(filename)s:%(lineno)d)")
        self.app_name = app_name
        msg = self.formatter_msg(self.msg_format)
        logging.Formatter.__init__(self, msg)

    def formatter_msg(self, msg):
        """ Formats a console message with fancy colors
        """
        msg = msg.replace("$NAME", self.COLORS['NAME'])
        msg = msg.replace("$RESET", RESET_SEQ)
        return msg

    def format(self, record):
        colored_record = copy.copy(record)
        colored_record.app_name = self.app_name
        levelname = colored_record.levelname
        levelname_color = self.COLORS[levelname] + levelname + RESET_SEQ
        colored_record.levelname = levelname_color
        return logging.Formatter.format(self, colored_record)

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """ The json formatter
    """
    def __init__(self, *args, **kwargs):
        self.app_name = kwargs['app_name']
        super(CustomJsonFormatter, self).__init__(*args)

    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['app_name'] = self.app_name

# pylint: disable=too-many-instance-attributes
class ModelLogging:
    """ The modellogging class
    """
    def __init__(self, settings=None, flask_app=None):
        """ Init the logger

            Args:
                settings (obj): The settings

        """
        # Set up our own logger first
        module_levels = getattr(settings, 'LOGGING_LEVEL_MODULES', {})
        this_level = module_levels.get("ModelLogging", "DEBUG")

        self.app_name = getattr(settings, 'APP_NAME', 'default_app_name')
        self.handlers = getattr(settings, 'LOGGING_HANDLERS', ['console', 'file'])
        self.level_console = getattr(settings, 'LOGGING_LEVEL_CONSOLE', 'DEBUG')
        self.level_default = getattr(settings, 'LOGGING_LEVEL_DEFAULT', 'DEBUG')
        self.level_file = getattr(settings, 'LOGGING_LEVEL_FILE', 'DEBUG')
        self.file_path = getattr(settings, 'LOGGING_FILE_PATH', "./logs/log.txt")
        self.file_rotate_backup_count = getattr(settings, 'LOGGING_FILE_ROTATE_BACKUP_COUNT', 5)
        self.file_rotate_interval = getattr(settings, 'LOGGING_FILE_ROTATE_INTERVAL', 1)
        self.file_rotate_when = getattr(settings, 'LOGGING_FILE_ROTATE_WHEN', "d")
        self.format_console = getattr(settings, 'LOGGING_FORMAT_CONSOLE', 'color')
        self.format_file = getattr(settings, 'LOGGING_FORMAT_FILE', 'json')
        self.json_keys = getattr(settings, 'LOGGING_JSON_KEYS', ['asctime', 'created',
                                                                 'filename', 'funcName',
                                                                 'levelname', 'lineno',
                                                                 'module', 'message',
                                                                 'name', 'pathname'])
        self.level_modules = getattr(settings, 'LOGGING_LEVEL_MODULES', {})
        self.log = logging.getLogger(self.__class__.__name__)
        self.add_named_loggers({"ModelLogging": this_level})
        self.log = logging.getLogger(self.__class__.__name__)
        self.flask_app = flask_app
        self.add_loggers()

    @staticmethod
    def indent():
        return " "*(len(inspect.stack())-4)

    def add_loggers(self):
        """ Add the default, module and app loggers

            Args:
                flask_app (App): A flask app

            Returns:
                App: A flask app
        """
        self.log.debug("%sAdding root logger", self.indent())
        self.add_default_logging()
        self.log.debug("%sAdded root logger", self.indent())
        self.log.debug("%sAdding named loggers", self.indent())
        self.add_named_loggers(self.level_modules)
        self.log.debug("%sAdded named loggers", self.indent())


        #
        # # Set up flask logging
        # if self.flask_app:
        #     log_level = self.settings.LOGGING_LEVELS.get("app.logger",
        #                                                  self.settings.LOGGING_LEVELS['default'])
        #     flask_app = self.setup_flask_logger(flask_app, log_level=log_level)
        #     return flask_app
        return None

    def add_default_logging(self):
        """ Setup the default logger
        """
        logger = getLogger()
        log_level = self.level_default
        _logger = self.setup_logger(logger=logger, log_level=log_level, propagate=True)

    def add_named_loggers(self, modules):
        """ Set up named (module) loggers
        """
        for name, log_level in modules.items():
            _looger = self.setup_logger(logger=getLogger(name), log_level=log_level)

    def setup_logger(self, logger, log_level, propagate=False):
        """ Set up a logger

            Args:
                logger (Logger):  An instance of Logger
                log_level (string): The log level to set
                propagate (bool): Pass logging messages to the handlers of ancestor loggers

            Returns:
                Logger: with handlers and level set

        """
        self.log.debug("%sSetting up logger: %s", self.indent(), logger.name)
        logger.handlers = []
        if 'console' in self.handlers:
            self.log.debug("%sAdding console handler to: %s", self.indent(), logger.name)
            logger.addHandler(self.console_handler())
            self.log.debug("%sAdded console handler to: %s", self.indent(), logger.name)
        if 'file' in self.handlers:
            self.log.debug("%sAdding file handler to: %s", self.indent(), logger.name)
            logger.addHandler(self.file_handler())
            self.log.debug("%sAdded file handler to: %s", self.indent(), logger.name)
        self.log.debug("%sSetting %s log level to: %s", self.indent(), logger.name, log_level)
        logger.setLevel(log_level)
        self.log.debug("%sSet %s log level to: %s", self.indent(), logger.name, log_level)
        logger.propagate = propagate
        return logger

    def console_handler(self):
        """ Set up the console handler
        """
        self.log.debug("%sAdding console handler", self.indent())
        handler = StreamHandler()
        self.log.debug("%sSetting console handler level: %s", self.indent(), self.level_console)
        handler.setLevel(logging.getLevelName(self.level_console))
        self.log.debug("%sSet console handler level: %s",
                       self.indent(), self.level_console)
        self.log.debug("%sAdding formatter to console handler: %s",
                       self.indent(), self.format_console)
        handler = self.add_formatter_to_handler(handler=handler,
                                                log_format=self.format_console)
        self.log.debug("%sAdded formatter to console handler: %s",
                       self.indent(), self.format_console)
        self.log.debug("%sAdded console handler", self.indent())
        return handler

    def file_handler(self):
        """ Set up a file handler
        """
        self.log.debug("%sAdding file handler", self.indent())
        self.log.debug("%sMaking log directory", self.indent())
        self.mkdir_p(os.path.dirname(self.file_path))
        handler = TimedRotatingFileHandler(self.file_path,
                                           when=self.file_rotate_when,
                                           interval=self.file_rotate_interval,
                                           backupCount=self.file_rotate_backup_count)
        self.log.debug("%sSet file handler level: %s",
                       self.indent(), self.level_console)
        handler.setLevel(logging.getLevelName(self.level_file))
        self.log.debug("%sAdded formatter to file handler: %s",
                       self.indent(), self.format_console)
        handler = self.add_formatter_to_handler(handler=handler,
                                                log_format=self.format_file)
        self.log.debug("%sAdded file handler", self.indent())
        return handler

    def add_formatter_to_handler(self, handler, log_format):
        """ Add a formatter to a logger

            Args:
                handler (handler): A log handler
                log_format (str): The name of a format (simple, color, json)

            Returns:
                handler: The log handler with the formatter set

        """
        self.log.debug("%sAdding %s formatter to: %s", self.indent(), log_format, handler)
        if log_format == "color":
            handler.setFormatter(ColorFormatter(app_name=self.app_name))
        elif log_format == "json":
            handler.setFormatter(self.json_formatter(app_name=self.app_name,
                                                     logging_json_keys=self.json_keys))
        elif log_format == "simple":
            handler.setFormatter(SimpleFormatter(app_name=self.app_name))
            self.log.debug("%sAdded %s formatter to: %s", self.indent(), log_format, handler)
        return handler

    # def setup_flask_logger(self, flask_app, log_level, propagate=False):
    #     flask_app.logger.handlers = []
    #     if 'console_color' in self.settings.LOGGING_HANDLERS:
    #         flask_app.logger.addHandler(self.console_handler())
    #     if 'file' in self.settings.LOGGING_HANDLERS:
    #         flask_app.logger.addHandler(self.file_handler())
    #     if 'console_json' in self.settings.LOGGING_HANDLERS:
    #         flask_app.logger.addHandler(self.console_json_handler())
    #     if 'file_json' in self.settings.LOGGING_HANDLERS:
    #         flask_app.logger.addHandler(self.file_json_handler())
    #     flask_app.logger.setLevel(log_level)
    #     flask_app.logger.propagate = propagate
    #     return flask_app

    @staticmethod
    def json_formatter(app_name, logging_json_keys):
        """ Set up a json formatter
        """
        log_format = lambda x: ['%({0:s})'.format(i) for i in x]
        custom_format = ' '.join(log_format(logging_json_keys))
        cjf = CustomJsonFormatter(custom_format, app_name=app_name)
        return cjf

    def mkdir_p(self, path):
        """ Make a directory if it deosn't exists

        Args:
            path (string): The directory to ensure

        """
        try:
            os.makedirs(path)
            self.log.debug("%sMade log directory: %s", self.indent(), path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                self.log.debug("%sLog directory exists: %s", self.indent(), path)
                pass
            else:
                raise
