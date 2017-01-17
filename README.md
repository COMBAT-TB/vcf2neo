# **vcf2neo**
A tool to import SnpEff produces variant calling format files to a Neo4j Graph database.

This tool does the following:
    
   * Starts up a Neo4j docker container
   * Mounts/Copies the reference data in the `/data` directory of the container
   * Gets VCF files from a provided directory 
   * Maps and loads the VCF data in Graph database
    

## Usage

**Clone this repository:**

```
$ git clone https://github.com/SANBI-SA/vcf2neo.git
$ cd vcf2neo
```
**Create a virtual environment:**

```
$ virtualenv envname
$ source envname/bin/activate
$ pip install -r requirements.txt
$ pip install --editable .
$ vcf2neo --help
$ vcf2neo init data/vcf data/db/data
```
