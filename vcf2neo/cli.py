import sys
import click
from db import build_relationships
from docker import Docker
from vcfproc import Vcf


@click.group()
def cli():
    """
    This script parses a VCF file and builds a Neo4j Graph database.
    """
    pass


@cli.command()
@click.argument('vcf_dir', type=click.Path(exists=True, dir_okay=True), required=True)
@click.argument('owner', type=unicode, required=True)
@click.argument('history_id', type=unicode, required=False)
@click.argument('refdb_dir', type=click.Path(exists=True, dir_okay=True), required=False)
# When running vcf2neo with Dockerfile/docker-compose, we don't want
# docker inside docker.
@click.option('-d/-D', default=True, help='Run Neo4j docker container.')
def init(vcf_dir, owner, history_id, d, refdb_dir=None):
    """
    Copy reference database and load VCF to Neo4j Graph database.
    :param vcf_dir:
    :param refdb_dir:
    :param d:
    :return:
    """
    if d:
        docker = Docker(refdb_dir=refdb_dir)
        docker.run()
    vcf = Vcf(vcf_dir=vcf_dir, owner=owner, history_id=history_id)
    sys.stderr.write("About to process vcf files...\n")
    vcf.process()
    sys.stderr.write("About to build relationships...\n")
    build_relationships()
    sys.stderr.write("Done loading VCF file to Graph database!")

if __name__ == '__main__':
    cli()
