from django.contrib import admin

from crawler.models import JobinjaJob


@admin.register(JobinjaJob)
class JobinjaJobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "published", "updated_at")
    search_fields = ("title", "company", "location", "url")
    list_filter = ("published", "location")
