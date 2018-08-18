# Help
.DEFAULT_GOAL := help

.PHONY: help

build: ## Build the kubectl docker image. Ex: make VERSION=v1.10.0 build
	@docker build -t gitcoin/kubectl:$(VERSION) --build-arg VERSION=$(VERSION) --build-arg VCS_REF=$(git log --pretty=format:'%h' -n 1) --build-arg BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ") --no-cache .

push: ## Push the kubectl docker image to Docker Hub. Ex: make VERSION=v1.10.0 push
	@docker push gitcoin/kubectl:$(VERSION)
	@docker tag gitcoin/kubectl:$(VERSION) gitcoin/kubectl:latest
	@docker push gitcoin/kubectl:latest

pull: ## Pull the kubectl docker image from Docker Hub. Ex: make VERSION=v1.10.0 pull
	@docker pull gitcoin/kubectl:$(VERSION)
	@docker pull gitcoin/kubectl:latest

help: ## Display command information and usage instructions. Ex: make or make help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
