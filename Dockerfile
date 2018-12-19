FROM python:2.7-alpine
MAINTAINER Thoba Lose "thoba@sanbi.ac.za"
LABEL Name=vcf2neo Version="0.1"
RUN apk update \
    && apk upgrade \
    && apk add --no-cache wget linux-headers musl-dev gcc libffi-dev \
    libressl-dev \
    libssl-dev \
    openssl-dev \
    && mkdir -p /code/data \
    && pip install -U pip

RUN wget -O vcf.tar.bz2 'https://drive.google.com/uc?export=download&id=0By2-i8xoBou_Wl9yUXZIWXRIeFU'
RUN echo '351338cfccc9326764abf58a1dd8915d  vcf.tar.bz2'|md5sum -c
RUN tar xvfj vcf.tar.bz2
RUN mv vcf refvcf
COPY requirements.txt /code
RUN pip install -Ur /code/requirements.txt

COPY . /code
WORKDIR /code
RUN pip install --editable .
CMD ["vcf2neo" ,"load_vcf", "-D", "/refvcf", "zahra"]
