FROM python:3.6-slim-stretch
ENV PYTHONUNBUFFERED 1
ENV C_FORCE_ROOT true
RUN mkdir /code && \
    apt-get update && \
    apt-get install build-essential -y && \
    apt-get install -y --no-install-recommends apt-utils && \
    apt-get install -y --no-install-recommends pgtop tk-dev python3-tk libsecp256k1-dev libsecp256k1-0 gettext graphviz libgraphviz-dev wget git dos2unix gcc libc6-dev libc-dev libssl-dev make automake libtool autoconf pkg-config libffi-dev libgdal-dev gdal-bin libgdal20 python3-gdal && \
    pip install --upgrade pip wheel setuptools && \
    pip3 install dumb-init && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --recursive https://github.com/maxmind/libmaxminddb.git && \
    cd libmaxminddb && \
    ./bootstrap && \
    ./configure && \
    make && \
    make check && \
    make install && \
    echo /usr/local/lib  >> /etc/ld.so.conf.d/local.conf && \
    ldconfig

# GeoIP2 Data Files
RUN mkdir -p /usr/share/GeoIP/ && \
    wget http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz && \
    wget http://geolite.maxmind.com/download/geoip/database/GeoLite2-Country.mmdb.gz && \
    gunzip GeoLite2-City.mmdb.gz && \
    gunzip GeoLite2-Country.mmdb.gz && \
    mv *.mmdb /usr/share/GeoIP/

WORKDIR /code
COPY requirements/ /code/

RUN pip install -r test.txt
ADD . /code/

RUN dos2unix /code/bin/docker-command.bash && \
    dos2unix /code/bin/celery/worker.bash && \
    apt-get purge -y --auto-remove dos2unix wget gcc tk-dev libc6-dev libc-dev libssl-dev make automake libtool autoconf pkg-config libffi-dev apt-utils

ENTRYPOINT ["/usr/local/bin/dumb-init", "--"]
CMD ["bash", "/code/bin/docker-command.bash"]

ARG BUILD_DATE
ARG VCS_REF
ARG VERSION="NA"
LABEL org.label-schema.build-date=$BUILD_DATE \
    org.label-schema.name="Gitcoin Web" \
    org.label-schema.description="Grow Open Source" \
    org.label-schema.url="https://gitcoin.co" \
    org.label-schema.vcs-ref=$VCS_REF \
    org.label-schema.vcs-url="https://github.com/gitcoinco/web/" \
    org.label-schema.vendor="Gitcoin" \
    org.label-schema.version=$VERSION \
    org.label-schema.schema-version="1.0"
