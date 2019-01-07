
import math, logging

from .Tank import Tank


_logger = logging.getLogger('VerticalCapsuleTank')


class VerticalCapsuleTank(Tank):

    def __init__(self, id, conf):
        super().__init__(id, conf)
        self.length = float(conf['length']) if 'length' in conf else 0
        self.width = float(conf['width']) if 'width' in conf else 0
        self.depth = float(conf['depth']) if 'depth' in conf else 0
        self.radius = self.width / 2
        self.halfCircleArea = math.pi * math.pow(self.radius, 2) / 2
        super().__postinit__()

    def __repr__(self):
        return 'VerticalCapsuleTank[name: {}, gauge: {}]'.format(self.name, self.gauge)
        
    def capacity(self):
        return ((self.halfCircleArea * 2) + (self.width * (self.depth - self.width))) * self.length / 1000
        
    def depthToVolume(self, depth):
        area = 0
        
        if depth < self.radius:
            _logger.debug('in lower portion of tank')
            h = depth
            segmentArea = (math.pow(self.radius, 2) * math.acos((self.radius - h) / self.radius)) - ((self.radius - h) * math.sqrt((2 * self.radius * h) - math.pow(h, 2)))
            area = segmentArea
            
        else:
            area = area + self.halfCircleArea
            
            if depth < self.depth - self.radius:
                _logger.debug('in middle portion of tank')
                area = area + (self.width * (depth - self.radius))
                
            else:
                _logger.debug('in upper portion of tank')
                area = area + (self.width * (self.depth - self.width))
                
                h = self.depth - depth
                segmentArea = (math.pow(self.radius, 2) * math.acos((self.radius - h) / self.radius)) - ((self.radius - h) * math.sqrt((2 * self.radius * h) - math.pow(h, 2)))
                area = area + self.halfCircleArea - segmentArea
                
        return area * self.length / 1000
    
