# 要件定義: Obsidian Inbox 自動タスクCRM / 秘書エージェント

## 1. 何を作るか

Obsidian を中心にした、個人用の完全自動タスクCRMを作る。

ユーザーは Obsidian の Inbox / Daily Note / Weekly Note に自然にメモを書く。システムはそれを読み取り、タスク化、分類、専門エージェント割当、WBS化、進捗計算、Google Calendar登録、Telegram配信までを自動で行う。

## 2. 目標

- Inbox に雑に投げ込んだメモを自動で拾う
- 開発、調査、資料作成、事務、連絡などに分類する
- 分類結果に応じて専門エージェントへ依頼を作る
- 金曜日時点の Daily Note / Weekly Note に書いた週次目標をWBSへ分解する
- WBSの完了状況から進捗率を自動計算する
- Daily Note / Weekly Note のAI管理欄を自動更新する
- Google Calendarへ1時間単位の作業予定を登録する
- Telegramへ毎朝・毎夕・毎週の進捗レポートを送る
- 秘書エージェントが、今の状況、遅延リスク、今日やるべきことを助言する

## 3. ユーザーの使い方

### 3.1 Inboxに投げ込む

ユーザーは `Inbox.md` に何でも書く。

```md
- 新しい予約管理アプリを作りたい。まずMVPを作る。
- 競合サービスの料金を調査したい。
- 田中さんに来週の打ち合わせ候補日を送る。
- 金曜日までに営業資料を完成させる。
```

システムは自動で以下のように判断する。

| 入力 | 分類 | 割当先 |
|---|---|---|
| 予約管理アプリを作りたい | development | 開発エージェント |
| 競合サービス料金調査 | research | 調査エージェント |
| 田中さんに候補日を送る | communication | 秘書 / 連絡エージェント |
| 営業資料完成 | writing | 資料作成エージェント |

### 3.2 週次目標を書く

金曜日または週次ノートに、ユーザーは大きい目標だけを書く。

```md
## 今週の目標
- 新しい予約管理アプリのMVPを作る
- 競合サービスを5社調査する
- 営業資料を完成させる
```

システムはこれをWBSへ分解する。

```md
## WBS

### 新しい予約管理アプリのMVPを作る
- [ ] 要件定義を作る #dev #wbs
- [ ] 画面一覧を作る #dev #wbs
- [ ] DB設計を作る #dev #wbs
- [ ] API設計を作る #dev #wbs
- [ ] MVPを実装する #dev #wbs
- [ ] テストを書く #dev #wbs
- [ ] 動作確認する #dev #wbs
```

### 3.3 進捗が自動更新される

Daily Note / Weekly Note に以下のようなAI管理欄が作られる。

```md
<!-- AI_TASK_CRM:START -->
## Weekly Progress

- 予約管理アプリMVP: 43% 完了
- 競合調査: 25% 完了
- 営業資料: 80% 完了

## AI Secretary Advice

開発MVPはAPI設計とテストが未着手です。今日の午前にAPI設計を1時間確保するのがおすすめです。
<!-- AI_TASK_CRM:END -->
```

AIは marker で囲まれた範囲だけを更新し、ユーザーが自由に書いた文章は壊さない。

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

```text
AI-CRM/agent_outbox/development/task_001.md
AI-CRM/agent_outbox/research/task_002.md
AI-CRM/agent_outbox/communication/task_003.md
```

初期版では、Codex / Claude Code へ直接実行させず、まず依頼書生成までにする。これにより誤実行を防ぎ、人間が内容を確認できる。

### FR-004 WBS生成

大きな目標を、実行可能な子タスクに分解する。

WBS項目は以下の情報を持つ。

- 親目標ID
- 子タスクID
- タイトル
- 完了条件
- 成果物
- 推定工数
- 優先度
- 担当エージェント
- ステータス

### FR-005 進捗率計算

初期版の計算式。

```text
進捗率 = 完了済み子タスク数 / 全子タスク数 * 100
```

将来版。

```text
進捗率 = 完了済み見積時間 / 全見積時間 * 100
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

毎夕送る内容。

- 今日完了したタスク
- 未完了タスク
- 明日の優先候補

毎週金曜に送る内容。

- 今週の達成率
- 未達目標
- 来週へ持ち越すタスク
- 改善提案

### FR-009 Custom GPT連携

ChatGPTの画面から以下を依頼できる。

```text
Inboxを処理して
今週の目標をWBS化して
今日の予定を作って
Telegramに進捗を送って
遅れているタスクを整理して
```

FastAPIの外部APIをCustom GPT Actionsから呼び出す。

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

### NFR-003 ローカルファースト

- Obsidian Markdownを正本とする
- DBは補助的にする
- Git管理できる構造にする

### NFR-004 拡張性

- エージェント種別を追加できる
- Codex / Claude Code / 手動実行を切り替えられる
- Telegram以外の通知先も追加できる

## 6. 推奨Vault構成

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

## 7. ステータス定義

| ステータス | 意味 |
|---|---|
| inbox | 未分類 |
| classified | 分類済み |
| assigned | エージェント割当済み |
| wbs_created | WBS化済み |
| scheduled | カレンダー登録済み |
| in_progress | 進行中 |
| blocked | 停止中 |
| done | 完了 |
| archived | アーカイブ済み |

## 8. MVPの順番

### MVP-1 Inbox分類

- Inboxを読む
- タスクを分類する
- agent_outboxに依頼書を作る

### MVP-2 WBS生成

- Weekly Goalを読む
- WBSへ分解する
- AI管理欄へ保存する

### MVP-3 進捗更新

- WBSのチェック状態を読む
- 親目標ごとの進捗率を計算する
- Daily / Weekly Noteへ反映する

### MVP-4 Telegram秘書レポート

- 今日やるべきこと
- 週次進捗
- 遅延リスク
- 秘書コメント

を送信する。

### MVP-5 Google Calendar連携

- 未完了タスクを1時間単位で登録する

### MVP-6 Custom GPT連携

- ChatGPTの画面からAPIを呼び出せるようにする

## 9. 受け入れ条件

### AC-001 Inbox分類

Inboxに未処理メモがある状態で実行すると、分類され、適切なagent_outboxに依頼書が生成される。

### AC-002 WBS生成

Weekly Goalに大きな目標がある状態で実行すると、複数の実行可能タスクに分解される。

### AC-003 進捗更新

WBSに完了済みと未完了のタスクが混在する状態で実行すると、進捗率が正しく更新される。

### AC-004 安全更新

Daily Noteにユーザーの自由記述がある状態で実行しても、marker外の文章は変更されない。

### AC-005 Telegram配信

今日の予定と週次進捗がある状態で実行すると、秘書レポート文面が生成される。

## 10. 未決定事項

ユーザー確認が必要なもの。

1. Inboxは `Inbox.md` か `Inbox/` フォルダか
2. Daily Noteのフォルダ名
3. Weekly Noteを使っているか、金曜日のDaily Noteを週次管理に使うか
4. 週の開始曜日
5. 週次目標の見出し名
6. 自動でCalendar登録してよい時間帯
7. Telegram配信時間
8. Codex / Claude Codeへの連携を、依頼書生成だけにするか、自動実行まで進めるか
