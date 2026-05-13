from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    obsidian_vault_path: Path
    daily_notes_dir: str
    daily_note_date_format: str
    todo_files: list[str]
    timezone: str
    workday_start: str
    workday_end: str
    slot_minutes: int
    default_task_minutes: int
    google_calendar_id: str
    google_credentials_file: Path
    google_token_file: Path
    telegram_bot_token: Optional[str]
    telegram_chat_id: Optional[str]
    agent_api_key: Optional[str]
    enable_scheduler: bool
    daily_digest_time: str


def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        obsidian_vault_path=Path(os.getenv("OBSIDIAN_VAULT_PATH", "./vault")).expanduser(),
        daily_notes_dir=os.getenv("DAILY_NOTES_DIR", "Daily"),
        daily_note_date_format=os.getenv("DAILY_NOTE_DATE_FORMAT", "%Y-%m-%d"),
        todo_files=_csv(os.getenv("TODO_FILES", "TODO.md")),
        timezone=os.getenv("TIMEZONE", "Asia/Tokyo"),
        workday_start=os.getenv("WORKDAY_START", "09:00"),
        workday_end=os.getenv("WORKDAY_END", "18:00"),
        slot_minutes=int(os.getenv("SLOT_MINUTES", "60")),
        default_task_minutes=int(os.getenv("DEFAULT_TASK_MINUTES", "60")),
        google_calendar_id=os.getenv("GOOGLE_CALENDAR_ID", "primary"),
        google_credentials_file=Path(os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")),
        google_token_file=Path(os.getenv("GOOGLE_TOKEN_FILE", "token.json")),
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN") or None,
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID") or None,
        agent_api_key=os.getenv("AGENT_API_KEY") or None,
        enable_scheduler=os.getenv("ENABLE_SCHEDULER", "false").lower() == "true",
        daily_digest_time=os.getenv("DAILY_DIGEST_TIME", "07:30"),
    )
