from vcf import *


class GalaxyUser(GraphObject):
    __primarykey__ = 'email'

    username = Property()
    email = Property()

    owns = RelatedTo("VariantSet", "OWNS_SET")
