from base.geodata import GeodataUtils
from base.results import ResultsUtils
from base.arcmap import ArcmapUtils


def geodata(cls):
    setattr(cls, "geodata", GeodataUtils())
    return cls


def arcmap(cls):
    setattr(cls, "arcmap", ArcmapUtils())
    return cls


def results(cls):
    setattr(cls, "results", ResultsUtils())
    return cls
