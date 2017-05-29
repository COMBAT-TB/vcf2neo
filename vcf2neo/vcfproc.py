"""
Interface to handle VCF files
"""
from __future__ import print_function

import getpass
import glob
import sys
import time
import uuid

import vcf

from db import create_variant_set_nodes, create_call_set_nodes, create_variant_site_nodes


class Vcf(object):
    """
    Handling VCF processing.
    """
    OWNER = getpass.getuser()
    REF_COL_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'www.internationalgenome.org'))

    def __init__(self, vcf_dir=None, owner=OWNER, history_id=None, col_id=REF_COL_ID):
        self.vcf_dir = vcf_dir
        self.owner = owner
        self.history_id = history_id
        self.col_id = col_id

    def process(self):
        try:
            sys.stderr.write(
                "We have the following VCF files in directory ({}):\n".format(self.vcf_dir))
            print("We have the following VCF files in directory ({}):\n".format(self.vcf_dir))
            known_sites = dict()
            vset_name = str(self.vcf_dir).split('/')[-1]
            v_set = create_variant_set_nodes(set_name=vset_name, owner=str(
                self.owner), history_id=str(self.history_id), col_id=str(self.col_id))
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
        except Exception as e:
            print("An Error has occured while processing vcf2neo")
            raise Exception(e)


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
