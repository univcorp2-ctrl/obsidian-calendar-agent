# Obsidian Calendar Agent

Obsidian の Daily Note / TODO リストを読み取り、タスクを 1 時間単位の Google Calendar イベントへ自動登録し、毎朝 Telegram に今日の予定を配信する Python/FastAPI アプリです。

## できること

- Obsidian Vault 内の Markdown から未完了タスク `- [ ]` を抽出
- Daily Note の日付をもとに、その日のタスクとして扱う
- TODO ファイル内の `📅 YYYY-MM-DD` / `due: YYYY-MM-DD` / `#today` を抽出
- `⏱ 2h` / `duration: 90m` などを読み、1 時間単位に分解
- Google Calendar の既存予定を避けて登録
- Telegram に今日の予定を自動配信
- Custom GPT Actions から `/sync/today` などを呼び出し可能

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

TODO ファイル例: `TODO.md`

```md
- [ ] 契約書レビュー 📅 2026-05-13 ⏱ 2h #p1
- [ ] 今日やる細かい雑務 #today ⏱ 1h
```

## セットアップ

### 1. Python 環境

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Google Calendar API

Google Cloud Console で Calendar API を有効化し、OAuth クライアントの `credentials.json` を作成してプロジェクト直下へ置きます。

初回だけ以下を実行して OAuth 認可を完了します。

```bash
python -m obsidian_calendar_agent.cli auth-google
```

生成された `token.json` は秘密情報なので Git に入れないでください。

### 3. Telegram Bot

BotFather で Bot を作り、`.env` に `TELEGRAM_BOT_TOKEN` と `TELEGRAM_CHAT_ID` を設定します。

### 4. .env 設定

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

## 使い方

### ドライラン

```bash
python -m obsidian_calendar_agent.cli sync --date 2026-05-13 --dry-run
```

### Google Calendar に登録

```bash
python -m obsidian_calendar_agent.cli sync --date 2026-05-13
```

### Telegram に今日の予定を送信

```bash
python -m obsidian_calendar_agent.cli telegram-today --date 2026-05-13
```

### API サーバー起動

```bash
uvicorn obsidian_calendar_agent.app:app --host 0.0.0.0 --port 8000
```

## Custom GPT 連携

1. この API を HTTPS で公開します。例: Cloud Run / Render / Railway / VPS + Nginx など。
2. `openapi/gpt-actions.yaml` の `servers.url` を公開 URL に変更します。
3. GPT Builder の Actions に OpenAPI schema を貼り付けます。
4. Authentication は API Key を選び、Header 名を `X-API-Key` にします。
5. `.env` の `AGENT_API_KEY` と同じ値を GPT Actions 側に登録します。

GPT に依頼する例:

```text
今日のObsidianタスクをGoogleカレンダーに1時間単位で登録して。まずはドライランで確認して。
```

## 自動実行

`.env` の `ENABLE_SCHEDULER=true` にすると、API 起動中に以下を自動実行します。

- 毎時: 今日の Obsidian タスクを Google Calendar に同期
- 毎日 `DAILY_DIGEST_TIME`: Telegram に今日の予定を送信

本番では systemd / Docker / Cloud Run Jobs / cron など、落ちても復帰する仕組みと組み合わせてください。

## テスト

```bash
pytest
```

## 注意事項

- Google Calendar へ登録済みのイベントは、タスクのハッシュから生成したイベント ID で重複登録を防ぎます。
- Telegram Bot のメッセージは通常チャットと同じエンドツーエンド暗号ではないため、機密情報を送らない運用にしてください。
- Obsidian Vault をクラウド同期している場合、同期競合や未同期ファイルに注意してください。
