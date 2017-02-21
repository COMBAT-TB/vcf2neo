from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom
from vcf import *

class User(GraphObject):
    username = Property()
    email = Property()

    owns = RelatedTo("VariantSet", "OWNS_SET")
