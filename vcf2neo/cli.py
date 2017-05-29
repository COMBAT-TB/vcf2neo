import sys
import click
import time
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
@click.argument('col_id', type=unicode, required=False)
@click.argument('refdb_dir', type=click.Path(exists=True, dir_okay=True), required=False)
@click.option('-d/-D', default=True, help='Run Neo4j docker container.')
def init(vcf_dir, owner, history_id, col_id, d, refdb_dir=None):
    """
    Copy reference database and load VCF to Neo4j Graph database.
    :param vcf_dir:
    :param refdb_dir:
    :param history_id
    :param col_id
    :param owner
    :param d:
    :return:
    """
    try:
        if d:
            docker = Docker(refdb_dir=refdb_dir)
            docker.run()
        vcf = Vcf(vcf_dir=vcf_dir, owner=owner, history_id=history_id, col_id=col_id)
        sys.stderr.write("About to process vcf files...\n")
        start = time.time()
        vcf.process()
        end = time.time()
        sys.stderr.write("Done loading VCF files to Graph database!\n It took me {} ms.\n".format(end - start))
    except Exception as e:
        raise Exception(e)

if __name__ == '__main__':
    cli()
