"""
Interface to handle VCF files
"""
import glob

import vcf
from db import create_variant_set_nodes


class Vcf(object):
    """
    Handling VCF processing.
    """

    def __init__(self, vcf_dir=None):
        self.vcf_dir = vcf_dir

    def inspect(self):
        for vcf_file in glob.glob(self.vcf_dir + "/*.vcf"):
            print(vcf_file)
            set_name = str(vcf_file).replace(str(self.vcf_dir) + "/", "")
            # TODO: What is the best way to
            if 'XDR' in str(vcf_file):
                create_variant_set_nodes(set_name)
                vcf_reader = vcf.Reader(open(vcf_file, 'r'))
                for record in vcf_reader:
                    print("\n")
                    print(record)
                    print("\n")
                    for r in record.INFO['ANN']:
                        print(r.split('|'))
