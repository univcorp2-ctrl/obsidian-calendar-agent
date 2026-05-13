from __future__ import annotations

from datetime import date
from html import escape
from typing import Any


class DailyDigestBuilderAgent:
    def build(self, target_date: date, events: list[dict[str, Any]]) -> str:
        lines = [f"<b>今日の予定: {target_date.isoformat()}</b>"]
        if not events:
            lines.append("予定はありません。")
            return "\n".join(lines)

        for event in events:
            summary = escape(event.get("summary", "(no title)"))
            start = event.get("start", {})
            time_label = start.get("dateTime", start.get("date", ""))
            if "T" in time_label:
                time_label = time_label.split("T", 1)[1][:5]
            lines.append(f"・{escape(time_label)} {summary}")
        return "\n".join(lines)
