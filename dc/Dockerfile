FROM alpine:latest
LABEL Maintainer="thoba@sanbi.ac.za"

RUN apk update \
    && apk upgrade \
    && mkdir -p /data/guides \
    && apk add --no-cache openssl wget

ENV DB_VERSION="3258008"

RUN wget "https://zenodo.org/record/${DB_VERSION}/files/neodb-db-data.tar.bz2" \
    -O neodb_db_data.tar.bz2 \
    && tar xvfj neodb_db_data.tar.bz2 \
    && rm -rf neodb_db_data.tar.bz2 \
    && cp -r databases /data/ \
    && wget https://raw.githubusercontent.com/COMBAT-TB/combat-tb-neodb/master/dc/guides/combattb_neodb.html \
    -P /data/guides/

VOLUME /data
