from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("crawler", "0003_create_karboom"),
    ]

    operations = [
        migrations.AddField(
            model_name="querajob",
            name="company_description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="querajob",
            name="tags",
            field=models.TextField(blank=True),
        ),
    ]
