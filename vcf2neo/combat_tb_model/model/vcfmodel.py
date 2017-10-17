# from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom
import uuid

from core import *

# class Phenotype(GraphObject):
#     __primarykey__ = 'type'
#     # type {XDR, DR, MDR, SUS}
#     _type = Property()
#     has_var = RelatedFrom("Variant", "HAS_VAR")
# Adapting GA4GH Variant Data Model
# https://ga4gh-schemas.readthedocs.io/en/latest/api/variants.html
# VariantSet = Phenotype
# TODO: Dataset and ReferenceSet?
REF_COL_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'www.internationalgenome.org'))


class VariantSet(GraphObject):
    __primarykey__ = 'col_id'
    name = Property()
    owner = Property()
    history_id = Property()
    col_id = Property()

    has_variant = RelatedFrom("VariantSite", "BELONGS_TO_VSET")
    has_call = RelatedTo("Call", "HAS_CALL")
    forms_tree = RelatedFrom("FastTree", "FROM_VARIANT_SET")
    has_callsets = RelatedFrom("CallSet", "HAS_CALLS_IN")

    def __init__(self, name, owner, history_id=None, col_id=None):
        self.name = name
        self.owner = owner
        self.history_id = history_id
        self.col_id = col_id


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


class Variant(GraphObject):
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
    impact = Property()

    occurs_in = RelatedTo("Gene", "OCCURS_IN")
    location = RelatedTo("FeatureLoc", "LOCATED_AT")

    has_call = RelatedTo("Call", "HAS_CALL")
    belongs_to_vset = RelatedTo("VariantSet", "BELONGS_TO_VSET")

    def __init__(self, chrom, pos, ref_allele, alt_allele, pk, impact, gene=None):
        self.chrom = chrom
        self.pos = pos
        self.ref_allele = ref_allele
        self.alt_allele = alt_allele
        self.gene = gene
        self.pk = pk
        self.impact = impact


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
