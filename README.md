# Obsidian Calendar Agent

[![CI](https://github.com/univcorp2-ctrl/obsidian-calendar-agent/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/univcorp2-ctrl/obsidian-calendar-agent/actions/workflows/ci.yml)
[![CD Smoke](https://github.com/univcorp2-ctrl/obsidian-calendar-agent/actions/workflows/cd.yml/badge.svg?branch=main)](https://github.com/univcorp2-ctrl/obsidian-calendar-agent/actions/workflows/cd.yml)

Obsidian の Daily Note / TODO リストを読み取り、タスクを 1 時間単位の Google Calendar イベントへ自動登録し、毎朝 Telegram に今日の予定を配信する Python/FastAPI アプリです。

加えて、10年ロードマップから今週・来週・再来週・4週間後の金曜日目標数字を逆算し、ObsidianのDaily Noteへ自動書き込みするCLIを備えています。

## できること

- Obsidian Vault 内の Markdown から未完了タスク `- [ ]` を抽出
- Daily Note の日付をもとに、その日のタスクとして扱う
- TODO ファイル内の `📅 YYYY-MM-DD` / `due: YYYY-MM-DD` / `#today` を抽出
- `⏱ 2h` / `duration: 90m` などを読み、1 時間単位に分解
- Google Calendar の既存予定を避けて登録
- Telegram に今日の予定を自動配信
- 10年ロードマップから週次金曜目標を逆算
- Local CLIのCodex / Claudeによるロードマップレビュー
- Custom GPT Actions から `/sync/today` などを呼び出し可能

## 外部APIなしの確認

```bash
python scripts/smoke_test.py
pytest -q
python -m obsidian_calendar_agent.cli roadmap-weekly --start-date 2026-05-11 --weeks 4 --json
```

またはまとめて:

```bash
bash scripts/verify_all.sh
```

## 10年ロードマップから週次目標を作る

Markdownで確認:

```bash
python -m obsidian_calendar_agent.cli roadmap-weekly --start-date 2026-05-11 --weeks 4
```

Obsidianへ書き込み:

```bash
python -m obsidian_calendar_agent.cli roadmap-weekly --start-date 2026-05-11 --weeks 4 --write
```

Claude / Codex CLIでレビューしてから書き込み:

```bash
python -m obsidian_calendar_agent.cli roadmap-weekly \
  --start-date 2026-05-11 \
  --weeks 4 \
  --review \
  --review-command 'claude --print < {input}' \
  --write
```

## 全体構成

```text
Obsidian Vault
  └─ Daily Notes / TODO.md
        ↓ Markdown Parser Agent
Task Splitter / Hourly Planner Agent
        ↓
Google Calendar Writer Agent
        ↓
Telegram Daily Digest Agent
        ↑
Custom GPT Actions → FastAPI API

10-year Roadmap JSON
        ↓
Roadmap Reverse Planner
        ↓
Weekly Friday Target Writer
        ↓
Local CLI AI Review: Claude / Codex
```

## 推奨タスク記法

Daily Note 例: `Daily/2026-05-13.md`

```md
# 2026-05-13

## Tasks
- [ ] 提案書の構成を作る ⏱ 2h #p1
- [ ] 経費精算を処理する ⏱ 30m
- [ ] 15:00から営業資料レビュー ⏰ 15:00 ⏱ 1h
- [x] 完了済みタスク
- [ ] カレンダー登録しないタスク #gcal-skip
```

## セットアップ

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

`.env` の例:

```env
OBSIDIAN_VAULT_PATH=/absolute/path/to/your/ObsidianVault
DAILY_NOTES_DIR=Daily
DAILY_NOTE_DATE_FORMAT=%Y-%m-%d
TODO_FILES=TODO.md,Projects/Inbox.md
TIMEZONE=Asia/Tokyo
WORKDAY_START=09:00
WORKDAY_END=18:00
GOOGLE_CALENDAR_ID=primary
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.json
TELEGRAM_BOT_TOKEN=123456:xxxx
TELEGRAM_CHAT_ID=123456789
AGENT_API_KEY=change-me-long-random
ENABLE_SCHEDULER=false
DAILY_DIGEST_TIME=07:30
```

## Google Calendar API

Google Cloud Console で Calendar API を有効化し、OAuth クライアントの `credentials.json` を作成してプロジェクト直下へ置きます。

初回だけ以下を実行して OAuth 認可を完了します。

```bash
python -m obsidian_calendar_agent.cli auth-google
```

生成された `token.json` は秘密情報なので Git に入れないでください。

## 使い方

ドライラン:

```bash
python -m obsidian_calendar_agent.cli sync --date 2026-05-13 --dry-run
```

Google Calendar に登録:

```bash
python -m obsidian_calendar_agent.cli sync --date 2026-05-13
```

Telegram に今日の予定を送信:

```bash
python -m obsidian_calendar_agent.cli telegram-today --date 2026-05-13
```

API サーバー起動:

```bash
uvicorn obsidian_calendar_agent.app:app --host 0.0.0.0 --port 8000
```

## CI/CD

CI:

```bash
bash scripts/verify_all.sh
```

失敗時のローカル修正ループ:

```bash
export REPAIR_COMMAND='claude --print < {log}'
bash scripts/ci_repair_loop.sh
```

CD SmokeではDocker buildとAPI `/health` の確認を行います。

## 詳細ドキュメント

- `docs/requirements.md`
- `docs/architecture.md`
- `docs/roadmap-weekly-targets.md`
- `docs/ci-cd.md`
- `docs/plugin-recommendations.md`
