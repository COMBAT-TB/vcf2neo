from os import getenv

from BCBio import GFF
from py2neo import Graph, watch, Node

# https://neo4j.com/developer/kb/explanation-of-error-on-session-connection-using-uniform-drivers/
graph = Graph(password=getenv("NEO4J_PASSWORD", ""), encrypted=False)
watch("neo4j.bolt")


def delete_data():
    """
    Delete existing data
    :return:
    """
    print "Deleting all nodes and relationships..."
    return graph.run("MATCH (n) DETACH DELETE n").dump()


def get_feature_name(feature):
    """
    Get Feature Name
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


def create_feature_nodes(feature):
    """
    Create Feature Nodes
    :param feature:
    :return:
    """
    names = get_feature_name(feature)
    name = names.get("Name", names.get("UniqueName"))
    unique_name = names.get("UniqueName", name)
    _feature = Node("Feature", name=name, type=feature.type, uniquename=unique_name)
    graph.create(_feature)
    print("CREATED:", _feature)


def load_gff_data(gff_file, limit):
    """
    Extract and load features to Neo4j
    :param gff_file:
    :param limit:
    :return:
    """
    in_file = open(gff_file)
    print("About to parse gff_file and load to graph...")
    print("LIMIT:", limit)
    limit_info = dict(gff_type=limit)

    for rec in GFF.parse(gff_file, limit_info=limit_info):
        for feature in rec.features:
            if feature.type == 'gene':
                create_feature_nodes(feature)
            else:
                create_feature_nodes(feature)
    in_file.close()


def parse_gff():
    """
    Parse GFF file
    :return:
    """
    gff_file = "MTB_H37rv.gff3"
    limits = [["gene", "pseudogene", "exon", "tRNA_gene", "ncRNA_gene", "rRNA_gene"], ["transcript"], ["CDS"]]
    for limit in limits:
        print("Loading", limit, " to database...")
        load_gff_data(gff_file, limit)
        print("Done loading", limit, "features to database")


if __name__ == '__main__':
    delete_data()
    parse_gff()
    print(graph)
