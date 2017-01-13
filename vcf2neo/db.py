"""
Interface to the Neo4j Database
"""
from combat_tb_model.model import VariantSet

from py2neo import Graph, getenv, watch

graph = Graph(host=getenv("DB", "localhost"), http_port=7476, bolt=True, password=getenv("NEO4J_PASSWORD", ""))
watch("neo4j.bolt")


def create_variant_set_nodes(set_name):
    """
    Create VarianSet Nodes
    :return:
    """
    v_set = VariantSet(name=str(set_name))
    graph.create(v_set)


def create_variant_site_nodes():
    """
     Create VariantSite Nodes
    :return:
    """
    pass


def create_call_set_nodes():
    """
    Create CallSet Nodes
    :return:
    """
    pass


def create_call_nodes():
    """
    Create Call Nodes
    :return:
    """
    pass
