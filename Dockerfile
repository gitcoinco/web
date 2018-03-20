FROM python:3.6-slim-jessie
ENV PYTHONUNBUFFERED 1
RUN mkdir /code && \
    apt-get update && \
    apt-get install -y --no-install-recommends dos2unix gcc g++ libc6-dev libc-dev libssl-dev make automake libtool autoconf pkg-config libffi-dev apt-utils && \
    pip3 install dumb-init && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /code
COPY requirements/ /code/
RUN pip install -r test.txt
RUN pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.0.0/en_core_web_sm-2.0.0.tar.gz#en_core_web_sm
COPY bin/docker-command.bash /bin/docker-command.bash
RUN pip install -r dev.txt && \
    dos2unix /bin/docker-command.bash && \
    apt-get purge -y --auto-remove dos2unix gcc libc6-dev libc-dev libssl-dev make automake libtool autoconf pkg-config libffi-dev
ENTRYPOINT ["/usr/local/bin/dumb-init", "--"]
CMD ["bash", "/bin/docker-command.bash"]
