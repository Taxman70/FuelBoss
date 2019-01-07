
import os, logging
from flask import Flask, request, send_from_directory, send_file, abort

from .config import config


_logger = logging.getLogger('App')


app = Flask(__name__,
    static_url_path = '',
    static_folder = config.getpath('server', 'contentDir')
)



@app.route('/js/<path:path>')
def send_js(path):
    _logger.debug('Request for /js/{}'.format(path))
    return send_from_directory(config.getpath('server', 'contentDir') + '/js', path)
    
@app.route('/css/<path:path>')
def send_css(path):
    _logger.debug('Request for /css/{}'.format(path))
    return send_from_directory(config.getpath('server', 'contentDir') + '/css', path)
    
@app.route('/fonts/<path:path>')
def send_fonts(path):
    _logger.debug('Request for /fonts/{}'.format(path))
    return send_from_directory(config.getpath('server', 'contentDir') + '/fonts', path)
    
@app.route('/img/<path:path>')
def send_img(path):
    _logger.debug('Request for /img/{}'.format(path))
    return send_from_directory(config.getpath('server', 'contentDir') + '/img', path)
    
@app.route('/media/<path:path>')
def send_media(path):
    _logger.debug('Request for /media/{}'.format(path))
    return send_from_directory(config.getpath('server', 'contentDir') + '/media', path)
    
@app.route('/favicon/<path:path>')
def send_favicon(path):
    _logger.debug('Request for /favicon/{}'.format(path))
    return send_from_directory(config.getpath('server', 'contentDir') + '/favicon', path)

@app.route('/audio/<path:path>')
def send_audio(path):
    _logger.debug('Request for /audio/{}'.format(path))
    return send_from_directory(config.getpath('audio', 'audioDir'), path)

@app.route('/tank/<int:tankId>/rrd/<int:graphId>')
def send_tankRRD(tankId, graphId):
    _logger.debug('Request for /tank/{}/rrd/{}'.format(tankId, graphId))
    from .models.Tank import Tank
    tank = Tank.tankForId(tankId)
    if tank is None:
        abort(404)
    file = tank.rrd.graph(graphId)
    if file is None:
        abort(404)
    if os.path.isfile(file):
        return send_file(file, mimetype = 'image/png')
    abort(500)
    
@app.route('/', defaults = { 'path': ''})
@app.route('/<path:path>')
def index(path):
    _logger.debug('Request for /{}'.format(path))
    return send_from_directory(config.getpath('server', 'contentDir'), 'index.html')


