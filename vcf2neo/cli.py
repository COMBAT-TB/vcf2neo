#!/usr/bin/env python

import os
import sys
import time

import click

from vcf2neo.db import GraphDb
from vcf2neo.docker import Docker
from vcf2neo.vcfproc import process_vcf_files


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
@click.option('-d/-D', default=False, help='Run Neo4j docker container.')
def load_vcf(vcf_dir, owner, history_id, d, output_dir=None):
    """
    Copy reference database and load VCF to Neo4j Graph database.
    :param output_dir:
    :param history_id:
    :param owner:
    :param vcf_dir:
    :param refdb_dir:
    :param d:
    :return:
    """
    docker = None
    if d:
        if output_dir is None:
            exit("When running in Docker spawn mode we need an output dir.")
        docker = Docker(output_dir)
        docker.run()
        http_port = docker.http_port
        bolt_port = docker.bolt_port
    else:
        http_port = 7474
        bolt_port = 7687

    db = GraphDb(host=os.environ.get("DATABASE_URL", "localhost"), password="",
                 use_bolt=True, bolt_port=bolt_port, http_port=http_port)
    sys.stdout.write("Database IP: {}\n".format(db.graph.address.host))

    start = time.time()
    process_vcf_files(db, vcf_dir=vcf_dir, owner=owner, history_id=history_id)
    if d:
        docker.stop()
    end = time.time()
    sys.stdout.write("\nDone in {} ms.\n".format(end - start))


if __name__ == '__main__':
    cli()
