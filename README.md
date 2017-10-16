# COMBAT_TB_MODEL

COMBAT-TB Graph Model, a [Chado](https://github.com/GMOD/Chado) -derived graph model.

## Overview

The COMBAT-TB Graph model is based on three Chado Modules:

* CV
* Sequence
* Publication

A diagram depicting the Graph model can be found [here,](docs/chado_graph_model_draft.jpg) with the accompanying documentation [here](docs/genome_annotation_model.md).

## Usage

### With the Docker engine:

Pull and run the [neo4j docker image](https://hub.docker.com/_/neo4j/):

```
$ docker run -d \
    -p 7687:7687 \
    -p 7474:7474 \
    -e NEO4J_AUTH=none \
    --name ctbmodel \
    -v=$HOME/neo4j/data:/data \
    neo4j:3.0.4
```

Clone this repository:

```
$ git clone git@github.com:SANBI-SA/combat_tb_model.git
$ cd combat_tb_model
```

Create a virtual environment:

```
$ virtualenv envname
$ source envname/bin/activate
$ pip install -r requirements.txt
$ python main.py
```
*Point your browser at [http://localhost:7474](http://localhost:7474) .*

### With `docker-compose`, assuming you have `docker-compose` installed
```
$ docker-compose up -d
```
