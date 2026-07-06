from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("crawler", "0004_enrich_quera"),
    ]

    operations = [
        migrations.CreateModel(
            name="JobvisionJob",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("jobvision_id", models.PositiveIntegerField(unique=True)),
                ("title", models.CharField(max_length=500)),
                ("company", models.CharField(blank=True, max_length=255)),
                ("location", models.CharField(blank=True, max_length=255)),
                ("published", models.CharField(blank=True, max_length=255)),
                ("published_at", models.CharField(blank=True, max_length=255)),
                ("salary", models.CharField(blank=True, max_length=255)),
                ("experience", models.CharField(blank=True, max_length=255)),
                ("work_type", models.CharField(blank=True, max_length=255)),
                ("industry", models.CharField(blank=True, max_length=255)),
                ("benefits", models.TextField(blank=True)),
                ("tags", models.TextField(blank=True)),
                ("url", models.URLField(max_length=1000, unique=True)),
                ("job_description", models.TextField(blank=True)),
                ("company_description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": '"crawler"."jobvision"',
                "ordering": ["-created_at"],
            },
        ),
    ]
