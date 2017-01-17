from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom


class Organism(GraphObject):
    __primarykey__ = 'genus'

    abbreviation = Property()
    genus = Property()
    species = Property()
    common_name = Property()
    comment = Property()

    dbxref = RelatedTo("DbXref", "XREF")

    def __init__(self, abbreviation=None, genus=None, species=None, common_name=None, comment=None):
        self.abbreviation = abbreviation
        self.genus = genus
        self.species = species
        self.common_name = common_name
        self.comment = comment


class Feature(GraphObject):
    __primarykey__ = 'uniquename'

    name = Property()
    uniquename = Property()
    residues = Property()
    seqlen = Property()
    md5checksum = Property()
    parent = Property()  # To build related_to rel.
    is_analysis = Property()
    is_obsolete = Property()
    timeaccessioned = Property()
    timelastmodfied = Property()
    ontology_id = Property()

    belongs_to = RelatedTo("Organism", "BELONGS_TO")
    location = RelatedTo("FeatureLoc", "LOCATED_AT")
    related_to = RelatedTo("Feature", "RELATED_TO")
    published_in = RelatedTo("Publication", "PUBLISHED_IN")
    dbxref = RelatedTo("DbXref", "XREF")
    cvterm = RelatedTo("CvTerm", "ASSOC_WITH")


class Gene(Feature):
    so_id = "SO:0000704"

    biotype = Property()
    description = Property()
    is_a = RelatedTo("Feature", "IS_A")


class PseudoGene(Feature):
    so_id = "SO:0000336"

    biotype = Property()
    description = Property()
    is_a = RelatedTo("Feature", "IS_A")


class Transcript(Feature):
    so_id = "SO:0000673"

    biotype = Property()
    is_a = RelatedTo("Feature", "IS_A")
    part_of = RelatedTo("Gene", "PART_OF")


class TRna(Feature):
    so_id = "SO:0000253"


class NCRna(Feature):
    so_id = "SO:0000655"


class RRna(Feature):
    so_id = "SO:0000252"


class Exon(Feature):
    so_id = "SO:0000147"

    is_a = RelatedTo("Feature", "IS_A")
    part_of = RelatedTo("Transcript", "PART_OF")


class CDS(Feature):
    so_id = "SO:0000316"

    is_a = RelatedTo("Feature", "IS_A")
    part_of = RelatedTo("Transcript", "PART_OF")
    polypeptide = RelatedFrom('Polypeptide', "DERIVES_FROM")


class Polypeptide(Feature):
    so_id = "SO:0000104"

    family = Property()
    function = Property()
    pdb_id = Property()
    domain = Property()
    three_d = Property()
    mass = Property()

    derives_from = RelatedTo("CDS", "DERIVES_FROM")
    interacts_with = RelatedTo("Polypeptide", "INTERACTS_WITH")


class FeatureLoc(GraphObject):
    __primarykey__ = 'srcfeature_id'  # used feature.uniquename

    srcfeature_id = Property()
    fmin = Property()
    is_fmin_partial = Property()
    fmax = Property()
    is_fmax_partial = Property()
    strand = Property()
    phase = Property()
    residue_info = Property()
    locgroup = Property()
    rank = Property()

    feature = RelatedFrom("Feature", "ON")
    published_in = RelatedTo("Publication", "PUBLISHED_IN")

    def __init__(self, srcfeature_id, fmin=None, is_fmin_partial=None, fmax=None, is_fmax_partial=None, strand=None,
                 phase=None, residue_info=None, locgroup=None,
                 rank=None):
        self.srcfeature_id = srcfeature_id
        self.fmin = fmin
        self.is_fmin_partial = is_fmin_partial
        self.fmax = fmax
        self.is_fmax_partial = is_fmax_partial
        self.strand = strand
        self.phase = phase
        self.residue_info = residue_info
        self.locgroup = locgroup
        self.rank = rank
        if self.fmin > self.fmax:
            raise ValueError("fmin cannot be greater than fmax: {} > {}.".format(self.fmin, self.fmax))


class Publication(GraphObject):
    __primarykey__ = 'pmid'

    pmid = Property()
    title = Property()
    volumetitle = Property()
    volume = Property()
    series_name = Property()
    issue = Property()
    year = Property()
    pages = Property()
    miniref = Property()
    uniquename = Property()
    is_obsolete = Property()
    publisher = Property()
    pubplace = Property()

    author = RelatedFrom("Author", "WROTE")


class Author(GraphObject):
    __primarykey__ = 'givennames'

    editor = Property()
    surname = Property()
    givennames = Property()
    suffix = Property()
    rank = Property()

    wrote = RelatedTo("Publication", "WROTE")

    def __init__(self, editor=None, surname=None, givennames=None, suffix=None):
        self.editor = editor
        self.surname = surname
        self.givennames = givennames
        self.suffix = suffix


class CvTerm(GraphObject):
    __primarykey__ = 'name'

    name = Property()
    definition = Property()
    is_obsolete = Property()
    namespace = Property()

    dbxref = RelatedTo("DbXref", "XREF")
    is_a = RelatedTo("CvTerm", "IS_A")
    part_of = RelatedTo("CvTerm", "PART_OF")
    feature = RelatedFrom("Feature", "ASSOC_WITH")

    def __init__(self, name=None, definition=None, is_obsolete=None):
        self.name = name
        self.definition = definition
        self.is_obsolete = is_obsolete


class DbXref(GraphObject):
    __primarykey__ = 'accession'

    accession = Property()
    version = Property()
    db = Property()
    description = Property()

    def __init__(self, db, accession, version, description=None):
        self.accession = accession
        self.version = version
        self.db = db
        self.description = description


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
    __primarykey__ = 'name'
    name = Property()

    has_var = RelatedTo("VariantSite", "HAS_VAR")
    has_call = RelatedTo("Call", "HAS_CALL")

    def __init__(self, name):
        self.name = name


# VariantSite = Variant
class VariantSite(GraphObject):
    # __primarykey__ = 'pos'

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

    # occurs_in = RelatedTo("Phenotype", "OCCURS_IN")
    location = RelatedTo("FeatureLoc", "LOCATED_AT")

    has_call = RelatedTo("Call", "HAS_CALL")
    belongs_to_vset = RelatedTo("VariantSet", "BELONGS_TO_VSET")

    def __init__(self, chrom, pos, ref_allele, alt_allele, gene=None):
        self.chrom = chrom
        self.pos = pos
        self.ref_allele = ref_allele
        self.alt_allele = alt_allele
        self.gene = gene


# CallSet = VCF file
class CallSet(GraphObject):
    __primarykey__ = 'name'
    name = Property()

    has_call = RelatedTo("Call", "HAS_CALL")
    has_calls_in = RelatedTo("VariantSet", "HAS_CALLS_IN")

    def __init__(self, name):
        self.name = name


class Call(GraphObject):
    # __primarykey__ = 'genotype'
    genotype = Property()
    ref_allele = Property()
    alt_allele = Property()
    gene = Property()

    associated_with = RelatedTo("VariantSite", "ASSOC_WITH_VARIANT")
    belongs_to_cset = RelatedTo("CallSet", "BELONGS_TO_SET")

    def __init__(self, pos, ref_allele, alt_allele, gene=None):
        self.pos = pos
        self.ref_allele = ref_allele
        self.alt_allele = alt_allele
        self.gene = gene
