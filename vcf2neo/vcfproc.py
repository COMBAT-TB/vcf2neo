"""
Interface to handle VCF files
"""
from __future__ import print_function

import getpass
import os
import sys

import vcf


def process_vcf_files(db, vcf_dir, owner=None, history_id=None):
    owner = owner if owner else getpass.getuser()
    known_sites = dict()
    if os.path.isdir(vcf_dir):
        for root, dirs, files in os.walk(vcf_dir):
            v_set_name = os.path.basename(os.path.abspath(root))
            sys.stdout.write(
                "Processing file in: {}\n".format(os.path.abspath(root)))
            v_set = db.create_variant_set_nodes(
                set_name=v_set_name, owner=str(owner), history_id=history_id)
            for _file in files:
                _file = '/'.join([os.path.abspath(vcf_dir), _file])
                if check_file(_file) and _file.endswith(".vcf"):
                    # TODO: Remove the two files from data
                    if 'Drug' not in str(_file):
                        sys.stdout.write("Processing: {}!\n".format(_file))
                        with open(_file, 'r') as vcf_input:
                            vcf_reader = vcf.Reader(vcf_input)
                            c_set_name = os.path.basename(
                                os.path.abspath(_file))
                            c_set = db.create_call_set_nodes(
                                set_name=c_set_name, v_set=v_set
                            )
                            known_sites = get_variant_sites(
                                db, known_sites, vcf_reader, v_set=v_set,
                                c_set=c_set)


def get_variant_sites(db, known_sites, vcf_reader, v_set=None,
                      c_set=None):
    # sites = []
    for record in vcf_reader:
        print(".", end='')
        annotation = get_variant_ann(record=record)
        known_sites = db.create_variant_site_nodes(
            record, known_sites, annotation, v_set, c_set)
    return known_sites


def get_variant_ann(record):
    ann = record.INFO['ANN'][0].split('|')
    return ann


def check_file(vcf_file):
    _file = False
    if os.path.exists(vcf_file) and os.stat(vcf_file).st_size > 0:
        _file = True
    return _file
