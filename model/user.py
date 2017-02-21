from vcf import *


class GalaxyUser(GraphObject):
    username = Property()
    email = Property()

    owns = RelatedTo("VariantSet", "OWNS_SET")
