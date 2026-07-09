from dataclasses import dataclass
from typing import Callable

from django.db import models

from crawler import jobinja, jobvision, karboom, quera
from crawler.models import JobinjaJob, JobvisionJob, KarboomJob, QueraJob


@dataclass(frozen=True)
class SourceConfig:
    name: str
    label: str
    crawl: Callable[..., list[dict]]
    model: type[models.Model]
    fields: tuple[str, ...]

    @property
    def table_name(self) -> str:
        return self.model._meta.db_table.replace('"', "")


SOURCE_CONFIGS = {
    "jobinja": SourceConfig(
        name="jobinja",
        label="Jobinja",
        crawl=jobinja.crawl,
        model=JobinjaJob,
        fields=(
            "title",
            "company",
            "location",
            "contract",
            "salary",
            "experience",
            "published",
            "job_description",
        ),
    ),
    "quera": SourceConfig(
        name="quera",
        label="Quera",
        crawl=quera.crawl,
        model=QueraJob,
        fields=(
            "title",
            "company",
            "location",
            "experience",
            "published",
            "published_at",
            "tags",
            "job_description",
            "company_description",
        ),
    ),
    "karboom": SourceConfig(
        name="karboom",
        label="Karboom",
        crawl=karboom.crawl,
        model=KarboomJob,
        fields=(
            "title",
            "company",
            "location",
            "published",
            "salary",
            "job_description",
        ),
    ),
    "jobvision": SourceConfig(
        name="jobvision",
        label="Jobvision",
        crawl=jobvision.crawl,
        model=JobvisionJob,
        fields=(
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
        ),
    ),
}
