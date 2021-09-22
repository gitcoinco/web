FROM ubuntu:18.04

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV DEBIAN_FRONTEND=noninteractive

ARG PACKAGES="libpq-dev libxml2 libxslt1-dev libfreetype6 libjpeg-dev libmaxminddb-dev bash git tar gzip inkscape libmagic-dev"
ARG BUILD_DEPS="gcc g++ curl postgresql libxml2-dev libxslt-dev libfreetype6 libffi-dev libjpeg-dev autoconf automake libtool make dos2unix libvips libvips-dev"
ARG CHROME_DEPS="fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 libcairo2 libcups2 libcurl3-gnutls libdrm2 libexpat1 libgbm1 libglib2.0-0 libnspr4 libgtk-3-0 libpango-1.0-0 libx11-6 libxcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxkbcommon0 libxrandr2 libxshmfence1 xdg-utils"
ARG CYPRESS_DEPS="libgtk2.0-0 libgbm-dev libnotify-dev libgconf-2-4 libnss3 libxss1 libxtst6 xauth xvfb"

# Inkscape
RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:inkscape.dev/stable
RUN apt-get update

# Install general dependencies.
RUN apt-get install -y $PACKAGES
RUN apt-get update --fix-missing
RUN apt-get install -y $BUILD_DEPS --fix-missing

# Install google chrome for cypress testing
WORKDIR /usr/src
RUN apt-get update && apt-get install -y wget
RUN wget "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
RUN apt-get install -y $CHROME_DEPS
RUN dpkg -i google-chrome-stable_current_amd64.deb

# Install cypress dependencies
RUN apt-get install -y $CYPRESS_DEPS

RUN apt-get install -y libsodium-dev

RUN add-apt-repository universe
RUN apt-get update
RUN apt-get install -y python3-pip

WORKDIR /code

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

RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN apt-get update
RUN apt-get install -y yarn
RUN yarn global add n
RUN n stable

EXPOSE 9222
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
