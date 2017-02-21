<<<<<<< HEAD
from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom
from vcf import *
=======
from vcf import *


class GalaxyUser(GraphObject):
    __primarykey__ = 'email'
>>>>>>> f192a35453cbe46d12e519a189a84ef8e46cc05a

    username = Property()
    email = Property()

    owns = RelatedTo("VariantSet", "OWNS_SET")
