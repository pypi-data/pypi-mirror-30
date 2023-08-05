#!/usr/bin/python2
# encoding=utf-8
from dandan import value
import logging
import logging.config


def getLogger(name="dandan", level=logging.DEBUG, filename=None, backup_count=10):
    '''
    Get logger for convenient method

    Args:
        * name (string): logger name, default as 'dandan'
        * level (logger level, optional): level of this logger such as DEBUG, INFO, WARNING, ERROR, FATAL
        * filename (string, optional): filename for timerotedlogger
        * backup_count (int, optional): file backup count, if file count larger than count, then oldest file will be deleted.

    Returns:
        * logger: the logger named name
    '''

    logger = logging.getLogger(name)
    if len(logger.handlers) > 0:
        return logger
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '[%(asctime)s] [%(module)s] [%(lineno)d] [%(levelname)s] | %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
                "level": "DEBUG",
            },
            'null': {
                'class': 'logging.NullHandler',
            },
        },
        'loggers': {
            name: {
                'handlers': ['console', ],
                'level': level,
                'propagate': True,
            },
        },
    }
    config = value.AttrDict(config)
    if filename:
        config.handlers.file = {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'verbose',
            'filename': filename,
            'when': "MIDNIGHT",
            "level": "INFO",
            "backupCount": backup_count,
        }
        config.loggers[name].handlers.append(config.handlers.file)

    logging.config.dictConfig(config)
    return logging.getLogger(name)
