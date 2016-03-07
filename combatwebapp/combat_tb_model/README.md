# **combat-tb neomodel**

A Graph Model for the COMBAT-TB Project

## Usage

**Make sure [Neo4j](http://neo4j.com/download/other-releases/) is running first!**
```
$ $NEO4J_HOME/bin/neo4j status
```

**Set location of your Neo4j Database via environment variables [`NEO4J_USERNAME`, `NEO4J_PASSWORD`, `NEO4J_REST_URL`]:**

```
$ export NEO4J_USERNAME=username
$ export NEO4J_PASSWORD=password
$ export NEO4J_REST_URL=http://$NEO4J_USERNAME:$NEO4J_PASSWORD@localhost:7474/db/data/
```

**or**
```
$ chmod +x run.sh && ./run.sh
``` 
