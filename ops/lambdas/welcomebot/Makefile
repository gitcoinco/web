# Help
.DEFAULT_GOAL := help

.PHONY: help

init: ## Initialize the Zappa project for our AWS Lambda function and API Gateway.
	@echo "Attempting to initialize Zappa"
	@zappa init
	@echo "Zappa initialized. Update domain_name and certificate_arn in zappa_settings.json, then run: make deploy && make certify"

deploy: ## Deploy the welcomebot project for the first time. Run this once.
	@echo "Deploying Welcomebot"
	@zappa deploy welcomebot
	@echo "Welcomebot deployed!"

update: ## Update the welcomebot project.
	@echo "Updating Welcomebot"
	@zappa update welcomebot
	@echo "Welcomebot updated!"

undeploy: ## Undeploy the welcomebot.
	@echo "Undeploying Welcomebot"
	@zappa undeploy welcomebot
	@echo "Welcomebot undeployed!"

certify: ## Certify the AWS ACM certificate and establish your CNAME for welcomebot.
	@echo "Certifying Welcomebot"
	@zappa certify welcomebot
	@echo "Welcomebot certified!"

help: ## Display command information and usage instructions. Ex: make or make help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
