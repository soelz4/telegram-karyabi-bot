from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("crawler", "0001_create_jobinja"),
    ]

    operations = [
        migrations.CreateModel(
            name="QueraJob",
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
                ("experience", models.CharField(blank=True, max_length=255)),
                ("published", models.CharField(blank=True, max_length=255)),
                ("published_at", models.CharField(blank=True, max_length=255)),
                ("url", models.URLField(max_length=1000, unique=True)),
                ("job_description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": '"crawler"."quera"',
                "ordering": ["-created_at"],
            },
        ),
    ]
