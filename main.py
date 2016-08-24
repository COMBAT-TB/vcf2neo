from os import getenv
from py2neo import Graph, watch
from model import Organism, Feature, FeatureLoc, Publication, Author, CvTerm, DbXref
# Set up a link to the local graph database.
graph = Graph(password=getenv("NEO4J_PASSWORD", ""))
watch("neo4j.bolt")

if __name__ == '__main__':
    print(graph)
