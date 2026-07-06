# telegram-karyabi-bot

Simple Django crawler that stores Jobinja jobs in PostgreSQL.

## Run

```bash
docker compose --env-file docker/.env -f docker/docker-compose.yaml up -d postgres
.venv/bin/python manage.py migrate
.venv/bin/python manage.py crawl_jobs --max-pages 2 --delay 2
```
