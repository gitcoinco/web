# Help
.DEFAULT_GOAL := help

.PHONY: help

compress-images: ## Compress and optimize images throughout the repository. Requires optipng, svgo, and jpeg-recompress.
	@./scripts/compress_images.bash

eslint: ## Run eslint against the project directory. Requires node, npm, and project dependencies.
	@npm run eslint

fix-eslint: ## Run eslint --fix against the project directory. Requires node, npm, and project dependencies.
	@npm run eslint:fix

fix-isort: ## Run isort against python files in the project directory.
	@docker-compose exec web isort -rc --atomic .

fix: fix-eslint fix-isort ## Attempt to run all fixes against the project directory.

fresh: ## Completely destroy all compose assets and start compose with a fresh build.
	@docker-compose down -v; docker-compose up -d --build;

logs: ## Print and actively tail the docker compose logs.
	@docker-compose logs -f

pytest: ## Run pytest (Backend)
	@docker-compose exec web pytest -p no:ethereum

tests: pytest eslint ## Run the full test suite.

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
