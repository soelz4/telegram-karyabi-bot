from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.RunSQL(
            sql="CREATE SCHEMA IF NOT EXISTS crawler;",
            reverse_sql="DROP SCHEMA IF EXISTS crawler CASCADE;",
        ),
        migrations.CreateModel(
            name="JobinjaJob",
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
                ("title", models.CharField(max_length=500)),
                ("company", models.CharField(blank=True, max_length=255)),
                ("location", models.CharField(blank=True, max_length=255)),
                ("contract", models.CharField(blank=True, max_length=255)),
                ("salary", models.CharField(blank=True, max_length=255)),
                ("experience", models.CharField(blank=True, max_length=255)),
                ("published", models.CharField(blank=True, max_length=255)),
                ("url", models.URLField(max_length=1000, unique=True)),
                ("job_description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": '"crawler"."jobinja"',
                "ordering": ["-created_at"],
            },
        ),
    ]
