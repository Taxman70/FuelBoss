
import os, configparser, logging, time

from .bus import bus


_logger = logging.getLogger('Config')
config = None
_lastConfigCheckTime = 0
_lastConfigModifiedTime = None
_rootDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_defaultConfig = os.path.join(_rootDir, 'etc', 'config-default.ini')
_localConfig = os.path.join(_rootDir, 'etc', 'config.ini')


@bus.on('server/tick')
def _bus_serverTick():
    global _lastConfigCheckTime
    if (time.time() - _lastConfigCheckTime) > config.getfloat('server', 'configCheckInterval'):
        _lastConfigCheckTime = time.time()
        mtime = os.path.getmtime(_defaultConfig)
        if os.path.isfile(_localConfig):
            mtime = max(mtime, os.path.getmtime(_localConfig))
        if mtime > _lastConfigModifiedTime:
            load()

def load():
    global config, _lastConfigModifiedTime
    
    if config is None:
        config = configparser.ConfigParser(
            interpolation = None,
            converters = {
                'path': _resolvePath
            }
        )
        config.optionxform = str    # preserve option case

    _lastConfigModifiedTime = os.path.getmtime(_defaultConfig)
    if os.path.isfile(_localConfig):
        _lastConfigModifiedTime = max(_lastConfigModifiedTime, os.path.getmtime(_localConfig))

    config.clear()
    config.read(_defaultConfig)
    if os.path.isfile(_localConfig):
        config.read(_localConfig)
    _logger.info('Configuration loaded')
    bus.emit('config/loaded')
        
    return config

def _resolvePath(str):
    str = os.path.expanduser(str)
    if os.path.isabs(str):
        return str
    else:
        return os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), str))
