FROM python:3-alpine
LABEL MAINTAINER="thoba@sanbi.ac.za"

RUN apk update \
    && apk upgrade \
    && mkdir /code \
    && apk add --no-cache py-pip git build-base libxml2-dev libxslt-dev

COPY requirements.txt /code

RUN pip install -r /code/requirements.txt

COPY . /code
WORKDIR /code

RUN pip install -e .

ENTRYPOINT ["./docker-entrypoint.sh"]
