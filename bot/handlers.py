from bot.messages import (
    CALLBACK_BACK,
    CALLBACK_CLOSE,
    EMPTY_QUERY_TEXT,
    HELP_TEXT,
    JOB_NOT_FOUND_TEXT,
    START_TEXT,
    format_job_detail,
    format_results,
    parse_job_callback,
    remove_keyboard,
    search_prompt,
)
from crawler.services import get_job, search_jobs


class BotHandler:
    def __init__(
        self,
        telegram,
        search=search_jobs,
        get_job_by_id=get_job,
        limit: int = 5,
    ):
        self.telegram = telegram
        self.search = search
        self.get_job_by_id = get_job_by_id
        self.limit = limit
        self.result_messages = {}

    def handle_update(self, update: dict) -> None:
        if update.get("callback_query"):
            self.handle_callback_query(update["callback_query"])
            return

        self.handle_message(update.get("message") or {})

    def handle_message(self, message: dict) -> None:
        chat = message.get("chat") or {}
        chat_id = chat.get("id")
        if chat_id is None:
            return

        text = (message.get("text") or "").strip()
        if not text:
            self.telegram.send_message(chat_id=chat_id, text=EMPTY_QUERY_TEXT)
            return

        if text.startswith("/start"):
            self.telegram.send_message(
                chat_id=chat_id,
                text=START_TEXT,
                reply_markup=remove_keyboard(),
            )
            return

        if text.startswith("/help"):
            self.telegram.send_message(chat_id=chat_id, text=HELP_TEXT)
            return

        if text.startswith("/search"):
            response_text, reply_markup = search_prompt()
            self.telegram.send_message(
                chat_id=chat_id,
                text=response_text,
                reply_markup=reply_markup,
            )
            return

        self.send_search_results(chat_id, text)

    def handle_callback_query(self, callback_query: dict) -> None:
        callback_id = callback_query["id"]
        data = callback_query.get("data", "")
        message = callback_query.get("message") or {}
        chat = message.get("chat") or {}
        chat_id = chat.get("id")
        message_id = message.get("message_id")

        self.telegram.answer_callback_query(callback_query_id=callback_id)
        if chat_id is None or message_id is None:
            return

        if data == CALLBACK_CLOSE:
            self.result_messages.pop(message_id, None)
            self.telegram.delete_message(chat_id=chat_id, message_id=message_id)
            return

        if data == CALLBACK_BACK:
            self.show_previous_results(chat_id, message_id)
            return

        job_key = parse_job_callback(data)
        if job_key:
            self.show_job_detail(chat_id, message_id, *job_key)

    def send_search_results(self, chat_id: int, query: str) -> None:
        jobs = self.search(query, limit=self.limit)
        text, reply_markup = format_results(query, jobs)
        response = self.telegram.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
        )
        message_id = (response.get("result") or {}).get("message_id")
        if message_id:
            self.result_messages[message_id] = {
                "query": query,
                "jobs": jobs,
            }

    def show_previous_results(self, chat_id: int, message_id: int) -> None:
        state = self.result_messages.get(message_id)
        if not state:
            text, reply_markup = search_prompt()
        else:
            text, reply_markup = format_results(state["query"], state["jobs"])

        self.telegram.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=reply_markup,
        )

    def show_job_detail(
        self,
        chat_id: int,
        message_id: int,
        source: str,
        job_id: str,
    ) -> None:
        job = self.get_job_by_id(source, job_id)
        if not job:
            self.telegram.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=JOB_NOT_FOUND_TEXT,
            )
            return

        text, reply_markup = format_job_detail(job)
        self.telegram.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=reply_markup,
        )
