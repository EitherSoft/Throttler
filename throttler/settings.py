import logging.config
import tornado
import os
from tornado.options import define, options


define('port', default=5000, help="run on the given port", type=int)
define("config", default=None, help="tornado config file")
define("debug", default=False, help="debug mode")

tornado.options.parse_command_line()

f = open(os.path.abspath(os.path.dirname(__file__)) + '/calculate_next_request_time.lua')

settings = {
    'debug': options.debug,
    'duration': 300,
    'limit': 10,
    'calculate_next_request_time': f.read()
}

f.close()

# Redis settings
REDIS = {
    'host': '127.0.0.1',
    'port': 6379,
    'selected_db': 0,
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'main_formatter': {
            'format': '%(levelname)s:%(name)s: %(message)s '
            '(%(asctime)s; %(filename)s:%(lineno)d)',
            'datefmt': "%Y-%m-%d %H:%M:%S",
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'main_formatter',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
        }
    }
}

logging.config.dictConfig(LOGGING)

if options.config:
    tornado.options.parse_config_file(options.config)
