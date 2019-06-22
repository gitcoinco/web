# Help
.DEFAULT_GOAL := help

.PHONY: help

REPO_NAME := gitcoinco/web
CONTAINER_NAME := $(addsuffix _web_1, $(subst -,, $(shell pwd | xargs basename)))
SHA1 := $$(git log -1 --pretty=%h)
GIT_TAG := ${REPO_NAME}:${SHA1}
LATEST_TAG := ${REPO_NAME}:latest
CURRENT_BRANCH := $$(git symbolic-ref -q --short HEAD)
WEB_CONTAINER_ID := $$(docker inspect --format="{{.Id}}" ${CONTAINER_NAME})

autotranslate: ## Automatically translate all untranslated entries for all LOCALES in settings.py.
	@echo "Starting makemessages..."
	@docker-compose exec web python3 app/manage.py makemessages -a -d django -i node_modules -i static -i ipfs
	@echo "Starting JS makemessages..."
	@docker-compose exec web python3 app/manage.py makemessages -a -d djangojs -i node_modules -i static -i assets/v2/js/lib/ipfs-api.js
	@echo "Starting autotranslation of messages..."
	@docker-compose exec web python3 app/manage.py translate_messages -u
	# TODO: Add check for messed up python var strings.
	@echo "Starting compilemessages..."
	@docker-compose exec web python3 app/manage.py compilemessages -f
	@echo "Translation Completed!"

build: ## Build the Gitcoin Web image.
	@docker build \
		--stream \
		--pull \
		--build-arg BUILD_DATETIME=`date -u +"%Y-%m-%dT%H:%M:%SZ"` \
		--build-arg "SHA1=${SHA1}" \
		${VERSION:+--build-arg "VERSION=$VERSION"} \
		-t "${GIT_TAG}" .
	@docker tag "${GIT_TAG}" "${LATEST_TAG}"

login: ## Login to Docker Hub.
	@docker log -u "${DOCKER_USER}" -p "${DOCKER_PASS}"

push: ## Push the Docker image to the Docker Hub repository.
	@docker push "${REPO_NAME}"

collect-static: ## Collect newly added static resources from the assets directory.
	@docker-compose exec -e DJANGO_SETTINGS_MODULE="app.settings" web bash -c "cd /code/app && python3 manage.py collectstatic -i other --no-input"

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

fix-yapf: ## Run yapf against any included or newly introduced Python code.
	@docker-compose exec web yapf -i -r -e "app/**/migrations/*.py" -e "app/app/settings.py" -p app/app/ app/avatar/ app/credits/ app/dataviz/ app/enssubdomain/ app/ethos/ app/github/

fix: fix-eslint fix-stylelint fix-isort fix-yapf ## Attempt to run all fixes against the project directory.

fresh: ## Completely destroy all compose assets and start compose with a fresh build.
	@docker-compose down -v; docker-compose up -d --build;

load_initial_data: ## Load initial development fixtures.
	@docker-compose exec -e DJANGO_SETTINGS_MODULE="app.settings" web python3 app/manage.py loaddata initial

logs: ## Print and actively tail the docker compose logs.
	@docker-compose logs -f

cypress: ## Open cypress testing UI
	@npx cypress open

pytest: ## Run pytest (Backend)
	@docker-compose exec -e DJANGO_SETTINGS_MODULE="app.settings" web pytest -p no:ethereum

pytest-pdb: ## Run pytest with pdb support (Backend)
	@docker-compose exec -e DJANGO_SETTINGS_MODULE="app.settings" web pytest -p no:ethereum --pdb --pdbcls=IPython.terminal.debugger:Pdb

stylelint: ## Run stylelint against the project directory. Requires node, npm, and project dependencies.
	@npm run stylelint

tests: pytest eslint stylelint ## Run the full test suite.

migrate: ## Migrate the database schema with the latest unapplied migrations.
	@docker-compose exec -e DJANGO_SETTINGS_MODULE="app.settings" web python3 app/manage.py migrate

migrations: ## Generate migration files for schema changes.
	@docker-compose exec -e DJANGO_SETTINGS_MODULE="app.settings" web python3 app/manage.py makemigrations

compilemessages: ## Execute compilemessages for translations on the web container.
	@docker-compose exec -e DJANGO_SETTINGS_MODULE="app.settings" web python3 app/manage.py compilemessages

makemessages: ## Execute makemessages for translations on the web container.
	@docker-compose exec -e DJANGO_SETTINGS_MODULE="app.settings" web python3 app/manage.py makemessages

get_ipdb_shell: ## Drop into the active Django shell for inspection via ipdb.
	@echo "Attaching to container: ($(CONTAINER_NAME)) - ($(WEB_CONTAINER_ID))"
	@docker attach $(WEB_CONTAINER_ID)

get_django_shell: ## Open a standard Django shell.
	@docker-compose exec -e DJANGO_SETTINGS_MODULE="app.settings" web python3 app/manage.py shell

get_shell_plus: ## Open a standard Django shell.
	@docker-compose exec -e DJANGO_SETTINGS_MODULE="app.settings" web python3 app/manage.py shell_plus

pgactivity: ## Run pg_activivty against the local postgresql instance.
	@docker-compose exec web scripts/pg_activity.bash

pgtop: ## Run pg_top against the local postgresql instance.
	@docker-compose exec web scripts/pg_top.bash

update_fork: ## Update the current fork master branch with upstream master.
	@echo "Updating the current fork with the Gitcoin upstream master branch..."
	@git checkout master
	@git fetch upstream
	@git merge upstream/master
	@git push origin master
	@echo "Updated!"

update_stable: ## Update the stable branch with master.
	@echo "This will alter the live state of Gitcoin."
	@echo "Have you verified your changes and wish to continue? [y/N] " && read response && [ $${response:-N} == y ]
	@git checkout master; git pull --rebase; git checkout stable; git reset --hard master;
	@echo "The stable branch has been reset. You might be prompted to enter your password."
	@echo "Force push changes to Github? [y/N] " && read response && [ $${response:-N} == y ]
	@git push origin stable --force


help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
