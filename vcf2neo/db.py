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


def create_variant_site_nodes(record, annotation=None):
    """
     Create VariantSite Nodes
    :return:
    """
    pos = record.POS
    chrom = record.CHROM
    ref_allele = record.REF
    alt_allele = record.ALT

    v_site = VariantSite(chrom=str(chrom), pos=str(pos), ref_allele=str(ref_allele), alt_allele=str(alt_allele),
                         gene=annotation[4])
    graph.create(v_site)
    return v_site


def create_call_set_nodes(set_name):
    """
    Create CallSet Nodes
    :return:
    """
    c_set = CallSet(name=set_name)
    graph.create(c_set)


def create_call_nodes(record, gene=None):
    """
    Create Call Nodes
    :return:
    """
    call = Call(pos=str(record.POS), ref_allele=str(record.REF), alt_allele=str(record.ALT), gene=gene)
    graph.create(call)


def build_relationships():
    """
    Build Relationships
    :return:
    """
    c_sets = CallSet.select(graph)
    v_sets = VariantSet.select(graph)
    for v_set in v_sets:
        for c_set in c_sets:
            if v_set.name in c_set.name:
                c_set.has_calls_in.add(v_set)
                graph.push(c_set)

    v_sites = VariantSite.select(graph)
    for v_site in v_sites:
        call = Call.select(graph).where("_.gene = '{}'".format(v_site.gene)).first()
        if call:
            v_site.has_call.add(call)
            graph.push(v_site)
            call.associated_with.add(v_site)
            graph.push(call)
