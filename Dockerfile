FROM python:3.7-alpine3.8

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ARG PACKAGES="postgresql-libs libxml2 libxslt freetype libffi jpeg libmaxminddb bash git tar gzip inkscape libmagic"
ARG BUILD_DEPS="gcc g++ postgresql-dev libxml2-dev libxslt-dev freetype-dev libffi-dev jpeg-dev linux-headers autoconf automake libtool make dos2unix"
WORKDIR /code

# Install general dependencies.
RUN apk add --no-cache --update $PACKAGES && \
    apk add --no-cache --update --repository http://dl-cdn.alpinelinux.org/alpine/edge/community/ vips && \
    apk add --no-cache --update --virtual .builder $BUILD_DEPS

# GeoIP2 Data Files
RUN mkdir -p /usr/share/GeoIP/ && \
    wget http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz && \
    wget http://geolite.maxmind.com/download/geoip/database/GeoLite2-Country.mmdb.gz && \
    gunzip GeoLite2-City.mmdb.gz && \
    gunzip GeoLite2-Country.mmdb.gz && \
    mv *.mmdb /usr/share/GeoIP/

# Upgrade package essentials.
RUN pip3 install --upgrade pip setuptools wheel dumb-init pipenv

COPY requirements/ /code/
RUN pip3 install --upgrade -r test.txt

COPY bin/docker-command.bash /bin/docker-command.bash
RUN dos2unix /bin/docker-command.bash && \
    apk del .builder

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
