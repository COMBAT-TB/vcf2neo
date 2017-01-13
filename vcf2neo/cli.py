import glob

import click
from docker import Docker
from vcf import Vcf
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

    click.echo(os.getcwd())
    click.echo(vcf_dir)
    click.echo(refdb_dir)
    docker = Docker(refdb_dir=refdb_dir)
    docker.run()
    vcf = Vcf(vcf_dir=vcf_dir)
    vcf.ls()
