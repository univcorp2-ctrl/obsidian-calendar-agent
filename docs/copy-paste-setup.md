# コピペ用: 前準備から実行確認まで

この手順は macOS / Linux を前提にしています。Windows PowerShell 用も下にあります。

## 0. まず外部APIなしで動作確認する

Google Calendar / Telegram の設定前に、Obsidian Markdown の読み取りと1時間単位への分解だけを確認します。

```bash
git clone https://github.com/univcorp2-ctrl/obsidian-calendar-agent.git
cd obsidian-calendar-agent

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

python scripts/smoke_test.py
pytest -q
```

成功すると、`task_count` と `block_count` が表示されます。

## 1. .env を作る

```bash
cp .env.example .env
python - <<'PY'
import secrets
print('AGENT_API_KEY=' + secrets.token_urlsafe(32))
PY
```

表示された `AGENT_API_KEY=...` を `.env` の `AGENT_API_KEY` に貼り付けます。

## 2. Obsidian Vault の場所を設定する

```bash
pwd
```

Obsidian Vault の絶対パスを確認して、`.env` を編集します。

```env
OBSIDIAN_VAULT_PATH=/Users/YOUR_NAME/Documents/ObsidianVault
DAILY_NOTES_DIR=Daily
TODO_FILES=TODO.md,Projects/Inbox.md
TIMEZONE=Asia/Tokyo
WORKDAY_START=09:00
WORKDAY_END=18:00
```

Daily Note 例:

```md
# 2026-05-13

## Tasks
- [ ] 提案書の構成を作る ⏱ 2h #p1
- [ ] 営業資料レビュー ⏰ 15:00 ⏱ 1h
- [ ] 経費精算 ⏱ 30m
- [ ] カレンダー登録しないタスク #gcal-skip
```

TODO.md 例:

```md
- [ ] 契約書レビュー 📅 2026-05-13 ⏱ 2h #p1
- [ ] 今日の雑務 #today ⏱ 1h
```

## 3. Google Calendar API の前準備

Google Cloud Console で以下を行います。

1. プロジェクトを作成または選択
2. Google Calendar API を有効化
3. OAuth consent screen を設定
4. OAuth Client ID を作成
5. Application type はまず `Desktop app` を選択
6. JSON をダウンロードして、リポジトリ直下に `credentials.json` として保存

その後、初回認可を実行します。

```bash
source .venv/bin/activate
python -m obsidian_calendar_agent.cli auth-google
```

ブラウザでGoogle認可を完了すると、`token.json` が生成されます。

## 4. Google Calendar へ登録せずにドライランする

```bash
source .venv/bin/activate
python -m obsidian_calendar_agent.cli sync --date 2026-05-13 --dry-run
```

今日の日付で実行する場合:

```bash
python -m obsidian_calendar_agent.cli sync --dry-run
```

## 5. Google Calendar へ本登録する

```bash
source .venv/bin/activate
python -m obsidian_calendar_agent.cli sync --date 2026-05-13
```

今日の日付で本登録する場合:

```bash
python -m obsidian_calendar_agent.cli sync
```

## 6. Telegram Bot の前準備

Telegram で `@BotFather` を開き、`/newbot` でBotを作ります。発行されたBot Tokenを `.env` に入れます。

自分の `chat_id` を取得する簡易手順:

1. 作ったBotにTelegram上で何かメッセージを送る
2. 以下を実行する

```bash
source .venv/bin/activate
python - <<'PY'
import os, httpx
from dotenv import load_dotenv
load_dotenv()
token = os.environ['TELEGRAM_BOT_TOKEN']
url = f'https://api.telegram.org/bot{token}/getUpdates'
print(httpx.get(url, timeout=20).text)
PY
```

出力内の `message.chat.id` を `.env` の `TELEGRAM_CHAT_ID` に入れます。

```env
TELEGRAM_BOT_TOKEN=123456:xxxxxxxx
TELEGRAM_CHAT_ID=123456789
```

## 7. 今日の予定をTelegramへ送る

```bash
source .venv/bin/activate
python -m obsidian_calendar_agent.cli telegram-today
```

日付指定:

```bash
python -m obsidian_calendar_agent.cli telegram-today --date 2026-05-13
```

## 8. APIサーバーを起動する

```bash
source .venv/bin/activate
uvicorn obsidian_calendar_agent.app:app --host 0.0.0.0 --port 8000
```

ヘルスチェック:

```bash
curl http://localhost:8000/health
```

ドライランAPI:

```bash
curl -X POST http://localhost:8000/sync/today \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_AGENT_API_KEY" \
  -d '{"date":"2026-05-13","dry_run":true}'
```

本登録API:

```bash
curl -X POST http://localhost:8000/sync/today \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_AGENT_API_KEY" \
  -d '{"dry_run":false}'
```

Telegram送信API:

```bash
curl -X POST http://localhost:8000/telegram/send-today \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_AGENT_API_KEY" \
  -d '{}'
```

## 9. Custom GPT Actions に接続する

1. APIをHTTPSで公開します。
2. `openapi/gpt-actions.yaml` の `servers.url` を公開URLに変更します。
3. GPT Builder の Actions に schema を貼り付けます。
4. Authentication は `API Key` を選びます。
5. Header名は `X-API-Key` にします。
6. 値は `.env` の `AGENT_API_KEY` と同じにします。

GPTへの依頼例:

```text
今日のObsidianタスクをGoogleカレンダーへ1時間単位で登録して。まずドライランで確認して。
```

## Windows PowerShell版: 外部APIなしの動作確認

```powershell
git clone https://github.com/univcorp2-ctrl/obsidian-calendar-agent.git
cd obsidian-calendar-agent

py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

python scripts/smoke_test.py
pytest -q
```
