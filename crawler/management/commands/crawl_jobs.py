import logging

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from crawler.sources import SOURCE_CONFIGS, SourceConfig


class Command(BaseCommand):
    help = "Crawl jobs and sync them into source-specific tables."

    def add_arguments(self, parser):
        parser.add_argument(
            "source",
            nargs="?",
            choices=[*SOURCE_CONFIGS.keys(), "all"],
            default="all",
            help="Crawler source to run.",
        )
        parser.add_argument(
            "--max-pages",
            type=int,
            default=2,
            help="Maximum pages for crawlers that support pagination.",
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=2.0,
            help="Delay in seconds between crawler requests.",
        )
        parser.add_argument(
            "--replace",
            action="store_true",
            help="Delete selected table rows before inserting the latest crawl result.",
        )
        parser.add_argument(
            "--prune",
            action="store_true",
            help="Delete selected table rows whose URLs were not seen in this crawl.",
        )
        parser.add_argument(
            "--fail-fast",
            action="store_true",
            help="Stop at the first source failure instead of continuing.",
        )

    def handle(self, *args, **options):
        self.validate_options(options)
        self.configure_logging(options["verbosity"])

        failures = []
        configs = self.get_selected_configs(options["source"])

        for config in configs:
            try:
                self.stdout.write(f"{config.name}: crawling...")
                jobs = config.crawl(
                    max_pages=options["max_pages"],
                    delay_seconds=options["delay"],
                )
                created_count, updated_count, deleted_count = self.sync_jobs(
                    config=config,
                    jobs=jobs,
                    replace=options["replace"],
                    prune=options["prune"],
                )
            except Exception as exc:
                failures.append((config.name, exc))
                self.stderr.write(self.style.ERROR(f"{config.name}: failed: {exc}"))
                if options["fail_fast"]:
                    raise CommandError(f"{config.name}: failed: {exc}") from exc
                continue

            if not jobs:
                self.stdout.write(
                    self.style.WARNING(f"{config.name}: crawler returned no jobs.")
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f"{config.table_name}: {created_count} created, "
                    f"{updated_count} updated, {deleted_count} deleted."
                )
            )

        if failures:
            names = ", ".join(name for name, _ in failures)
            raise CommandError(f"{len(failures)} crawler(s) failed: {names}")

    def get_selected_configs(self, source):
        if source == "all":
            return SOURCE_CONFIGS.values()
        return [SOURCE_CONFIGS[source]]

    def validate_options(self, options) -> None:
        if options["max_pages"] < 1:
            raise CommandError("--max-pages must be at least 1.")
        if options["delay"] < 0:
            raise CommandError("--delay cannot be negative.")

    def configure_logging(self, verbosity: int) -> None:
        level = logging.INFO if verbosity >= 2 else logging.WARNING
        logger = logging.getLogger("crawler")
        logger.setLevel(level)
        logger.propagate = False

        if not logger.handlers:
            logger.addHandler(logging.StreamHandler(self.stderr))

        for handler in logger.handlers:
            handler.setLevel(level)

    @transaction.atomic
    def sync_jobs(
        self,
        *,
        config: SourceConfig,
        jobs: list[dict],
        replace: bool,
        prune: bool,
    ):
        jobs = self.dedupe_jobs(jobs)
        urls = [job["url"] for job in jobs]
        deleted_count = 0

        if not jobs:
            return 0, 0, 0

        if replace:
            deleted_count += self.delete_model_jobs(config.model)

        existing_urls = set(
            config.model.objects.filter(url__in=urls).values_list("url", flat=True)
        )

        if jobs:
            config.model.objects.bulk_create(
                [self.build_row(config, job) for job in jobs],
                update_conflicts=True,
                unique_fields=["url"],
                update_fields=list(config.fields),
            )

        if prune and urls and not replace:
            deleted_count += self.delete_stale_jobs(config.model, urls)

        created_count = len(set(urls) - existing_urls)
        updated_count = len(set(urls) & existing_urls)
        return created_count, updated_count, deleted_count

    def dedupe_jobs(self, jobs: list[dict]) -> list[dict]:
        deduped = []
        seen_urls = set()

        for job in jobs:
            url = job.get("url")
            title = job.get("title")
            if not url or not title or url in seen_urls:
                continue

            seen_urls.add(url)
            deduped.append(job)

        return deduped

    def build_row(self, config: SourceConfig, job: dict):
        return config.model(
            url=job["url"],
            **{field: job.get(field) or "" for field in config.fields},
        )

    def delete_model_jobs(self, model) -> int:
        deleted_count, _ = model.objects.all().delete()
        return deleted_count

    def delete_stale_jobs(self, model, urls: list[str]) -> int:
        deleted_count, _ = model.objects.exclude(url__in=urls).delete()
        return deleted_count
