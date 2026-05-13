from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, time
from pathlib import Path
from typing import Any, Optional


@dataclass(frozen=True)
class Task:
    id: str
    title: str
    source_path: Path
    line_no: int
    date: date
    duration_minutes: int
    priority: int
    fixed_start: Optional[time]
    raw_line: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["source_path"] = str(self.source_path)
        data["date"] = self.date.isoformat()
        data["fixed_start"] = self.fixed_start.isoformat() if self.fixed_start else None
        return data


@dataclass(frozen=True)
class CalendarBlock:
    event_id: str
    title: str
    start: datetime
    end: datetime
    source_task_id: str
    description: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["start"] = self.start.isoformat()
        data["end"] = self.end.isoformat()
        return data
