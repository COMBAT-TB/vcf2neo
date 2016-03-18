from combat_tb_model import *
from neomodel import DoesNotExist, db
from flask import Flask, render_template, request

app = Flask(__name__)


def cypher_search(name):
    print 'cypher_search...'
    res = None
    query = "MATCH (n:Gene) where n.name=~'(?i){}.*' OR n.locus_tag=~'(?i){}.*' " \
            "OR n.preffered_name=~'(?i){}.*' OR n.uniprot_entry=~'(?i){}.*' RETURN n".format(name, name, name, name)
    result, meta = db.cypher_query(query)
    for row in result:
        res = Gene.inflate(row[0])
    return res


# Search nodes
def search_nodes(name):
    try:
        print 'Searching Gene Nodes with Name=', name
        # node = Gene.nodes.get(name=name)
        node = cypher_search(name)
        if node:
            print node.name
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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    term = gene = pseudogene = ortholog_name = location = protein = None
    go_terms = []
    inter_pro = []
    if request.method == 'POST':
        term = request.form['gene']
        gene = search_nodes(term)
        class_name = gene.__class__.__name__
        print class_name
        if gene:
            location = str(gene.start) + '..' + str(gene.end)
            if 'Ps' not in class_name:
                for ortholog in gene.has_ortholog.match():
                    ortholog_name = ortholog.locus_name
                for go in gene.has_go_terms.match():
                    go_terms.append(str(go.go_id))
                for inter in gene.has_interpro_terms.match():
                    inter_pro.append(str(inter.interpro_id))
                for cdc in gene.translated.match():
                    for prot in cdc.translated_.match():
                        protein = prot
            elif 'Ps' in class_name:
                pseudogene = gene.biotype
    return render_template('results.html', term=term, gene=gene, pseudogene=pseudogene, ortholog_name=ortholog_name,
                           location=location, go_terms=go_terms, inter_pro=inter_pro, protein=protein)


@app.route('/about')
def about():
    return render_template('about.html')
