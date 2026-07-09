from django.core.management.base import BaseCommand

from crawler.sources import SOURCE_CONFIGS


class Command(BaseCommand):
    help = "Delete crawled jobs from one source table or all source tables."

    def add_arguments(self, parser):
        parser.add_argument(
            "source",
            nargs="?",
            choices=[*SOURCE_CONFIGS.keys(), "all"],
            default="all",
            help="Source table to clear.",
        )

    def handle(self, *args, **options):
        total_deleted = 0

        for config in self.get_selected_configs(options["source"]):
            deleted_count, _ = config.model.objects.all().delete()
            total_deleted += deleted_count
            self.stdout.write(
                f"{config.name}: deleted {deleted_count} rows from {config.table_name}."
            )

        self.stdout.write(self.style.SUCCESS(f"Deleted {total_deleted} jobs."))

    def get_selected_configs(self, source):
        if source == "all":
            return SOURCE_CONFIGS.values()
        return [SOURCE_CONFIGS[source]]
