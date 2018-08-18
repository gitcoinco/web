# Help
.DEFAULT_GOAL := help

.PHONY: help

build: ## Build the job docker image. Ex: make build
	@docker build -t gitcoin/job:latest --build-arg VERSION=$(git log --pretty=format:'%h' -n 1) --build-arg VCS_REF=$(git rev-parse HEAD) --build-arg BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ") .

push: ## Push the job docker image to Docker Hub. Ex: make push
	@docker tag gitcoin/job:latest gitcoin/job:$(git log --pretty=format:'%h' -n 1)
	@docker push gitcoin/job:$(git log --pretty=format:'%h' -n 1)

pull: ## Pull the job docker image from Docker Hub. Ex: make pull
	@docker pull gitcoin/job:$(git log --pretty=format:'%h' -n 1)
	@docker pull gitcoin/job:latest

help: ## Display command information and usage instructions. Ex: make or make help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
