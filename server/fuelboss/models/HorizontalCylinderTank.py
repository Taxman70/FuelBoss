
import math, logging

from .Tank import Tank


_logger = logging.getLogger('HorizontalCylinderTank')


class HorizontalCylinderTank(Tank):

    def __init__(self, id, conf):
        super().__init__(id, conf)
        self.length = float(conf['length']) if 'length' in conf else 0
        self.depth = float(conf['depth']) if 'depth' in conf else 0
        self.cylinderArea = math.pi * (self.width / 2) * (self.length / 2)
        super().__postinit__()

    def __repr__(self):
        return 'HorizontalCylinderTank[name: {}, gauge: {}]'.format(self.name, self.gauge)
        
    def capacity(self):
        return (math.pi * math.pow(self.depth / 2, 2)) * self.depth / 1000
        
    def depthToVolume(self, depth):
        radius = self.depth / 2
        h = depth
        segmentArea = (math.pow(radius, 2) * math.acos((radius - h) / radius)) - ((radius - h) * math.sqrt((2 * radius * h) - math.pow(h, 2)))
        return segmentArea * self.length / 1000
