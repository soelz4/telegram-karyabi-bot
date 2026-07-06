from django.contrib import admin

from crawler.models import JobinjaJob, KarboomJob, QueraJob


@admin.register(JobinjaJob)
class JobinjaJobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "published", "updated_at")
    search_fields = ("title", "company", "location", "url")
    list_filter = ("published", "location")


@admin.register(QueraJob)
class QueraJobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "experience", "published")
    search_fields = ("title", "company", "location", "url")
    list_filter = ("experience", "published", "location")


@admin.register(KarboomJob)
class KarboomJobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "published", "salary")
    search_fields = ("title", "company", "location", "url")
    list_filter = ("published", "location")
