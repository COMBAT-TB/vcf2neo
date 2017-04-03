# **vcf2neo**

A tool to import SnpEff produced vcf files to a Neo4j Graph database.

This tool does the following:

-   Starts up a Neo4j docker container (if used with `-d`)
-   Downloads the reference [database](https://zenodo.org/record/252101#.WIHfgvF95hH) in the `/data` directory of the container
-   Gets VCF files from a provided directory
-   Maps and loads the VCF data in Graph database

## Usage

**Clone this repository:**

```
$ git clone https://github.com/SANBI-SA/vcf2neo.git
$ cd vcf2neo
```

-   **Standalone :computer: :**

    ```
     $ virtualenv envname
     $ source envname/bin/activate
     $ pip install -r requirements.txt
     $ pip install --editable .
     $ vcf2neo --help
     $ vcf2neo init -d data/refvcf data/db/data
    ```

-   **Using docker/docker-compose :whale: :**

    ```
    $ docker-compose up --build -d
    ```
