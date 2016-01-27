from neomodel import (StructuredNode, StringProperty, BooleanProperty, IntegerProperty, RelationshipTo,
                      RelationshipFrom, Relationship)


class Gene(StructuredNode):
    """
    Genes
    """
    print 'Gene Nodes'
    gene_id = StringProperty(Unique_Index=True, index=True, required=True)
    # uniprot_entry = StringProperty(Unique_Index=True, required=True)
    dbxref = StringProperty(Unique_Index=True, index=True)
    ncbi_id = StringProperty(Unique_Index=True)
    ncbi_acc = StringProperty(Unique_Index=True)
    ensembl_id = StringProperty(Unique_Index=True)
    name = StringProperty(index=True)
    locus_tag = StringProperty(index=True)
    gene_synonym = StringProperty(index=True)
    coding = StringProperty()  # Coding (Sub-Feature=CDS) or Non-Coding (Sub-Feature != CDS)
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


class Pseudogene(StructuredNode):
    """
    Transcripts
    """
    print 'Pseudogene Nodes'
    pseudogene_id = StringProperty(Unique_Index=True, index=True, required=True)
    name = StringProperty()
    gene_id = StringProperty(index=True)
    description = StringProperty(index=True)
    biotype = StringProperty()
    start = IntegerProperty()
    end = IntegerProperty()
    strand = IntegerProperty()
    location = StringProperty()
    sequence = StringProperty()


class Transcript(StructuredNode):
    """
    Transcripts
    """
    print 'Transcript Nodes'
    transcript_id = StringProperty(Unique_Index=True, index=True, required=True)
    name = StringProperty()
    gene = StringProperty(index=True)
    note = StringProperty(index=True)
    coding = StringProperty()
    start = IntegerProperty()
    end = IntegerProperty()
    strand = IntegerProperty()
    location = StringProperty()
    sequence = StringProperty()


class CDS(StructuredNode):
    """
    CDS
    """
    print 'CDS Nodes'
    cds_id = StringProperty(Unique_Index=True)
    name = StringProperty(Unique_Index=True, index=True)
    transcript = StringProperty()
    product = StringProperty(index=True)
    protein_id = StringProperty(index=True)


class Exon(StructuredNode):
    """
    Exon
    """
    print 'Exon Nodes'
    exon_id = StringProperty()
    name = StringProperty()
    location = StringProperty()
    transcript = StringProperty(index=True)


class Protein(StructuredNode):
    """
    Proteins
    """
    print 'Protein Nodes'
    protein_id = StringProperty(Unique_Index=True, required=True)
    dbxref = StringProperty(Unique_Index=True, index=True)
    ncbi_id = StringProperty(Unique_Index=True)
    ncbi_acc = StringProperty(Unique_Index=True)
    uniprot_id = StringProperty(Unique_Index=True)
    swissprot_id = StringProperty(Unique_Index=True)
    pdb = StringProperty()
    ensembl_id = StringProperty(Unique_Index=True)
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
