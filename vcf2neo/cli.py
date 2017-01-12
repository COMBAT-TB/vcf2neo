import click
from docker import Docker


@click.group()
def cli():
    """
    This script parses a VCF file and builds a Neo4j Graph database.
    """
    pass


@cli.command()
def init():
    """
    Copy reference database and load VCF to Neo4j Graph database.
    """
    click.echo("Starting docker...")
    docker = Docker()
    docker.run()
    docker.stop()


