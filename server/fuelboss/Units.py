
class Units:

    def __init__(self, conf):
        parts = conf.split(',')
        self.abbreviation = parts[0]
        self.plural = parts[1]
        self.fromLiters = float(parts[2])
        self.precision = int(parts[3])
        
    def toUnits(self, liters):
        return liters * self.fromLiters
        
    def format(self, liters):
        return ('{:0.' + self.precision + 'f}').format(self.toUnits(liters))
        
    def toDict(self):
        return {
            'abbreviation': self.abbreviation,
            'plural': self.plural,
            'fromLiters': self.fromLiters,
            'precision': self.precision,
        }
        