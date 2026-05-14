# アーキテクチャ: Obsidian Inbox 自動タスクCRM / 秘書エージェント

## 1. 全体構成

このシステムは、Obsidian Vaultを中心にしたローカルファーストの自動タスクCRMである。

```text
User
  ↓
Obsidian Vault
  ├─ Inbox.md
  ├─ Daily/*.md
  ├─ Weekly/*.md
  └─ AI-CRM/*
      ↓
Inbox Reader
      ↓
Task Classifier / Router
      ↓
Agent Outbox Generator
      ↓
WBS Generator
      ↓
Progress Calculator
      ↓
Obsidian Writer
      ↓
Google Calendar Scheduler
      ↓
Telegram Secretary Digest
      ↑
Custom GPT Actions / FastAPI

10-year Roadmap Image / Structured JSON
      ↓
Roadmap Reverse Planner
      ↓
Weekly Friday Target Generator
      ↓
Local CLI AI Review: Codex CLI / Claude CLI
      ↓
Obsidian Daily Friday Note Writer
```

## 2. 新規追加: Roadmap Reverse Planner

### 2.1 役割

添付された10年ロードマップ画像の数値を `data/roadmap_targets_10yr.json` として構造化し、現在地から未来の年末目標までを逆算して、今週・来週・再来週・4週間後の金曜日時点の目標数字を作る。

### 2.2 入力

```text
data/roadmap_targets_10yr.json
```

主なマイルストーン:

- 2026-05-11 現在地
- 2026-12-31 2026年度末
- 2028-12-31 2028年末
- 2029-12-31 2029年末
- 2035-12-31 2035年末

対象指標:

- 純資産
- 現金
- 保有室数
- 月自由資金
- 年間買付額
- 年間売却額
- 仲介売上
- 年間利益
- 必要借入実行額

### 2.3 計算方式

初期版は日数按分で計算する。

```text
週次目標 = 前マイルストーン + (次マイルストーン - 前マイルストーン) × 経過日数 / 区間日数
```

例:

```text
現在地 2026-05-11
次目標 2026-12-31
生成日 2026-05-15金曜日

進捗率 = 4日 / 234日
```

### 2.4 出力

金曜日Daily Note:

```text
Daily/2026-05-15.md
Daily/2026-05-22.md
Daily/2026-05-29.md
Daily/2026-06-05.md
```

月次サマリー:

```text
AI-CRM/roadmap/2026-05-weekly-targets.md
```

### 2.5 安全更新

Daily Noteには以下のmarker内だけを更新する。

```md
<!-- AI_ROADMAP_TARGETS:START -->
AI生成領域
<!-- AI_ROADMAP_TARGETS:END -->
```

既存のユーザー文章は変更しない。更新前に `AI-CRM/backups/` へバックアップする。

## 3. Local CLI AI Review

### 3.1 目的

週次目標数字は機械的な日数按分だけでは不十分な場合がある。そのため、Codex CLI / Claude CLIなどのローカルCLIにレビューさせる。

APIを直接呼ばず、ユーザーのローカル環境にインストール済みのCLIをサブプロセスとして呼ぶ。

### 3.2 コマンド指定

CLI引数:

```bash
python -m obsidian_calendar_agent.cli roadmap-weekly \
  --start-date 2026-05-11 \
  --weeks 4 \
  --review \
  --review-command 'claude --print < {input}'
```

環境変数:

```bash
export ROADMAP_REVIEW_COMMANDS='claude --print < {input}||codex exec --file {input}'
```

### 3.3 出力

CLIレビュー結果は、生成Markdownの `## CLI AIレビュー` に追記される。

## 4. CI/CD

### 4.1 CI

`.github/workflows/ci.yml` で以下を実行する。

```text
python -m compileall obsidian_calendar_agent scripts
python scripts/smoke_test.py
pytest -q
python -m obsidian_calendar_agent.cli roadmap-weekly --start-date 2026-05-11 --weeks 4 --json
```

### 4.2 CD Smoke

`.github/workflows/cd.yml` で以下を実行する。

```text
Docker build
Docker container start
GET /health
```

本番デプロイはまだ行わない。まずDockerイメージとして起動できることだけを確認する。

### 4.3 失敗時の修正ループ

GitHub Actions自体に勝手にコードを書き換えさせるのは危険なので、自動修正はローカルCLI修正ループとして提供する。

```bash
export REPAIR_COMMAND='claude --print < {log}'
bash scripts/ci_repair_loop.sh
```

このスクリプトは以下を行う。

```text
1. scripts/verify_all.sh を実行
2. 失敗ログを .repair/last_failure.log に保存
3. REPAIR_COMMAND にログを渡す
4. 修正後に再テスト
5. 成功するまで指定回数繰り返す
```

## 5. 既存コンポーネント

### 5.1 Inbox Reader

- `Inbox.md` または `Inbox/` を読む
- 未処理のメモ、タスク、アイデアを抽出する

### 5.2 Task Classifier / Router

- Inbox項目を分類する
- 専門エージェントを決める
- 分類理由を保存する

分類カテゴリ:

```text
development
research
writing
communication
admin
planning
calendar
unknown
```

### 5.3 Agent Outbox Generator

- 専門エージェントに渡す依頼書Markdownを生成する
- 初期版では外部AIを直接実行せず、依頼書だけ作る

### 5.4 WBS Generator

- 大きな目標を実行可能な小タスクへ分解する
- タスクごとに完了条件、推定工数、担当エージェントを付ける

### 5.5 Progress Calculator

```text
進捗率 = 完了済み子タスク数 / 全子タスク数 * 100
```

### 5.6 Google Calendar Scheduler

- WBSタスクを1時間単位の予定へ変換する
- 既存予定を避ける
- Google Calendarへ登録する

### 5.7 Telegram Secretary Digest

- 今日の予定
- 進捗率
- 遅延タスク
- 秘書コメント

をTelegramへ送信する。

## 6. 推奨Vault構成

```text
ObsidianVault/
  Inbox.md
  Daily/
    2026-05-15.md
  Weekly/
    2026-W20.md
  AI-CRM/
    roadmap/
      2026-05-weekly-targets.md
    agent_outbox/
      development/
      research/
      writing/
      communication/
      admin/
    agent_results/
    logs/
    backups/
```

## 7. 推奨実装順序

1. Roadmap Reverse Planner
2. CI/CD Smoke
3. Markdown安全更新
4. Inbox Reader
5. 分類ルールベース版
6. Agent Outbox生成
7. Weekly Goal Reader
8. WBS Generator
9. Progress Calculator
10. Telegram Digest
11. Google Calendar Scheduler
12. Custom GPT Actions
13. Codex / Claude Code Adapter
