#!/usr/bin/env python

import os
import sys
import time

import click

from vcf2neo.db import NeoDb
from vcf2neo.docker import Docker
from vcf2neo.vcfproc import process_vcf_files

HOST = os.environ.get("DATABASE_URL", "localhost")


@click.group()
def cli():
    """
    This script parses a VCF file and builds a Neo4j Graph database.
    """
    pass


try:
    # Python 2
    u_str = unicode
except NameError:
    # Python 3
    u_str = str


@cli.command()
@click.argument('vcf_dir', type=click.Path(exists=True, dir_okay=True),
                required=True)
@click.argument('owner', type=u_str, required=False)
@click.argument('history_id', type=u_str, required=False)
@click.argument('output_dir', type=click.Path(exists=True, dir_okay=True),
                required=False)
# @click.option('--docker/--no-docker', default=False,
#               help='Run Combat-TB-NeoDB container.')
@click.option('--phenotype', '-p', required=True,
              type=click.Choice(['XDR', 'MDR', 'SUSCEPTIBLE', 'UNKNOWN']),
              help='Specify phenotype.')
@click.option('--antibiotic', '-a', multiple=True, required=True,
              help='Specify antibiotic. E.g. Rifampicin')
def load_vcf(vcf_dir, owner, history_id, phenotype=None,
             antibiotic=None, output_dir=None):
    """

    Load SnpEff annotated VCF files to genes and drugs in NeoDb.
    """

    # TODO: Look into docker implemantation
    container, docker = None, None
    if docker:
        if output_dir is None:
            exit("When running in Docker spawn mode we need an output dir.")
        container = Docker(output_dir)
        container.run()
        http_port = container.http_port
        bolt_port = container.bolt_port
    else:
        http_port = 7474
        bolt_port = 7687

    neo_db = NeoDb(host=HOST, password="",
                   use_bolt=True, bolt_port=bolt_port, http_port=http_port)
    start = time.time()
    antibiotic = '\t'.join(antibiotic)
    process_vcf_files(neo_db, vcf_dir=vcf_dir, phenotype=phenotype,
                      antibiotic=antibiotic, owner=owner,
                      history_id=history_id)
    if docker:
        container.stop()
    end = time.time()
    sys.stdout.write(f"\nDone in {end - start} ms.\n")


if __name__ == '__main__':
    cli()
