from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

# Allow both `python scripts/smoke_test.py` and `python -m scripts.smoke_test`.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from obsidian_calendar_agent.config import Settings
from obsidian_calendar_agent.parser import ObsidianTaskParserAgent
from obsidian_calendar_agent.planner import HourlyPlannerAgent


def make_settings(vault_path: Path) -> Settings:
    return Settings(
        obsidian_vault_path=vault_path,
        daily_notes_dir="Daily",
        daily_note_date_format="%Y-%m-%d",
        todo_files=["TODO.md"],
        timezone="Asia/Tokyo",
        workday_start="09:00",
        workday_end="18:00",
        slot_minutes=60,
        default_task_minutes=60,
        google_calendar_id="primary",
        google_credentials_file=vault_path / "credentials.json",
        google_token_file=vault_path / "token.json",
        telegram_bot_token=None,
        telegram_chat_id=None,
        agent_api_key=None,
        enable_scheduler=False,
        daily_digest_time="07:30",
    )


def main() -> None:
    target_date = date(2026, 5, 13)
    with TemporaryDirectory() as tmp:
        vault = Path(tmp) / "vault"
        daily_dir = vault / "Daily"
        daily_dir.mkdir(parents=True)

        (daily_dir / "2026-05-13.md").write_text(
            "\n".join(
                [
                    "# 2026-05-13",
                    "",
                    "## Tasks",
                    "- [ ] 提案書の構成を作る ⏱ 2h #p1",
                    "- [ ] 営業資料レビュー ⏰ 15:00 ⏱ 1h",
                    "- [x] 完了済みタスク",
                    "- [ ] カレンダー登録しないタスク #gcal-skip",
                ]
            ),
            encoding="utf-8",
        )
        (vault / "TODO.md").write_text(
            "\n".join(
                [
                    "- [ ] 契約書レビュー 📅 2026-05-13 ⏱ 2h #p1",
                    "- [ ] 別日のタスク 📅 2026-05-14 ⏱ 1h",
                    "- [ ] 今日の雑務 #today ⏱ 1h",
                    "- [ ] 日付なしなので対象外",
                ]
            ),
            encoding="utf-8",
        )

        settings = make_settings(vault)
        tasks = ObsidianTaskParserAgent(settings).parse_for_date(target_date)
        blocks = HourlyPlannerAgent(settings).plan(tasks, target_date)

        result = {
            "status": "ok",
            "target_date": target_date.isoformat(),
            "task_count": len(tasks),
            "block_count": len(blocks),
            "tasks": [task.to_dict() for task in tasks],
            "blocks": [block.to_dict() for block in blocks],
        }

        assert result["task_count"] == 4, result
        assert result["block_count"] == 6, result
        assert blocks[0].start.hour == 9, result
        assert any(block.start.hour == 15 for block in blocks), result

        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
