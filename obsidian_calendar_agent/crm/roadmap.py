from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Iterable, Optional

from obsidian_calendar_agent.config import Settings

ROADMAP_MARKER_START = "<!-- AI_ROADMAP_TARGETS:START -->"
ROADMAP_MARKER_END = "<!-- AI_ROADMAP_TARGETS:END -->"
DEFAULT_ROADMAP_PATH = Path(__file__).resolve().parents[2] / "data" / "roadmap_targets_10yr.json"


@dataclass(frozen=True)
class TargetRange:
    label: str
    low: float
    high: float
    unit: str

    def interpolate(self, other: "TargetRange", ratio: float) -> "TargetRange":
        return TargetRange(
            label=self.label,
            low=self.low + (other.low - self.low) * ratio,
            high=self.high + (other.high - self.high) * ratio,
            unit=self.unit,
        )

    def to_dict(self) -> dict[str, Any]:
        return {"label": self.label, "low": self.low, "high": self.high, "unit": self.unit, "formatted": self.format()}

    def format(self) -> str:
        if abs(self.low - self.high) < 0.000001:
            return f"{_format_number(self.low, self.unit)}{self.unit}"
        return f"{_format_number(self.low, self.unit)}〜{_format_number(self.high, self.unit)}{self.unit}"


@dataclass(frozen=True)
class RoadmapMilestone:
    label: str
    date: date
    age: int
    targets: dict[str, TargetRange]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RoadmapMilestone":
        return cls(
            label=data["label"],
            date=datetime.strptime(data["date"], "%Y-%m-%d").date(),
            age=int(data["age"]),
            targets={key: TargetRange(**value) for key, value in data["targets"].items()},
        )


@dataclass(frozen=True)
class WeeklyRoadmapTarget:
    target_date: date
    week_label: str
    previous_milestone: str
    next_milestone: str
    progress_to_next_milestone: float
    targets: dict[str, TargetRange]

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_date": self.target_date.isoformat(),
            "week_label": self.week_label,
            "previous_milestone": self.previous_milestone,
            "next_milestone": self.next_milestone,
            "progress_to_next_milestone": round(self.progress_to_next_milestone, 4),
            "targets": {key: value.to_dict() for key, value in self.targets.items()},
        }


class RoadmapPlannerAgent:
    """Reverse-calculates weekly Friday targets from long-term numeric milestones."""

    def __init__(self, milestones: list[RoadmapMilestone], source: str = ""):
        if len(milestones) < 2:
            raise ValueError("At least two roadmap milestones are required")
        self.milestones = sorted(milestones, key=lambda item: item.date)
        self.source = source

    @classmethod
    def from_json(cls, path: Path = DEFAULT_ROADMAP_PATH) -> "RoadmapPlannerAgent":
        data = json.loads(path.read_text(encoding="utf-8"))
        milestones = [RoadmapMilestone.from_dict(item) for item in data["milestones"]]
        return cls(milestones=milestones, source=data.get("source", str(path)))

    def weekly_targets(self, start_date: date, weeks: int = 4) -> list[WeeklyRoadmapTarget]:
        if weeks <= 0:
            raise ValueError("weeks must be positive")
        return [self.target_for(friday, index) for index, friday in enumerate(_next_fridays(start_date, weeks), start=1)]

    def target_for(self, target_date: date, week_index: int = 1) -> WeeklyRoadmapTarget:
        previous, next_milestone = self._bounds(target_date)
        total_days = max(1, (next_milestone.date - previous.date).days)
        elapsed_days = min(max(0, (target_date - previous.date).days), total_days)
        ratio = elapsed_days / total_days
        targets: dict[str, TargetRange] = {}
        for key, previous_value in previous.targets.items():
            next_value = next_milestone.targets[key]
            targets[key] = previous_value.interpolate(next_value, ratio)
        return WeeklyRoadmapTarget(
            target_date=target_date,
            week_label=_week_label(week_index),
            previous_milestone=previous.label,
            next_milestone=next_milestone.label,
            progress_to_next_milestone=ratio,
            targets=targets,
        )

    def render_markdown(self, weekly_targets: list[WeeklyRoadmapTarget], review_text: Optional[str] = None) -> str:
        lines = [
            "## 10年ロードマップ逆算: 週次目標数字",
            "",
            f"- 生成日: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"- 基準データ: {self.source}",
            "- 計算方法: 現在地から次の年末目標までを日数按分し、各金曜日時点の目標数字に分解",
            "- 注意: これは自動生成された目安。実績入力やAI/CLIレビューにより毎週更新する",
            "",
        ]

        for weekly_target in weekly_targets:
            lines.extend(
                [
                    f"### {weekly_target.week_label}: {weekly_target.target_date.isoformat()} 金曜日時点",
                    "",
                    f"- 区間: {weekly_target.previous_milestone} → {weekly_target.next_milestone}",
                    f"- 区間進捗: {weekly_target.progress_to_next_milestone * 100:.1f}%",
                    "",
                    "| 指標 | 目標数字 |",
                    "|---|---:|",
                ]
            )
            for target in weekly_target.targets.values():
                lines.append(f"| {target.label} | {target.format()} |")
            lines.append("")
            lines.extend(self._action_hints(weekly_target))
            lines.append("")

        if review_text:
            lines.extend(["## CLI AIレビュー", "", review_text.strip(), ""])

        return "\n".join(lines).strip() + "\n"

    def _bounds(self, target_date: date) -> tuple[RoadmapMilestone, RoadmapMilestone]:
        if target_date <= self.milestones[0].date:
            return self.milestones[0], self.milestones[1]
        for previous, next_milestone in zip(self.milestones, self.milestones[1:]):
            if previous.date <= target_date <= next_milestone.date:
                return previous, next_milestone
        return self.milestones[-2], self.milestones[-1]

    def _action_hints(self, weekly_target: WeeklyRoadmapTarget) -> list[str]:
        annual_purchase = weekly_target.targets["annual_purchase"].format()
        required_borrowing = weekly_target.targets["required_borrowing"].format()
        rooms = weekly_target.targets["rooms"].format()
        return [
            "#### 今週の行動KPI候補",
            "",
            f"- [ ] 保有室数目標 {rooms} に向けて、候補物件・融資・売却案件を棚卸しする #roadmap #kpi",
            f"- [ ] 年間買付額 {annual_purchase} ペースに対して、今週の買付候補を更新する #roadmap #buy",
            f"- [ ] 必要借入実行額 {required_borrowing} ペースに対して、銀行面談・資料提出の進捗を更新する #roadmap #finance",
            "- [ ] 実績値をDaily/Weekly Noteに追記し、来週目標を再計算する #roadmap #review",
        ]


class ObsidianRoadmapWriter:
    def __init__(self, settings: Settings):
        self.settings = settings

    def write_daily_friday_targets(self, weekly_targets: list[WeeklyRoadmapTarget], planner: RoadmapPlannerAgent) -> list[Path]:
        written: list[Path] = []
        for weekly_target in weekly_targets:
            path = self._daily_note_path(weekly_target.target_date)
            content = planner.render_markdown([weekly_target])
            self._write_marker(path, content)
            written.append(path)
        return written

    def write_monthly_summary(self, weekly_targets: list[WeeklyRoadmapTarget], planner: RoadmapPlannerAgent) -> Path:
        if not weekly_targets:
            raise ValueError("weekly_targets is empty")
        first = weekly_targets[0].target_date
        path = self.settings.obsidian_vault_path / "AI-CRM" / "roadmap" / f"{first:%Y-%m}-weekly-targets.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(planner.render_markdown(weekly_targets), encoding="utf-8")
        return path

    def _daily_note_path(self, target_date: date) -> Path:
        filename = target_date.strftime(self.settings.daily_note_date_format) + ".md"
        return self.settings.obsidian_vault_path / self.settings.daily_notes_dir / filename

    def _write_marker(self, path: Path, body: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        old_text = path.read_text(encoding="utf-8") if path.exists() else f"# {path.stem}\n\n"
        if path.exists():
            backup_dir = self.settings.obsidian_vault_path / "AI-CRM" / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / f"{path.stem}.{datetime.now():%Y%m%d%H%M%S}.bak.md"
            shutil.copy2(path, backup_path)
        new_text = upsert_marker(old_text, body, ROADMAP_MARKER_START, ROADMAP_MARKER_END)
        path.write_text(new_text, encoding="utf-8")


class ExternalCliReviewAgent:
    """Runs local AI CLIs such as Codex or Claude CLI against generated roadmap markdown.

    This does not call any API directly. The command is executed locally and may itself use
    whatever authentication the user has configured for that CLI.
    """

    def __init__(self, commands: Iterable[str], timeout_seconds: int = 180):
        self.commands = [command for command in commands if command.strip()]
        self.timeout_seconds = timeout_seconds

    def review(self, markdown: str) -> str:
        if not self.commands:
            return "CLIレビューコマンドが未指定のため、レビューは実行していません。"
        outputs: list[str] = []
        with TemporaryDirectory() as tmp:
            prompt_path = Path(tmp) / "roadmap_review_prompt.md"
            prompt_path.write_text(self._build_prompt(markdown), encoding="utf-8")
            for command in self.commands:
                result = self._run_command(command, prompt_path)
                outputs.append(result)
        return "\n\n".join(outputs)

    def _run_command(self, command: str, prompt_path: Path) -> str:
        if "{input}" in command:
            command_to_run = command.replace("{input}", str(prompt_path))
        else:
            command_to_run = f"{command} < {prompt_path}"
        completed = subprocess.run(
            command_to_run,
            shell=True,
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
            check=False,
        )
        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()
        status = "success" if completed.returncode == 0 else f"failed({completed.returncode})"
        body = stdout or stderr or "出力なし"
        return f"### `{command}`: {status}\n\n{body}"

    def _build_prompt(self, markdown: str) -> str:
        return "\n".join(
            [
                "あなたは事業計画レビュー担当です。以下の10年ロードマップ逆算週次目標を確認してください。",
                "APIではなくローカルCLIレビューとして実行されています。",
                "出力は以下の観点で短く具体的にしてください。",
                "",
                "1. 数字の違和感",
                "2. 今週やるべきKPI",
                "3. 来週へ向けたリスク",
                "4. Obsidianに追記すべきメモ",
                "",
                markdown,
            ]
        )


def upsert_marker(text: str, body: str, start_marker: str, end_marker: str) -> str:
    block = f"{start_marker}\n{body.rstrip()}\n{end_marker}"
    if start_marker in text and end_marker in text:
        before = text.split(start_marker, 1)[0].rstrip()
        after = text.split(end_marker, 1)[1].lstrip()
        return f"{before}\n\n{block}\n\n{after}".rstrip() + "\n"
    return text.rstrip() + "\n\n" + block + "\n"


def _next_fridays(start_date: date, weeks: int) -> list[date]:
    friday = 4
    days_until_friday = (friday - start_date.weekday()) % 7
    first_friday = start_date + timedelta(days=days_until_friday)
    return [first_friday + timedelta(days=7 * index) for index in range(weeks)]


def _week_label(index: int) -> str:
    labels = {1: "今週", 2: "来週", 3: "再来週", 4: "4週間後"}
    return labels.get(index, f"{index}週間後")


def _format_number(value: float, unit: str) -> str:
    if unit == "室":
        return str(int(round(value)))
    if abs(value) >= 100:
        return f"{value:.0f}"
    if abs(value) >= 10:
        return f"{value:.1f}".rstrip("0").rstrip(".")
    if abs(value) >= 1:
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return f"{value:.2f}".rstrip("0").rstrip(".")


def commands_from_env() -> list[str]:
    raw = os.getenv("ROADMAP_REVIEW_COMMANDS", "")
    return [item.strip() for item in raw.split("||") if item.strip()]
