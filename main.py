import time
from os import getenv

from BCBio import GFF
from py2neo import Graph, watch
from tqdm import tqdm

from model.model import Organism, Feature, FeatureLoc, Gene, PseudoGene, CDS, Transcript, Exon, TRna, NCRna, RRna

graph = Graph(host=getenv("DB", "localhost"), bolt=True,
              password=getenv("NEO4J_PASSWORD", ""))

watch("neo4j.bolt")


def delete_data():
    """
    Delete existing data.
    :return:
    """
    print("Deleting all nodes and relationships in {}".format(graph))
    graph.delete_all()


def create_organism_nodes():
    abbrev = "H37Rv"
    genus = "Mycobacterium"
    species = "M. tuberculosis"
    common_name = "TB"

    organism = Organism(abbreviation=abbrev, genus=genus,
                        species=species, common_name=common_name)
    graph.create(organism)


def create_feature_nodes(feature):
    """
    Create Feature Nodes.
    :param feature:
    :return:
    """
    if feature.qualifiers.get('Parent'):
        parent = feature.qualifiers['Parent'][0]
    else:
        parent = None

    names = get_feature_name(feature)
    name = names.get("Name", names.get("UniqueName"))
    unique_name = names.get("UniqueName", name)

    _feature = Feature()
    _feature.name = name
    _feature.type = feature.type
    _feature.parent = parent
    _feature.uniquename = unique_name
    graph.create(_feature)


def get_feature_name(feature):
    """
    Get Feature Name and UniqueName.
    :param feature:
    :return:
    """
    names = dict()
    if feature.qualifiers.get("Name"):
        names["Name"] = feature.qualifiers["Name"][0]
        names["UniqueName"] = feature.id
    else:
        names["Name"] = names["UniqueName"] = feature.id
    return names


def create_gene_nodes(feature):
    """
    Create Gene Nodes.
    :param feature:
    :return:
    """
    names = get_feature_name(feature)
    name = names.get("Name", names.get("UniqueName"))
    unique_name = names.get("UniqueName", name)

    gene = Gene()
    gene.ontology_id = gene.so_id
    gene.name = name
    gene.uniquename = unique_name
    graph.create(gene)


def create_exon_nodes(feature):
    """
    Create Exon Nodes
    :param feature:
    :return:
    """
    names = get_feature_name(feature)
    name = names.get("Name", names.get("UniqueName"))
    unique_name = names.get("UniqueName", name)

    exon = Exon()
    exon.ontology_id = exon.so_id
    exon.name = name
    exon.uniquename = unique_name
    graph.create(exon)


def create_pseudogene_nodes(feature):
    """
    Create Pseudogene Nodes
    :param feature:
    :return:
    """
    names = get_feature_name(feature)
    name = names.get("Name", names.get("UniqueName"))
    unique_name = names.get("UniqueName", name)

    pseudogene = PseudoGene()
    pseudogene.ontology_id = pseudogene.so_id
    pseudogene.name = name
    pseudogene.uniquename = unique_name
    graph.create(pseudogene)


def create_rna_nodes(feature):
    """
    Create RNA Nodes
    :param feature:
    :return:
    """
    names = get_feature_name(feature)
    name = names.get("Name", names.get("UniqueName"))
    unique_name = names.get("UniqueName", name)

    if feature.type == 'tRNA_gene':
        trna = TRna()
        trna.ontology_id = trna.so_id
        trna.name = name
        trna.uniquename = unique_name
        graph.create(trna)
    if feature.type == 'ncRNA_gene':
        ncrna = NCRna()
        ncrna.ontology_id = ncrna.so_id
        ncrna.name = name
        ncrna.uniquename = unique_name
        graph.create(ncrna)
    if feature.type == 'rRNA_gene':
        rrna = RRna()
        rrna.ontology_id = rrna.so_id
        rrna.name = name
        rrna.uniquename = unique_name
        graph.create(rrna)


def create_transcript_nodes(feature):
    """
    Create Transcipt Nodes
    :param feature:
    :return:
    """
    names = get_feature_name(feature)
    name = names.get("Name", names.get("UniqueName"))
    unique_name = names.get("UniqueName", name)

    transcript = Transcript()
    transcript.ontology_id = transcript.so_id
    transcript.name = name
    transcript.uniquename = unique_name
    graph.create(transcript)


def create_cds_nodes(feature):
    """
    Create CDS Nodes
    :param feature:
    :return:
    """
    names = get_feature_name(feature)
    name = names.get("Name", names.get("UniqueName"))
    unique_name = names.get("UniqueName", name)

    cds = CDS()
    cds.name = name
    cds.uniquename = unique_name
    graph.create(cds)


def create_featureloc_nodes(feature):
    """
    Create FeatureLoc Nodes.
    :param feature:
    :return:
    """
    srcfeature_id = get_feature_name(feature).get("UniqueName")
    feature_loc = FeatureLoc(srcfeature_id=srcfeature_id, fmin=feature.location.start, fmax=feature.location.end,
                             strand=feature.location.strand)
    graph.create(feature_loc)


def build_relationships():
    """
    Build relationships.
    :return:
    """
    print("Building Relationships...")
    features = Feature.select(graph)
    for feature in features:
        # Find organism via __primarykey__ and link with feature via BELONGS_TO
        org = Organism.select(graph, 'Mycobacterium').first()
        feature.belongs_to.add(org)
        graph.push(org)
        # Find feature with a parent attr. matching this features uniquename
        # and link them via RELATED_TO
        _feature = Feature.select(graph).where(
            "_.parent = '{}'".format(feature.uniquename)).first()
        if _feature:
            feature.related_to.add(_feature)
            graph.push(_feature)
        # Building is_a relationships
        gene = Gene.select(graph).where(
            "_.uniquename = '{}'".format(feature.uniquename)).first()
        if gene:
            gene.is_a.add(feature)
            graph.push(gene)
            # Find feature with this gene's uniquename as a parent
            _feature = Feature.select(graph).where(
                "_.parent = '{}'".format(gene.uniquename)).first()
            if _feature:
                # Find transcript: A gene is a parent to it.
                transcript = Transcript.select(
                    graph).where(
                        "_.parent = '{}'".format(_feature.uniquename)).first()
                if transcript:
                    transcript.part_of.add(gene)
                    graph.push(transcript)

        p_gene = PseudoGene.select(graph).where(
            "_.uniquename = '{}'".format(feature.uniquename)).first()
        if p_gene:
            p_gene.is_a.add(feature)
            graph.push(p_gene)
        transcript = Transcript.select(graph).where(
            "_.uniquename = '{}'".format(feature.uniquename)).first()
        if transcript:
            transcript.is_a.add(feature)
            graph.push(transcript)
            # Find feature with this transcript's uniquename as a parent
            _feature = Feature.select(graph).where(
                "_.parent = '{}'".format(transcript.uniquename)).first()
            if _feature:
                # Find exon: A transcript is a parent to it
                exon = Exon.select(graph).where(
                    "_.uniquename = '{}'".format(_feature.uniquename)).first()
                if exon:
                    exon.part_of.add(transcript)
                    graph.push(exon)
                # Find cds: A transcript is a parent to it
                cds = CDS.select(graph).where(
                    "_.uniquename = '{}'".format(_feature.uniquename)).first()
                if cds:
                    cds.part_of.add(transcript)
                    graph.push(cds)

        exon = Exon.select(graph).where(
            "_.uniquename = '{}'".format(feature.uniquename)).first()
        if exon:
            exon.is_a.add(feature)
            graph.push(exon)
        cds = CDS.select(graph).where(
            "_.uniquename = '{}'".format(feature.uniquename)).first()
        if cds:
            cds.is_a.add(feature)
            graph.push(cds)
        # Find feature location with a srcfeature_id attr. matching this features uniquename and link them via
        # LOCATED_AT
        _feature = FeatureLoc.select(graph).where(
            "_.srcfeature_id = '{}'".format(feature.uniquename)).first()
        if _feature:
            feature.location.add(_feature)
        graph.push(feature)


def load_gff_data(gff_file, limit):
    """
    Extract and load features to Neo4j.
    :param gff_file:
    :param limit:
    :return:
    """
    in_file = open(gff_file)
    limit_info = dict(gff_type=limit)
    rna = ["tRNA_gene", "ncRNA_gene", "rRNA_gene"]
    for rec in GFF.parse(gff_file, limit_info=limit_info):
        for feature in tqdm(rec.features):
            create_feature_nodes(feature)
            if feature.type == 'gene':
                create_gene_nodes(feature)
            elif feature.type == 'pseudogene':
                create_pseudogene_nodes(feature)
            elif feature.type == 'exon':
                create_exon_nodes(feature)
            elif feature.type in rna:
                create_rna_nodes(feature)
            elif feature.type == 'transcript':
                create_transcript_nodes(feature)
            elif feature.type == 'CDS':
                create_cds_nodes(feature)
            create_featureloc_nodes(feature)
    in_file.close()


def parse_gff():
    """
    Parse GFF file.
    :return:
    """
    gff_file = "data/MTB_H37rv.gff3"
    create_organism_nodes()
    limits = [["transcript"], ["CDS"], ["gene"], ["pseudogene"], ["exon"],
              ["tRNA_gene", "ncRNA_gene", "rRNA_gene"]]
    for limit in limits:
        print("Loading", limit, "...")
        load_gff_data(gff_file, limit)
    print("Done.")


if __name__ == '__main__':
    time.sleep(10)
    delete_data()
    parse_gff()
    build_relationships()
