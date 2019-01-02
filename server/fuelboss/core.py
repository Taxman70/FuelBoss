
import logging, re, math

from .config import config
from .bus import bus
from .serial import serial


_mainTankPattern = re.compile(r"M(\d+)")
_auxTankPattern = re.compile(r"A(\d+)")

_logger = logging.getLogger('Core')

mainTankLiters = 0
auxTankLiters = 0



@bus.on('config/loaded')
@bus.on('server/start2')
def bus_test():
    _processMainTankReading(config.getint('test', 'mainTank'))
    

@bus.on('serial/event')
def bus_serial_event(ev):
    m = _mainTankPattern.match(ev)
    if m:
        _processMainTankReading(int(m.group(1)))
        return
    m = _auxTankPattern.match(ev)
    if m:
        _processAuxTankReading(int(m.group(1)))
    
    
def _processMainTankReading(microSecs):
    global mainTankLiters
    
    _logger.debug('main tank microSecs: {}'.format(microSecs))
    cm = (microSecs / 58) - config.getfloat('mainTank', 'deadZone')
    _logger.debug('main tank measure: {:0.3f}cm'.format(cm))
    width = config.getfloat('mainTank', 'width')
    height = config.getfloat('mainTank', 'height')
    depth = config.getfloat('mainTank', 'depth')
    
    radius = width / 2
    
    if cm > height:
        _logger.warning('main tank reading is invalid: less than empty')
        return
        
    if cm < 0:
        _logger.warning('main tank reading is invalid: more than full')
        return
        
    mainTankLiters = 0
    
    if cm < (height - radius):
        _logger.debug('above lower rounded portion of tank')
        halfCircleArea = math.pi * math.pow(radius, 2) / 2
        mainTankLiters = mainTankLiters + (halfCircleArea * depth / 1000)
        
        if cm < radius:
            _logger.debug('above the middle straight portion of tank')
            mainTankLiters = mainTankLiters + ((height - width) * width * depth / 1000)
            
            # add half cicle - circle segment
            h = cm
            segmentArea = (math.pow(radius, 2) * math.acos((radius - h) / radius)) - ((radius - h) * math.sqrt((2 * radius * h) - math.pow(h, 2)))
            mainTankLiters = mainTankLiters + ((halfCircleArea - segmentArea) * depth / 1000)
            
        else:
            _logger.debug('in straight portion of tank')
            mainTankLiters = mainTankLiters + (((height - width) - (cm - radius)) * width * depth / 1000)
            
    else:
        _logger.debug('in rounded lower portion of tank')
    
        h = height - cm
        segmentArea = (math.pow(radius, 2) * math.acos((radius - h) / radius)) - ((radius - h) * math.sqrt((2 * radius * h) - math.pow(h, 2)))
        mainTankLiters = mainTankLiters + (segmentArea * depth / 1000)

    _logger.debug('main tank: {:0.3f}l ({:0.3f}g)'.format(mainTankLiters, mainTankLiters * 0.264172))
    
    
def _processAuxTankReading(analogValue):
    global auxTankGallons
    pass