FROM ubuntu:18.04

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV DEBIAN_FRONTEND=noninteractive

ARG PACKAGES="libpq-dev libxml2 libxslt1-dev libfreetype6 libjpeg-dev libmaxminddb-dev bash git tar gzip inkscape libmagic-dev"
ARG BUILD_DEPS="gcc g++ postgresql libxml2-dev libxslt-dev libfreetype6 libffi-dev libjpeg-dev autoconf automake libtool make dos2unix libvips libvips-dev"
WORKDIR /code

# Inkscape
RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:inkscape.dev/stable
RUN apt-get update

# Install general dependencies.
RUN apt-get install -y $PACKAGES
RUN apt-get update
RUN apt-get install -y $BUILD_DEPS

RUN apt-get install -y wget
RUN apt-get install -y libsodium-dev

RUN apt-get install -y python3-pip

COPY dist/* ./

# GeoIP2 Data Files
RUN mkdir -p /usr/share/GeoIP/ && \
    gunzip GeoLite2-City.mmdb.tar.gz && \
    gunzip GeoLite2-Country.mmdb.tar.gz && \
    tar -xvf GeoLite2-City.mmdb.tar && \
    tar -xvf GeoLite2-Country.mmdb.tar && \
    mv GeoLite2-City_20200128/*.mmdb /usr/share/GeoIP/ && \
    mv GeoLite2-Country_20200128/*.mmdb /usr/share/GeoIP/

# Upgrade package essentials.
RUN pip3 install --upgrade pip==20.0.2 setuptools wheel dumb-init pipenv

COPY requirements/ /code/
RUN apt-get update
RUN apt-get install -y build-essential libssl-dev python3-dev
RUN apt-get install -y libsecp256k1-dev
RUN pip3 install --upgrade -r test.txt

COPY bin/docker-command.bash /bin/docker-command.bash
RUN dos2unix /bin/docker-command.bash

COPY app/ /code/app/

ENTRYPOINT ["/usr/local/bin/dumb-init", "--"]
CMD ["bash", "/bin/docker-command.bash"]

ARG BUILD_DATETIME
ARG SHA1

LABEL co.gitcoin.description="Gitcoin web application image" \
    co.gitcoin.documentation="https://github.com/gitcoinco/web/blob/master/docs/RUNNING_LOCALLY_DOCKER.md" \
    co.gitcoin.licenses="AGPL-3.0" \
    co.gitcoin.image.revision=$SHA1 \
    co.gitcoin.image.vendor="Gitcoin" \
    co.gitcoin.image.source="https://github.com/gitcoinco/web" \
    co.gitcoin.image.title="Gitcoin Web" \
    co.gitcoin.image.created=$BUILD_DATETIME
