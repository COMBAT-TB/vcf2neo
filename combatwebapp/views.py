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
        raise e


@app.route('/')
def index():
    # gene = search_nodes('Rv0016c')
    return render_template('index.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    gene = None
    if request.method == 'POST':
        term = request.form['gene']
        gene = search_nodes(term)
    return render_template('results.html', gene=gene.name)


@app.route('/about')
def about():
    return render_template('about.html')
