#!/usr/bin/env python

# Copyright 2016 SANBI, University of the Western Cape
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function, division

import sys
from operator import itemgetter

import click
from scipy.stats import fisher_exact
from statsmodels.sandbox.stats.multicomp import multipletests

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

# if 'NEO4J_REST_URL' not in os.environ:
#     NEO4J_CONFIG_FILE = os.environ.get('NEO4J_LOGIN_FILE', os.path.expanduser('~/.neo4j'))
#     if not os.path.isfile(NEO4J_CONFIG_FILE):
#         exit("Please put your Neo4J login details in {}".format(NEO4J_CONFIG_FILE))
#     neo4j_config = yaml.load(open(NEO4J_CONFIG_FILE))
#     os.environ['NEO4J_REST_URL'] = neo4j_config['combat_tb']
# url = urlparse(os.environ['NEO4J_REST_URL'])
# if '@' in url.netloc:
#     (host, port) = url.netloc.split('@')[1].split(':')
# else:
#     (host, port) = url.netloc.split(':')
# timeout = int(os.environ.get('NEO4J_WAIT_TIMEOUT', 30)) # time to wait till neo4j
# connected = False
# print('host, port', host, port, file=sys.stderr)
# while timeout > 0:
#     try:
#         socket.create_connection((host, port), 1)
#     except socket.error:
#         timeout -= 1
#         time.sleep(1)
#     else:
#         connected = True
#         break
# if connected:
#     print('connecting to {}'.format(os.environ['NEO4J_REST_URL']), file=sys.stderr)
# else:
#     sys.exit('timed out trying to connect to {}'.format(os.environ['NEO4J_REST_URL']))


from ..combat_tb_model import model
from py2neo import Graph, getenv

graph = Graph(host=getenv("DB", "localhost"), bolt=True, password=getenv("NEO4J_PASSWORD", ""))


def enrichment_analysis(geneset, mode='over', multipletest_method='fdr_bh'):
    if mode not in ('over', 'under'):
        raise ValueError("mode must be 'over' or 'under'")
    if multipletest_method not in ('fdr_bh', 'bonferroni'):
        raise ValueError("multipletest_method must be 'fdr_bh' (Benjamini-Hochberg) or 'bonferroni' (Bonferroni)")
    background_gene_count = len(model.Gene().nodes)
    goterm_prevalence_query = '''MATCH (t:GoTerm) <-[:ASSOCIATED_WITH]- (:Protein) <-[:TRANSLATED]-
    (:CDS) <-[:PROCESSED_INTO]- (:Transcript) <-[:TRANSCRIBED]- (g:Gene) RETURN
    t.go_id, t.name, count(g) AS t_count ORDER BY t_count DESC
    '''
    goterm_prevalence, _ = graph.data(goterm_prevalence_query)
    goterm_prevalence_dict = dict()
    for goterm_id, _, count in goterm_prevalence:
        goterm_prevalence_dict[goterm_id] = count
    geneset_strs = ['"' + name + '"' for name in geneset]
    tag_list = "[{}]".format(', '.join(geneset_strs))
    gs_goterm_prevalence_query = '''MATCH (t:GoTerm) <-[:ASSOCIATED_WITH]- (:Protein) <-[:TRANSLATED]-
    (:CDS) <-[:PROCESSED_INTO]- (:Transcript) <-[:TRANSCRIBED]- (g:Gene) WHERE g.locus_tag IN {tag_list}
    RETURN t.go_id, t.name, count(g) AS t_count ORDER BY t_count DESC
    '''.format(tag_list=tag_list)
    gs_goterm_prevalence, _ = graph.data(gs_goterm_prevalence_query)
    geneset_size = len(geneset)
    p_vals = []
    if mode == 'over':
        fe_test_mode = 'greater'
    else:
        fe_test_mode = 'less'
    for goterm_id, goterm_name, gs_goterm_count in gs_goterm_prevalence:
        # Fisher Exact test matrix
        #          GO term XXX      Not GO Term XXX
        # geneset     A                 B
        # background  C                 D
        background_goterm_count = goterm_prevalence_dict[goterm_id]
        fe_matrix = ((gs_goterm_count, geneset_size - gs_goterm_count),
                     (background_goterm_count, background_gene_count - background_goterm_count))
        _, p_val = fisher_exact(fe_matrix, alternative=fe_test_mode)
        p_vals.append((goterm_id, goterm_name, p_val))
    p_vals = sorted(p_vals, key=itemgetter(2))
    goterm_ids, goterm_names, uncorr_p_vals = zip(*p_vals)
    _, corrected_p_vals, _, _ = multipletests(uncorr_p_vals, is_sorted=True, method=multipletest_method)
    p_vals = zip(goterm_ids, goterm_names, uncorr_p_vals, corrected_p_vals)
    # for goterm_it, goterm_name, p_val, corr_p_val in p_vals:
    #     print(goterm_it, goterm_name, p_val, corr_p_val)
    return (p_vals)


@click.command()
@click.option('--mode', '-M', default='over', type=click.Choice(('over', 'under')))
@click.option('--multipletest_corr', '-T', default='BH', type=click.Choice(('BH', 'BON')))
@click.argument('geneset_file', type=click.File('r'))
@click.argument('output_file', required=False, default=sys.stdout, type=click.File('w'))
def analyse_geneset(geneset_file, output_file, mode='over', multipletest_corr='BH'):
    geneset = []
    for line in geneset_file:
        geneset.append(line.rstrip().split()[0].replace('rv_', 'Rv'))
    if multipletest_corr == 'BH':
        multi = 'fdr_bh'
    else:
        multi = 'bonferroni'
    results = enrichment_analysis(geneset, mode=mode, multipletest_method=multi)
    print('GO Term ID\tGO Term Name\tCorrected p-val\tUncorrected p-val', file=output_file)
    for goterm_id, goterm_name, uncorr_p_val, corr_p_val in results:
        print(goterm_id, goterm_name, corr_p_val, uncorr_p_val, file=output_file, sep='\t')
    output_file.close()


if __name__ == '__main__':
    analyse_geneset()
