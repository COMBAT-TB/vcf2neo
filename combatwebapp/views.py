from __future__ import print_function

import json
import os
import subprocess
import sys

import flask_login
import requests as requests
from bioblend import galaxy
from bioblend.galaxy.datasets import DatasetClient, DatasetTimeoutException
from flask import Flask, Response, render_template, request, redirect, url_for, flash
from flask.ext.login import UserMixin, login_user, login_required, current_user
from flask.ext.login import logout_user
from flask_wtf.csrf import CSRFProtect

from combat_tb_model.model import *
from dbconn import graph, find_interacting_proteins, search_gene, search_feature
from forms import LoginForm, SearchForm
from gsea import enrichment_analysis

app = Flask(__name__)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

csrf = CSRFProtect(app)

CACHE_DIR = 'cache'
TMP_DIR = 'tmp'


def mkdir_if_needed(directory):
    if not os.path.isdir(directory):
        os.mkdir(directory)


mkdir_if_needed(CACHE_DIR)
mkdir_if_needed(TMP_DIR)

GALAXY_URL = 'http://ctbgx.sanbi.ac.za/'  # 'http://localhost:8080/'
gi = None


def connect_to_galaxy(api_key=None, email=None, password=None):
    print("Connecting to Galaxy Instance...")
    global gi
    gi = galaxy.GalaxyInstance(url=GALAXY_URL, key=api_key, email=email, password=password)
    return gi


#################################################
# Testing flask-login
#################################################

class User(UserMixin):
    pass


user = User()


@login_manager.user_loader
def user_loader(email):
    if email is None:
        return
    user.id = email
    return user


@app.route('/')
def index():
    form = SearchForm()
    return render_template('index.html', form=form, user=user)


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
        term = str(request.args.get('featurename')).strip('gene:')
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
        return render_template('m_results.html', features=features, length=length, user=user)
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
                               interactor=interact, h_interact=h_interact, user=user)
    else:
        gene = None
        protein = []
        return render_template('results.html', term=term, gene=gene, protein=protein)


@app.route('/about')
def about():
    return render_template('about.html', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'GET':
        return render_template("login.html", form=form, user=None)
    else:
        if form.validate_on_submit():
            email = request.form['email']
            form_pass = request.form['password']
            url = GALAXY_URL + "api/authenticate/baseauth"
            response = requests.get(url, auth=(email, form_pass))
            if response.status_code == 200:
                api_key = response.json()['api_key']
                _g = connect_to_galaxy(api_key=api_key)
                print("Galaxy user email: " + _g.users.get_current_user()['email'])
                # TODO: This should not be here: We already have a 200.
                if email == _g.users.get_current_user()['email']:
                    user.id = email
                    login_user(user)
                # Let's redirect to previous page, when you went to a service without being logged in.
                url = 'index'
                if request.args.get('next'):
                    url = str(request.args.get('next')).strip('/')
                return redirect(url_for(url) or url_for('index'))
            else:
                flash('Invalid details, please try again.', 'error')
                return redirect(url_for('login'))
        else:
            return redirect(url_for('login'))


@app.route('/logout')
def logout():
    logout_user()
    user.id = None
    return redirect(url_for('index'))


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login', next=request.path))


@app.route('/jbrowse')
def jbrowse():
    return render_template('jbrowse.html', user=None)


@app.route('/gsea')
@login_required
def gsea():
    return render_template('gsea.html', user=user)


@app.route('/api/gsea/<hash>/download')
@login_required
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
@login_required
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
@login_required
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
@login_required
def galaxy_histories():
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
@login_required
def galaxy_dataset(history_id):
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


def get_dc_list(history_id):
    """
    Get dataset collections
    :param history_id:
    :return:
    """
    history_contents = gi.histories.show_history(history_id, contents=True, deleted=False, visible=True, details=False)
    collection_ids = [d.get('id') for d in history_contents if d.get('history_content_type') == 'dataset_collection']
    dc_list = [gi.histories.show_dataset_collection(history_id, _id) for _id in collection_ids]
    vcf_dc_list = [col for col in dc_list if 'SnpEff' in col['name'] and 'stats' not in col['name']]

    return vcf_dc_list


@app.route('/api/galaxy_col_datasets/<history_id>')
@login_required
def galaxy_col_dataset(history_id):
    datasets = gi.histories.show_matching_datasets(history_id, name_filter="SnpEff on data \d+")
    vcf_datasets = None
    if datasets:
        vcf_datasets = [dataset for dataset in datasets if
                        dataset.get('extension') == 'vcf' and dataset.get('deleted') is False and dataset.get(
                            'purged') is False and dataset.get('file_size') > 0]

    return Response(
        json.dumps(vcf_datasets),
        mimetype='application/json',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )


@app.route('/api/galaxy_dataset_col/<history_id>')
@login_required
def galaxy_dataset_col(history_id):
    dc_list = get_dc_list(history_id)
    return Response(
        json.dumps(dc_list),
        mimetype='application/json',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )


@app.route('/api/load_col_datasets/<history_id>')
@login_required
def load_col_dataset(history_id):
    datasets = gi.histories.show_matching_datasets(history_id, name_filter="SnpEff on data \d+")
    vcf_datasets = None
    dataset_ids = []
    if datasets:
        vcf_datasets = [dataset for dataset in datasets if
                        dataset.get('extension') == 'vcf' and dataset.get('deleted') is False and dataset.get(
                            'purged') is False and dataset.get('file_size') > 0]
        for ds in vcf_datasets:
            dataset_ids.append(ds.get('id'))
    dc_list = get_dc_list(history_id)
    elements = [item.get('elements') for item in dc_list]
    element_identifiers = [[[el.get('element_identifier') for el in element] for element in elements]]
    dc_name = [dc.get('name') for dc in dc_list]

    try:
        p = subprocess.Popen(["mkdir", "{}".format(dc_name[0])], stdout=subprocess.PIPE)
        out, err = p.communicate()
        sys.stdout.write(out)

        timeout = 10000  # 10 seconds
        data_dict = dict()
        dc = DatasetClient(gi)
        for dataset_id in dataset_ids:
            vcf_file = dc.download_dataset(dataset_id, file_path=str(os.getcwd() + "/" + str(dc_name[0])),
                                           wait_for_completion=True,
                                           maxwait=timeout)
            data = dc.download_dataset(dataset_id, wait_for_completion=True, maxwait=timeout)
            data_dict[vcf_file[str(vcf_file).find('G'):]] = data

        p = subprocess.Popen(
            ["vcf2neo", "init", "-D", "{}".format(os.getcwd() + "/" + dc_name[0]), "{}".format(current_user.id)],
            stdout=subprocess.PIPE)
        out, err = p.communicate()
        sys.stdout.write(str(out))
    except (AssertionError, DatasetTimeoutException, OSError, ValueError) as e:
        sys.stderr.write(str(e))
        print(e, file=sys.stderr)

    return Response(
        json.dumps(vcf_datasets),
        mimetype='application/json',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )


# @app.route('/testjsx')
# def testjsx():
#     return render_template('test.html')

@app.route('/vcf')
@login_required
def vcf():
    return render_template('vcf.html', user=user)
