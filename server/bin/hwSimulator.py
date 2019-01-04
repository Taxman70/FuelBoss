#!/usr/bin/python3

import sys, os, time, argparse, serial, re, datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fuelboss.config

config = fuelboss.config.load()

args = None
port = None
loopDelta = 0.25


class Gauge:

    def __init__(self, gauge, enabled = True, interval = 1, value = 0, minValue = 0, maxValue = 100, dir = 1):
        self.gauge = gauge
        self.enabled = enabled
        self.interval = interval
        self.value = value
        self.minValue = minValue
        self.maxValue = maxValue
        self.dir = dir
        self.lastUpdateTime = 0
        
    def update(self):
        if not self.enabled: return False
        if ((time.time() - self.lastUpdateTime) > self.interval):
            self.lastUpdateTime = time.time()
            self.value = self.value + self.dir
            if self.value > self.maxValue:
                self.value = self.maxValue
                self.dir = -self.dir
            elif self.value < self.minValue:
                self.value = self.minValue
                self.dir = -self.dir
            return True
        else:
            return False
            
gauges = [
#    Gauge(0, minValue = 1450, maxValue = 7930, value = 1450, dir = 100),
    Gauge(1, enabled = False),
    Gauge(2, enabled = False),
    Gauge(3, value = 95),
    Gauge(4, enabled = False),
    Gauge(5, enabled = False),
    Gauge(6, enabled = False),
]

def run():
    global port
    
    port = serial.Serial(args.port, config.getint('serial', 'speed'), timeout = loopDelta)
    print('Serial port {} opened at {}'.format(port.name, port.baudrate))

    buffer = ''
    while True:
        try:
            ch = port.read()
            if ch:
                ch = ch.decode('ascii')
                if ch == '\r' or ch == '\n':
                    if buffer:
                        processCommand(buffer)
                        buffer = ''
                else:
                    buffer = buffer + ch
            loopGauges()
        except KeyboardInterrupt:
            break
        
def processCommand(cmd):
    print('{:%Y-%m-%d %X,%f} <- {}'.format(datetime.datetime.now(), cmd))
    
    m = re.match(r"[A-Z].*\~([0-9A-F]{2})", cmd)
    if m:
        sentCS = int(m.group(1), 16)
        cmd = cmd[:-3]
        cs = 0
        for c in cmd.encode('ascii'):
            cs = cs ^ c
        if cs != sentCS:
            sendError('CHK')
            return

    ch = cmd[0].upper()

    if ch == 'E':
        processEEPROMCommand(cmd[1:])
        
    else:
        sendError('invalid command')
    
def processEEPROMCommand(cmd):
    ch = cmd[0].upper()
    if ch == 'C':   # clear
        sendOK()
    else:
        sendError('invalid EEPROM command')
    

def loopGauges():
    for gauge in gauges:
        if gauge.update():
            sendGaugeEvent(gauge.gauge, gauge.value)
        




# Utilities    
    
def readInt(str):
    neg = False
    i = 0
    if str[0] == '-':
        str = str[1:]
        neg = True
    while str and str[0].isdigit():
        i = (i * 10) + (ord(str[0]) - ord('0'))
        str = str[1:]
    return (-i if neg else i, str)

def readUInt(str):
    i = 0
    while str and str[0].isdigit():
        i = (i * 10) + (ord(str[0]) - ord('0'))
        str = str[1:]
    return (i, str)

def readDelim(str, delim = ','):
    if str and str[0] == delim:
        str = str[1:]
        return (True, str)
    else:
        return (False, str)
    
def send(str):
    port.write((str + '\n').encode('ascii'))
    print('{:%Y-%m-%d %X,%f} -> {}'.format(datetime.datetime.now(), str))
    
def sendError(str):
    send('!' + str)

def sendMessage(str):
    send('#' + str)
    
def sendOK():
    send('OK')
    
def sendEvent(str):
    send('*' + str)
    
def sendGaugeEvent(gauge, value):
    sendEvent('G{},{}'.format(int(gauge), int(value)))
    
def sendSwitchEvent(switch, value):
    sendEvent('S{},{}'.format(int(switch), int(value)))
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Hardware Simulator')
    parser.add_argument('port', help = 'the serial port to connect to')
    args = parser.parse_args()
    run()
        