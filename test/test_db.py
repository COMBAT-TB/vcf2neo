"""
Test dbconn module
"""
import os

import pytest
from py2neo import Graph

db = Graph(host=os.environ.get("DATABASE_URL", "localhost"), bolt=True,
           password=os.environ.get("NEO4J_PASSWORD", ""))


def test_db_nodes():
    result = db.node_labels
    assert "Variant" in result
    assert "VariantSet" in result
    assert "Gene" in result
    assert "MRna" in result
    assert "CDS" in result
    assert "Protein" in result


@pytest.mark.parametrize("test_input,expected", [
    ("MATCH (g:Gene) OPTIONAL MATCH ((g)<-[:PART_OF]-(t)) RETURN t.parent",
     type(None)),
    ("MATCH (g:Gene) OPTIONAL MATCH ((g)-[:LOCATED_AT]->(l)) RETURN l.fmax",
     type(None)),
    ("MATCH (g:Gene) OPTIONAL MATCH ((g)-[:ENCODES]->(p)) RETURN p.parent",
     type(None)),
    ("MATCH (g:Gene)<-[:OCCURS_IN]-(v:Variant) where tolower("
     "g.name)='rv0897c' RETURN v.gene", type(None)),
])
def test_db_data(test_input, expected):
    assert isinstance(type(db.evaluate(test_input)), expected) is False
