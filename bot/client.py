import logging

import requests

logger = logging.getLogger(__name__)


class TelegramClient:
    api_base_url = "https://api.telegram.org"

    def __init__(self, token: str, timeout: int = 30):
        self.token = token
        self.timeout = timeout
        self.session = requests.Session()

    def get_updates(self, *, offset: int | None = None, timeout: int = 30) -> list[dict]:
        payload = {"timeout": timeout, "allowed_updates": ["message"]}
        if offset is not None:
            payload["offset"] = offset
        return self.request("getUpdates", payload).get("result", [])

    def send_message(
        self,
        *,
        chat_id: int,
        text: str,
        reply_markup: dict | None = None,
        disable_web_page_preview: bool = True,
    ) -> dict:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": disable_web_page_preview,
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return self.request("sendMessage", payload)

    def request(self, method: str, payload: dict) -> dict:
        response = self.session.post(
            self.url(method),
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        if not data.get("ok"):
            raise RuntimeError(data.get("description") or f"Telegram {method} failed")
        return data

    def url(self, method: str) -> str:
        return f"{self.api_base_url}/bot{self.token}/{method}"
