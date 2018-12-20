"""
Interface to handle VCF files
"""
from __future__ import print_function

import getpass
import glob
import time
import sys

import vcf


class Vcf(object):
    """
    Handling VCF processing.
    """
    try:
        OWNER = getpass.getuser()
    except KeyError:
        OWNER = 'nobody'

    def __init__(self, db, vcf_dir=None, owner=OWNER, history_id=None):
        self.vcf_dir = vcf_dir
        self.owner = owner
        self.history_id = history_id
        self.db = db

    def process(self):
        sys.stdout.write("VCF files in DIR ({}):\n".format(self.vcf_dir))
        known_sites = dict()
        vset_name = str(self.vcf_dir).split('/')[-1]

        v_set = self.db.create_variant_set_nodes(set_name=vset_name,
                                                 owner=str(self.owner),
                                                 history_id=str(
                                                     self.history_id))

        for vcf_file in glob.glob(self.vcf_dir + "/*.vcf"):
            # TODO: Remove the two files from data
            if 'Drug' not in str(vcf_file):
                sys.stdout.write("Processing: {}!\n".format(vcf_file))
                start = time.time()
                vcf_input = open(vcf_file, 'r')
                vcf_reader = vcf.Reader(vcf_input)
                # TODO: Have a standard way of identifying variant_set_names
                vcf_file_name = str(vcf_file).replace(str(self.vcf_dir) + "/",
                                                      "")
                c_set = self.db.create_call_set_nodes(set_name=vcf_file_name,
                                                      v_set=v_set)
                known_sites = self.get_variant_sites(known_sites, vcf_reader,
                                                     v_set=v_set, c_set=c_set)
                end = time.time()
                sys.stdout.write(
                    "Processed {} in {}!\n".format(vcf_file_name.upper(),
                                                   end - start))
                time.sleep(2)

    def get_variant_sites(self, known_sites, vcf_reader=None, v_set=None,
                          c_set=None):
        # sites = []
        for record in vcf_reader:
            print(".", end='')
            annotation = self.get_variant_ann(record=record)
            known_sites = self.db.create_variant_site_nodes(
                record, known_sites, annotation, v_set, c_set)
        return known_sites

    @staticmethod
    def get_variant_ann(record=None):
        ann = record.INFO['ANN'][0].split('|')
        return ann
