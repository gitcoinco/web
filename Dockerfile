FROM python:2.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD requirements-dev.txt /code/
RUN pip install -r requirements-dev.txt
ADD . /code/