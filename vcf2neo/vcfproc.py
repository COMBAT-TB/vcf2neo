"""
Interface to handle VCF files
"""
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
        for vcf_file in glob.glob(self.vcf_dir + "/*.vcf"):
            # TODO: Remove the two files from data
            if 'Drug' not in str(vcf_file):
                print(vcf_file)
                sys.stderr.write("Processing: {}!\n".format(vcf_file))
                print("Processing: {}!\n".format(vcf_file))
                start = time.time()
                vcf_reader = vcf.Reader(open(vcf_file, 'r'))
                # TODO: Have a standard way of identifying variant_set_names
                vcf_file_name = str(vcf_file).replace(
                    str(self.vcf_dir) + "/", "")
                vset_name = str(self.vcf_dir).split('/')[-1]
                # TODO: Let's use the file name for now
                create_variant_set_nodes(set_name=vcf_file_name)
                create_call_set_nodes(set_name=vcf_file_name)
                known_sites = self.get_variant_sites(
                    known_sites, vcf_reader, vcf_file_name)
                end = time.time()
                sys.stderr.write("Processed {} in {}!\n".format(
                    vcf_file_name.upper(), end - start))
                print("Processed {} in {}!\n".format(
                    vcf_file_name.upper(), end - start))
                time.sleep(2)
        for pos in known_sites:
            [v_site, calls] = known_sites[pos]
            for call in calls:
                v_site.has_call.add(call)
            graph.push(v_site)

    def get_variant_sites(self, known_sites, vcf_reader=None, vcf_file_name=None):
        sites = []
        for record in vcf_reader:
            print("\n")
            print(record)
            annotation = self.get_variant_ann(record)
            known_sites = create_variant_site_nodes(
                record, known_sites, annotation, vcf_file_name)
        return known_sites

    @staticmethod
    def get_variant_ann(record=None):
        ann = record.INFO['ANN'][0].split('|')
        print(ann)
        return ann
