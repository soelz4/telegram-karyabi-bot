from django.core.management.base import BaseCommand
from django.db import transaction

from crawler import jobinja, quera
from crawler.models import JobinjaJob, QueraJob


class Command(BaseCommand):
    help = "Crawl jobs and upsert them into PostgreSQL."

    crawlers = {
        "jobinja": {
            "crawl": jobinja.crawl,
            "model": JobinjaJob,
            "fields": [
                "title",
                "company",
                "location",
                "contract",
                "salary",
                "experience",
                "published",
                "job_description",
            ],
        },
        "quera": {
            "crawl": quera.crawl,
            "model": QueraJob,
            "fields": [
                "title",
                "company",
                "location",
                "experience",
                "published",
                "published_at",
                "job_description",
            ],
        },
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "source",
            nargs="?",
            choices=[*self.crawlers.keys(), "all"],
            default="jobinja",
            help="Crawler source to run.",
        )
        parser.add_argument(
            "--max-pages",
            type=int,
            default=2,
            help="Maximum pages for crawlers that support pagination options.",
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=2.0,
            help="Delay in seconds for crawlers that support request throttling.",
        )

    def handle(self, *args, **options):
        source = options["source"]
        selected = self.crawlers if source == "all" else {source: self.crawlers[source]}

        for name, config in selected.items():
            jobs = config["crawl"](
                max_pages=options["max_pages"],
                delay_seconds=options["delay"],
            )
            created_count, updated_count = self.save_jobs(
                config["model"],
                config["fields"],
                jobs,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Saved {name} jobs to crawler.{name} "
                    f"({created_count} created, {updated_count} updated)."
                )
            )

    @transaction.atomic
    def save_jobs(self, model, fields, jobs):
        urls = [job["url"] for job in jobs]
        existing_urls = set(
            model.objects.filter(url__in=urls).values_list("url", flat=True)
        )
        rows = [
            model(
                url=job["url"],
                **{field: job.get(field, "") for field in fields},
            )
            for job in jobs
        ]

        model.objects.bulk_create(
            rows,
            update_conflicts=True,
            unique_fields=["url"],
            update_fields=fields,
        )

        created_count = len(set(urls) - existing_urls)
        updated_count = len(set(urls) & existing_urls)
        return created_count, updated_count
