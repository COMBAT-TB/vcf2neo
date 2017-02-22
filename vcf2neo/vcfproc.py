"""
Interface to handle VCF files
"""
import sys
import getpass
import glob
import time

import vcf
from db import create_variant_set_nodes, create_call_set_nodes, create_variant_site_nodes


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
        for vcf_file in glob.glob(self.vcf_dir + "/*.vcf"):
            if 'Drug' not in vcf_file:
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
                create_variant_set_nodes(
                    set_name=vset_name, owner=str(self.owner), history_id=str(self.history_id))
                create_call_set_nodes(set_name=vcf_file_name, vset=vset_name)
                self.get_variant_sites(
                    vcf_reader=vcf_reader, vset_name=vset_name)
                end = time.time()
                sys.stderr.write("Processed {} in {}!\n".format(
                    vcf_file_name.upper(), end - start))
                print("Processed {} in {}!\n".format(
                    vcf_file_name.upper(), end - start))
                time.sleep(2)
        sys.stderr.write("Done Processing!\n")
        print("Done Processing!\n")

    def get_variant_sites(self, vcf_reader=None, vset_name=None):
        for record in vcf_reader:
            print("\n")
            print(record)
            annotation = self.get_variant_ann(record=record)
            create_variant_site_nodes(record, annotation, vset_name)

    @staticmethod
    def get_variant_ann(record=None):
        ann = record.INFO['ANN'][0].split('|')
        print(ann)
        return ann
