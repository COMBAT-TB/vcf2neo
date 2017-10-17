FROM python:2.7
MAINTAINER Thoba Lose "thoba@sanbi.ac.za"

RUN apt-get update -y --fix-missing && apt-get upgrade -y
RUN mkdir /code && \
    pip install -U pip
COPY requirements.txt /code
RUN pip install -r /code/requirements.txt
COPY . /code
WORKDIR /code
CMD ["python", "main.py"]
