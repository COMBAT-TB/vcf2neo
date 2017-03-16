# from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom
from core import *
from galaxyuser import GalaxyUser
from fasttree import FastTree


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
    _uuid = Property()

    has_variant = RelatedTo("VariantSite", "HAS_VARIANT")
    has_call = RelatedTo("Call", "HAS_CALL")
    owned_by = RelatedFrom("GalaxyUser", "OWNS_SET")
    forms_tree = RelatedFrom("FastTree", "FROM_VARIANT_SET")

    def __init__(self, name, owner, _uuid, history_id=None):
        self.name = name
        self.owner = owner
        self.history_id = history_id
        self._uuid = _uuid


# VariantSite = Variant
class VariantSite(GraphObject):
    # NOTE: relies on FeatureLoc from core.py
    # make __primarykey__ = VariantSite.name+POS
    __primarykey__ = '_uuid'

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
    _uuid = Property()

    occurs_in = RelatedTo("Gene", "OCCURS_IN")
    location = RelatedTo("FeatureLoc", "LOCATED_AT")

    has_call = RelatedTo("Call", "HAS_CALL")
    belongs_to_vset = RelatedTo("VariantSet", "BELONGS_TO_VSET")

    def __init__(self, chrom, pos, ref_allele, alt_allele, _uuid, gene=None):
        self.chrom = chrom
        self.pos = pos
        self.ref_allele = ref_allele
        self.alt_allele = alt_allele
        self.gene = gene
        self._uuid = _uuid


# CallSet = VCF file
class CallSet(GraphObject):
    __primarykey__ = '_uuid'
    name = Property()
    vset = Property()
    identifier = Property()
    _uuid = Property()

    has_call = RelatedTo("Call", "HAS_CALL")
    has_calls_in = RelatedTo("VariantSet", "HAS_CALLS_IN")

    def __init__(self, name, vset, _uuid):
        self.name = name
        self.vset = vset
        self._uuid = _uuid


class Call(GraphObject):
    # make __primarykey__ = CallSet.name+VariantSet.name
    __primarykey__ = '_uuid'
    genotype = Property()
    ref_allele = Property()
    alt_allele = Property()
    gene = Property()
    pos = Property()
    _uuid = Property()

    associated_with = RelatedTo("VariantSite", "ASSOC_WITH_VARIANT")
    belongs_to_cset = RelatedTo("CallSet", "BELONGS_TO_SET")

    def __init__(self, pos, ref_allele, alt_allele, _uuid, gene=None):
        self.pos = pos
        self.ref_allele = ref_allele
        self.alt_allele = alt_allele
        self.gene = gene
        self._uuid = _uuid
