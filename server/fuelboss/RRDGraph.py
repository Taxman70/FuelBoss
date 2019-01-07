
class RRDGraph:

    def __init__(self, days, title, func, width = None, height = None):
        self.days = int(days)
        self.title = title
        self.func = func
        self.width = int(width) if width else None
        self.height = int(height) if height else None
