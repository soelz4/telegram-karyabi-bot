from django.test import SimpleTestCase

from bot.handlers import BotHandler
from bot.messages import (
    CALLBACK_CLOSE,
    HELP_TEXT,
    SEARCH_PROMPT_TEXT,
    START_TEXT,
    format_job_detail,
    format_results,
    parse_job_callback,
    truncate,
)


JOB = {
    "id": 7,
    "source": "jobinja",
    "source_label": "Jobinja",
    "title": "Python Developer",
    "company": "Acme",
    "location": "Tehran",
    "published": "today",
    "salary": "Negotiable",
    "experience": "Senior",
    "contract": "Full-time",
    "work_type": "",
    "industry": "",
    "job_description": "Build useful software.\nWork with Django.",
    "subtitle": "Acme | Tehran | Jobinja",
    "button_text": "Python Developer - Acme",
    "url": "https://example.com/jobs/1",
}


class BotMessageTests(SimpleTestCase):
    def test_truncate_shortens_long_button_text(self):
        self.assertEqual(truncate("a" * 70, 10), "aaaaaaa...")

    def test_format_results_returns_callback_options_and_close(self):
        text, reply_markup = format_results("python", [JOB])

        self.assertIn('Results for "python"', text)
        self.assertEqual(
            reply_markup["inline_keyboard"][0][0]["callback_data"],
            "job:jobinja:7",
        )
        self.assertEqual(
            reply_markup["inline_keyboard"][1][0]["callback_data"],
            CALLBACK_CLOSE,
        )

    def test_format_job_detail_returns_open_back_close_buttons(self):
        text, reply_markup = format_job_detail(JOB)

        self.assertIn("Python Developer", text)
        self.assertIn("Company: Acme", text)
        self.assertEqual(reply_markup["inline_keyboard"][0][0]["url"], JOB["url"])
        self.assertEqual(
            reply_markup["inline_keyboard"][1][0]["callback_data"],
            "back",
        )

    def test_parse_job_callback(self):
        self.assertEqual(parse_job_callback("job:jobinja:7"), ("jobinja", "7"))
        self.assertIsNone(parse_job_callback("close"))


class BotHandlerTests(SimpleTestCase):
    def test_start_command_sends_intro_and_removes_old_keyboard(self):
        telegram = FakeTelegram()
        handler = BotHandler(telegram, search=lambda query, limit: [])

        handler.handle_update(make_message_update("/start"))

        self.assertEqual(telegram.messages[0]["text"], START_TEXT)
        self.assertEqual(
            telegram.messages[0]["reply_markup"],
            {"remove_keyboard": True},
        )

    def test_help_command_sends_examples(self):
        telegram = FakeTelegram()
        handler = BotHandler(telegram, search=lambda query, limit: [])

        handler.handle_update(make_message_update("/help"))

        self.assertEqual(telegram.messages[0]["text"], HELP_TEXT)

    def test_search_command_sends_prompt(self):
        telegram = FakeTelegram()
        handler = BotHandler(telegram, search=lambda query, limit: [])

        handler.handle_update(make_message_update("/search"))

        self.assertEqual(telegram.messages[0]["text"], SEARCH_PROMPT_TEXT)

    def test_text_message_searches_jobs_with_selectable_options(self):
        telegram = FakeTelegram()
        handler = BotHandler(
            telegram,
            search=lambda query, limit: [JOB],
            limit=3,
        )

        handler.handle_update(make_message_update("Python"))

        self.assertIn('Results for "Python"', telegram.messages[0]["text"])
        self.assertEqual(
            telegram.messages[0]["reply_markup"]["inline_keyboard"][0][0][
                "callback_data"
            ],
            "job:jobinja:7",
        )

    def test_job_callback_edits_message_to_job_detail(self):
        telegram = FakeTelegram()
        handler = BotHandler(
            telegram,
            search=lambda query, limit: [JOB],
            get_job_by_id=lambda source, job_id: JOB,
        )

        handler.handle_update(make_callback_update("job:jobinja:7"))

        self.assertIn("Company: Acme", telegram.edits[0]["text"])
        self.assertEqual(
            telegram.edits[0]["reply_markup"]["inline_keyboard"][0][0]["url"],
            JOB["url"],
        )

    def test_back_callback_restores_previous_results(self):
        telegram = FakeTelegram()
        handler = BotHandler(telegram, search=lambda query, limit: [JOB])
        handler.result_messages[55] = {"query": "Python", "jobs": [JOB]}

        handler.handle_update(make_callback_update("back", message_id=55))

        self.assertIn('Results for "Python"', telegram.edits[0]["text"])

    def test_close_callback_deletes_message(self):
        telegram = FakeTelegram()
        handler = BotHandler(telegram, search=lambda query, limit: [])

        handler.handle_update(make_callback_update(CALLBACK_CLOSE, message_id=55))

        self.assertEqual(telegram.deleted[0]["message_id"], 55)


class FakeTelegram:
    def __init__(self):
        self.messages = []
        self.edits = []
        self.deleted = []
        self.answers = []
        self.next_message_id = 100

    def send_message(self, **payload):
        self.messages.append(payload)
        self.next_message_id += 1
        return {"result": {"message_id": self.next_message_id}}

    def edit_message_text(self, **payload):
        self.edits.append(payload)

    def delete_message(self, **payload):
        self.deleted.append(payload)

    def answer_callback_query(self, **payload):
        self.answers.append(payload)


def make_message_update(text: str) -> dict:
    return {
        "update_id": 1,
        "message": {
            "chat": {"id": 123},
            "text": text,
        },
    }


def make_callback_update(data: str, message_id: int = 55) -> dict:
    return {
        "update_id": 2,
        "callback_query": {
            "id": "callback-id",
            "data": data,
            "message": {
                "message_id": message_id,
                "chat": {"id": 123},
            },
        },
    }
