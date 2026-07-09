from dataclasses import dataclass
from datetime import datetime

from crawler.sources import SOURCE_CONFIGS, SourceConfig

DEFAULT_LIMIT = 10
MAX_LIMIT = 50
PER_SOURCE_MULTIPLIER = 3
NORMALIZE_TRANSLATION = str.maketrans(
    {
        "ي": "ی",
        "ى": "ی",
        "ك": "ک",
        "ة": "ه",
        "ۀ": "ه",
    }
)
RANKED_FIELDS = (
    ("title", 100),
    ("company", 45),
    ("tags", 35),
    ("industry", 30),
    ("work_type", 25),
    ("location", 20),
    ("experience", 15),
    ("salary", 10),
    ("job_description", 5),
    ("company_description", 4),
)


@dataclass(frozen=True)
class SearchResult:
    id: int
    source: str
    source_label: str
    title: str
    company: str
    location: str
    published: str
    url: str
    score: int
    updated_at: datetime
    salary: str = ""
    experience: str = ""
    contract: str = ""
    work_type: str = ""
    industry: str = ""
    tags: str = ""
    benefits: str = ""
    job_description: str = ""
    company_description: str = ""

    @property
    def subtitle(self) -> str:
        parts = [self.company, self.location, self.source_label]
        return " | ".join(part for part in parts if part)

    @property
    def button_text(self) -> str:
        company = f" - {self.company}" if self.company else ""
        return f"{self.title}{company}"

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "source": self.source,
            "source_label": self.source_label,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "published": self.published,
            "url": self.url,
            "score": self.score,
            "updated_at": self.updated_at,
            "salary": self.salary,
            "experience": self.experience,
            "contract": self.contract,
            "work_type": self.work_type,
            "industry": self.industry,
            "tags": self.tags,
            "benefits": self.benefits,
            "job_description": self.job_description,
            "company_description": self.company_description,
            "subtitle": self.subtitle,
            "button_text": self.button_text,
        }


def search_jobs(query: str, limit: int = DEFAULT_LIMIT) -> list[dict]:
    normalized_query = normalize_query(query)
    limit = normalize_limit(limit)
    if not normalized_query or limit <= 0:
        return []

    terms = normalized_query.split()
    results = []

    for config in SOURCE_CONFIGS.values():
        results.extend(
            search_source(config, query=normalized_query, terms=terms, limit=limit)
        )

    results.sort(
        key=lambda result: (result.score, result.updated_at),
        reverse=True,
    )
    return [result.as_dict() for result in results[:limit]]


def search_source(
    config: SourceConfig,
    *,
    query: str,
    terms: list[str],
    limit: int,
) -> list[SearchResult]:
    per_source_limit = max(limit * PER_SOURCE_MULTIPLIER, limit)
    jobs = config.model.objects.search(query)[:per_source_limit]

    results = []
    for job in jobs:
        score = score_job(job, terms)
        if score <= 0:
            continue
        results.append(serialize_job(config, job, score))

    return results


def serialize_job(config: SourceConfig, job, score: int) -> SearchResult:
    return SearchResult(
        id=job.id,
        source=config.name,
        source_label=config.label,
        title=job.title,
        company=job.company,
        location=job.location,
        published=job.published,
        url=job.url,
        score=score,
        updated_at=job.updated_at,
        salary=getattr(job, "salary", ""),
        experience=getattr(job, "experience", ""),
        contract=getattr(job, "contract", ""),
        work_type=getattr(job, "work_type", ""),
        industry=getattr(job, "industry", ""),
        tags=getattr(job, "tags", ""),
        benefits=getattr(job, "benefits", ""),
        job_description=getattr(job, "job_description", ""),
        company_description=getattr(job, "company_description", ""),
    )


def get_job(source: str, job_id: int | str) -> dict | None:
    config = SOURCE_CONFIGS.get(source)
    if not config:
        return None

    try:
        job = config.model.objects.get(id=job_id)
    except (config.model.DoesNotExist, ValueError, TypeError):
        return None

    return serialize_job(config, job, score=0).as_dict()


def score_job(job, terms: list[str]) -> int:
    score = 0

    for field, weight in get_ranked_fields(job).items():
        value = normalize_query(getattr(job, field, ""))
        if not value:
            continue

        score += score_value(value, terms, weight)

    return score


def score_value(value: str, terms: list[str], weight: int) -> int:
    matches = sum(1 for term in terms if term in value)
    if not matches:
        return 0

    score = matches * weight
    if all(term in value for term in terms):
        score += weight
    if value.startswith(" ".join(terms)):
        score += weight
    return score


def get_ranked_fields(job) -> dict[str, int]:
    model_fields = {field.name for field in job._meta.fields}
    return {field: weight for field, weight in RANKED_FIELDS if field in model_fields}


def normalize_query(value: str | None) -> str:
    return " ".join((value or "").translate(NORMALIZE_TRANSLATION).casefold().split())


def normalize_limit(limit: int | str | None) -> int:
    try:
        limit = int(limit or DEFAULT_LIMIT)
    except (TypeError, ValueError):
        return DEFAULT_LIMIT
    return min(max(limit, 0), MAX_LIMIT)
