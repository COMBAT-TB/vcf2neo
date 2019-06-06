# vcf2neo

[![Build Status](https://travis-ci.org/COMBAT-TB/vcf2neo.svg?branch=master)](https://travis-ci.org/COMBAT-TB/vcf2neo)
[![Coverage Status](https://coveralls.io/repos/github/COMBAT-TB/vcf2neo/badge.svg?branch=master)](https://coveralls.io/github/COMBAT-TB/vcf2neo?branch=master)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1219127.svg)](https://doi.org/10.5281/zenodo.1219127)

A tool to import and map **[SnpEff annotated](http://snpeff.sourceforge.net/SnpEff.html)** VCF files to [COMBAT-TB NeoDB](https://github.com/COMBAT-TB/combat-tb-neodb) Graph database.

**Prerequisites**:

- [`docker`](https://docs.docker.com/v17.12/install/) and [`docker-compose`](https://docs.docker.com/compose/install/) :whale:

## Usage

**Clone repository**:

```sh
$ git clone https://github.com/SANBI-SA/vcf2neo.git
...
$ cd vcf2neo
```

**Build [COMBAT-TB NeoDB](https://github.com/COMBAT-TB/combat-tb-neodb)**:

```sh
$ docker-compose up --build -d
...
```

**Install and run `vcf2neo`**:

- Using `pip`

```sh
$ pip install -i https://test.pypi.org/simple/ vcf2neo
...
```

- or via `setup` in `virtualenv`

```sh
$ virtualenv envname
...
$ source envname/bin/activate
$ pip install -r requirements.txt
$ python setup.py install
```

**Import and map SnpEff annotated VCF files to genes and drugs in NeoDB**:

You change the default database location (`localhost`) by setting the
`DATABASE_URL` environment variable to `remote`.

```sh
$ vcf2neo --help
Usage: vcf2neo [OPTIONS] COMMAND [ARGS]...
...
$ vcf2neo load_vcf PATH/TO/VCF_DIR
```

**Exploring variant data**:

Point your browser to [localhost:7474](http://0.0.0.0:7474) to access the Neo4j browser.

To view the schema, run:

```cql
call db.schema.visualization
```

Sample [Cypher](https://neo4j.com/developer/cypher-query-language/) query:

```cql
MATCH(g:Gene)--(v:Variant)--(cs:CallSet)
RETURN g.name as gene, v.consequence as variant, cs.name as file
LIMIT 25
```
