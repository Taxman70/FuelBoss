#!/usr/bin/python3

import sys, os, time, argparse, serial, re, datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import project.config

config = project.config.load()

args = None
port = None
loopDelta = 0.25

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
            # call loop* functions
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
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Hardware Simulator')
    parser.add_argument('port', help = 'the serial port to connect to')
    args = parser.parse_args()
    run()
        