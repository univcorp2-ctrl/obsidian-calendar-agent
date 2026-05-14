# 要件定義: Obsidian Inbox 自動タスクCRM / 秘書エージェント

## 1. 何を作るか

Obsidian を中心にした、個人用の完全自動タスクCRMを作る。

ユーザーは Obsidian の Inbox / Daily Note / Weekly Note に自然にメモを書く。システムはそれを読み取り、タスク化、分類、専門エージェント割当、WBS化、進捗計算、Google Calendar登録、Telegram配信までを自動で行う。

さらに、10年後の大目標数字から逆算し、今週金曜日、来週金曜日、再来週金曜日、4週間後金曜日の目標数字を自動生成し、ObsidianのDaily NoteまたはAI-CRM領域へ書き込む。

## 2. 目標

- Inbox に雑に投げ込んだメモを自動で拾う
- 開発、調査、資料作成、事務、連絡などに分類する
- 分類結果に応じて専門エージェントへ依頼を作る
- 金曜日時点の Daily Note / Weekly Note に書いた週次目標をWBSへ分解する
- 10年ロードマップから逆算した週次KPIを自動生成する
- WBSの完了状況から進捗率を自動計算する
- Daily Note / Weekly Note のAI管理欄を自動更新する
- Google Calendarへ1時間単位の作業予定を登録する
- Telegramへ毎朝・毎夕・毎週の進捗レポートを送る
- 秘書エージェントが、今の状況、遅延リスク、今日やるべきことを助言する
- CI/CDでテストを自動化し、ローカルCLIによる修正ループを用意する

## 3. ユーザーの使い方

### 3.1 Inboxに投げ込む

ユーザーは `Inbox.md` に何でも書く。

```md
- 新しい予約管理アプリを作りたい。まずMVPを作る。
- 競合サービスの料金を調査したい。
- 田中さんに来週の打ち合わせ候補日を送る。
- 金曜日までに営業資料を完成させる。
```

### 3.2 週次目標を書く

金曜日または週次ノートに、ユーザーは大きい目標だけを書く。

```md
## 今週の目標
- 新しい予約管理アプリのMVPを作る
- 競合サービスを5社調査する
- 営業資料を完成させる
```

### 3.3 10年ロードマップから週次数字を作る

ユーザーが設定した10年後の大目標から、システムは今月の金曜日ごとの目標数字を自動生成する。

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

生成例:

```md
<!-- AI_ROADMAP_TARGETS:START -->
## 10年ロードマップ逆算: 週次目標数字

### 今週: 2026-05-15 金曜日時点

| 指標 | 目標数字 |
|---|---:|
| 純資産 | 0.62〜0.83億円 |
| 現金 | 0.21〜0.22億円 |
| 保有室数 | 27〜28室 |

#### 今週の行動KPI候補
- [ ] 候補物件・融資・売却案件を棚卸しする #roadmap #kpi
- [ ] 実績値をDaily/Weekly Noteに追記し、来週目標を再計算する #roadmap #review
<!-- AI_ROADMAP_TARGETS:END -->
```

## 4. 機能要件

### FR-001 Inbox読み取り

- `Inbox.md` または `Inbox/` フォルダを読む
- 未処理アイテムを検出する
- 処理済みには `processed` または `id:` を付与する

### FR-002 自動分類

分類カテゴリは以下。

- `development`: 開発
- `research`: 調査
- `writing`: 執筆 / 資料作成
- `communication`: 連絡
- `admin`: 事務
- `planning`: 企画 / 設計
- `calendar`: 日程調整
- `unknown`: 要確認

### FR-003 専門エージェント割当

分類結果に応じて、`AI-CRM/agent_outbox/` に依頼書Markdownを作る。

### FR-004 WBS生成

大きな目標を、実行可能な子タスクに分解する。

### FR-005 進捗率計算

初期版の計算式。

```text
進捗率 = 完了済み子タスク数 / 全子タスク数 * 100
```

### FR-006 Obsidian更新

- Daily Note / Weekly Note のAI管理欄だけを更新する
- 更新前にバックアップを作る
- ユーザーの自由記述は変更しない

### FR-007 Google Calendar登録

- 未完了タスクを1時間単位に分解する
- 既存予定と重複しないように登録する
- 固定時刻があるタスクは固定時刻を優先する
- 完了済みタスクは登録しない

### FR-008 Telegram配信

毎朝送る内容。

- 今日の予定
- 今日やるべきタスク
- 週次目標の進捗率
- 遅れているタスク
- 秘書コメント

### FR-009 Custom GPT連携

ChatGPTの画面から以下を依頼できる。

```text
Inboxを処理して
今週の目標をWBS化して
今日の予定を作って
Telegramに進捗を送って
遅れているタスクを整理して
```

### FR-010 10年ロードマップ逆算

- `data/roadmap_targets_10yr.json` を基準データとして読む
- 現在地から次の年末目標までを日数按分する
- 今週、来週、再来週、4週間後の金曜日目標を生成する
- Obsidianの金曜日Daily Noteへ `AI_ROADMAP_TARGETS` markerで書き込む
- 月次サマリーを `AI-CRM/roadmap/YYYY-MM-weekly-targets.md` に保存する

### FR-011 CLI AIレビュー

- API直叩きではなく、ローカルのCodex CLI / Claude CLIを呼び出せる
- `--review-command` または `ROADMAP_REVIEW_COMMANDS` でCLIコマンドを指定する
- CLIレビュー結果をObsidianの生成欄に追記できる

### FR-012 CI/CDと修正ループ

- GitHub Actions CIでcompile、スモークテスト、pytest、roadmap CLIテストを実行する
- CD SmokeでDocker buildとAPI health checkを行う
- CIが失敗した場合に備え、ローカルCLI修正ループ `scripts/ci_repair_loop.sh` を提供する

## 5. 非機能要件

### NFR-001 安全性

- いきなりGoogle Calendarへ本登録しない。dry-runを標準にする
- Markdown更新前にバックアップする
- AI更新範囲はmarker内に限定する
- 外部AIへ送る前に依頼書を保存する

### NFR-002 透明性

- なぜその分類になったか理由を保存する
- どのエージェントへ渡したかを保存する
- どのタスクがどのCalendarイベントになったか追跡する
- ロードマップ週次目標は、どの長期目標区間から逆算したかを保存する

### NFR-003 ローカルファースト

- Obsidian Markdownを正本とする
- DBは補助的にする
- Git管理できる構造にする
- AIレビューはAPI直呼びではなく、ローカルCLIを差し替え可能にする

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
    agent_results/
    logs/
    backups/
```

## 7. MVPの順番

1. 10年ロードマップ逆算CLI
2. Markdown安全更新
3. Inbox Reader
4. 分類ルールベース版
5. Agent Outbox生成
6. Weekly Goal Reader
7. WBS Generator
8. Progress Calculator
9. Telegram Digest
10. Google Calendar Scheduler
11. Custom GPT Actions
12. Codex / Claude Code Adapter

## 8. 受け入れ条件

### AC-001 Roadmap CLI

`python -m obsidian_calendar_agent.cli roadmap-weekly --start-date 2026-05-11 --weeks 4 --json` を実行すると、4つの金曜日目標がJSONで出力される。

### AC-002 Obsidian書き込み

`--write` を付けると、各金曜日Daily Noteと月次サマリーが作られる。

### AC-003 安全更新

Daily Noteにユーザーの自由記述がある状態で実行しても、marker外の文章は変更されない。

### AC-004 CI

GitHub Actions CIがcompile、スモークテスト、pytest、roadmap CLIテストを通す。

### AC-005 CD Smoke

GitHub Actions CD SmokeがDocker imageをbuildし、`/health` の応答を確認する。

## 9. 未決定事項

1. Inboxは `Inbox.md` か `Inbox/` フォルダか
2. Daily Noteのフォルダ名
3. Weekly Noteを使っているか、金曜日のDaily Noteを週次管理に使うか
4. 週の開始曜日
5. 週次目標の見出し名
6. 自動でCalendar登録してよい時間帯
7. Telegram配信時間
8. Codex / Claude Codeへの連携を、依頼書生成だけにするか、自動実行まで進めるか
9. ロードマップの実績値をどのファイル・見出しに書くか
10. ロードマップ数値の再計算を毎週何曜日・何時に行うか
