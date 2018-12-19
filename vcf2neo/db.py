"""
Interface to the Neo4j Database
"""
import logging
import socket
import sys
import time

from py2neo import Graph, watch
from vcf2neo.combat_tb_model.model.core import Gene
from vcf2neo.combat_tb_model.model.vcfmodel import VariantSet, CallSet, Variant


class GraphDb(object):
    def __init__(self, host, password=None, bolt_port=7687, http_port=7474,
                 use_bolt=False, debug=False):
        if password is None:
            password = ''
        self.debug = debug
        self.graph = self.connect(host, password, bolt_port, http_port,
                                  use_bolt)

    def connect(self, host, password, bolt_port, http_port, use_bolt=False,
                timeout=30):
        """connect - make connection to Neo4j DB

        :param use_bolt:
        :type host: str - hostname or IP of Neo4j database server
        :type password: str - password for Neo4j database server
        :type bolt_port: int - port for Neo4j Bolt protocol
        :type http_port: int - port for Neo4j HTTP protocol
        :type timeout: int - timeout for waiting for the Neo4j connection"""

        connected = False
        # print("testing if we can connect at:", http_port)
        while timeout > 0:
            try:
                socket.create_connection((host, http_port), 1)
            except socket.error:
                timeout -= 1
                time.sleep(1)
            else:
                connected = True
                break
        if not connected:
            raise socket.timeout('timed out trying to connect to {}'.format(
                host, http_port))
        logging.debug(
            "connecting graph to http port: {} bolt_port: {} host: {}".format(
                http_port, bolt_port, host))
        self.bolt_port = bolt_port
        self.http_port = http_port
        sys.stdout.write(
            "connecting to http port: {} bolt_port: {} host: {} bolt: {}\n".
                format(http_port, bolt_port, host, use_bolt))
        time.sleep(5)

        graph = Graph('http://{}:{}/db/data/'.format(host, self.http_port),
                      'bolt://{}:{}/'.format(host, self.bolt_port),
                      bolt=use_bolt, password=password,
                      bolt_port=bolt_port,
                      http_port=http_port)
        if self.debug:
            watch("neo4j.bolt")
        logging.debug("connected", graph)
        return graph

    def create_variant_set_nodes(self, set_name, owner, history_id):
        """
        Create VariantSet Nodes
        :return:
        """
        v_set = VariantSet(name=str(set_name), owner=str(
            owner), history_id=history_id)
        self.graph.create(v_set)
        return v_set

    def create_variant_site_nodes(self, record, known_sites,
                                  annotation, v_set=None, c_set=None):
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
            v_site = Variant(chrom=str(chrom), pos=pos,
                             ref_allele=str(ref_allele),
                             alt_allele=str(alt_allele),
                             gene=annotation[4],
                             pk=str(v_set.name) + str(pos),
                             impact=annotation[2])
            self.graph.create(v_site)
            v_site.belongs_to_cset.add(c_set)
            c_set.has_variant.add(v_site)
            known_sites[pos] = v_site
        gene = Gene.select(self.graph, "gene:" + str(v_site.gene)).first()
        if gene:
            v_site.occurs_in.add(gene)
            self.graph.push(v_site)

        if v_set:
            v_site.belongs_to_vset.add(v_set)
            self.graph.push(v_site)
        return known_sites

    def create_call_set_nodes(self, set_name, v_set):
        """
        Create CallSet Nodes
        :return:
        """
        c_set = CallSet(name=set_name)
        c_set.has_calls_in.add(v_set)
        self.graph.create(c_set)
        return c_set

