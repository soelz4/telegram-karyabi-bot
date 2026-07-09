import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from bot.client import TelegramClient
from bot.handlers import BotHandler
from bot.runner import BotRunner


class Command(BaseCommand):
    help = "Run the Telegram bot with long polling."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=5,
            help="Maximum job results to return per search message.",
        )
        parser.add_argument(
            "--poll-timeout",
            type=int,
            default=30,
            help="Telegram long-poll timeout in seconds.",
        )
        parser.add_argument(
            "--retry-delay",
            type=int,
            default=5,
            help="Delay in seconds after Telegram polling errors.",
        )

    def handle(self, *args, **options):
        self.validate_options(options)
        self.configure_logging(options["verbosity"])

        token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
        if not token:
            raise CommandError("TELEGRAM_BOT_TOKEN is not configured.")

        telegram = TelegramClient(token=token)
        handler = BotHandler(telegram, limit=options["limit"])
        runner = BotRunner(
            telegram,
            handler,
            poll_timeout=options["poll_timeout"],
            retry_delay=options["retry_delay"],
        )
        runner.run_forever()

    def validate_options(self, options) -> None:
        if options["limit"] < 1:
            raise CommandError("--limit must be at least 1.")
        if options["poll_timeout"] < 1:
            raise CommandError("--poll-timeout must be at least 1.")
        if options["retry_delay"] < 0:
            raise CommandError("--retry-delay cannot be negative.")

    def configure_logging(self, verbosity: int) -> None:
        level = logging.INFO if verbosity >= 2 else logging.WARNING
        logger = logging.getLogger("bot")
        logger.setLevel(level)
        logger.propagate = False

        if not logger.handlers:
            logger.addHandler(logging.StreamHandler(self.stderr))

        for handler in logger.handlers:
            handler.setLevel(level)
