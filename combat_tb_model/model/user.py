
from py2neo.ogm import GraphObject, Property, RelatedTo
from combat_tb_model.model.vcf import VariantSet


class GalaxyUser(GraphObject):
    __primarykey__ = 'email'

    username = Property()
    email = Property()

    owns = RelatedTo("VariantSet", "OWNS_SET")

    def __init__(self, email=None, username=None):
        self.email = email
        self.username = username
