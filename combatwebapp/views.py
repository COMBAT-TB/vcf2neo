from combat_tb_model import *
from neomodel import DoesNotExist
from flask import Flask, render_template

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
