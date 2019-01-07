
import logging, re, math

from .config import config
from .bus import bus
from .serial import serial
from .models.Tank import Tank


_gaugeEventPattern = re.compile(r"G(\d+),(\d+)")
_switchEventPattern = re.compile(r"S(\d+),(\d+)")

_logger = logging.getLogger('Core')




@bus.on('serial/event')
def bus_serial_event(ev):
    m = _gaugeEventPattern.match(ev)
    if m:
        _processGaugeReading(int(m.group(1)), int(m.group(2)))
        return
    m = _switchEventPattern.match(ev)
    if m:
        _processSwitchReading(int(m.group(1)), int(m.group(2)))
    
def _processGaugeReading(gauge, value):
    tank = Tank.tankForGauge(gauge)
    if not tank:
        _logger.warning('No tank found for gauge {}. Maybe the gauge should be disabled?'.format(gauge))
        return
    tank.updateVolume(value)
    
def _processSwitchReading(switch, value):
    pass
    
def restart():
    cmd = config.get('core', 'restartCommand').split(' ')
    out = subprocess.run(cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
            universal_newlines = True)
    if out.returncode != 0:
        _logger.error('Error trying to restart: {}'.format(out.stdout))
        
def shutdown():
    cmd = config.get('core', 'shutdownCommand').split(' ')
    out = subprocess.run(cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
            universal_newlines = True)
    if out.returncode != 0:
        _logger.error('Error trying to shutdown: {}'.format(out.stdout))
    
