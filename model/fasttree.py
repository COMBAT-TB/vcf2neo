from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom
from vcf import *


class FastTree(GraphObject):
    __primarykey__ = 'name'
    name = Property()
    data = Property()
    history_id = Property()

    has_var = RelatedTo("VariantSet", "HAS_VAR")

    def __init__(self, name, data, history_id):
        self.name = name
        self.data = data
        self.history_id = history_id
