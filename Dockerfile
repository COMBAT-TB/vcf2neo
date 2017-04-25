FROM python:2.7-alpine
MAINTAINER Thoba Lose "thoba@sanbi.ac.za"
LABEL Name=vcf2neo Version="0.1"
RUN apk update \
    && apk upgrade \
    && mkdir -p /code/data \
    && pip install -U pip
RUN apk add wget linux-headers musl-dev gcc
RUN wget "https://doc-00-5c-docs.googleusercontent.com/docs/securesc/ha0ro937gcuc7l7deffksulhg5h7mbp1/3ovp6p4bpil90k42tpe74ndqnrfcidfb/1493107200000/07482904762578063898/*/0By2-i8xoBou_Wl9yUXZIWXRIeFU?e=download" \
    -O vcf.tar.bz2
RUN echo '351338cfccc9326764abf58a1dd8915d  vcf2neo.tar.bz2'|md5sum -c
RUN tar xvfj vcf.tar.bz2
RUN mv vcf refvcf
COPY requirements.txt /code
RUN pip install -Ur /code/requirements.txt

COPY . /code
WORKDIR /code
RUN pip install --editable .
CMD ["vcf2neo" ,"init", "-D", "/refvcf", "zahra"]
