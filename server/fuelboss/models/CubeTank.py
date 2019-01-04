
from .Tank import Tank


class CubeTank(Tank):

    def __init__(self, id, conf):
        super().__init__(id, conf)
        self.length = float(conf['length']) if 'length' in conf else 0
        self.width = float(conf['width']) if 'width' in conf else 0
        self.depth = float(conf['depth']) if 'depth' in conf else 0

    def __repr__(self):
        return 'CubeTank[name: {}, gauge: {}]'.format(self.name, self.gauge)
        
    def capacity(self):
        return (self.width * self.length * self.depth) / 1000
        
    def depthToVolume(self, depth):
        return (self.width * self.length * depth) / 1000
    
