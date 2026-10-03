FROM node:16

RUN curl -fsSL https://get.pulumi.com | sh -s -- --version 3.95.0
ENV PATH="/root/.pulumi/bin:${PATH}"
