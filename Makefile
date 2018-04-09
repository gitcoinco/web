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

fix-stylelint: ## Run stylelint --fix against the project directory. Requires node, npm, and project dependencies.
	@npm run stylelint:fix

fix: fix-eslint fix-stylelint fix-isort ## Attempt to run all fixes against the project directory.

fresh: ## Completely destroy all compose assets and start compose with a fresh build.
	@docker-compose down -v; docker-compose up -d --build;

logs: ## Print and actively tail the docker compose logs.
	@docker-compose logs -f

pytest: ## Run pytest (Backend)
	@docker-compose exec web pytest -p no:ethereum

stylelint: ## Run stylelint against the project directory. Requires node, npm, and project dependencies.
	@npm run stylelint

tests: pytest eslint stylelint ## Run the full test suite.

migrate: ## Migrate the database schema with the latest unapplied migrations.
	@docker-compose exec web python3 app/manage.py migrate

migrations: ## Generate migration files for schema changes.
	@docker-compose exec web python3 app/manage.py makemigrations

compilemessages: ## Execute compilemessages for translations on the web container.
	@docker-compose exec web python3 app/manage.py compilemessages

makemessages: ## Execute makemessages for translations on the web container.
	@docker-compose exec web python3 app/manage.py makemessages

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
