from combat_tb_model import *
from neomodel import DoesNotExist
from flask import Flask, render_template, request

app = Flask(__name__)


# Search nodes
def search_nodes(name):
    try:
        print 'Searching Gene Nodes with Name=', name
        node = Gene.nodes.get(name=name)
        return node
    except DoesNotExist, e:
        pass
    try:
        print 'Searching Pseudogene Nodes with Gene_ID=', name
        node = Pseudogene.nodes.get(gene_id=name)
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
    term = gene = pseudogene = ortholog_name = location = None
    if request.method == 'POST':
        term = request.form['gene']
        gene = search_nodes(term.capitalize())
        class_name = gene.__class__.__name__
        print class_name
        if gene:
            location = str(gene.start) + '..' + str(gene.end)
            if 'Ps' not in class_name:
                for ortholog in gene.has_ortholog.match():
                    ortholog_name = ortholog.locus_name
            elif 'Ps' in class_name:
                pseudogene = gene.biotype
    return render_template('results.html', term=term, gene=gene, pseudogene=pseudogene, ortholog_name=ortholog_name,
                           location=location)


@app.route('/about')
def about():
    return render_template('about.html')
