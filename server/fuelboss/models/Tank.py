
import logging, importlib

from ..config import config
from ..bus import bus
from .Units import Units


_logger = logging.getLogger('Tank')
tanks = []


@bus.on('server/start1')
@bus.on('config/loaded')
def _bus_config_loaded():
    global tanks
    tanks = []
    for i in range(10):
        if config.has_section('tank' + str(i)):
            conf = config['tank' + str(i)]
            type = conf['type'] if 'type' in conf else 'cube'
            className = type[:1].capitalize() + type[1:] + 'Tank'
            try:
                tankModule = importlib.import_module('.' + className, 'fuelboss.models')
                classDef = getattr(tankModule, className)
                tank = classDef(i, conf)
                tanks.append(tank)
            except ImportError:
                _logger.error('Unkown tank type "{}"!'.format(type))

    _logger.info('{} tanks configured'.format(len(tanks)))

class Tank:

    DEFAULT_UNITS = 'l,liters,1,1'
    
    @staticmethod
    def tankForGauge(gauge):
        return next((t for t in tanks if t.gauge == gauge), None)
    
    def __init__(self, id, conf):
        self.id = id
        self.name = conf['name'] if 'name' in conf else 'unknown'
        self.type = conf['type'] if 'type' in conf else 'cube'
        self.gauge = int(conf['gauge']) if 'gauge' in conf else 1
        self.toDepth = conf['toDepth'] if 'toDepth' in conf else 'g'
        self.units = Units(conf['units'] if 'units' in conf else DEFAULT_UNITS)

        for param in [k for k in conf.keys() if k.startswith('param-')]:
            setattr(self, param[6:], float(conf[param]))
    
        self.liters = 0
        self.filled = 0
    
    def __repr__(self):
        return 'Tank[name: {}, type: {}, gauge: {}]'.format(self.name, self.type, self.gauge)
        

    def updateVolume(self, value):
        depth = eval(self.toDepth)
        _logger.debug('tank "{}" depth is {:0.3f}'.format(self.name, depth))
        
        if depth > self.depth:
            _logger.warning('tank "{}" reading is invalid: more than full'.format(self.name))
            depth = self.depth
        elif depth < 0:
            _logger.warning('tank "{}" reading is invalid: less than empty'.format(self.name))
            depth = 0

        self.liters = self.depthToVolume(depth)
        self.filled = self.liters / self.capacity()
        
        _logger.debug('tank "{}": {:0.3f}l ({:0.3f}g), {:0.1f}%'.format(self.name, self.liters, self.liters * 0.264172, self.filled * 100))
        bus.emit('tank/changed', self)
        
    def toDict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'liters': self.liters,
            'filled': self.filled,
        }
        