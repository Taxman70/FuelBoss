
import logging, importlib

from ..config import config
from ..bus import bus


_logger = logging.getLogger('Switch')
switches = []


@bus.on('server/start1')
@bus.on('config/loaded')
def _bus_config_loaded():
    global switches
    switches = []
    for i in range(10):
        if config.has_section('switch' + str(i)):
            conf = config['switch' + str(i)]
            switch = Switch(i, conf)
            switches.append(switch)

    _logger.info('{} switches configured'.format(len(switches)))

class Switch:

    @staticmethod
    def switchForSwitch(switch):
        return next((s for s in switches if s.switch == switch), None)
    
    @staticmethod
    def switchForId(id):
        return next((s for s in switches if s.id == id), None)
    
    def __init__(self, id, conf):
        self.id = id
        self.name = conf['name'] if 'name' in conf else 'unknown'
        self.switch = int(conf['switch']) if 'switch' in conf else 1
        self.invert = bool(conf['invert']) if 'invert' in conf else False
        self.value = False
        
    def __repr__(self):
        return 'Switch[name: {}, switch: {}]'.format(self.name, self.switch)
        
    def update(self, value):
        value = value == 1
        if self.invert: value = not value
        if self.value == value:
            return
        self.value = value
        
        _logger.debug('switch "{}" changed to {}'.format(self.name, value))
        
        bus.emit('switch/changed', self)
        
    def toDict(self):
        return {
            'id': self.id,
            'name': self.name,
            'value': self.value,
        }
        