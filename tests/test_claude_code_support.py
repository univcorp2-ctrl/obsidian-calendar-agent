from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_claude_project_memory_exists_and_mentions_verification() -> None:
    path = ROOT / "CLAUDE.md"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "bash scripts/verify_all.sh" in text
    assert "AI_ROADMAP_TARGETS" in text
    assert "認証情報" in text


def test_claude_commands_exist() -> None:
    commands_dir = ROOT / ".claude" / "commands"
    expected = {
        "verify.md",
        "fix-ci.md",
        "roadmap-weekly.md",
        "docker-smoke.md",
    }
    assert commands_dir.exists()
    assert expected.issubset({path.name for path in commands_dir.glob("*.md")})


def test_claude_verify_command_uses_same_ci_entrypoint() -> None:
    text = (ROOT / ".claude" / "commands" / "verify.md").read_text(encoding="utf-8")
    assert "bash scripts/verify_all.sh" in text
    assert "pytest" not in text or "scripts/verify_all.sh" in text


def test_claude_fix_ci_command_does_not_delete_tests_or_use_production_services() -> None:
    text = (ROOT / ".claude" / "commands" / "fix-ci.md").read_text(encoding="utf-8")
    assert "テストを削除" in text
    assert "外部APIへ本番書き込み" in text
    assert "bash scripts/verify_all.sh" in text


def test_claude_settings_example_is_not_active_settings() -> None:
    assert (ROOT / ".claude" / "settings.example.json").exists()
    # Active project settings can run hooks automatically. Keep only a reviewed example in the repo.
    assert not (ROOT / ".claude" / "settings.json").exists()
