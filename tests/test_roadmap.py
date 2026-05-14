from __future__ import annotations

from datetime import date
from pathlib import Path

from obsidian_calendar_agent.config import Settings
from obsidian_calendar_agent.crm.roadmap import ObsidianRoadmapWriter, RoadmapPlannerAgent, upsert_marker


def settings(tmp_path: Path) -> Settings:
    return Settings(
        obsidian_vault_path=tmp_path,
        daily_notes_dir="Daily",
        daily_note_date_format="%Y-%m-%d",
        todo_files=[],
        timezone="Asia/Tokyo",
        workday_start="09:00",
        workday_end="18:00",
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


def test_roadmap_generates_four_friday_targets() -> None:
    planner = RoadmapPlannerAgent.from_json()
    targets = planner.weekly_targets(date(2026, 5, 11), weeks=4)

    assert [target.target_date.isoformat() for target in targets] == [
        "2026-05-15",
        "2026-05-22",
        "2026-05-29",
        "2026-06-05",
    ]
    assert targets[0].targets["net_assets"].low > 0.6
    assert targets[0].targets["rooms"].high > 26
    assert "10年ロードマップ逆算" in planner.render_markdown(targets)


def test_marker_upsert_preserves_user_text() -> None:
    original = "# 2026-05-15\n\nユーザーの自由記述\n"
    updated = upsert_marker(original, "AI本文", "<!-- START -->", "<!-- END -->")

    assert "ユーザーの自由記述" in updated
    assert "<!-- START -->" in updated
    assert "AI本文" in updated
    assert "<!-- END -->" in updated


def test_roadmap_writer_creates_daily_notes_and_summary(tmp_path: Path) -> None:
    planner = RoadmapPlannerAgent.from_json()
    targets = planner.weekly_targets(date(2026, 5, 11), weeks=2)
    writer = ObsidianRoadmapWriter(settings(tmp_path))

    written = writer.write_daily_friday_targets(targets, planner)
    summary = writer.write_monthly_summary(targets, planner)

    assert len(written) == 2
    assert all(path.exists() for path in written)
    assert summary.exists()
    assert "AI_ROADMAP_TARGETS" in written[0].read_text(encoding="utf-8")
    assert "今週" in written[0].read_text(encoding="utf-8")
