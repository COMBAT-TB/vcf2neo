import click


@click.group()
def cli():
    """
    This script parses a VCF file and builds a Neo4j Graph database.
    """
    pass


@click.command()
def init():
    """
    Copy reference database and load VCF to Neo4j Graph database.
    """
    click.echo("VCF meets Neo4j!")
