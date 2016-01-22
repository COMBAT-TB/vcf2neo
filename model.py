from neomodel import (StructuredNode, StringProperty, BooleanProperty, IntegerProperty, RelationshipTo,
                      RelationshipFrom, Relationship)


class Gene(StructuredNode):
    """
    Genes
    """
    print 'Gene Nodes'
    gene_id = StringProperty(Unique_Index=True, index=True, required=True)
    # uniprot_entry = StringProperty(Unique_Index=True, required=True)
    name = StringProperty(index=True)
    locus_tag = StringProperty(index=True)
    gene_synonym = StringProperty(index=True)
    coding = BooleanProperty()  # Coding (Sub-Feature=CDS) or Non-Coding (Sub-Feature != CDS)
    protein_id = StringProperty(index=True)
    pseudo = StringProperty()
    sub_feature = StringProperty()
    start = IntegerProperty()
    end = IntegerProperty()
    strand = StringProperty()
    location = StringProperty()
    length = IntegerProperty()

    # @property
    # def getLocation(self):
    #   location = '{}...{} ({})'.format(self.start, self.end, self.strand)
    #   return location


class Transcript(StructuredNode):
    """
    Transcripts
    """
    print 'Transcript Nodes'
    transcript_id = StringProperty(Unique_Index=True, index=True, required=True)  # This will be the name
    start = IntegerProperty()
    end = IntegerProperty()
    strand = IntegerProperty()
    location = StringProperty()
    _type = StringProperty(index=True)  # I am planning to group these types [ncRNA, tRNA, rRNA, transcript]
    product = StringProperty(index=True)
    parent = StringProperty()  # The Parent gene
    gene = StringProperty(index=True)
    note = StringProperty(index=True)
    sequence = StringProperty()


class CDS(StructuredNode):
    """
    CDS
    """
    print 'CDS Nodes'
    cds_id = StringProperty(Unique_Index=True)
    name = StringProperty(Unique_Index=True, index=True)
    gene_id = StringProperty(Unique_Index=True)
    product = StringProperty(index=True)
    protein_id = StringProperty(index=True)


class Exon(StructuredNode):
    """
    Exon
    """
    print 'Exon Nodes'
    exon_id = StringProperty()
    location = StringProperty()
    _type = StringProperty()
    gene_id = StringProperty(index=True)
    parent = StringProperty()
    codons = IntegerProperty()
    product = StringProperty(index=True)
    note = StringProperty()


class Protein(StructuredNode):
    """
    Proteins
    """
    print 'Protein Nodes'
    protein_id = StringProperty(Unique_Index=True, required=True)
    name = StringProperty(index=True)
    sequence = StringProperty()
    length = IntegerProperty()
    transcript = StringProperty(Unique_Index=True, required=True)


class Ortholog(StructuredNode):
    """
    Ortholog
    """
    print 'Ortholog Nodes'
    name = StringProperty(index=True)
    organism = StringProperty()


class GoTerm(StructuredNode):
    """
    GO Terms
    """
    print 'GO Nodes'
    go_id = StringProperty(Unique_Index=True, index=True)
    name = StringProperty(index=True)
    namespace = StringProperty(index=True)


class InterPro(StructuredNode):
    """
    InterPro
    """
    print 'InterPro Nodes'
    interpro_id = StringProperty(Unique_Index=True, index=True)
    name = StringProperty()


class Pfam(StructuredNode):
    """
    Pfam
    """
    print 'Pfam Nodes'
    pfam_id = StringProperty(Unique_Index=True)
    name = StringProperty()


class Domain(StructuredNode):
    print 'Domain Nodes'
    name = StringProperty(index=True)
