FROM python:2.7
MAINTAINER Thoba Lose "thoba@sanbi.ac.za"

RUN wget "https://zenodo.org/record/252101/files/data.tar.bz2" \
    -O data.tar.bz2
RUN tar xvfj data.tar.bz2

VOLUME /data
