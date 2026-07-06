.DEFAULT_GOAL := help

help: ## Show commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

postgres: ## Start PostgreSQL
	docker compose --env-file .env -f docker/docker-compose.yaml up -d postgres

migrate: ## Run migrations
	.venv/bin/python manage.py migrate

crawl-jobinja: ## Crawl 2 Jobinja pages into PostgreSQL
	.venv/bin/python manage.py crawl_jobs jobinja --max-pages 2 --delay 2

crawl-quera: ## Crawl 2 Quera pages into PostgreSQL
	.venv/bin/python manage.py crawl_jobs quera --max-pages 2 --delay 2

crawl-karboom: ## Crawl 1 Karboom page into PostgreSQL
	.venv/bin/python manage.py crawl_jobs karboom --max-pages 1 --delay 2

crawl-jobvision: ## Crawl Jobvision page 2 into PostgreSQL
	.venv/bin/python manage.py crawl_jobs jobvision --start-page 2 --max-pages 1 --delay 2

crawl-all: ## Crawl one page from every source into PostgreSQL
	.venv/bin/python manage.py crawl_jobs all --max-pages 1 --delay 2
