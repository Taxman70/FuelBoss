
import math, logging

from .Tank import Tank


_logger = logging.getLogger('HorizontalCapsuleTank')


class HorizontalCapsuleTank(Tank):

    def __init__(self, id, conf):
        super().__init__(id, conf)
        self.length = float(conf['length']) if 'length' in conf else 0
        self.width = float(conf['width']) if 'width' in conf else 0
        self.depth = float(conf['depth']) if 'depth' in conf else 0
        self.radius = self.width / 2
        self.halfCircleArea = math.pi * math.pow(self.radius, 2) / 2

    def __repr__(self):
        return 'HorizontalCapsuleTank[name: {}, gauge: {}]'.format(self.name, self.gauge)
        
    def capacity(self):
        return ((math.pi * math.pow(self.depth / 2, 2)) + ((self.width - self.depth) * self.depth)) * self.length / 1000
        
    def depthToVolume(self, depth):
        radius = self.depth / 2
        h = depth
        segmentArea = (math.pow(radius, 2) * math.acos((radius - h) / radius)) - ((radius - h) * math.sqrt((2 * radius * h) - math.pow(h, 2)))
        return (segmentArea + ((self.width - self.depth) * depth)) * self.length / 1000
