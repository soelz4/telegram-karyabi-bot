# telegram-karyabi-bot

Simple Django crawler that stores jobs from Jobinja, Quera, Karboom, and Jobvision in PostgreSQL.

## Run

```bash
cp .env.example .env
docker compose --env-file .env -f docker/docker-compose.yaml up -d postgres
.venv/bin/python manage.py migrate
.venv/bin/python manage.py crawl_jobs jobinja --max-pages 2 --delay 2
.venv/bin/python manage.py crawl_jobs quera --max-pages 2 --delay 2
.venv/bin/python manage.py crawl_jobs karboom --max-pages 1 --delay 2
.venv/bin/python manage.py crawl_jobs jobvision --start-page 2 --max-pages 1 --delay 2
.venv/bin/python manage.py crawl_jobs all --max-pages 1 --delay 2
```
