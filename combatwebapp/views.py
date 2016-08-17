from __future__ import print_function

import json
import os
import sys

from flask import Flask, Response, render_template, request
from neomodel import DoesNotExist, db

from neomodel.cardinality import CardinalityViolation
from combat_tb_model.model import *
from gsea import enrichment_analysis
from bioblend import galaxy
from bioblend.galaxy.datasets import DatasetClient, DatasetTimeoutException
from bioblend.galaxy.client import ConnectionError

app = Flask(__name__)

CACHE_DIR = 'cache'
TMP_DIR = 'tmp'


def mkdir_if_needed(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)


mkdir_if_needed(CACHE_DIR)
mkdir_if_needed(TMP_DIR)


def connect_to_galaxy(galaxy_url='http://demo.sanbi.ac.za/', api_key=None):
    if api_key is None:
        api_key = os.environ.get('GALAXY_API_KEY')
    gi = galaxy.GalaxyInstance(url=galaxy_url, key=api_key)
    return gi


def cypher_search(name):
    print('cypher_search...')
    arr = []
    res = None
    query = "MATCH (n:Gene) where n.name=~'(?i){}.*' OR n.locus_tag=~'(?i){}.*' " \
            "OR n.preffered_name=~'(?i){}.*' OR n.uniprot_entry=~'(?i){}.*' RETURN n " \
            "UNION MATCH (n:Pseudogene) where n.name=~'(?i){}.*' RETURN n " \
            "UNION MATCH (n:Gene)-[:ORTHOLOG]->(o:Ortholog) where o.locus_name=~'(?i){}.*' RETURN n " \
            "".format(name, name, name, name, name, name)
    result, meta = db.cypher_query(query)
    for row in result:
        res = Gene.inflate(row[0])
        arr.append(res)
    print(len(arr))
    print([entry.name for entry in arr])
    return arr


# Search nodes
def search_nodes(name):
    try:
        print('Searching Gene Nodes with Name=', name)
        # node = Gene.nodes.get(name=name)
        node = cypher_search(name)
        if node:
            print(node)
        return node
    except DoesNotExist as e:
        pass
    try:
        print('Searching Pseudogene Nodes with Gene_ID=', name)
        node = Pseudogene.nodes.get(pseudogene_id='gene:' + name)
        return node
    except DoesNotExist as e:
        pass
    try:
        print('Searching Transcript Nodes with Gene=', name)
        node = Transcript.nodes.get(gene=name)
        return node
    except DoesNotExist as e:
        pass
    try:
        print('Searching Protein Node with Parent=', name)
        node = Protein.nodes.get(parent=name)
        return node
    except DoesNotExist as e:
        pass
    return None


def search_node(name):
    nodes = []
    try:
        print('Searching Gene Nodes with Name=', name)
        node = Gene.nodes.get(name=name)
        if node:
            print(node)
            nodes.append(node)
        return nodes
    except DoesNotExist as e:
        try:
            print('Searching Pseudogene Nodes with Name=', name)
            node = Pseudogene.nodes.get(name=name)
            if node:
                print(node)
                nodes.append(node)
            return nodes
        except DoesNotExist as e:
            raise e


def find_interacting_proteins(locus_tag):
    GO_TERM_NODE_COLOUR = '#70ff66'
    PROTEIN_NODE_COLOUR = '#7d82e8'
    INTERPRO_NODE_COLOUR = '#ff6666'

    def go_term_subgraph(protein, terms_seen):
        subgraph = []
        edges = []
        go_terms = protein.associated_with.all()
        for term in go_terms:
            if term.go_id not in terms_seen:
                term_dict = dict(data=dict(id=term.go_id,
                                           label='{} ({})'.format(term.name, term.go_id),
                                           node_colour=GO_TERM_NODE_COLOUR))
                terms_seen.add(term.go_id)
                subgraph.append(term_dict)
            edges.append(dict(data=dict(id='{}_{}'.format(protein.protein_id, term.go_id),
                                        source=protein.protein_id,
                                        target=term.go_id)))
        subgraph.extend(edges)
        return subgraph

    def interpro_term_subgraph(protein, terms_seen):
        subgraph = []
        edges = []
        interpro_terms = protein.associated_.all()
        for term in interpro_terms:
            if term.interpro_id not in terms_seen:
                if term.name is not None:
                    interpro_label = '{} ({})'.format(term.name, term.interpro_id)
                else:
                    interpro_label = term.interpro_id
                term_dict = dict(data=dict(id=term.interpro_id,
                                           label=interpro_label,
                                           node_colour=INTERPRO_NODE_COLOUR))
                terms_seen.add(term.interpro_id)
                subgraph.append(term_dict)
            edges.append(dict(data=dict(id='{}_{}'.format(protein.protein_id, term.interpro_id),
                                        source=protein.protein_id,
                                        target=term.interpro_id)))
        subgraph.extend(edges)
        return subgraph

    def protein_node(protein, gene_name=None):
        if gene_name is not None:
            protein_label = '{} ({})'.format(gene_name, protein.uniprot_id)
        else:
            protein_label = protein.uniprot_id
        return (dict(data=dict(id=protein.protein_id,
                               label=protein_label,
                               node_colour=PROTEIN_NODE_COLOUR)))

    gene = Gene.nodes.get(locus_tag=locus_tag)
    gene_name = gene.name
    protein = gene.transcribed.all()[0].encodes.all()[0].translated_.all()[0]
    interactions_graph = []
    styles = [{'selector': 'node',
               'style': {'label': 'data(label)', 'background-color': 'data(node_colour)'}}]
    try:
        tb_interactions = protein.interacts.all()
        interactions_graph.append(protein_node(protein, gene_name=gene_name))
        go_terms_seen = set()
        interpro_terms_seen = set()
        interactions_graph.extend(go_term_subgraph(protein, go_terms_seen))
        interactions_graph.extend(interpro_term_subgraph(protein, interpro_terms_seen))
        edges = []
        for partner_protein in tb_interactions:
            query = 'MATCH (g:Gene) -[:TRANSCRIBED]-> () -[:PROCESSED_INTO]-> () -[:TRANSLATED]-> ' \
                    '(:Protein {{uniprot_id: "{}"}}) RETURN g.name'.format(partner_protein.uniprot_id)
            (result, _) = db.cypher_query(query)
            gene_name = result[0][0]
            print("gene_name: ", gene_name, file=sys.stderr)
            edges.append(dict(data=dict(id='{}_{}'.format(protein.protein_id, partner_protein.protein_id),
                                        source=protein.protein_id,
                                        target=partner_protein.protein_id)))
            interactions_graph.append(protein_node(partner_protein, gene_name=gene_name))
            interactions_graph.extend(go_term_subgraph(partner_protein, go_terms_seen))
            interactions_graph.extend(interpro_term_subgraph(partner_protein, interpro_terms_seen))
        interactions_graph.extend(edges)
    except CardinalityViolation:
        tb_interactions = []
    try:
        human_interactions = protein.interacts_.all()
    except CardinalityViolation:
        human_interactions = []
    # print('gene:', gene, protein, tb_interactions, human_interactions, file=sys.stderr)
    interactions_graph_str = json.dumps(interactions_graph)
    styles_str = json.dumps(styles)
    # print("got here: {}".format(interactions_graph_str), file=sys.stderr)
    # desired output as per http://blog.js.cytoscape.org/2016/05/24/getting-started/
    # elements: [
    # // nodes
    # { data: { id: 'a' } },
    # { data: { id: 'b' } },
    # // edges
    # {
    #     data: {
    #         id: 'ab',
    #         source: 'a',
    #         target: 'b'
    #     }
    # } ]
    return dict(elements=interactions_graph, styles=styles)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    gene = term = pseudogene = ortholog_name = protein = interact = h_interact = None
    go_terms = []
    inter_pro = []
    ints = []
    h_ints = []
    publications = []
    aus = dict()
    pdb_ids = []
    print('ITEMS:', request.args.items())
    if request.method == 'GET':
        term = request.args.get('gene')
        gene = search_node(term)
    if request.method == 'POST':
        term = request.form['gene']
        gene = search_nodes(term)
    print(term)
    class_name = gene.__class__.__name__
    print(class_name)
    if gene and len(gene) > 1:
        print(len(gene))
        length = len(gene)
        print('Gene is an array...', len(gene))
        return render_template('m_results.html', genes=gene, length=length)
    elif gene and len(gene) == 1:
        # Trying to zoom out
        location = str(int(gene[0].start)) + '..' + str(int(gene[0].end))
        if 'Ps' not in gene[0].__class__.__name__:
            print(gene[0].__class__.__name__)
            for ortholog in gene[0].has_ortholog.match():
                ortholog_name = ortholog.locus_name
            for go in gene[0].has_go_terms.match():
                go_terms.append(go)
            for inter in gene[0].has_interpro_terms.match():
                inter_pro.append(str(inter.interpro_id))
            for cdc in gene[0].translated.match():
                for prot in cdc.translated_.match():
                    protein = prot
            try:
                for actor in protein.interacts.match():
                    ints.append(actor)
            except Exception as e:
                pass
            try:
                for h_actor in protein.interacts_.match():
                    h_ints.append(h_actor)
            except Exception as e:
                pass
            interact = [a.uniprot_id for a in ints]
            h_interact = [a.protein_id for a in h_ints]
            if gene[0].citation:
                # Dealing with unicode
                citation = gene[0].citation.encode('utf-8').replace('[', '').replace(']', '').split(', ')
                cite = [ct[1:-1] for ct in citation]
                for entry in cite:
                    if len(entry) > 0:
                        pub = Publication.nodes.get(pubmed_id=entry)
                        publications.append(pub)
                # Dealing with Unicode
                for p in publications:
                    au = p.authors.encode('utf-8').replace('[', '').replace(']', '').split(', ')
                    aus[p.pubmed_id] = [a[1:-1] for a in au]
                # Dealing with Unicode
                structure_ids = protein.pdb_id.encode('utf-8').replace('[', '').replace(']', '').split(', ')
                pdb_ids = [struc[2:-1] for struc in structure_ids]

        elif 'Ps' in gene[0].__class__.__name__:
            pseudogene = gene[0].biotype

        return render_template('results.html', term=term, gene=gene[0], pseudogene=pseudogene,
                               ortholog_name=ortholog_name, citation=publications, authors=aus, pdb_ids=pdb_ids,
                               location=location, go_terms=go_terms, inter_pro=inter_pro, protein=protein,
                               interactor=interact, h_interact=h_interact)
    else:
        gene = None
        return render_template('results.html', term=term, gene=gene)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/gsea')
def gsea():
    return render_template('gsea.html')


@app.route('/api/gsea/<hash>/download')
def download_gsea(hash):
    cache_filename = os.path.join(CACHE_DIR, hash + '.json')
    data = None
    if os.path.exists(cache_filename):
        data = json.load(open(cache_filename))
    data_str = 'GO Term ID\tGO Term Name\tRaw p-value\tCorrected p-value\r\n' + \
               '\r\n'.join(['\t'.join([str(cell) for cell in row]) for row in data]) + '\r\n'

    return Response(data_str, mimetype='text/tab-separated-values',
                    headers={'Content-Disposition': 'attachment; filename=gsea.tsv'})


@app.route('/api/gsea/<hash>', methods=['GET', 'POST'])
def process_gsea(hash):
    cache_filename = os.path.join(CACHE_DIR, hash + '.json')
    if request.method == 'POST' and not os.path.isfile(cache_filename):
        # don't recompute if we already have this data
        gsea_request = request.get_json()
        geneset = gsea_request['geneset']
        mode = gsea_request['mode']
        multipletest_corr = gsea_request['multipletest_comp']

        results = enrichment_analysis(geneset, mode=mode, multipletest_method=multipletest_corr)
        json_filename = os.path.join(TMP_DIR, hash + '.json')
        with open(json_filename, 'w') as output:
            output.write(json.dumps(results))
        os.rename(json_filename, cache_filename)

    json_result_str = '{}'
    try:
        with open(cache_filename) as input:
            results = json.loads(input.read())
            json_result_str = json.dumps(results)
    except IOError:
        pass

    return Response(
        json_result_str,
        mimetype='application/json',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )


@app.route('/api/ppi_data/<locus_tag>')
def ppi_data(locus_tag):
    data = find_interacting_proteins(locus_tag)
    print(data, file=sys.stderr)
    return Response(
        json.dumps(data),
        mimetype='application/json',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )


@app.route('/api/galaxy_histories')
def galaxy_histories():
    try:
        gi = connect_to_galaxy()
    except ConnectionError as e:
        print(e, file=sys.stderr)
        hist_list = []
    else:
        hist_list = [history for history in gi.histories.get_histories() if history.get('deleted') == False and
                     history.get('purged') == False]
    return Response(
        json.dumps(hist_list),
        mimetype='application/json',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )


@app.route('/api/galaxy_datasets/<history_id>')
def galaxy_dataset(history_id):
    try:
        gi = connect_to_galaxy()
    except ConnectionError as e:
        print(e, file=sys.stderr)
        dataset_list = []
    else:
        dataset_list = [dataset for dataset in gi.histories.show_history(history_id, contents=True) if
                        dataset.get('extension') == 'txt' and dataset.get('deleted') == False and dataset.get(
                            'purged') == False]

    return Response(
        json.dumps(dataset_list),
        mimetype='application/json',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )


@app.route('/api/galaxy_dataset/<dataset_id>')
def load_galaxy_dataset(dataset_id):
    timeout = 10000  # 10 seconds
    try:
        gi = connect_to_galaxy()
    except ConnectionError as e:
        print(e, file=sys.stderr)
        data = ''
    else:
        try:
            dc = DatasetClient(gi)
            data = dc.download_dataset(dataset_id, wait_for_completion=True, maxwait=timeout)
        except (AssertionError, DatasetTimeoutException) as e:
            print(e, file=sys.stderr)
            data = ''

    return Response(
        json.dumps(data),
        mimetype='application/json',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )

# @app.route('/testjsx')
# def testjsx():
#     return render_template('test.html')
