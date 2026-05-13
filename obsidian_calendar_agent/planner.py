from __future__ import annotations

import hashlib
import math
from datetime import date, datetime, time, timedelta
from typing import Iterable, Optional
from zoneinfo import ZoneInfo

from .config import Settings
from .models import CalendarBlock, Task

BusyInterval = tuple[datetime, datetime]


class HourlyPlannerAgent:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.tz = ZoneInfo(settings.timezone)
        self.slot_minutes = settings.slot_minutes
        self.workday_start = self._parse_time(settings.workday_start)
        self.workday_end = self._parse_time(settings.workday_end)

    def plan(self, tasks: list[Task], target_date: date, busy: Optional[list[BusyInterval]] = None) -> list[CalendarBlock]:
        busy = busy or []
        tasks_sorted = sorted(tasks, key=lambda t: (t.fixed_start is None, t.priority, t.line_no, t.title))
        blocks: list[CalendarBlock] = []
        occupied = list(busy)

        for task in tasks_sorted:
            chunks = max(1, math.ceil(task.duration_minutes / self.slot_minutes))
            for index in range(chunks):
                start = self._find_start(task, target_date, occupied, index)
                end = start + timedelta(minutes=self.slot_minutes)
                occupied.append((start, end))
                title = task.title if chunks == 1 else f"{task.title} ({index + 1}/{chunks})"
                blocks.append(
                    CalendarBlock(
                        event_id=self._event_id(task.id, index),
                        title=title,
                        start=start,
                        end=end,
                        source_task_id=task.id,
                        description=(
                            "Created from Obsidian task.\n"
                            f"Source: {task.source_path}:{task.line_no}\n"
                            f"Original estimate: {task.duration_minutes} minutes\n"
                            f"Raw: {task.raw_line}"
                        ),
                    )
                )

        return sorted(blocks, key=lambda b: b.start)

    def _find_start(self, task: Task, target_date: date, occupied: list[BusyInterval], chunk_index: int) -> datetime:
        if task.fixed_start is not None:
            base = datetime.combine(target_date, task.fixed_start, tzinfo=self.tz)
            candidate = base + timedelta(minutes=self.slot_minutes * chunk_index)
            if not self._conflicts(candidate, candidate + timedelta(minutes=self.slot_minutes), occupied):
                return candidate

        cursor = datetime.combine(target_date, self.workday_start, tzinfo=self.tz)
        end_of_day = datetime.combine(target_date, self.workday_end, tzinfo=self.tz)
        while cursor + timedelta(minutes=self.slot_minutes) <= end_of_day:
            slot_end = cursor + timedelta(minutes=self.slot_minutes)
            if not self._conflicts(cursor, slot_end, occupied):
                return cursor
            cursor = slot_end

        # Workday overflow: continue after configured end time instead of dropping tasks.
        cursor = end_of_day
        while self._conflicts(cursor, cursor + timedelta(minutes=self.slot_minutes), occupied):
            cursor += timedelta(minutes=self.slot_minutes)
        return cursor

    def _conflicts(self, start: datetime, end: datetime, intervals: Iterable[BusyInterval]) -> bool:
        return any(start < busy_end and end > busy_start for busy_start, busy_end in intervals)

    def _parse_time(self, value: str) -> time:
        return datetime.strptime(value, "%H:%M").time()

    def _event_id(self, task_id: str, chunk_index: int) -> str:
        digest = hashlib.sha1(f"{task_id}:{chunk_index}".encode("utf-8")).hexdigest()
        return "obs" + digest[:32]
