from __future__ import print_function

import json
import os
import sys

import flask_login
from bioblend import galaxy
from bioblend.galaxy.datasets import DatasetClient, DatasetTimeoutException
from flask import Flask, Response, render_template, request, redirect, url_for, flash
from flask.ext.login import UserMixin, login_user, login_required
from flask_wtf.csrf import CSRFProtect
from py2neo import Graph, getenv

from combat_tb_model.model import *
from forms import LoginForm
from gsea import enrichment_analysis

graph = Graph(host=getenv("DB", "192.168.2.217"), http_port=7474, bolt=True,
              password=getenv("NEO4J_PASSWORD", ""))

app = Flask(__name__)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

csrf = CSRFProtect(app)

CACHE_DIR = 'cache'
TMP_DIR = 'tmp'


def mkdir_if_needed(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)


mkdir_if_needed(CACHE_DIR)
mkdir_if_needed(TMP_DIR)
gi = None


def connect_to_galaxy(galaxy_url='http://localhost:8080/', api_key=None, email=None, password=None):
    global gi
    if api_key is None and 'GALAXY_API_KEY' in os.environ:
        api_key = os.environ.get('GALAXY_API_KEY')
        gi = galaxy.GalaxyInstance(url=galaxy_url, key=api_key, email=email, password=password)
    else:
        gi = galaxy.GalaxyInstance(url=galaxy_url, email=email, password=password)
    return gi


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
            print("gene_name: ", gene_name, file=sys.stderr)
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


@app.route('/')
def index():
    return render_template('index.html')


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


@app.route('/search', methods=['GET', 'POST'])
def search():
    gene = term = PseudoGene = ortholog_name = protein = interact = h_interact = None
    go_terms = []
    inter_pro = []
    ints = []
    h_ints = []
    publications = []
    aus = dict()
    pdb_ids = []
    features = None
    if request.method == 'GET':
        term = request.args.get('gene')[5:]
        # gene = search_gene(term)
        features = search_feature(term)
    if request.method == 'POST':
        term = request.form['gene']
        features = search_feature(term)
    if len(features) > 1:
        print(len(features))
        length = len(features)
        for feature in features:
            gene = search_gene(feature.uniquename)
        print('Feature is an array...', len(features))
        return render_template('m_results.html', features=features, length=length)
    elif len(features) == 1:
        for feature in features:
            gene = search_gene(feature.uniquename)
            gene_uname = gene.uniquename
            try:
                protein = Polypeptide.select(graph).where(
                    "_.parent = '{}'".format(gene_uname[gene_uname.find(':') + 1:])).first()
            except Exception as e:
                raise e
            finally:
                go_term_s = protein.cvterm
                for go in go_term_s:
                    go_terms.append(go)
                interpro_terms = protein.dbxref
                for inter in interpro_terms:
                    if 'nterPro' in inter.db:
                        inter_pro.append(inter.accession)
                pdb_ids = protein.pdb_id
                for pub in protein.published_in:
                    publications.append(pub)

            locs = feature.location
            for loc in locs:
                print(loc.fmin, loc.fmax)
                location = str(loc.fmin) + '..' + str(loc.fmax)
                loc = loc
        return render_template('results.html', term=term, gene=gene, PseudoGene=PseudoGene,
                               ortholog_name=ortholog_name, citation=publications, authors=aus, pdb_ids=pdb_ids,
                               loc=loc, location=location, go_terms=go_terms, inter_pro=inter_pro, protein=protein,
                               interactor=interact, h_interact=h_interact)
    else:
        gene = None
        protein = []
        return render_template('results.html', term=term, gene=gene, protein=protein)


@app.route('/about')
def about():
    return render_template('about.html')


#################################################
# Testing flask-login
#################################################

# Our mock database.
users = {'thoba@sanbi.ac.za': {'password': 'galaxy'}}


class User(UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return
    user = User()
    user.id = email
    return user


# @login_manager.request_loader
# def request_loader(request):
#     email = request.form.get('email')
#     if email not in users:
#         return
#
#     user = User()
#     user.id = email
#
#     # DO NOT ever store passwords in plaintext and always compare password
#     # hashes using constant-time comparison!
#     user.is_authenticated = request.form['pw'] == users[email]['pw']
#
#     return user


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'GET':
        return render_template("login.html", form=form)
    else:
        if form.validate_on_submit():
            email = request.form['email']
            form_pass = request.form['password']
            user_pass = users[email]['password']
            if form_pass == user_pass:
                user = User()
                user.id = email
                login_user(user)
                g = connect_to_galaxy(email=email, password=form_pass)
                hist_list = [history for history in gi.histories.get_histories() if history.get('deleted') is False and
                             history.get('purged') is False]
                print(hist_list)
                print(gi.users.get_users())
                return redirect(url_for('protected'))
        else:
            return redirect(url_for('login'))


@app.route('/protected')
@login_required
def protected():
    print('Logged in as: ' + flask_login.current_user.id)
    # return 'Logged in as: ' + flask_login.current_user.id
    return redirect(url_for('gsea'))


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('login'))


@login_manager.unauthorized_handler
def unauthorized_handler():
    flash('Unauthorized')
    return redirect(url_for('login'))


@app.route('/gsea')
@login_required
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
    # try:
    #     gi = connect_to_galaxy(email='thoba@sanbi.ac.za', password='galaxy')
    # except ConnectionError as e:
    #     print(e, file=sys.stderr)
    #     hist_list = []
    # else:
    hist_list = [history for history in gi.histories.get_histories() if history.get('deleted') is False and
                 history.get('purged') is False]
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
    # try:
    #     gi = connect_to_galaxy()
    # except ConnectionError as e:
    #     print(e, file=sys.stderr)
    #     dataset_list = []
    # else:
    dataset_list = [dataset for dataset in gi.histories.show_history(history_id, contents=True) if
                    dataset.get('extension') == 'txt' and dataset.get('deleted') is False and dataset.get(
                        'purged') is False]

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
    # try:
    #     gi = connect_to_galaxy()
    # except ConnectionError as e:
    #     print(e, file=sys.stderr)
    #     data = ''
    # else:
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
