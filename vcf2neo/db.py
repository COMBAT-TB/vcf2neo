"""
Interface to the Neo4j Database
"""
import sys
import uuid
from py2neo import Graph, getenv, watch
from vcf2neo.combat_tb_model.model.core import *
from vcf2neo.combat_tb_model.model.vcfmodel import *
from vcf2neo.combat_tb_model.model.galaxyuser import *

graph = Graph(host=getenv("DB", "192.168.2.211"), http_port=7474,
              bolt=True, password=getenv("NEO4J_PASSWORD", ""))
# watch("neo4j.bolt")


def create_variant_set_nodes(set_name, owner, history_id):
    """
    Create VariantSet Nodes
    :return:
    """
    v_set = VariantSet(name=str(set_name), owner=str(
        owner), history_id=history_id)
    graph.create(v_set)
    return v_set


def create_variant_site_nodes(record, known_sites, annotation=None, v_set=None, c_set=None):
    """
     Create VariantSite Nodes
    :return:
    """
    pos = record.POS
    chrom = record.CHROM
    ref_allele = record.REF
    alt_allele = record.ALT

    if pos in known_sites:
        # we have already seen this variant site in another VCF file
        # data structure known_sites:
        # key: pos (genomic position)
        # value: VariantSite
        v_site = known_sites[pos]
        # known_sites[pos][1].append(call)
    else:
        # we don't know about this variant site yet
        v_site = VariantSite(chrom=str(chrom), pos=pos, ref_allele=str(ref_allele),
                             alt_allele=str(alt_allele), gene=annotation[4],
                             pk=str(v_set.name) + str(pos), impact=annotation[2])
        graph.create(v_site)
        known_sites[pos] = v_site
    gene = Gene.select(graph, "gene:" + str(v_site.gene)).first()
    if gene:
        v_site.occurs_in.add(gene)
        graph.push(v_site)
    call = create_call_nodes(record, v_set, c_set, annotation[4])
    if c_set is not None:
        call.belongs_to_cset.add(c_set)
        graph.push(call)
    v_site.has_call.add(call)
    if v_set:
        v_site.belongs_to_vset.add(v_set)
        graph.push(v_site)
    return known_sites


def create_call_set_nodes(set_name, v_set):
    """
    Create CallSet Nodes
    :return:
    """
    c_set = CallSet(name=set_name)
    c_set.has_calls_in.add(v_set)
    graph.create(c_set)
    return c_set


def create_call_nodes(record, v_set, c_set, annotation=None):
    """
    Create Call Nodes
    :return:
    """
    call = Call(pos=record.POS, ref_allele=str(record.REF),
                alt_allele=str(record.ALT),
                pk=str(v_set.name) + str(c_set.name) + str(record.POS), gene=annotation[4])
    graph.create(call)
    return call
