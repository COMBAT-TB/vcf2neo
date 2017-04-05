"""
Interface to handle VCF files
"""
from __future__ import print_function
import sys
import getpass
import glob
import time

import vcf
from db import create_variant_set_nodes, create_call_set_nodes, create_variant_site_nodes, graph


class Vcf(object):
    """
    Handling VCF processing.
    """
    OWNER = getpass.getuser()

    def __init__(self, vcf_dir=None, owner=OWNER, history_id=None):
        self.vcf_dir = vcf_dir
        self.owner = owner
        self.history_id = history_id

    def process(self):
        sys.stderr.write(
            "We have the following VCF files in directory ({}):\n".format(self.vcf_dir))
        print("We have the following VCF files in directory ({}):\n".format(self.vcf_dir))
        known_sites = dict()
        vset_name = str(self.vcf_dir).split('/')[-1]
        v_set = create_variant_set_nodes(set_name=vset_name, owner=str(
            self.owner), history_id=str(self.history_id))
        for vcf_file in glob.glob(self.vcf_dir + "/*.vcf"):
            # TODO: Remove the two files from data
            if 'Drug' not in str(vcf_file):
                sys.stderr.write("Processing: {}!\n".format(vcf_file))
                print("Processing: {}!\n".format(vcf_file))
                start = time.time()
                vcf_reader = vcf.Reader(open(vcf_file, 'r'))
                # TODO: Have a standard way of identifying variant_set_names
                vcf_file_name = str(vcf_file).replace(
                    str(self.vcf_dir) + "/", "")
                c_set = create_call_set_nodes(set_name=vcf_file_name, v_set=v_set)
                known_sites = self.get_variant_sites(
                    known_sites, vcf_reader, v_set=v_set, c_set=c_set)
                end = time.time()
                sys.stderr.write("Processed {} in {}!\n".format(
                    vcf_file_name.upper(), end - start))
                print("Processed {} in {}!\n".format(
                    vcf_file_name.upper(), end - start))
                time.sleep(2)

    def get_variant_sites(self, known_sites, vcf_reader=None, v_set=None, c_set=None):
        sites = []
        for record in vcf_reader:
            print(".", end='')
            # print("\n")
            # print(record)
            annotation = self.get_variant_ann(record=record)
            known_sites = create_variant_site_nodes(
                record, known_sites, annotation, v_set, c_set)
        print()
        return known_sites

    @staticmethod
    def get_variant_ann(record=None):
        ann = record.INFO['ANN'][0].split('|')
        # print(ann)
        return ann
