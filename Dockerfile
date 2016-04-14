FROM python:2.7
MAINTAINER Thoba Lose "thoba@sanbi.ac.za"
RUN pip install -U pip
ADD . /code
WORKDIR /code
##Not good practice
#ENV NEO4J_USER neo4j
#ENV NE04J_PASSWD Neo4j
#ENV NEO4J_REST_URL http://$NEO4J_USER:$NE04J_PASSWD@thoba.sanbi.ac.za:7476/db/data/
RUN pip install -r requirements.txt
#EXPOSE 5000
CMD ["python" ,"run.py"]