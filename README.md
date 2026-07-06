# telegram-karyabi-bot

Simple Django crawler that stores Jobinja jobs in PostgreSQL.

## Run

```bash
docker compose --env-file docker/.env -f docker/docker-compose.yaml up -d postgres
.venv/bin/python manage.py migrate
.venv/bin/python manage.py crawl_jobs jobinja --max-pages 2 --delay 2
.venv/bin/python manage.py crawl_jobs quera --max-pages 2 --delay 2
```
