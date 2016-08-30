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
    type = Property()
    parent = Property()  # To build belongs_to rel.
    is_analysis = Property()
    is_obsolete = Property()
    timeaccessioned = Property()
    timelastmodfied = Property()

    belongs_to = RelatedTo("Organism", "BELONGS_TO")
    location = RelatedTo("FeatureLoc", "LOCATED_AT")
    related = RelatedTo("Feature", "RELATED_TO")
    published_in = RelatedTo("Publication", "PUBLISHED_IN")
    dbxref = RelatedTo("DbXref", "XREF")


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

    feature = RelatedFrom(Feature, "ON")
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
    __primarykey__ = 'uniquename'

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


class Author(GraphObject):
    __primarykey__ = 'rank'

    editor = Property()
    surname = Property()
    givennames = Property()
    suffix = Property()

    wrote = RelatedTo("Publication", "WROTE")


class CvTerm(GraphObject):
    __primarykey__ = 'name'

    name = Property()
    definition = Property()
    is_obsolete = Property()

    dbxref = RelatedTo("DbXref", "XREF")
    related = RelatedTo("CvTerm", "RELATED_TO")


class DbXref(GraphObject):
    __primarykey__ = 'accession'

    accession = Property()
    version = Property()
    db = Property()
    description = Property()
