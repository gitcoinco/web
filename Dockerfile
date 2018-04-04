FROM python:3.6-slim-jessie
ENV PYTHONUNBUFFERED 1
RUN mkdir /code && \
    apt-get update && \
    apt-get install -y --no-install-recommends graphviz wget git dos2unix gcc libc6-dev libc-dev libssl-dev make automake libtool autoconf pkg-config libffi-dev && \
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
RUN pip install -r dev.txt && \
    dos2unix /bin/docker-command.bash && \
    apt-get purge -y --auto-remove dos2unix wget gcc libc6-dev libc-dev libssl-dev make automake libtool autoconf pkg-config libffi-dev
ENTRYPOINT ["/usr/local/bin/dumb-init", "--"]
CMD ["bash", "/bin/docker-command.bash"]
