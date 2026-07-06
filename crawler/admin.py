from django.contrib import admin

from crawler.models import JobinjaJob, JobvisionJob, KarboomJob, QueraJob


class JobAdmin(admin.ModelAdmin):
    search_fields = ("title", "company", "location", "url")


@admin.register(JobinjaJob)
class JobinjaJobAdmin(JobAdmin):
    list_display = ("title", "company", "location", "published", "updated_at")
    list_filter = ("published", "location")


@admin.register(QueraJob)
class QueraJobAdmin(JobAdmin):
    list_display = ("title", "company", "location", "experience", "published")
    list_filter = ("experience", "published", "location")


@admin.register(KarboomJob)
class KarboomJobAdmin(JobAdmin):
    list_display = ("title", "company", "location", "published", "salary")
    list_filter = ("published", "location")


@admin.register(JobvisionJob)
class JobvisionJobAdmin(JobAdmin):
    list_display = ("title", "company", "location", "published", "salary")
    list_filter = ("published", "location", "industry")
