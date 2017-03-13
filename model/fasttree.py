from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom
from vcfmodel import *


class FastTree(GraphObject):
    __primarykey__ = 'name'
    name = Property()
    data = Property()
    history_id = Property()

    from_variant_set = RelatedTo("VariantSet", "FROM_VARIANT_SET")

    def __init__(self, name, data, history_id):
        self.name = name
        self.data = data
        self.history_id = history_id
