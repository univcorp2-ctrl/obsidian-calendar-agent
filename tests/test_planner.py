from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from obsidian_calendar_agent.config import Settings
from obsidian_calendar_agent.models import Task
from obsidian_calendar_agent.planner import HourlyPlannerAgent


def settings(tmp_path):
    return Settings(
        obsidian_vault_path=tmp_path,
        daily_notes_dir="Daily",
        daily_note_date_format="%Y-%m-%d",
        todo_files=[],
        timezone="Asia/Tokyo",
        workday_start="09:00",
        workday_end="12:00",
        slot_minutes=60,
        default_task_minutes=60,
        google_calendar_id="primary",
        google_credentials_file=tmp_path / "credentials.json",
        google_token_file=tmp_path / "token.json",
        telegram_bot_token=None,
        telegram_chat_id=None,
        agent_api_key=None,
        enable_scheduler=False,
        daily_digest_time="07:30",
    )


def task(task_id, title, minutes, priority=3):
    return Task(
        id=task_id,
        title=title,
        source_path=Path("Daily/2026-05-13.md"),
        line_no=1,
        date=date(2026, 5, 13),
        duration_minutes=minutes,
        priority=priority,
        fixed_start=None,
        raw_line=title,
    )


def test_planner_splits_into_hourly_blocks(tmp_path):
    planner = HourlyPlannerAgent(settings(tmp_path))
    blocks = planner.plan([task("a", "提案書", 120)], date(2026, 5, 13))

    assert len(blocks) == 2
    assert blocks[0].title == "提案書 (1/2)"
    assert blocks[0].start.hour == 9
    assert blocks[1].start.hour == 10


def test_planner_respects_busy_intervals(tmp_path):
    planner = HourlyPlannerAgent(settings(tmp_path))
    busy = [
        (
            datetime(2026, 5, 13, 9, 0, tzinfo=ZoneInfo("Asia/Tokyo")),
            datetime(2026, 5, 13, 10, 0, tzinfo=ZoneInfo("Asia/Tokyo")),
        )
    ]
    blocks = planner.plan([task("a", "集中作業", 60)], date(2026, 5, 13), busy=busy)

    assert blocks[0].start.hour == 10
