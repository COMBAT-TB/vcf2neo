"""
Interface to handle VCF files
"""
import glob

import time
import vcf
from db import create_variant_set_nodes, create_call_set_nodes, create_variant_site_nodes, create_call_nodes


class Vcf(object):
    """
    Handling VCF processing.
    """

    def __init__(self, vcf_dir=None):
        self.vcf_dir = vcf_dir

    def process(self):
        print("We have the following VCF files in directory ({}):\n".format(self.vcf_dir))
        for vcf_file in glob.glob(self.vcf_dir + "/*.vcf"):
            print(vcf_file)
            vcf_reader = vcf.Reader(open(vcf_file, 'r'))
            # TODO: Have a standard way of identifying variant_set_names
            vcf_file_name = str(vcf_file).replace(str(self.vcf_dir) + "/", "")
            # TODO: What is the best way to
            if 'XDR' in str(vcf_file):
                self.get_variant_sites(vcf_reader)
                create_variant_set_nodes(set_name='XDR')
                create_call_set_nodes(set_name=vcf_file_name)
            if 'DR' in str(vcf_file):
                self.get_variant_sites(vcf_reader)
                create_variant_set_nodes(set_name='DR')
                create_call_set_nodes(set_name=vcf_file_name)
            if 'susceptable' in str(vcf_file):
                self.get_variant_sites(vcf_reader)
                create_variant_set_nodes(set_name='Susceptable')
                create_call_set_nodes(set_name=vcf_file_name)

    def get_variant_sites(self, vcf_reader=None):
        for record in vcf_reader:
            print("\n")
            print(record)
            self.get_variant_calls(record)
            create_variant_site_nodes(record)
            create_call_nodes(record)

    @staticmethod
    def get_variant_calls(record=None):
        print(record.INFO['ANN'][0].split('|'))
