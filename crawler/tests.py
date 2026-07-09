from datetime import datetime, timezone
from types import SimpleNamespace

from django.test import SimpleTestCase

from crawler import services


class SearchServiceTests(SimpleTestCase):
    def test_normalize_query_handles_spacing_and_arabic_characters(self):
        self.assertEqual(
            services.normalize_query("  Software   Engineer  يكي  "),
            "software engineer یکی",
        )

    def test_normalize_limit_clamps_values(self):
        self.assertEqual(services.normalize_limit(None), services.DEFAULT_LIMIT)
        self.assertEqual(services.normalize_limit("-1"), 0)
        self.assertEqual(services.normalize_limit("999"), services.MAX_LIMIT)

    def test_score_job_prioritizes_title_matches(self):
        title_match = make_job(title="Senior Software Engineer", company="")
        description_match = make_job(
            title="Backend Developer", job_description="Software Engineer"
        )

        terms = services.normalize_query("Software Engineer").split()

        self.assertGreater(
            services.score_job(title_match, terms),
            services.score_job(description_match, terms),
        )

    def test_search_result_includes_telegram_display_fields(self):
        result = services.SearchResult(
            id=1,
            source="jobinja",
            source_label="Jobinja",
            title="Software Engineer",
            company="Acme",
            location="Tehran",
            published="today",
            url="https://example.com/jobs/1",
            score=100,
            updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        ).as_dict()

        self.assertEqual(result["subtitle"], "Acme | Tehran | Jobinja")
        self.assertEqual(result["button_text"], "Software Engineer - Acme")


def make_job(**values):
    defaults = {
        "title": "",
        "company": "",
        "location": "",
        "tags": "",
        "industry": "",
        "work_type": "",
        "salary": "",
        "experience": "",
        "job_description": "",
        "company_description": "",
        "id": 1,
    }
    defaults.update(values)
    fields = [SimpleNamespace(name=name) for name in defaults]
    return SimpleNamespace(**defaults, _meta=SimpleNamespace(fields=fields))
