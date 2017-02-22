from vcf import *


class GalaxyUser(GraphObject):
    __primarykey__ = 'email'

    username = Property()
    email = Property()

    owns = RelatedTo("VariantSet", "OWNS_SET")

    def __init__(self, email=None, username=None):
        self.email = email
        self.username = username
