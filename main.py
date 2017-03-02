#!/usr/bin/env python
from __future__ import print_function
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import csv
import time
from os import getenv

from BCBio import GFF
from bioservices import UniProt
from py2neo import Graph, watch
from tqdm import tqdm

from model.core import Organism, Feature, FeatureLoc, Gene, PseudoGene, CDS, Transcript, Exon, TRna, NCRna, RRna, \
    DbXref, Polypeptide, CvTerm, Publication

# https://neo4j.com/developer/kb/explanation-of-error-on-session-connection-using-uniform-drivers/
graph = Graph(host=getenv("DB", "http://thoba.sanbi.ac.za:7474"), bolt=True,
              password=getenv("NEO4J_PASSWORD", ""), encrypted=False)

watch("neo4j.bolt")

gff_file = "data/MTB_H37rv.gff3"

u = UniProt(verbose=False)


def delete_data():
    """
    Delete existing data.
    :return:
    """
    print("Deleting all nodes and relationships in {}".format(graph))
    graph.delete_all()


def create_organism_nodes():
    abbrev = "H37Rv"
    genus = "Mycobacterium"
    species = "M. tuberculosis"
    common_name = "TB"

    organism = Organism(abbreviation=abbrev, genus=genus,
                        species=species, common_name=common_name)
    graph.create(organism)


def create_feature_nodes(feature):
    """
    Create Feature Nodes.
    :param feature:
    :return:
    """
    if feature.qualifiers.get('Parent'):
        parent = feature.qualifiers['Parent'][0]
    else:
        parent = None

    names = get_feature_name(feature)
    name = names.get("Name", names.get("UniqueName"))
    unique_name = names.get("UniqueName", name)

    _feature = Feature()
    _feature.name = name
    _feature.type = feature.type
    _feature.parent = parent
    _feature.uniquename = unique_name
    graph.create(_feature)


def get_feature_name(feature):
    """
    Get Feature Name and UniqueName.
    :param feature:
    :return:
    """
    names = dict()
    if feature.qualifiers.get("Name"):
        names["Name"] = feature.qualifiers["Name"][0]
        names["UniqueName"] = feature.id
    else:
        names["Name"] = names["UniqueName"] = feature.id
    return names


def create_gene_nodes(feature):
    """
    Create Gene Nodes.
    :param feature:
    :return:
    """
    names = get_feature_name(feature)
    name = names.get("Name", names.get("UniqueName"))
    unique_name = names.get("UniqueName", name)

    gene = Gene()
    gene.ontology_id = gene.so_id
    gene.name = name
    gene.uniquename = unique_name
    graph.create(gene)


def create_exon_nodes(feature):
    """
    Create Exon Nodes
    :param feature:
    :return:
    """
    names = get_feature_name(feature)
    name = names.get("Name", names.get("UniqueName"))
    unique_name = names.get("UniqueName", name)

    exon = Exon()
    exon.ontology_id = exon.so_id
    exon.name = name
    exon.uniquename = unique_name
    graph.create(exon)


def create_pseudogene_nodes(feature):
    """
    Create Pseudogene Nodes
    :param feature:
    :return:
    """
    names = get_feature_name(feature)
    name = names.get("Name", names.get("UniqueName"))
    unique_name = names.get("UniqueName", name)

    pseudogene = PseudoGene()
    pseudogene.ontology_id = pseudogene.so_id
    pseudogene.name = name
    pseudogene.uniquename = unique_name
    graph.create(pseudogene)


def create_rna_nodes(feature):
    """
    Create RNA Nodes
    :param feature:
    :return:
    """
    names = get_feature_name(feature)
    name = names.get("Name", names.get("UniqueName"))
    unique_name = names.get("UniqueName", name)

    if feature.type == 'tRNA_gene':
        trna = TRna()
        trna.ontology_id = trna.so_id
        trna.name = name
        trna.uniquename = unique_name
        graph.create(trna)
    if feature.type == 'ncRNA_gene':
        ncrna = NCRna()
        ncrna.ontology_id = ncrna.so_id
        ncrna.name = name
        ncrna.uniquename = unique_name
        graph.create(ncrna)
    if feature.type == 'rRNA_gene':
        rrna = RRna()
        rrna.ontology_id = rrna.so_id
        rrna.name = name
        rrna.uniquename = unique_name
        graph.create(rrna)


def create_transcript_nodes(feature):
    """
    Create Transcipt Nodes
    :param feature:
    :return:
    """
    names = get_feature_name(feature)
    name = names.get("Name", names.get("UniqueName"))
    unique_name = names.get("UniqueName", name)

    transcript = Transcript()
    transcript.ontology_id = transcript.so_id
    transcript.name = name
    transcript.uniquename = unique_name
    graph.create(transcript)


def create_cds_nodes(feature):
    """
    Create CDS Nodes
    :param feature:
    :return:
    """
    names = get_feature_name(feature)
    name = names.get("Name", names.get("UniqueName"))
    unique_name = names.get("UniqueName", name)

    cds = CDS()
    cds.name = name
    cds.uniquename = unique_name
    graph.create(cds)


def create_featureloc_nodes(feature):
    """
    Create FeatureLoc Nodes.
    :param feature:
    :return:
    """
    srcfeature_id = get_feature_name(feature).get("UniqueName")
    feature_loc = FeatureLoc(srcfeature_id=srcfeature_id, fmin=feature.location.start, fmax=feature.location.end,
                             strand=feature.location.strand)
    graph.create(feature_loc)


def build_relationships():
    """
    Build relationships.
    :return:
    """
    print("Building Relationships...")
    features = Feature.select(graph)
    for feature in features:
        # Find organism via __primarykey__ and link with feature via BELONGS_TO
        org = Organism.select(graph, 'Mycobacterium').first()
        feature.belongs_to.add(org)
        graph.push(org)
        # Find feature with a parent attr. matching this features uniquename
        # and link them via RELATED_TO
        _feature = Feature.select(graph).where(
            "_.parent = '{}'".format(feature.uniquename)).first()
        if _feature:
            feature.related_to.add(_feature)
            graph.push(_feature)
        # Building is_a relationships
        gene = Gene.select(graph).where(
            "_.uniquename = '{}'".format(feature.uniquename)).first()
        if gene:
            gene.is_a.add(feature)
            graph.push(gene)
            # Find feature with this gene's uniquename as a parent
            _feature = Feature.select(graph).where(
                "_.parent = '{}'".format(gene.uniquename)).first()
            if _feature:
                # Find transcript: A gene is a parent to it.
                transcript = Transcript.select(
                    graph).where(
                    "_.parent = '{}'".format(_feature.uniquename)).first()
                if transcript:
                    transcript.part_of.add(gene)
                    graph.push(transcript)

        p_gene = PseudoGene.select(graph).where(
            "_.uniquename = '{}'".format(feature.uniquename)).first()
        if p_gene:
            p_gene.is_a.add(feature)
            graph.push(p_gene)
        transcript = Transcript.select(graph).where(
            "_.uniquename = '{}'".format(feature.uniquename)).first()
        if transcript:
            transcript.is_a.add(feature)
            graph.push(transcript)
            # Find feature with this transcript's uniquename as a parent
            _feature = Feature.select(graph).where(
                "_.parent = '{}'".format(transcript.uniquename)).first()
            if _feature:
                # Find exon: A transcript is a parent to it
                exon = Exon.select(graph).where(
                    "_.uniquename = '{}'".format(_feature.uniquename)).first()
                if exon:
                    exon.part_of.add(transcript)
                    graph.push(exon)
                # Find cds: A transcript is a parent to it
                cds = CDS.select(graph).where(
                    "_.uniquename = '{}'".format(_feature.uniquename)).first()
                if cds:
                    cds.part_of.add(transcript)
                    graph.push(cds)

        exon = Exon.select(graph).where(
            "_.uniquename = '{}'".format(feature.uniquename)).first()
        if exon:
            exon.is_a.add(feature)
            graph.push(exon)
        cds = CDS.select(graph).where(
            "_.uniquename = '{}'".format(feature.uniquename)).first()
        if cds:
            cds.is_a.add(feature)
            graph.push(cds)
        # Find feature location with a srcfeature_id attr. matching this features uniquename and link them via
        # LOCATED_AT
        _feature = FeatureLoc.select(graph).where(
            "_.srcfeature_id = '{}'".format(feature.uniquename)).first()
        if _feature:
            feature.location.add(_feature)
        graph.push(feature)


def get_locus_tags(_gff_file, chunk):
    """
    Return a list of locus tags from gff_file
    :param _gff_file:
    :param chunk
    :return:
    """
    print("Getting locus_tags...")
    count = 0
    locus_tags = []
    for rec in GFF.parse(_gff_file, limit_info=dict(gff_type=['gene'])):
        for gene in rec.features:
            locus_tag = gene.qualifiers["gene_id"][0]
            count += 1
            locus_tags.append(locus_tag)
            if count == chunk:
                yield locus_tags
                locus_tags = []
                count = 0
    yield locus_tags


def search_uniprot(query, columns, proteome='UP000001584'):
    """
    Search UniProt and return results as list
    :param query:
    :param columns:
    :param proteome:
    :return:
    """
    query = "taxonomy:83332+AND+proteome:{}+AND+{}".format(proteome, query)

    result = u.search(query=query, frmt="tab", columns=columns, sort=None)
    reader = csv.reader(StringIO(result), delimiter='\t')
    try:
        reader.next()
    except StopIteration:
        return []
    else:
        return list(reader)


def create_cv_term_nodes(polypeptide, bp, cc, mf):
    """
    Create CvTerm Nodes.
    :param polypeptide:
    :param bp:
    :param cc:
    :param mf:
    :return:
    """
    # go(biological process)
    go_bp_ids = [t[t.find('G'):-1] for t in bp.split('; ') if t is not '']
    go_bp_defs = [t[:t.find('[') - 1] for t in bp.split('; ') if t is not '']
    # go(cellular component)
    go_cc_ids = [t[t.find('G'):-1] for t in cc.split('; ') if t is not '']
    go_cc_defs = [t[:t.find('[') - 1] for t in cc.split('; ') if t is not '']
    # go(molecular function)
    go_mf_ids = [t[t.find('G'):-1] for t in mf.split('; ') if t is not '']
    go_mf_defs = [t[:t.find('[') - 1] for t in mf.split('; ') if t is not '']

    # TODO: Find a way to refactor this.
    for _id in go_bp_ids:
        cv = CvTerm()
        for _def in go_bp_defs:
            cv.name = _id
            cv.definition = _def
            cv.namespace = "biological process"
            graph.create(cv)
            polypeptide.cvterm.add(cv)
            graph.push(polypeptide)

    for _id in go_mf_ids:
        cv = CvTerm()
        for _def in go_mf_defs:
            cv.name = _id
            cv.definition = _def
            cv.namespace = "cellular component"
            graph.create(cv)
            polypeptide.cvterm.add(cv)
            graph.push(polypeptide)
    for _id in go_cc_ids:
        cv = CvTerm()
        for _def in go_cc_defs:
            cv.name = _id
            cv.definition = _def
            cv.namespace = "molecular function"
            graph.create(cv)
            polypeptide.cvterm.add(cv)
            graph.push(polypeptide)


def create_interpro_term_nodes(polypeptide, entry):
    """
    Create InterPro Term Nodes.
    :param polypeptide:
    :param entry:
    :return:
    """
    # http://generic-model-organism-system-database.450254.n5.nabble.com/Re-GMOD-devel-Storing-Interpro-domains-in-Chado-td459778.html
    terms = [t for t in entry.split("; ") if t is not '']
    for interpro in terms:
        import time
        dbxref = DbXref(db="InterPro", accession=interpro, version=time.time())
        graph.create(dbxref)
        polypeptide.dbxref.add(dbxref)
        graph.push(polypeptide)


def create_pub_nodes(polypeptide, pubs):
    """
    Create Publication Nodes
    :param polypeptide:
    :param pubs:
    :return:
    """
    citations = [c for c in pubs.split("; ") if c is not '']

    for citation in citations:
        pub = Publication()
        pub.pmid = citation

        polypeptide.published_in.add(pub)
        graph.push(polypeptide)


def build_protein_interaction_rels(protein_interaction_dict):
    """
    Build protein-protein interactions
    :param protein_interaction_dict:
    :return:
    """
    for uni_id, interactors in protein_interaction_dict.items():
        if len(interactors) > 0:
            poly = Polypeptide.select(graph).where(
                "_.uniquename = '{}'".format(uni_id)).first()
            interactors = interactors.split('; ')
            for interactor in interactors:
                if interactor == 'Itself':
                    interactor = poly.uniquename
                _poly = Polypeptide.select(graph).where(
                    "_.uniquename = '{}'".format(interactor)).first()
                if _poly is None:
                    print("No Polypeptide with uniquename: {}".format(interactor))
                    time.sleep(2)
                else:
                    poly.interacts_with.add(_poly)
                    graph.push(poly)


def create_uniprot_nodes(uniprot_data):
    """
    Build DbXref nodes from UniProt results.
    :param uniprot_data:
    :return:
    """
    print("=========================================")
    print("About to create Nodes from UniProt data.")
    print("=========================================")
    time.sleep(2)
    count = 0
    protein_interaction_dict = dict()
    for entry in uniprot_data:
        protein_interaction_dict[entry[0]] = entry[6]
        count += 1

        dbxref = DbXref(db="UniProt", accession=entry[1], version=entry[0])
        graph.create(dbxref)

        polypeptide = Polypeptide()
        polypeptide.name = entry[9]
        polypeptide.uniquename = entry[0]
        polypeptide.ontology_id = polypeptide.so_id
        polypeptide.seqlen = entry[16]
        polypeptide.residues = entry[14]
        polypeptide.parent = entry[2]
        polypeptide.family = entry[17]
        polypeptide.function = entry[13]
        graph.create(polypeptide)

        gene = Gene.select(graph).where(
            "_.uniquename = 'gene:{}'".format(entry[2])).first()
        if gene:
            _feature = Feature.select(graph).where(
                "_.parent = '{}'".format(gene.uniquename)).first()
            if _feature:
                transcript = Transcript.select(graph).where(
                    "_.uniquename = '{}'".format(_feature.uniquename)).first()
                if transcript:
                    cds = CDS.select(graph).where("_.uniquename = '{}'".format(
                        "CDS" + transcript.uniquename[transcript.uniquename.find(":"):])).first()
                    if cds:
                        # Polypetide-derives_from->CDS
                        polypeptide.derives_from.add(cds)
                        cds.polypeptide.add(polypeptide)
                        graph.push(polypeptide)
                        graph.push(cds)

        polypeptide.dbxref.add(dbxref)
        graph.push(polypeptide)

        create_cv_term_nodes(polypeptide, entry[18], entry[19], entry[20])
        create_interpro_term_nodes(polypeptide, entry[5])
        create_pub_nodes(polypeptide, entry[11])
    build_protein_interaction_rels(protein_interaction_dict)
    print ("TOTAL:", count)


def query_uniprot(locus_tags):
    """
    Get data from UniProt
    :param locus_tags:
    :return:
    """
    print("Querying UniProt...")
    columns = "id, entry name, genes(OLN), genes, go-id, interpro, interactor, genes(PREFERRED), " \
              "feature(DOMAIN EXTENT), protein names, go, citation, 3d, comment(FUNCTION), sequence, mass, " \
              "length, families, go(biological process),  go(molecular function), go(cellular component)," \
              " genes(ALTERNATIVE), genes(ORF), version(sequence)"
    uniprot_data = []
    results = []
    for tag_list in locus_tags:
        query = '(' + '+OR+'.join(['gene:' + name for name in tag_list]) + ')'
        result = search_uniprot(query, columns)
        uniprot_data.append(result)

    for data in uniprot_data:
        for entry in data:
            results.append(entry)
    create_uniprot_nodes(results)
    return results


def load_gff_data(_gff_file, limit):
    """
    Extract and load features to Neo4j.
    :param _gff_file:
    :param limit:
    :return:
    """
    in_file = open(_gff_file)
    limit_info = dict(gff_type=limit)
    rna = ["tRNA_gene", "ncRNA_gene", "rRNA_gene"]
    for rec in GFF.parse(_gff_file, limit_info=limit_info):
        for feature in tqdm(rec.features):
            create_feature_nodes(feature)
            if feature.type == 'gene':
                create_gene_nodes(feature)
            elif feature.type == 'pseudogene':
                create_pseudogene_nodes(feature)
            elif feature.type == 'exon':
                create_exon_nodes(feature)
            elif feature.type in rna:
                create_rna_nodes(feature)
            elif feature.type == 'transcript':
                create_transcript_nodes(feature)
            elif feature.type == 'CDS':
                create_cds_nodes(feature)
            create_featureloc_nodes(feature)
    in_file.close()


def parse_gff(_gff_file):
    """
    Parse GFF file.
    :return:
    """
    create_organism_nodes()
    limits = [["transcript"], ["CDS"], ["gene"], ["pseudogene"], ["exon"],
              ["tRNA_gene", "ncRNA_gene", "rRNA_gene"]]
    for limit in limits:
        print("Loading", limit, "...")
        load_gff_data(_gff_file, limit)
    print("Done.")


if __name__ == '__main__':
    time.sleep(10)
    delete_data()
    parse_gff(gff_file)
    build_relationships()
    query_uniprot(get_locus_tags(gff_file, 400))
