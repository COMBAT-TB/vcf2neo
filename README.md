# **vcf2neo**
A tool to import variant calling format files to a Neo4j Graph database

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
