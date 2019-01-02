
from peewee import *

from ..db import db, ProjectModel, addModel


class Version(ProjectModel):
    name = CharField(unique = True)
    version = IntegerField()
    
    class Meta:
        database = db
        only_save_dirty = True

addModel(Version)
