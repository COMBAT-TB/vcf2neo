from os import getenv

from BCBio import GFF
from py2neo import Graph, watch
from tqdm import tqdm

from model.model import Organism, Feature, FeatureLoc

# https://neo4j.com/developer/kb/explanation-of-error-on-session-connection-using-uniform-drivers/
graph = Graph(bolt=True, password=getenv("NEO4J_PASSWORD", ""), encrypted=False)
watch("neo4j.bolt")


def delete_data():
    """
    Delete existing data
    :return:
    """
    print("Deleting all nodes and relationships...")
    graph.delete_all()


def create_organism_nodes():
    abbrev = "H37Rv"
    genus = "Mycobacterium"
    species = "M. tuberculosis"
    common_name = "TB"
    comment = ""

    organism = Organism(abbreviation=abbrev, genus=genus, species=species, common_name=common_name, comment=comment)
    graph.create(organism)


def create_feature_nodes(feature):
    """
    Create Feature Nodes
    :param feature:
    :return:
    """
    exclude = ['gene', 'pseudogene', 'tRNA_gene', 'ncRNA_gene', 'rRNA_gene']
    if feature.type in exclude:
        parent = None
    else:
        parent = feature.qualifiers['Parent'][0][feature.qualifiers['Parent'][0].find(":") + 1:]

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
    Get Feature Name and UniqueName
    :param feature:
    :return:
    """
    names = dict()
    if feature.qualifiers.get("Name"):
        names["Name"] = feature.qualifiers["Name"][0]
        names["UniqueName"] = feature.id[feature.id.find(":") + 1:]
    else:
        names["Name"] = names["UniqueName"] = feature.id[feature.id.find(":") + 1:]
    return names


def create_featureloc_nodes(feature):
    """
    Create FeatureLoc Nodes
    :param feature:
    :return:
    """
    srcfeature_id = get_feature_name(feature).get("UniqueName")
    feature_loc = FeatureLoc(srcfeature_id=srcfeature_id, fmin=feature.location.start, fmax=feature.location.end,
                             strand=feature.location.strand)
    graph.create(feature_loc)


def build_relationships():
    """
    Build relationships
    :return:
    """
    print("Building Relationships...")
    for feature in tqdm(Feature.select(graph)):
        org = Organism.select(graph, 'Mycobacterium').first()
        feature.belongs_to.add(org)
        graph.push(feature)

        _feature = (Feature.select(graph).where("_.parent = '{}'".format(feature.uniquename)).first())
        print _feature
        if _feature and feature.type is not _feature.type:
            feature.related.add(_feature)
            graph.push(feature)


def load_gff_data(gff_file, limit):
    """
    Extract and load features to Neo4j
    :param gff_file:
    :param limit:
    :return:
    """
    in_file = open(gff_file)
    limit_info = dict(gff_type=limit)
    for rec in GFF.parse(gff_file, limit_info=limit_info):
        for feature in tqdm(rec.features):
            create_feature_nodes(feature)
            create_featureloc_nodes(feature)
    in_file.close()


def parse_gff():
    """
    Parse GFF file
    :return:
    """
    gff_file = "data/MTB_H37rv.gff3"
    create_organism_nodes()
    limits = [["gene", "pseudogene", "exon", "tRNA_gene", "ncRNA_gene", "rRNA_gene"], ["transcript"], ["CDS"]]
    for limit in limits:
        print("Loading", limit, "...")
        load_gff_data(gff_file, limit)
    print("Done.")


if __name__ == '__main__':
    delete_data()
    parse_gff()
    build_relationships()
