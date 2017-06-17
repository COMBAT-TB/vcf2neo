FROM python:2.7-alpine
MAINTAINER Thoba Lose "thoba@sanbi.ac.za"
LABEL Name=vcf2neo-dc Version="0.1"

# RUN wget "https://zenodo.org/record/252101/files/data.tar.bz2" \
#     -O data.tar.bz2
# RUN tar xvfj data.tar.bz2
RUN apk update && apk add ca-certificates curl && update-ca-certificates
RUN curl -L 'https://drive.google.com/uc?export=download&id=0By2-i8xoBou_RURfaUR2bXhoSEU' >COMBAT_TB_db.tar.bz2
COPY sha256.txt .
RUN sha256sum -c sha256.txt 
RUN mkdir /data
# COPY COMBAT_TB_db.tar.bz2 .
RUN tar xvfj COMBAT_TB_db.tar.bz2; rm COMBAT_TB_db.tar.bz2; cp -r databases /data/
# COPY data /data
VOLUME /data
