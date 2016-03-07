#!/bin/sh
#This script will be used to initialise Neo4j and run the scripts to populate the database.

echo "Hello, $USER."
echo -n 'Please provide us with you Neo4j USERNAME: '
read username
echo -n 'Please provide us with you Neo4j PASSWORD: '
read password

export NEO4J_REST_URL=http://$username:$password@localhost:7474/db/data/

# python main.py
