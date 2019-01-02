
import functools, logging, re
from flask import request, session
from flask_socketio import SocketIO, emit

from .config import config
from .bus import bus
from .db import db, ModelError


socket = SocketIO()
_logger = logging.getLogger('Socket')


class ValidationError(Exception):
    pass
    
def success(d = None, **kwargs):
    out = {'error': False, **kwargs}
    if type(d) is dict:
        out = {**out, **d}
    return out

def error(msg):
    return {'error': str(msg)}

def socketEmit(*args, **kwargs):
    if not socket.server: return
    socket.emit(*args, **kwargs)

#--------------------------------
# decorators
#

def validate(rules):
    def wrap(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            if isinstance(args[0], dict):
                try:
                    validateParams(args[0], rules)
                    return f(*args, **kwargs)
                except ValidationError as e:
                    return error(e)
            else:
                return f(*args, **kwargs)
        return wrapped
    return wrap

#--------------------------------
# helpers
#

def validateParams(params, rules):
    for param, rule in rules.items():
        if param in params:
            if not isinstance(params[param], rule[0]):
                if params[param] is not None or (len(rule) > 1 and rule[1]):
                    raise ValidationError('{} is not of type {}'.format(param, str(rule[0])))
        else:
            if len(rule) == 1 or rule[1]:
                raise ValidationError('{} is required'.format(param))
    
#================================================================
# socket events
# These events represent the client-side API
#

#-------------------------------
# special
#
    
@socket.on_error_default  # handles all namespaces without an explicit error handler
def _socket_default_error_handler(e):
    _logger.exception(e)
    return error('An internal error has ocurred!')
    
@socket.on('connect')
def _socket_connect():
    _logger.info('Connection opened from {}'.format(request.remote_addr))

@socket.on('disconnect')
def _socket_disconnect():
    _logger.info('Connection closed from {}'.format(request.remote_addr))


    
    
    
#================================================================
# bus events
# These events represents things happening in the server the client needs to know about
#
    
