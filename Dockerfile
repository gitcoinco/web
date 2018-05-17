FROM python:3.6-slim-stretch
ENV PYTHONUNBUFFERED 1
RUN mkdir /code && \
    apt-get update && \
    apt-get install build-essential -y && \
    apt-get install -y --no-install-recommends apt-utils && \
    apt-get install -y --no-install-recommends libsecp256k1-dev libsecp256k1-0 gettext graphviz libgraphviz-dev wget git dos2unix gcc libc6-dev libc-dev libssl-dev make automake libtool autoconf pkg-config libffi-dev libgdal-dev gdal-bin libgdal20 python3-gdal && \
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
COPY bin/docker-command.bash /bin/docker-command.bash
RUN dos2unix /bin/docker-command.bash && \
    apt-get purge -y --auto-remove dos2unix wget gcc libc6-dev libc-dev libssl-dev make automake libtool autoconf pkg-config libffi-dev apt-utils
ENTRYPOINT ["/usr/local/bin/dumb-init", "--"]
CMD ["bash", "/bin/docker-command.bash"]
RUN apt-get update && \
    apt-get install -y tk-dev python3-tk
