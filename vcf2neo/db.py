"""
Interface to the Neo4j Database
"""
import sys
from combat_tb_model.model.vcf import *
from combat_tb_model.model.core import *
from combat_tb_model.model.user import *
from py2neo import Graph, getenv, watch

graph = Graph(host=getenv("DB", "localhost"), http_port=7474,
              bolt=True, password=getenv("NEO4J_PASSWORD", ""))
watch("neo4j.bolt")


def create_variant_set_nodes(set_name, owner, history_id):
    """
    Create VariantSet Nodes
    :return:
    """
    v_set = VariantSet(name=str(set_name), owner=str(
        owner), history_id=history_id)
    graph.create(v_set)


def create_variant_site_nodes(record, annotation=None, set_name=None):
    """
     Create VariantSite Nodes
    :return:
    """
    pos = record.POS
    chrom = record.CHROM
    ref_allele = record.REF
    alt_allele = record.ALT

    v_site = VariantSite(chrom=str(chrom), pos=pos, ref_allele=str(ref_allele),
                         alt_allele=str(alt_allele),
                         gene=annotation[4])
    graph.create(v_site)
    create_call_nodes(record, annotation[4])
    v_set = VariantSet.select(graph).where(
        "_.name = '{}'".format(set_name)).first()
    if v_set:
        v_site.belongs_to_vset.add(v_set)
        graph.push(v_site)
    return v_site


def create_call_set_nodes(set_name, vset):
    """
    Create CallSet Nodes
    :return:
    """
    c_set = CallSet(name=set_name, vset=vset)
    graph.create(c_set)


def create_call_nodes(record, annotation=None):
    """
    Create Call Nodes
    :return:
    """
    call = Call(pos=record.POS, ref_allele=str(record.REF),
                alt_allele=str(record.ALT), gene=annotation[4])
    graph.create(call)


def build_relationships(owner):
    """
    Build Relationships
    :return:
    """
    sys.stderr.write("Building relationships!\n")
    v_sets = VariantSet.select(graph).where("_.owner = '{}'".format(owner))
    if v_sets:
        sys.stderr.write("Building VariantSet relationships!\n")

        # c_sets = CallSet.select(graph)
        # v_sets = VariantSet.select(graph)
        for v_set in v_sets:
            c_sets = CallSet.select(graph).where("_.vset = '{}'".format(v_set.name))
            for c_set in c_sets:
                # Find a better way to handle this.
                if v_set.name == c_set.vset:
                    c_set.has_calls_in.add(v_set)
                    graph.push(c_set)

    sys.stderr.write("Building VariantSite relationships!\n")
    v_sites = VariantSite.select(graph)
    for v_site in v_sites:
        call = Call.select(graph).where(
            "_.pos = {}".format(v_site.pos)).first()
        if call:
            v_site.has_call.add(call)
            graph.push(v_site)
            call.associated_with.add(v_site)
            graph.push(call)
        gene = Gene.select(graph, "gene:" + str(v_site.gene)).first()
        if gene:
            v_site.occurs_in.add(gene)
            graph.push(v_site)
            # feature = Feature.select(graph).where(
            #     "_.uniquename = '{}'".format(gene.uniquename)).first()
            # if feature:
            #     for location in feature.location:
            #         v_site.location.add(location)
            #         graph.push(v_site)
    sys.stderr.write("Done building relationships!")
    return True
