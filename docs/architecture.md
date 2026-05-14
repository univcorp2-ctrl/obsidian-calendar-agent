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
      ├─ Development Agent Request
      ├─ Research Agent Request
      ├─ Writing Agent Request
      ├─ Communication Agent Request
      └─ Admin Agent Request
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
```

## 2. コンポーネント

### 2.1 Inbox Reader

役割:

- `Inbox.md` または `Inbox/` を読む
- 未処理のメモ、タスク、アイデアを抽出する
- すでに `processed` が付いているものは無視する

入力例:

```md
- 新しい予約管理アプリを作る
- 競合サービスを調査する
```

出力:

```json
[
  {
    "source": "Inbox.md:1",
    "text": "新しい予約管理アプリを作る",
    "status": "inbox"
  }
]
```

### 2.2 Task Classifier / Router

役割:

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

### 2.3 Agent Outbox Generator

役割:

- 専門エージェントに渡す依頼書Markdownを生成する
- 初期版では外部AIを直接実行せず、依頼書だけ作る

出力例:

```text
AI-CRM/agent_outbox/development/task_20260513_001.md
AI-CRM/agent_outbox/research/task_20260513_002.md
```

依頼書テンプレート:

```md
# Agent Task Request

- Task ID: task_20260513_001
- Category: development
- Assigned Agent: development_agent
- Priority: high
- Due: 2026-05-17

## Original Inbox Item

新しい予約管理アプリを作る

## Expected Output

- 要件定義
- MVP設計
- 実装タスク分解
- テスト方針
```

### 2.4 Weekly Goal Reader

役割:

- Weekly Noteまたは金曜日のDaily Noteを読む
- `## 今週の目標` セクションを抽出する

### 2.5 WBS Generator

役割:

- 大きな目標を実行可能な小タスクへ分解する
- タスクごとに完了条件、推定工数、担当エージェントを付ける

WBSのデータ形式:

```yaml
parent_goal: 新しい予約管理アプリのMVPを作る
children:
  - title: 要件定義を作る
    done: false
    estimate_minutes: 60
    agent: development
    acceptance: 要件一覧がMarkdownで作成されている
  - title: DB設計を作る
    done: false
    estimate_minutes: 60
    agent: development
    acceptance: テーブル一覧と主要カラムが定義されている
```

### 2.6 Progress Calculator

役割:

- WBSの完了状態を読む
- 親目標ごとの進捗率を計算する
- 遅延リスクを判定する

初期計算式:

```text
進捗率 = 完了済み子タスク数 / 全子タスク数 * 100
```

### 2.7 Obsidian Writer

役割:

- Daily Note / Weekly NoteへAI管理欄を更新する
- marker内のみ更新する
- 更新前にバックアップを作る

marker:

```md
<!-- AI_TASK_CRM:START -->
AI更新領域
<!-- AI_TASK_CRM:END -->
```

### 2.8 Google Calendar Scheduler

役割:

- WBSタスクを1時間単位の予定へ変換する
- 既存予定を避ける
- Google Calendarへ登録する

### 2.9 Telegram Secretary Digest

役割:

- 今日の予定
- 進捗率
- 遅延タスク
- 秘書コメント

をTelegramへ送信する。

### 2.10 Custom GPT API

役割:

- Custom GPT Actionsから呼ばれるAPIを提供する

エンドポイント案:

```text
POST /inbox/process
POST /weekly/wbs
POST /progress/update
POST /calendar/schedule
POST /telegram/digest
GET  /status/today
```

## 3. ファイル構成

推奨Vault構成:

```text
ObsidianVault/
  Inbox.md
  Daily/
    2026-05-13.md
  Weekly/
    2026-W20.md
  AI-CRM/
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

アプリ側構成:

```text
obsidian_calendar_agent/
  app.py
  cli.py
  config.py
  parser.py
  planner.py
  google_calendar.py
  telegram.py
  digest.py
  orchestrator.py
  crm/
    inbox_reader.py
    classifier.py
    router.py
    outbox_writer.py
    weekly_reader.py
    wbs_generator.py
    progress.py
    obsidian_writer.py
```

## 4. 処理フロー

### 4.1 Inbox処理フロー

```text
1. Inboxを読む
2. 未処理行を抽出
3. タスク分類
4. 専門エージェントを決定
5. agent_outboxに依頼書を保存
6. Inbox側に処理済みIDを付与
7. ログを保存
```

### 4.2 Weekly WBS処理フロー

```text
1. Weekly Noteまたは金曜日Daily Noteを読む
2. 週次目標セクションを抽出
3. 目標ごとにWBSを生成
4. AI_TASK_CRM marker内にWBSを保存
5. Google Calendar登録候補を作る
```

### 4.3 進捗更新フロー

```text
1. WBSのチェック状態を読む
2. 完了数 / 全体数を計算
3. 進捗率を算出
4. 遅延リスクを判定
5. 秘書コメントを生成
6. Daily / Weekly Noteを更新
7. Telegram文面を生成
```

## 5. エージェント設計

### 5.1 Development Agent

担当:

- システム開発
- コード実装
- テスト作成
- GitHub Issue / PR作成

### 5.2 Research Agent

担当:

- Web調査
- 競合調査
- 論文 / 資料調査
- 比較表作成

### 5.3 Writing Agent

担当:

- 提案書
- 営業資料
- 要件定義
- 報告書

### 5.4 Communication Agent

担当:

- メール文案
- 日程調整文案
- 返信草案

### 5.5 Admin Agent

担当:

- 経費
- 請求
- 書類整理
- 手続きタスク

### 5.6 Secretary Agent

担当:

- 優先順位判断
- 遅延リスク検知
- 今日やるべきことの助言
- Telegramレポート作成

## 6. 安全設計

### 6.1 Dry-run優先

外部サービスへ書き込む処理は、最初はdry-runで内容を確認する。

### 6.2 Marker内だけ更新

AIはDaily Note全体を再生成しない。marker内だけ更新する。

### 6.3 バックアップ

Markdown更新前に `AI-CRM/backups/` へコピーを保存する。

### 6.4 Agent Outbox方式

Codex / Claude Codeなどへの直接実行は初期版では行わない。まず依頼書を作り、人間が確認できる状態にする。

## 7. テスト方針

### 7.1 Unit Test

- Inbox抽出
- タスク分類ルール
- WBS生成
- 進捗率計算
- marker内Markdown更新

### 7.2 Integration Test

- Inboxからagent_outbox生成まで
- Weekly GoalからWBS生成まで
- WBSからTelegram文面生成まで

### 7.3 Dry-run Test

- Google Calendar登録予定を表示するが登録しない
- Telegram送信予定文面を表示するが送信しない

### 7.4 本番前テスト

- テスト用Vaultで実行
- テスト用Google Calendarで実行
- 自分だけのTelegram Chatで実行

## 8. 推奨実装順序

1. Markdown安全更新
2. Inbox Reader
3. 分類ルールベース版
4. Agent Outbox生成
5. Weekly Goal Reader
6. WBS Generator
7. Progress Calculator
8. Telegram Digest
9. Google Calendar Scheduler
10. Custom GPT Actions
11. Codex / Claude Code Adapter
