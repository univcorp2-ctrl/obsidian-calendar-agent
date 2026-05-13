from __future__ import annotations

from typing import Any

import httpx

from .config import Settings


class TelegramDigestAgent:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def send_message(self, text: str) -> dict[str, Any]:
        if not self.settings.telegram_bot_token or not self.settings.telegram_chat_id:
            raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required")
        url = f"https://api.telegram.org/bot{self.settings.telegram_bot_token}/sendMessage"
        payload = {"chat_id": self.settings.telegram_chat_id, "text": text, "parse_mode": "HTML"}
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
