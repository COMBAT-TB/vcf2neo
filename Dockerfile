FROM python:2.7-alpine
MAINTAINER Thoba Lose "thoba@sanbi.ac.za"
LABEL Name=vcf2neo Version="0.1"
RUN apk update \
    && apk upgrade\
    && mkdir -p /code/data \
    && pip install -U pip
RUN apk add wget linux-headers musl-dev gcc
RUN wget "https://drive.google.com/uc?export=download&id=0B5cdXx4b_kIyaDZGWEtBZF85TEU" \
    -O vcf.tar.bz2
RUN tar xvfj vcf.tar.bz2
RUN mv vcf refvcf
COPY requirements.txt /code
RUN pip install -r /code/requirements.txt

COPY . /code
WORKDIR /code
RUN pip install --editable .
CMD ["vcf2neo" ,"init", "-D", "/refvcf", "zahra"]
