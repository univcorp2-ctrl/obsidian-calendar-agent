from __future__ import annotations

from datetime import date

from obsidian_calendar_agent.config import Settings
from obsidian_calendar_agent.parser import ObsidianTaskParserAgent


def make_settings(tmp_path):
    return Settings(
        obsidian_vault_path=tmp_path,
        daily_notes_dir="Daily",
        daily_note_date_format="%Y-%m-%d",
        todo_files=["TODO.md"],
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


def test_parse_daily_note_tasks(tmp_path):
    daily = tmp_path / "Daily"
    daily.mkdir()
    (daily / "2026-05-13.md").write_text(
        "\n".join([
            "# 2026-05-13",
            "- [ ] 提案書の構成を作る ⏱ 2h #p1",
            "- [ ] レビュー ⏰ 15:00 ⏱ 1h",
            "- [x] 完了済み",
            "- [ ] 無視する #gcal-skip",
        ]),
        encoding="utf-8",
    )
    parser = ObsidianTaskParserAgent(make_settings(tmp_path))
    tasks = parser.parse_for_date(date(2026, 5, 13))

    assert len(tasks) == 2
    assert tasks[0].title == "提案書の構成を作る"
    assert tasks[0].duration_minutes == 120
    assert tasks[0].priority == 1
    assert tasks[1].fixed_start.isoformat() == "15:00:00"


def test_parse_todo_file_only_for_target_date_or_today(tmp_path):
    (tmp_path / "Daily").mkdir()
    (tmp_path / "TODO.md").write_text(
        "\n".join([
            "- [ ] 契約書レビュー 📅 2026-05-13 ⏱ 2h",
            "- [ ] 別日のタスク 📅 2026-05-14",
            "- [ ] 今日の雑務 #today",
            "- [ ] 日付なしなので対象外",
        ]),
        encoding="utf-8",
    )
    parser = ObsidianTaskParserAgent(make_settings(tmp_path))
    tasks = parser.parse_for_date(date(2026, 5, 13))

    assert [task.title for task in tasks] == ["契約書レビュー", "今日の雑務"]
