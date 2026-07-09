from django.db import models
from django.db.models import Q


SEARCH_FIELDS = (
    "title",
    "company",
    "location",
    "tags",
    "industry",
    "work_type",
    "salary",
    "experience",
    "job_description",
    "company_description",
)


class JobQuerySet(models.QuerySet):
    def search(self, query: str):
        query = " ".join((query or "").split())
        if not query:
            return self

        fields = self.get_search_fields()
        filters = Q()
        for term in query.split():
            term_filters = Q()
            for field in fields:
                term_filters |= Q(**{f"{field}__icontains": term})
            filters &= term_filters
        return self.filter(filters)

    def get_search_fields(self) -> list[str]:
        model_fields = {field.name for field in self.model._meta.fields}
        return [field for field in SEARCH_FIELDS if field in model_fields]


class JobinjaJob(models.Model):
    title = models.CharField(max_length=500)
    company = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    contract = models.CharField(max_length=255, blank=True)
    salary = models.CharField(max_length=255, blank=True)
    experience = models.CharField(max_length=255, blank=True)
    published = models.CharField(max_length=255, blank=True)
    url = models.URLField(max_length=1000, unique=True)
    job_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = JobQuerySet.as_manager()

    class Meta:
        db_table = '"crawler"."jobinja"'
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class QueraJob(models.Model):
    title = models.CharField(max_length=500)
    company = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    experience = models.CharField(max_length=255, blank=True)
    published = models.CharField(max_length=255, blank=True)
    published_at = models.CharField(max_length=255, blank=True)
    url = models.URLField(max_length=1000, unique=True)
    tags = models.TextField(blank=True)
    job_description = models.TextField(blank=True)
    company_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = JobQuerySet.as_manager()

    class Meta:
        db_table = '"crawler"."quera"'
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class KarboomJob(models.Model):
    title = models.CharField(max_length=500)
    company = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    published = models.CharField(max_length=255, blank=True)
    salary = models.CharField(max_length=255, blank=True)
    url = models.URLField(max_length=1000, unique=True)
    job_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = JobQuerySet.as_manager()

    class Meta:
        db_table = '"crawler"."karboom"'
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class JobvisionJob(models.Model):
    jobvision_id = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=500)
    company = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    published = models.CharField(max_length=255, blank=True)
    published_at = models.CharField(max_length=255, blank=True)
    salary = models.CharField(max_length=255, blank=True)
    experience = models.CharField(max_length=255, blank=True)
    work_type = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=255, blank=True)
    benefits = models.TextField(blank=True)
    tags = models.TextField(blank=True)
    url = models.URLField(max_length=1000, unique=True)
    job_description = models.TextField(blank=True)
    company_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = JobQuerySet.as_manager()

    class Meta:
        db_table = '"crawler"."jobvision"'
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
