# **vcf2neo**

[![Build Status](https://travis-ci.org/COMBAT-TB/vcf2neo.svg?branch=master)](https://travis-ci.org/COMBAT-TB/vcf2neo)
[![Coverage Status](https://coveralls.io/repos/github/COMBAT-TB/vcf2neo/badge.svg?branch=master)](https://coveralls.io/github/COMBAT-TB/vcf2neo?branch=master)

A tool to import **SnpEff annotated** vcf files to a Neo4j Graph database.

This tool does the following:

- Starts up a Neo4j docker container (if used with `-d`)
- Downloads the [COMBAT-TB](https://combattb.org/) reference database in the `/data` directory of the container
- Import and map SnpEff annotated VCF files to genes in the database

## Usage

- **Clone this repository:**

  ```sh
  $ git clone https://github.com/SANBI-SA/vcf2neo.git
  ...
  $ cd vcf2neo
  ```

- **Install [`docker`](https://docs.docker.com/v17.12/install/) and [`docker-compose`](https://docs.docker.com/compose/install/) and run :whale::**

  ```sh
  $ docker-compose up --build -d
  ...
  ```

  The above command will download and spin up the COMBAT-TB Neo4j reference
  database found in the DOI below:

  [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1219127.svg)
  ](https://doi.org/10.5281/zenodo.1219127)

- **Install and run `vcf2neo` :computer: :**

  ```sh
   $ virtualenv envname
   ...
   $ source envname/bin/activate
   $ pip install -r requirements.txt
   $ python setup.py install
   $ vcf2neo --help
   $ vcf2neo load_vcf PATH/TO/VCF_DIR
  ```

- Point your browser to [localhost:7474](http://0.0.0.0:7474) to access the Neo4j browser.

  To view the schema, run:

  ```java
  call db.schema
  ```

  Sample [Cypher](https://neo4j.com/developer/cypher-query-language/) query:

  ```java
  MATCH(g:Gene)<-[r:OCCURS_IN]-(v:Variant) RETURN g.name as gene, v.consequence as variant LIMIT 25
  ```
