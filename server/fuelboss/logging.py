
import logging, logging.handlers, re

from .config import config
from .bus import bus


_levelPattern = re.compile(r"^level\.(.*)")


@bus.on('config/loaded')
def _bus_config_loaded():
    _setLoggingLevels()
    
def configure():
    root = logging.getLogger()
    root.setLevel(getattr(logging, config.get('logging', 'logLevel')))
    
    handler = logging.handlers.RotatingFileHandler(
        config.getpath('logging', 'logFile'),
        maxBytes = config.getint('logging', 'logSize'),
        backupCount = config.getint('logging', 'logCount'))
        
    handler.setFormatter(logging.Formatter(fmt = config.get('logging', 'logFormat')))
    root.addHandler(handler)

    if config.getboolean('logging', 'console'):
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(fmt = config.get('logging', 'logFormat')))
        root.addHandler(handler)

    _setLoggingLevels()
    
def _setLoggingLevels():
    for (k, v) in config.items('logging'):
        m = _levelPattern.match(k)
        if m:
            logging.getLogger(m.group(1)).setLevel(getattr(logging, v))
