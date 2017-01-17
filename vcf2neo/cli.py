import glob

import click
from docker import Docker
from vcfproc import Vcf
from db import build_relationships
import os


@click.group()
def cli():
    """
    This script parses a VCF file and builds a Neo4j Graph database.
    """
    pass


@cli.command()
@click.argument('vcf_dir', type=click.Path(exists=True, dir_okay=True), required=True)
@click.argument('refdb_dir', type=click.Path(exists=True, dir_okay=True), required=True)
def init(vcf_dir, refdb_dir):
    """
    Copy reference database and load VCF to Neo4j Graph database.
    """
    docker = Docker(refdb_dir=refdb_dir)
    docker.run()
    vcf = Vcf(vcf_dir=vcf_dir)
    vcf.process()
    build_relationships()


if __name__ == '__main__':
    cli()
