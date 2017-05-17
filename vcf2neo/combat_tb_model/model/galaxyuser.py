from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom
#from vcfmodel import VariantSet

from .vcfmodel import *


class GalaxyUser(GraphObject):
    __primarykey__ = 'email'

    user_key = Property()
    username = Property()
    email = Property()

    owns = RelatedTo("VariantSet", "OWNS_SET")

    def __init__(self, user_key=None, email=None, username=None):
        self.user_key = user_key
        self.email = email
        self.username = username
