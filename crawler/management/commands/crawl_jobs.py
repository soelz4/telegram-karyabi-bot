from django.core.management.base import BaseCommand
from django.db import transaction

from crawler import jobinja, jobvision, karboom, quera
from crawler.models import JobinjaJob, JobvisionJob, KarboomJob, QueraJob


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
                "tags",
                "job_description",
                "company_description",
            ],
        },
        "karboom": {
            "crawl": karboom.crawl,
            "model": KarboomJob,
            "fields": [
                "title",
                "company",
                "location",
                "published",
                "salary",
                "job_description",
            ],
        },
        "jobvision": {
            "crawl": jobvision.crawl,
            "model": JobvisionJob,
            "supports_start_page": True,
            "fields": [
                "jobvision_id",
                "title",
                "company",
                "location",
                "published",
                "published_at",
                "salary",
                "experience",
                "work_type",
                "industry",
                "benefits",
                "tags",
                "job_description",
                "company_description",
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
        parser.add_argument(
            "--start-page",
            type=int,
            default=1,
            help="First page for crawlers that support explicit start pages.",
        )

    def handle(self, *args, **options):
        source = options["source"]
        selected = self.crawlers if source == "all" else {source: self.crawlers[source]}

        for name, config in selected.items():
            jobs = config["crawl"](**self.get_crawl_options(config, options))
            created_count, updated_count = self.save_jobs(config, jobs)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Saved {name} jobs to crawler.{name} "
                    f"({created_count} created, {updated_count} updated)."
                )
            )

    def get_crawl_options(self, config, options):
        crawl_options = {
            "max_pages": options["max_pages"],
            "delay_seconds": options["delay"],
        }
        if config.get("supports_start_page"):
            crawl_options["start_page"] = options["start_page"]
        return crawl_options

    @transaction.atomic
    def save_jobs(self, config, jobs):
        if not jobs:
            return 0, 0

        model = config["model"]
        fields = config["fields"]
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
