
from peewee import *

from ..db import db, FuelBossModel, addModel


class Version(FuelBossModel):
    name = CharField(unique = True)
    version = IntegerField()
    
    class Meta:
        database = db
        only_save_dirty = True

addModel(Version)
