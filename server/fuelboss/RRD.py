
import os, logging, rrdtool, time, re

from .bus import bus
from .config import config
from .RRDGraph import RRDGraph


_logger = logging.getLogger('RRD')
_rrdDir = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'var', 'rrd'))
_graphDir = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'var', 'rrd-graph'))


@bus.on('server/tick')
def _bus_server_tick():
    RRD.cleanGraphCache()

class RRD:

    DEFAULT_RRD = {
        'rrdStep': 60,
        # 1 day of 1 minute samples
        'rrdArchive1': 'AVERAGE:0.5:1:1440',
        # 5 years of daily samples
        'rrdArchive2': 'MIN:0.5:1440:1825'
    }
    
    lastGraphCleanTime = 0
    
    @classmethod
    def cleanGraphCache(cls):
        if (time.time() - cls.lastGraphCleanTime) > config.getfloat('rrd', 'cleanGraphCacheInterval'):
            cls.lastGraphCleanTime = time.time()
            for file in os.listdir(_graphDir):
                fullFile = os.path.join(_graphDir, file)
                if re.match(r".*\.png", file) and os.path.getmtime(fullFile) < time.time() - config.getfloat('rrd', 'maxGraphAge'):
                    _logger.info('Removing old graph file {}'.format(file))
                    os.remove(fullFile)
            
    def __init__(self, tank, conf):
        self.tank = tank
        if 'rrdStep' not in conf:
            conf = DEFAULT_RRD
        self.step = int(conf['rrdStep'])
        self.file = os.path.join(_rrdDir, 'tank{}.rrd'.format(tank.id))
        
        self.archives = []
        for i in range(1, 10):
            key = 'rrdArchive' + str(i)
            if key in conf:
                self.archives.append(conf[key])
            else:
                break
                
        self.graphs = []
        for i in range(1, 10):
            key = 'rrdGraph' + str(i)
            if key in conf:
                self.graphs.append(RRDGraph(*conf[key].split(',')))
            else:
                break
                
    def update(self, value):
        if not os.path.isfile(self.file):
            self.create()
            if not os.path.isfile(self.file):
                return
        rrdtool.update(self.file, 'N:{}'.format(value))
        
    def lastupdate(self):
        if not os.path.isfile(self.file):
            return 0
        data = rrdtool.lastupdate(self.file)
        return data['ds']['volume']
        
    def create(self):
        args = [
            self.file,
            '--start', 'now',
            '--step', str(self.step),
            'DS:volume:GAUGE:{}:0:U'.format(self.step * 2),
        ]
        for archive in self.archives:
            args.append('RRA:{}'.format(archive))
        rrdtool.create(*args)
        
    def graph(self, id):
        if id < 1 or id > len(self.graphs):
            return None
        file = os.path.join(_graphDir, 'tank{}-{}.png'.format(self.tank.id, id))
        if not os.path.isfile(file) or (os.path.getmtime(file) < time.time() - config.getfloat('rrd', 'maxGraphAge')):
            self.generateGraph(file, id)
        return file

    def generateGraph(self, file, id):
        _logger.debug('generating graph {} for tank {}'.format(id, self.tank.name))
        graph = self.graphs[id - 1]
        width = graph.width if graph.width else config.getint('rrd', 'graphWidth')
        height = graph.height if graph.height else config.getint('rrd', 'graphHeight')
        args = [
            file,
            '--title', self.tank.name + ((': ' + graph.title) if graph.title else ''),
            '--end', 'now',
            '--start', 'end-{}days'.format(graph.days),
            '--lower-limit=0',
            '--imgformat', 'PNG',
            '--width={}'.format(width),
            '--height={}'.format(height),
            'DEF:v={}:volume:{}'.format(self.file, graph.func),
            'CDEF:vc=v,{},*'.format(self.tank.units.fromLiters),
            'AREA:vc#4caf50:{}'.format(self.tank.units.plural),
        ]
        rrdtool.graph(*args)
        