from __future__ import annotations

from datetime import date
from typing import Any

from .config import Settings
from .digest import DailyDigestBuilderAgent
from .google_calendar import GoogleCalendarWriterAgent
from .parser import ObsidianTaskParserAgent
from .planner import HourlyPlannerAgent
from .telegram import TelegramDigestAgent


class ObsidianCalendarOrchestrator:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.parser = ObsidianTaskParserAgent(settings)
        self.planner = HourlyPlannerAgent(settings)
        self.calendar = GoogleCalendarWriterAgent(settings)
        self.digest_builder = DailyDigestBuilderAgent()
        self.telegram = TelegramDigestAgent(settings)

    def sync_day(self, target_date: date, dry_run: bool = False) -> dict[str, Any]:
        tasks = self.parser.parse_for_date(target_date)
        busy = [] if dry_run else self.calendar.busy_intervals_for_day(target_date)
        blocks = self.planner.plan(tasks, target_date, busy=busy)
        results = []
        if not dry_run:
            for block in blocks:
                results.append(self.calendar.create_block(block))
        return {
            "date": target_date.isoformat(),
            "dry_run": dry_run,
            "task_count": len(tasks),
            "block_count": len(blocks),
            "tasks": [task.to_dict() for task in tasks],
            "blocks": [block.to_dict() for block in blocks],
            "calendar_results": results,
        }

    async def send_today_digest(self, target_date: date) -> dict[str, Any]:
        events = self.calendar.list_events_for_day(target_date)
        message = self.digest_builder.build(target_date, events)
        telegram_result = await self.telegram.send_message(message)
        return {"date": target_date.isoformat(), "message": message, "telegram_result": telegram_result}

    def build_digest_text(self, target_date: date) -> dict[str, Any]:
        events = self.calendar.list_events_for_day(target_date)
        message = self.digest_builder.build(target_date, events)
        return {"date": target_date.isoformat(), "message": message, "event_count": len(events)}
