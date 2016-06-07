import os
import json
from combat_tb_model.model import *
from neomodel import DoesNotExist, db
from flask import Flask, Response, render_template, request
from gsea import enrichment_analysis

app = Flask(__name__)

CACHE_DIR = 'cache'
TMP_DIR = 'tmp'

def mkdir_if_needed(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)

mkdir_if_needed(CACHE_DIR)
mkdir_if_needed(TMP_DIR)

def cypher_search(name):
    print 'cypher_search...'
    arr = []
    res = None
    query = "MATCH (n:Gene) where n.name=~'(?i){}.*' OR n.locus_tag=~'(?i){}.*' " \
            "OR n.preffered_name=~'(?i){}.*' OR n.uniprot_entry=~'(?i){}.*' RETURN n " \
            "UNION MATCH (n:Pseudogene) where n.name=~'(?i){}.*' RETURN n ".format(name, name, name, name, name)
    result, meta = db.cypher_query(query)
    for row in result:
        res = Gene.inflate(row[0])
        arr.append(res)
    print len(arr)
    print [entry.name for entry in arr]
    return arr


# Search nodes
def search_nodes(name):
    try:
        print 'Searching Gene Nodes with Name=', name
        # node = Gene.nodes.get(name=name)
        node = cypher_search(name)
        if node:
            print node
        return node
    except DoesNotExist, e:
        pass
    try:
        print 'Searching Pseudogene Nodes with Gene_ID=', name
        node = Pseudogene.nodes.get(pseudogene_id='gene:' + name)
        return node
    except DoesNotExist, e:
        pass
    try:
        print 'Searching Transcript Nodes with Gene=', name
        node = Transcript.nodes.get(gene=name)
        return node
    except DoesNotExist, e:
        pass
    try:
        print 'Searching Protein Node with Parent=', name
        node = Protein.nodes.get(parent=name)
        return node
    except DoesNotExist, e:
        pass
    return None


def search_node(name):
    nodes = []
    try:
        print 'Searching Gene Nodes with Name=', name
        node = Gene.nodes.get(name=name)
        if node:
            print node
            nodes.append(node)
        return nodes
    except DoesNotExist, e:
        try:
            print 'Searching Pseudogene Nodes with Name=', name
            node = Pseudogene.nodes.get(name=name)
            if node:
                print node
                nodes.append(node)
            return nodes
        except DoesNotExist, e:
            raise e


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
    print 'ITEMS:', request.args.items()
    if request.method == 'GET':
        term = request.args.get('gene')
        gene = search_node(term)
    if request.method == 'POST':
        term = request.form['gene']
        gene = search_nodes(term)
    print term
    class_name = gene.__class__.__name__
    print class_name
    if gene and len(gene) > 1:
        print len(gene)
        length = len(gene)
        print 'Gene is an array...', len(gene)
        return render_template('m_results.html', genes=gene, length=length)
    elif gene and len(gene) == 1:
        # Trying to zoom out
        location = str(int(gene[0].start)) + '..' + str(int(gene[0].end))
        if 'Ps' not in gene[0].__class__.__name__:
            print gene[0].__class__.__name__
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
            except Exception, e:
                pass
            try:
                for h_actor in protein.interacts_.match():
                    h_ints.append(h_actor)
            except Exception, e:
                pass
            interact = [a.uniprot_id for a in ints]
            h_interact = [a.protein_id for a in h_ints]
            if gene[0].citation:
                # Dealing with unicode
                citation = gene[0].citation.encode('utf-8').replace('[', '').replace(']', '').split(', ')
                cite = [ct[1:-1] for ct in citation]
                aus = dict()
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
    if (os.path.exists(cache_filename)):
        data = json.load(open(cache_filename))
    data_str = 'GO Term ID\tGO Term Name\tRaw p-value\tCorrected p-value\r\n' + \
               '\r\n'.join(['\t'.join([ str(cell) for cell in row ]) for row in data]) + '\r\n'

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

