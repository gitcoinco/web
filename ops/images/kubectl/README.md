# Kubectl Docker Image

This image is based on `scratch`.

Usage:

```shell
docker run --rm -it -e KUBE_CA_CERT=<KUBE_CA_CERT> -e KUBE_ENDPOINT=<KUBE_ENDPOINT> -e KUBE_ADMIN_CERT=<KUBE_ADMIN_CERT> -e KUBE_ADMIN_KEY=<KUBE_ADMIN_KEY> -e KUBE_USERNAME=<KUBE_USERNAME> get pod
```
