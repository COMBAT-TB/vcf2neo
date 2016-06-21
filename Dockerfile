FROM python:2.7
MAINTAINER Thoba Lose "thoba@sanbi.ac.za"
RUN pip install -U pip
#    && pip install Flask==0.10.1 neomodel==2.0.2

# Install miniconda to /miniconda
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh
RUN bash Miniconda-latest-Linux-x86_64.sh -p /miniconda -b
RUN rm Miniconda-latest-Linux-x86_64.sh
ENV PATH=/miniconda/bin:${PATH}
RUN conda update -y conda
RUN conda install -y gunicorn click numpy pandas patsy python-dateutil PyYAML scipy six statsmodels

ADD . /code
WORKDIR /code
ENV GALAXY_API_KEY none
##Not good practice
#ENV NEO4J_USER neo4j
#ENV NE04J_PASSWD Neo4j
#ENV NEO4J_REST_URL http://$NEO4J_USER:$NE04J_PASSWD@thoba.sanbi.ac.za:7476/db/data/
RUN pip install -r requirements.txt
#EXPOSE 5000
CMD ["python" ,"run.py"]