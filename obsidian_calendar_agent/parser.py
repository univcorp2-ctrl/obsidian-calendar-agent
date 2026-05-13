from __future__ import annotations

import hashlib
import re
from datetime import date, datetime, time
from pathlib import Path
from typing import Iterable, Optional

from .config import Settings
from .models import Task

TASK_RE = re.compile(r"^\s*[-*]\s+\[(?P<checked>[ xX])\]\s+(?P<title>.+?)\s*$")
DURATION_RE = re.compile(
    r"(?:⏱|duration[:：]|dur[:：]|\[duration::)\s*(?P<value>\d+)\s*(?P<unit>h|hr|hour|hours|時間|m|min|mins|minute|minutes|分)?\]?",
    re.IGNORECASE,
)
TIME_RE = re.compile(r"(?:⏰|time[:：]|\[time::)\s*(?P<time>\d{1,2}:\d{2})\]?", re.IGNORECASE)
DATE_RE = re.compile(r"(?:📅|due[:：]|\[date::)\s*(?P<date>\d{4}-\d{2}-\d{2})\]?", re.IGNORECASE)
PRIORITY_RE = re.compile(r"#p(?P<num>[1-5])|#priority/(?P<word>high|medium|low)|#(high|medium|low)", re.IGNORECASE)
SKIP_TOKENS = ("#gcal-skip", "#calendar-skip", "#skip-calendar")


class ObsidianTaskParserAgent:
    def __init__(self, settings: Settings):
        self.settings = settings

    def parse_for_date(self, target_date: date) -> list[Task]:
        tasks: list[Task] = []
        daily_path = self.daily_note_path(target_date)
        if daily_path.exists():
            tasks.extend(self._parse_file(daily_path, target_date, include_undated=True))

        for rel_path in self.settings.todo_files:
            todo_path = self.settings.obsidian_vault_path / rel_path
            if todo_path.exists():
                tasks.extend(self._parse_file(todo_path, target_date, include_undated=False))

        return self._deduplicate(tasks)

    def daily_note_path(self, target_date: date) -> Path:
        filename = target_date.strftime(self.settings.daily_note_date_format) + ".md"
        return self.settings.obsidian_vault_path / self.settings.daily_notes_dir / filename

    def _parse_file(self, path: Path, target_date: date, include_undated: bool) -> Iterable[Task]:
        lines = path.read_text(encoding="utf-8").splitlines()
        for line_no, line in enumerate(lines, start=1):
            maybe_task = self._parse_line(path, line_no, line, target_date, include_undated)
            if maybe_task:
                yield maybe_task

    def _parse_line(
        self,
        path: Path,
        line_no: int,
        line: str,
        target_date: date,
        include_undated: bool,
    ) -> Optional[Task]:
        match = TASK_RE.match(line)
        if not match or match.group("checked").strip().lower() == "x":
            return None
        raw_title = match.group("title")
        if any(token in raw_title for token in SKIP_TOKENS):
            return None

        explicit_date = self._extract_date(raw_title)
        is_today_tagged = "#today" in raw_title
        if explicit_date and explicit_date != target_date:
            return None
        if not include_undated and explicit_date is None and not is_today_tagged:
            return None

        duration = self._extract_duration(raw_title) or self.settings.default_task_minutes
        fixed_start = self._extract_time(raw_title)
        priority = self._extract_priority(raw_title)
        clean_title = self._clean_title(raw_title)
        task_id = self._stable_id(path, line_no, line)

        return Task(
            id=task_id,
            title=clean_title,
            source_path=path,
            line_no=line_no,
            date=target_date,
            duration_minutes=duration,
            priority=priority,
            fixed_start=fixed_start,
            raw_line=line,
        )

    def _extract_duration(self, text: str) -> Optional[int]:
        match = DURATION_RE.search(text)
        if not match:
            return None
        value = int(match.group("value"))
        unit = (match.group("unit") or "m").lower()
        if unit in {"h", "hr", "hour", "hours", "時間"}:
            return value * 60
        return value

    def _extract_time(self, text: str) -> Optional[time]:
        match = TIME_RE.search(text)
        if not match:
            return None
        return datetime.strptime(match.group("time"), "%H:%M").time()

    def _extract_date(self, text: str) -> Optional[date]:
        match = DATE_RE.search(text)
        if not match:
            return None
        return datetime.strptime(match.group("date"), "%Y-%m-%d").date()

    def _extract_priority(self, text: str) -> int:
        match = PRIORITY_RE.search(text)
        if not match:
            return 3
        if match.group("num"):
            return int(match.group("num"))
        word = (match.group("word") or match.group(3) or "medium").lower()
        return {"high": 1, "medium": 3, "low": 5}.get(word, 3)

    def _clean_title(self, text: str) -> str:
        text = DURATION_RE.sub("", text)
        text = TIME_RE.sub("", text)
        text = DATE_RE.sub("", text)
        text = PRIORITY_RE.sub("", text)
        text = text.replace("#today", "")
        for token in SKIP_TOKENS:
            text = text.replace(token, "")
        return re.sub(r"\s+", " ", text).strip()

    def _stable_id(self, path: Path, line_no: int, line: str) -> str:
        payload = f"{path}:{line_no}:{line}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()[:24]

    def _deduplicate(self, tasks: list[Task]) -> list[Task]:
        seen: set[str] = set()
        unique: list[Task] = []
        for task in tasks:
            if task.id not in seen:
                unique.append(task)
                seen.add(task.id)
        return unique
