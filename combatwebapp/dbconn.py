from py2neo import Graph, getenv

from combat_tb_model.model import *

graph = Graph(host=getenv("DB", "192.168.2.217"), http_port=7474, bolt=True,
              password=getenv("NEO4J_PASSWORD", ""))


def search_gene(uniquename):
    """
    Search Gene Nodes
    :param uniquename:
    :return:
    """
    print('Searching Gene Nodes with Name=', uniquename)
    gene = Gene.select(graph).where(
        "_.name =~'(?i){}.*' OR _.uniquename=~'(?i){}.*'".format(str(uniquename), str(uniquename))).first()

    return gene


def search_feature(name):
    """
    Search Feature Nodes
    :param name:
    :return:
    """
    print('Searching Feature Nodes with Name=', name)
    features = list(
        Feature.select(graph).where("_.name =~'(?i){}.*' OR _.uniquename=~'gene:(?i){}.*'".format(name, name)))
    for feature in features:
        if 'gene:' not in feature.uniquename:
            features.pop()
    return features


def find_interacting_proteins(locus_tag):
    GO_TERM_NODE_COLOUR = '#70ff66'
    PROTEIN_NODE_COLOUR = '#7d82e8'
    INTERPRO_NODE_COLOUR = '#ff6666'

    def go_term_subgraph(protein, terms_seen):
        subgraph = []
        edges = []
        go_terms = protein.cvterm
        for term in go_terms:
            if term.name not in terms_seen:
                term_dict = dict(data=dict(id=term.name,
                                           label='{} ({})'.format(term.definition, term.name),
                                           node_colour=GO_TERM_NODE_COLOUR))
                terms_seen.add(term.name)
                subgraph.append(term_dict)
            edges.append(dict(data=dict(id='{}_{}'.format(protein.uniquename, term.name),
                                        source=protein.uniquename,
                                        target=term.name)))
        subgraph.extend(edges)
        return subgraph

    def interpro_term_subgraph(protein, terms_seen):
        subgraph = []
        edges = []
        interpro_terms = protein.dbxref
        for term in interpro_terms:
            if 'InterPro' in term.db:
                if term.accession not in terms_seen:
                    if term.version is not None:
                        interpro_label = '{} ({})'.format(term.version, term.accession)
                    else:
                        interpro_label = term.accession
                    term_dict = dict(data=dict(id=term.accession,
                                               label=interpro_label,
                                               node_colour=INTERPRO_NODE_COLOUR))
                    terms_seen.add(term.accession)
                    subgraph.append(term_dict)
                edges.append(dict(data=dict(id='{}_{}'.format(protein.uniquename, term.accession),
                                            source=protein.uniquename,
                                            target=term.accession)))
        subgraph.extend(edges)
        return subgraph

    def protein_node(protein, gene_name=None):
        if gene_name is not None:
            protein_label = '{} ({})'.format(gene_name, protein.uniquename)
        else:
            protein_label = protein.uniquename
        return (dict(data=dict(id=protein.uniquename,
                               label=protein_label,
                               node_colour=PROTEIN_NODE_COLOUR)))

    gene = Gene.select(graph, "gene:" + str(locus_tag)).first()
    gene_uname = gene.uniquename
    protein = Polypeptide.select(graph).where(
        "_.parent = '{}'".format(gene_uname[gene_uname.find(':') + 1:])).first()
    gene_name = gene.name
    interactions_graph = []
    styles = [{'selector': 'node',
               'style': {'label': 'data(label)', 'background-color': 'data(node_colour)'}}]
    try:
        tb_interactions = []
        for tb_protein in protein.interacts_with:
            tb_interactions.append(tb_protein)
        interactions_graph.append(protein_node(protein, gene_name=gene_name))
        go_terms_seen = set()
        interpro_terms_seen = set()
        interactions_graph.extend(go_term_subgraph(protein, go_terms_seen))
        interactions_graph.extend(interpro_term_subgraph(protein, interpro_terms_seen))
        edges = []
        for partner_protein in tb_interactions:
            query = 'MATCH(g:Gene)<-[:PART_OF]-()<-[:PART_OF]-(c:CDS)<-[:DERIVES_FROM]-(p:Polypeptide)' \
                    ' WHERE p.uniquename = "{}" RETURN g.name'.format(partner_protein.uniquename)
            result = graph.data(query)
            gene_name = result[0].get('g.name')
            # print("gene_name: ", gene_name, file=sys.stderr)
            edges.append(dict(data=dict(id='{}_{}'.format(protein.uniquename, partner_protein.uniquename),
                                        source=protein.uniquename,
                                        target=partner_protein.uniquename)))
            interactions_graph.append(protein_node(partner_protein, gene_name=gene_name))
            interactions_graph.extend(go_term_subgraph(partner_protein, go_terms_seen))
            interactions_graph.extend(interpro_term_subgraph(partner_protein, interpro_terms_seen))
        interactions_graph.extend(edges)
    # TODO: Exception Handling
    except Exception as e:
        raise e

    return dict(elements=interactions_graph, styles=styles)
