from django.core.management.base import BaseCommand
from django.db import transaction

from crawler.jobinja import crawl
from crawler.models import JobinjaJob


class Command(BaseCommand):
    help = "Crawl Jobinja and upsert jobs into crawler.jobinja."

    def add_arguments(self, parser):
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
        jobs = crawl(
            max_pages=options["max_pages"],
            delay_seconds=options["delay"],
        )
        created_count, updated_count = self.save_jobs(jobs)

        self.stdout.write(
            self.style.SUCCESS(
                f"Saved Jobinja jobs to crawler.jobinja "
                f"({created_count} created, {updated_count} updated)."
            )
        )

    @transaction.atomic
    def save_jobs(self, jobs):
        urls = [job["url"] for job in jobs]
        existing_urls = set(
            JobinjaJob.objects.filter(url__in=urls).values_list("url", flat=True)
        )
        rows = [
            JobinjaJob(
                title=job.get("title", ""),
                company=job.get("company", ""),
                location=job.get("location", ""),
                contract=job.get("contract", ""),
                salary=job.get("salary", ""),
                experience=job.get("experience", ""),
                published=job.get("published", ""),
                url=job["url"],
                job_description=job.get("job_description", ""),
            )
            for job in jobs
        ]

        JobinjaJob.objects.bulk_create(
            rows,
            update_conflicts=True,
            unique_fields=["url"],
            update_fields=[
                "title",
                "company",
                "location",
                "contract",
                "salary",
                "experience",
                "published",
                "job_description",
            ],
        )

        created_count = len(set(urls) - existing_urls)
        updated_count = len(set(urls) & existing_urls)
        return created_count, updated_count
