from bot.messages import EMPTY_QUERY_TEXT, HELP_TEXT, START_TEXT, format_results
from crawler.services import search_jobs


class BotHandler:
    def __init__(self, telegram, search=search_jobs, limit: int = 5):
        self.telegram = telegram
        self.search = search
        self.limit = limit

    def handle_update(self, update: dict) -> None:
        message = update.get("message") or {}
        chat = message.get("chat") or {}
        chat_id = chat.get("id")
        if chat_id is None:
            return

        text = (message.get("text") or "").strip()
        if not text:
            self.telegram.send_message(chat_id=chat_id, text=EMPTY_QUERY_TEXT)
            return

        if text.startswith("/start"):
            self.telegram.send_message(chat_id=chat_id, text=START_TEXT)
            return

        if text.startswith("/help"):
            self.telegram.send_message(chat_id=chat_id, text=HELP_TEXT)
            return

        jobs = self.search(text, limit=self.limit)
        response_text, reply_markup = format_results(text, jobs)
        self.telegram.send_message(
            chat_id=chat_id,
            text=response_text,
            reply_markup=reply_markup,
        )
