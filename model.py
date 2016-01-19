from neomodel import (StructuredNode, StringProperty,
                      IntegerProperty, RelationshipTo, RelationshipFrom, Relationship)


class Gene(StructuredNode):
    """
    Genes
    """
    print 'Gene Nodes'
    gene_id = StringProperty(Unique_Index=True, required=True)
    # uniprot_entry = StringProperty(Unique_Index=True, required=True)
    name = StringProperty()
    locus_tag = StringProperty()
    gene_synonym = StringProperty()
    protein_id = StringProperty()
    start = IntegerProperty()
    end = IntegerProperty()
    strand = StringProperty()
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
    transcript_id = IntegerProperty(Unique_Index=True, required=True) # This will be the name
    start = IntegerProperty()
    end = IntegerProperty()
    strand = IntegerProperty()
    _type = StringProperty() # I am planning to group these types [ncRNA, tRNA, rRNA, transcript]
    product = StringProperty()
    parent = StringProperty()
    gene = StringProperty()
    note = StringProperty()


class Protein(StructuredNode):
    """
    Proteins
    """
    print 'Protein Nodes'
    protein_id = StringProperty(Unique_Index=True, required=True)
    name = StringProperty()
    sequence = StringProperty()
    length = IntegerProperty()
    transcript = StringProperty(Unique_Index=True, required=True)


class Ortholog(StructuredNode):
    """
    Ortholog
    """
    print 'Ortholog Nodes'
    name = StringProperty()
    organism = StringProperty()


class GoTerm(StructuredNode):
    """
    GO Terms
    """
    print 'GO Nodes'
    go_id = StringProperty(Unique_Index=True, required=True)
    name = StringProperty()
    namespace = StringProperty()


class InterPro(StructuredNode):
    """
    InterPro
    """
    print 'InterPro Nodes'
    interpro_id = StringProperty(Unique_Index=True, required=True)
    name = StringProperty()


class Pfam(StructuredNode):
    """
    Pfam
    """
    print 'Pfam Nodes'
    pfam_id = StringProperty(Unique_Index=True, required=True)
    name = StringProperty()


class Domain(StructuredNode):
    print 'Domain Nodes'
    name = StringProperty()
