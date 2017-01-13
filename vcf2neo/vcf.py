"""
Interface to handle VCF files
"""
import glob


class Vcf(object):
    """
    Handling VCF processing.
    """

    def __init__(self, vcf_dir=None):
        self.vcf_dir = vcf_dir

    def ls(self):
        for f in glob.glob(self.vcf_dir + "/*.vcf"):
            print(f)
