.DEFAULT_GOAL := help

help: ## Show commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

postgres: ## Start PostgreSQL
	docker compose --env-file docker/.env -f docker/docker-compose.yaml up -d postgres

migrate: ## Run migrations
	.venv/bin/python manage.py migrate

crawl-jobinja: ## Crawl 2 Jobinja pages into PostgreSQL
	.venv/bin/python manage.py crawl_jobs jobinja --max-pages 2 --delay 2

crawl-quera: ## Crawl 2 Quera pages into PostgreSQL
	.venv/bin/python manage.py crawl_jobs quera --max-pages 2 --delay 2
