# telegram-karyabi-bot

Simple Django crawler that stores jobs from Jobinja, Quera, Karboom, and Jobvision in separate PostgreSQL tables.

## Run

```bash
cp .env.example .env
docker compose --env-file .env -f docker/docker-compose.yaml up -d postgres
.venv/bin/python manage.py migrate
.venv/bin/python manage.py crawl_jobs jobinja --max-pages 2 --delay 2
.venv/bin/python manage.py crawl_jobs quera --max-pages 2 --delay 2
.venv/bin/python manage.py crawl_jobs karboom --max-pages 1 --delay 2
.venv/bin/python manage.py crawl_jobs jobvision --max-pages 1 --delay 2
.venv/bin/python manage.py crawl_jobs all --max-pages 1 --delay 2
```

## Dev data commands

```bash
# Replace all currently crawled rows in the selected source tables with a fresh dev crawl.
.venv/bin/python manage.py crawl_jobs all --max-pages 1 --delay 2 --replace

# Delete rows from all source tables, or pass one source such as jobinja.
.venv/bin/python manage.py clear_jobs all

# For a full scheduled crawl, use enough pages and prune stale URLs after a successful run.
.venv/bin/python manage.py crawl_jobs all --max-pages 5 --delay 2 --prune

# Show crawler page/detail progress while debugging.
.venv/bin/python manage.py crawl_jobs all --max-pages 1 --delay 2 -v 2
```

`crawl_jobs all` continues to the next website if one source fails. It exits with an error after the successful sources are saved, so schedulers can still detect a partial failure. Use `--fail-fast` when you want the command to stop on the first broken source.

Empty crawls do not delete existing rows, even with `--replace`; use `clear_jobs` when you intentionally want to wipe data.

## Later scheduling

For production, run the crawl command every two hours from cron, systemd, Celery beat, or another scheduler:

```cron
0 */2 * * * cd /path/to/telegram-karyabi-bot && .venv/bin/python manage.py crawl_jobs all --max-pages 5 --delay 2 --prune
```

Jobs are stored in separate source tables:

- `crawler.jobinja`
- `crawler.quera`
- `crawler.karboom`
- `crawler.jobvision`

For the Telegram bot, use the service helper to search all four tables and return merged results:

```python
from crawler.services import search_jobs

jobs = search_jobs("Software Engineer", limit=10)
```

Each result is a dict ready for Telegram rendering:

```python
{
    "source": "jobinja",
    "source_label": "Jobinja",
    "title": "Software Engineer",
    "company": "Example Co",
    "location": "Tehran",
    "published": "today",
    "url": "https://...",
    "score": 250,
    "updated_at": datetime,
    "subtitle": "Example Co | Tehran | Jobinja",
    "button_text": "Software Engineer - Example Co",
}
```

Search normalizes Arabic/Persian character variants, searches all four source tables, ranks title matches highest, and caps `limit` at 50.
