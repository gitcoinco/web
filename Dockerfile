FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /code && \
    apt-get update && \
    apt-get install -y --no-install-recommends gcc libc6-dev libc-dev libssl-dev && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY requirements-dev.txt /code/
RUN pip install -r requirements-dev.txt && \
    apt-get purge -y --auto-remove gcc libc6-dev libc-dev libssl-dev
