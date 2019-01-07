
import math, logging

from .Tank import Tank


_logger = logging.getLogger('VerticalCylinderTank')


class VerticalCylinderTank(Tank):

    def __init__(self, id, conf):
        super().__init__(id, conf)
        self.length = float(conf['length']) if 'length' in conf else 0
        self.width = float(conf['width']) if 'width' in conf else 0
        self.depth = float(conf['depth']) if 'depth' in conf else 0
        self.cylinderArea = math.pi * (self.width / 2) * (self.length / 2)
        super().__postinit__()

    def __repr__(self):
        return 'VerticalCylinderTank[name: {}, gauge: {}]'.format(self.name, self.gauge)
        
    def capacity(self):
        return self.cylinderArea * self.depth / 1000
        
    def depthToVolume(self, depth):
        return self.cylinderArea * depth / 1000
