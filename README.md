# **vcf2neo**
[![Build Status](https://travis-ci.org/thobalose/vcf2neo.svg?branch=master)](https://travis-ci.org/thobalose/vcf2neo)

A tool to import SnpEff annotated vcf files to a Neo4j Graph database.

This tool does the following:

-   Starts up a Neo4j docker container (if used with `-d`)
-   Downloads the reference [database](https://zenodo.org/record/252101#.WIHfgvF95hH) in the `/data` directory of the container
-   Gets VCF files from a provided directory
-   Maps and loads the VCF data in Graph database

## Usage

- **Clone this repository:**

    ```
    $ git clone https://github.com/SANBI-SA/vcf2neo.git
    $ cd vcf2neo
    ```

- **Install [`docker`](https://docs.docker.com/v17.12/install/) and 
[`docker-compose`](https://docs.docker.com/compose/install/) and run :whale: 
:** 
    ```
    $ docker-compose up --build -d
    ```

-   **Install and run `vcf2neo` :computer: :**

    ```
     $ virtualenv envname
     $ source envname/bin/activate
     $ pip install -r requirements.txt
     $ pip install --editable .
     $ vcf2neo --help
     $ vcf2neo load_vcf -D PATH/TO/VCF_FILES
    ```
    
Point your browser to [localhost:7474](http://0.0.0.0:7474) to access the Neo4j browser.

To view the schema, run:

```java
call db.schema
```

Sample query:

```java
MATCH(g:Gene)-[r:OCCURS_IN]-(v:Variant) RETURN g.name as gene, v.consequence 
as variant LIMIT 25
```
