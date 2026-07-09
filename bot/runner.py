import logging
import time

logger = logging.getLogger(__name__)


class BotRunner:
    def __init__(self, telegram, handler, poll_timeout: int = 30, retry_delay: int = 5):
        self.telegram = telegram
        self.handler = handler
        self.poll_timeout = poll_timeout
        self.retry_delay = retry_delay
        self.offset = None

    def run_forever(self) -> None:
        logger.info("Telegram bot polling started.")
        while True:
            self.run_once()

    def run_once(self) -> None:
        try:
            updates = self.telegram.get_updates(
                offset=self.offset,
                timeout=self.poll_timeout,
            )
        except Exception as exc:
            logger.warning("Telegram polling failed: %s", exc)
            time.sleep(self.retry_delay)
            return

        for update in updates:
            self.offset = update["update_id"] + 1
            try:
                self.handler.handle_update(update)
            except Exception as exc:
                logger.exception("Telegram update handling failed: %s", exc)
