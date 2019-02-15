# Build Image
FROM alpine:3.8 as alpine
ARG VERSION=v1.12.3
WORKDIR /
RUN apk add -U --no-cache curl ca-certificates && \
    curl -L "https://storage.googleapis.com/kubernetes-release/release/$VERSION/bin/linux/amd64/kubectl" -o /usr/local/bin/kubectl && \
    chmod +x /usr/local/bin/kubectl
# Release Image
FROM scratch
ARG VERSION=v1.12.3
ARG VCS_REF
ARG BUILD_DATE
COPY --from=alpine /usr/local/bin/kubectl /bin/kubectl
LABEL org.label-schema.build-date=$BUILD_DATE \
    org.label-schema.name="Kubectl" \
    org.label-schema.description="Kubectl latest stable binary wrapped in a scratch image." \
    org.label-schema.url="https://gitcoin.co" \
    org.label-schema.vcs-ref=$VCS_REF \
    org.label-schema.vcs-url="https://github.com/gitcoinco/web/ops/images/kubectl" \
    org.label-schema.vendor="Gitcoin" \
    org.label-schema.version=$VERSION \
    org.label-schema.schema-version="1.0"
ENTRYPOINT ["/bin/kubectl"]
CMD ["help"]
