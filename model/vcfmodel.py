    # from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom
from .core import *
from .galaxyuser import GalaxyUser

# class Phenotype(GraphObject):
#     __primarykey__ = 'type'
#     # type {XDR, DR, MDR, SUS}
#     _type = Property()
#     has_var = RelatedFrom("Variant", "HAS_VAR")
# Adapting GA4GH Variant Data Model
# https://ga4gh-schemas.readthedocs.io/en/latest/api/variants.html
# VariantSet = Phenotype
# TODO: Dataset and ReferenceSet?
class VariantSet(GraphObject):
    __primarykey__ = 'history_id'
    name = Property()
    owner = Property()
    history_id = Property()

    has_variant = RelatedFrom("VariantSite", "BELONGS_TO_VSET")
    has_call = RelatedTo("Call", "HAS_CALL")
    owned_by = RelatedFrom("GalaxyUser", "OWNS_SET")
    forms_tree = RelatedFrom("FastTree", "FROM_VARIANT_SET")
    has_callsets = RelatedFrom("CallSet", "HAS_CALLS_IN")

    def __init__(self, name, owner, history_id=None):
        self.name = name
        self.owner = owner
        self.history_id = history_id


# VariantSite = Variant
class VariantSite(GraphObject):
    # NOTE: relies on FeatureLoc from core.py
    # make __primarykey__ = VariantSet.name+POS
    __primarykey__ = 'pk'

    pos = Property()
    feature_id = Property()
    biotype = Property()
    chrom = Property()
    ref_allele = Property()
    alt_allele = Property()
    quality = Property()
    depth = Property()
    gene = Property()
    gene_id = Property()
    known = Property()
    novel = Property()
    pk = Property()

    occurs_in = RelatedTo("Gene", "OCCURS_IN")
    location = RelatedTo("FeatureLoc", "LOCATED_AT")

    has_call = RelatedTo("Call", "HAS_CALL")
    belongs_to_vset = RelatedTo("VariantSet", "BELONGS_TO_VSET")

    def __init__(self, chrom, pos, ref_allele, alt_allele, pk, gene=None):
        self.chrom = chrom
        self.pos = pos
        self.ref_allele = ref_allele
        self.alt_allele = alt_allele
        self.gene = gene
        self.pk = pk


# CallSet = VCF file
class CallSet(GraphObject):
    __primarykey__ = 'name'
    name = Property()
    vset = Property()
    identifier = Property()

    has_call = RelatedFrom("Call", "BELONGS_TO_CSET")
    has_calls_in = RelatedTo("VariantSet", "HAS_CALLS_IN")

    def __init__(self, name):
        self.name = name
        # self.vset = vset


class Call(GraphObject):
    # make __primarykey__ = CallSet.name+VariantSet.name+pos
    __primarykey__ = 'pk'
    genotype = Property()
    ref_allele = Property()
    alt_allele = Property()
    gene = Property()
    pos = Property()
    pk = Property()
    impact = Property()

    associated_with = RelatedTo("VariantSite", "ASSOC_WITH_VARIANT")
    belongs_to_cset = RelatedTo("CallSet", "BELONGS_TO_CSET")

    def __init__(self, pos, ref_allele, alt_allele, pk, impact, gene=None):
        self.pos = pos
        self.ref_allele = ref_allele
        self.alt_allele = alt_allele
        self.impact = impact
        self.gene = gene
        self.pk = pk

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