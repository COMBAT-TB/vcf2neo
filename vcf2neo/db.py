"""
Interface to the Neo4j Database
"""
from combat_tb_model.model import VariantSet, CallSet, VariantSite, Call

from py2neo import Graph, getenv, watch

graph = Graph(host=getenv("DB", "localhost"), http_port=7575, bolt=True, password=getenv("NEO4J_PASSWORD", ""))
watch("neo4j.bolt")


def create_variant_set_nodes(set_name):
    """
    Create VariantSet Nodes
    :return:
    """
    v_set = VariantSet(name=str(set_name))
    graph.create(v_set)


def create_variant_site_nodes(record):
    """
     Create VariantSite Nodes
    :return:
    """
    pos = record.POS
    chrom = record.CHROM
    ref_allele = record.REF
    alt_allele = record.ALT

    v_site = VariantSite(chrom=str(chrom), pos=str(pos), ref_allele=str(ref_allele), alt_allele=str(alt_allele))
    graph.create(v_site)
    return v_site


def create_call_set_nodes(set_name):
    """
    Create CallSet Nodes
    :return:
    """
    c_set = CallSet(name=set_name)
    graph.create(c_set)


def create_call_nodes(record):
    """
    Create Call Nodes
    :return:
    """
    call = Call(pos=str(record.POS), ref_allele=str(record.REF), alt_allele=str(record.ALT))
    graph.create(call)
