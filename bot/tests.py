from django.test import SimpleTestCase

from bot.handlers import BotHandler
from bot.messages import HELP_TEXT, START_TEXT, format_results, truncate


class BotMessageTests(SimpleTestCase):
    def test_truncate_shortens_long_button_text(self):
        self.assertEqual(truncate("a" * 70, 10), "aaaaaaa...")

    def test_format_results_returns_inline_url_buttons(self):
        text, reply_markup = format_results(
            "python",
            [
                {
                    "title": "Python Developer",
                    "subtitle": "Acme | Tehran | Jobinja",
                    "button_text": "Python Developer - Acme",
                    "url": "https://example.com/jobs/1",
                }
            ],
        )

        self.assertIn('Results for "python"', text)
        self.assertEqual(
            reply_markup,
            {
                "inline_keyboard": [
                    [
                        {
                            "text": "Python Developer - Acme",
                            "url": "https://example.com/jobs/1",
                        }
                    ]
                ]
            },
        )


class BotHandlerTests(SimpleTestCase):
    def test_start_command_sends_intro(self):
        telegram = FakeTelegram()
        handler = BotHandler(telegram, search=lambda query, limit: [])

        handler.handle_update(make_update("/start"))

        self.assertEqual(telegram.messages[0]["text"], START_TEXT)

    def test_help_command_sends_examples(self):
        telegram = FakeTelegram()
        handler = BotHandler(telegram, search=lambda query, limit: [])

        handler.handle_update(make_update("/help"))

        self.assertEqual(telegram.messages[0]["text"], HELP_TEXT)

    def test_text_message_searches_jobs(self):
        telegram = FakeTelegram()
        handler = BotHandler(
            telegram,
            search=lambda query, limit: [
                {
                    "title": "Python Developer",
                    "subtitle": "Acme | Tehran | Jobinja",
                    "button_text": "Python Developer - Acme",
                    "url": "https://example.com/jobs/1",
                }
            ],
            limit=3,
        )

        handler.handle_update(make_update("Python"))

        self.assertIn('Results for "Python"', telegram.messages[0]["text"])
        self.assertEqual(
            telegram.messages[0]["reply_markup"]["inline_keyboard"][0][0]["url"],
            "https://example.com/jobs/1",
        )


class FakeTelegram:
    def __init__(self):
        self.messages = []

    def send_message(self, **payload):
        self.messages.append(payload)


def make_update(text: str) -> dict:
    return {
        "update_id": 1,
        "message": {
            "chat": {"id": 123},
            "text": text,
        },
    }
