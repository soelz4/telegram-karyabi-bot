from django.db import models


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

    class Meta:
        db_table = '"crawler"."jobinja"'
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
