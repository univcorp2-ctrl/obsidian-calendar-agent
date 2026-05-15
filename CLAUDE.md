# CLAUDE.md

このリポジトリは、Claude Codeで作業する前提のプロジェクトです。

## プロジェクト目的

Obsidianを中心にした個人用タスクCRM / 秘書エージェントを作る。

主な機能:

- Obsidian Inbox / Daily Note / Weekly Noteを読み取る
- メモやタスクを開発、調査、資料作成、連絡、事務などへ分類する
- 専門エージェント向けの依頼書を `AI-CRM/agent_outbox/` に作る
- 週次目標をWBSへ分解する
- 10年ロードマップから、今週・来週・再来週・4週間後の金曜日目標を逆算する
- ObsidianのDaily Noteへmarker内だけ安全に書き込む
- Google Calendarへ1時間単位で予定登録する
- Telegramへ秘書レポートを送る
- Custom GPT ActionsからFastAPIを呼べるようにする

## 最重要ルール

1. 外部サービスへ書き込む処理は、まずdry-runで確認する。
2. Obsidian Markdownを更新するときは、marker内だけ更新する。
3. ユーザーの自由記述を壊さない。
4. 既存ノートを更新する前にバックアップを作る。
5. Google Calendar / Telegram / Claude / Codexなどの認証情報をコミットしない。
6. 変更後は必ず `bash scripts/verify_all.sh` を通す。
7. CI/CDが落ちる変更を残さない。
8. GitHub ActionsでAIが勝手に本番書き込みする構成にはしない。

## まず読むファイル

- `docs/requirements.md`
- `docs/architecture.md`
- `docs/roadmap-weekly-targets.md`
- `docs/ci-cd.md`
- `data/roadmap_targets_10yr.json`
- `obsidian_calendar_agent/crm/roadmap.py`
- `tests/test_roadmap.py`

## よく使うコマンド

### 全検証

```bash
bash scripts/verify_all.sh
```

### 単体テスト

```bash
pytest -q
```

### 外部APIなしスモークテスト

```bash
python scripts/smoke_test.py
```

### 10年ロードマップから週次金曜目標を生成

```bash
python -m obsidian_calendar_agent.cli roadmap-weekly --start-date 2026-05-11 --weeks 4
```

### JSONで確認

```bash
python -m obsidian_calendar_agent.cli roadmap-weekly --start-date 2026-05-11 --weeks 4 --json
```

### Obsidianへ書き込み

```bash
python -m obsidian_calendar_agent.cli roadmap-weekly --start-date 2026-05-11 --weeks 4 --write
```

### Docker CD Smoke相当

```bash
docker build -t obsidian-calendar-agent:local .
docker run -d --rm --name obsidian-calendar-agent-local -p 8000:8000 -e AGENT_API_KEY=local-test-key -e ENABLE_SCHEDULER=false obsidian-calendar-agent:local
curl --fail http://localhost:8000/health
docker stop obsidian-calendar-agent-local
```

## Claude Codeでの作業フロー

1. まず要件を `docs/requirements.md` と `docs/architecture.md` で確認する。
2. 実装前に、変更するファイルとテスト方針を短く整理する。
3. 変更する。
4. `bash scripts/verify_all.sh` を実行する。
5. 失敗したら、失敗ログを読み、原因を特定して修正する。
6. 再度 `bash scripts/verify_all.sh` を実行する。
7. 成功したら、変更点・テスト結果・注意点を報告する。

## Claude Code用コマンド

このリポジトリには `.claude/commands/` を用意している。

Claude Code内で `/` を入力すると、次のプロジェクトコマンドを使える。

- `/verify` : 全検証を実行し、失敗時は修正方針を出す
- `/fix-ci` : CI/CD失敗を前提に、ログ確認、修正、再テストまで行う
- `/roadmap-weekly` : 10年ロードマップから週次金曜目標を生成する
- `/docker-smoke` : CD Smoke相当のDocker起動確認を行う

## Roadmap Reverse Plannerの注意

`data/roadmap_targets_10yr.json` は、ユーザー提供の10年ロードマップ画像から構造化した基準データ。

初期版の計算式:

```text
週次目標 = 前マイルストーン + (次マイルストーン - 前マイルストーン) × 経過日数 / 区間日数
```

これは機械的な目安。将来は実績値、銀行面談数、買付候補、売却予定、仲介パイプラインを反映して補正する。

## Markdown更新ルール

Daily Noteのロードマップ欄はこの範囲だけ更新する。

```md
<!-- AI_ROADMAP_TARGETS:START -->
AI生成欄
<!-- AI_ROADMAP_TARGETS:END -->
```

このmarker外は絶対に書き換えない。

## 認証情報

以下はコミット禁止。

- `.env`
- `credentials.json`
- `token.json`
- Telegram Bot Token
- Google OAuth Token
- Claude / Codex / OpenAI / Anthropic API Key

## 実装時の優先順位

1. テストが通ること
2. Obsidianの自由記述を壊さないこと
3. 外部API書き込みはdry-run優先
4. Claude Code / Codex CLI / GitHub Actionsで再現可能なこと
5. 後からCustom GPT Actionsへ接続しやすいこと
