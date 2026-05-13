from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime

from .config import load_settings
from .google_calendar import GoogleCalendarWriterAgent
from .orchestrator import ObsidianCalendarOrchestrator


def _parse_date(value: str | None):
    return datetime.strptime(value, "%Y-%m-%d").date() if value else datetime.now().date()


def main() -> None:
    parser = argparse.ArgumentParser(description="Obsidian to Google Calendar agent")
    sub = parser.add_subparsers(dest="command", required=True)

    auth = sub.add_parser("auth-google", help="Run Google OAuth flow and create token.json")
    auth.set_defaults(func=cmd_auth_google)

    sync = sub.add_parser("sync", help="Sync Obsidian tasks to Google Calendar")
    sync.add_argument("--date", help="Target date YYYY-MM-DD")
    sync.add_argument("--dry-run", action="store_true")
    sync.set_defaults(func=cmd_sync)

    telegram = sub.add_parser("telegram-today", help="Send today's digest to Telegram")
    telegram.add_argument("--date", help="Target date YYYY-MM-DD")
    telegram.set_defaults(func=cmd_telegram_today)

    args = parser.parse_args()
    args.func(args)


def cmd_auth_google(args) -> None:
    settings = load_settings()
    GoogleCalendarWriterAgent(settings).authenticate()
    print("Google OAuth token created or refreshed.")


def cmd_sync(args) -> None:
    settings = load_settings()
    result = ObsidianCalendarOrchestrator(settings).sync_day(_parse_date(args.date), dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_telegram_today(args) -> None:
    settings = load_settings()
    result = asyncio.run(ObsidianCalendarOrchestrator(settings).send_today_digest(_parse_date(args.date)))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
