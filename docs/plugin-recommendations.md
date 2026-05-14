# Obsidianプラグイン調査: WBS / ガント / タスクCRM向けランキング

調査日: 2026-05-14

## 結論

このプロジェクトでは、以下の組み合わせを推奨する。

```text
基本タスク管理: Tasks
集計・進捗表示: Dataview または Datacore
WBS/プロジェクト管理UI: Project Manager
ガント/タイムライン表示: Markwhen または Mermaid
日次時間割表示: Day Planner
```

最初に全部入れる必要はない。MVPでは `Tasks + Dataview + Mermaid` から始め、WBS/ガントUIが必要になった段階で `Project Manager` または `Markwhen` を追加する。

## ランキング

### 1位: Project Manager

URL: https://community.obsidian.md/plugins/project-manager  
GitHub: https://github.com/StepanKropachev/obsidian-pm

評価: WBS / ガント / カンバン / テーブルを一体で扱いたい場合の最有力候補。

特徴:

- Table / Gantt / Kanban views
- MarkdownファイルとYAML frontmatterに保存
- 依存関係、マイルストーン、サブタスク、時間計測、繰り返しタスクに対応
- Obsidian内で完結するプロジェクト管理に近い

向いている用途:

- WBSを視覚化したい
- ガントチャートをドラッグ操作したい
- 進捗・依存関係・担当エージェントを管理したい

注意:

- 比較的新しいため、最初はテストVaultで検証する
- 自動化スクリプトとfrontmatter形式を合わせる必要がある

### 2位: Tasks

URL: https://community.obsidian.md/plugins/obsidian-tasks-plugin  
GitHub: https://github.com/obsidian-tasks-group/obsidian-tasks

評価: Obsidian内のタスク管理基盤として最重要。

特徴:

- Vault全体のタスクを検索・抽出できる
- due date、recurring task、done dateに対応
- クエリ結果からチェックを入れると元ファイルも更新される
- ダウンロード数が多く成熟している

向いている用途:

- Daily Note / Inbox / Weekly Note に散らばるタスクを集約する
- 未完了タスクを一覧化する
- WBSタスクを通常のMarkdownチェックボックスで管理する

注意:

- ガントチャートやWBS UIそのものではない
- 自動分類やAI割当は別システム側で実装する

### 3位: Dataview

URL: https://community.obsidian.md/plugins/dataview  
GitHub: https://github.com/blacksmithgu/obsidian-dataview

評価: 進捗率、タスク一覧、プロジェクト別ダッシュボードに必須級。

特徴:

- Markdown frontmatterやinline fieldsからデータを取り出せる
- Vaultを簡易データベースのように扱える
- タスクCRMの一覧・集計・フィルタに強い

向いている用途:

- 週次目標ごとの進捗率表示
- `agent: development` のタスクだけ表示
- `status: blocked` のタスクだけ抽出

注意:

- クエリ記法を覚える必要がある
- WBSの自動生成そのものは行わない

### 4位: Markwhen

URL: https://community.obsidian.md/plugins/markwhen  
GitHub: https://github.com/mark-when/obsidian-plugin

評価: Markdown風の記法でタイムラインやガントを表現したい場合に有力。

特徴:

- markwhen記法でタイムライン / ガント / カレンダーを描ける
- WBSを日付つきで可視化しやすい
- テキストで管理できるためAI生成と相性がよい

向いている用途:

- WBSからガントチャートを自動生成する
- プロジェクト全体の期間を見たい
- Markdownに近い記法でスケジュールを保存したい

注意:

- タスク管理の正本というより、可視化レイヤーとして使うのがよい

### 5位: TaskNotes

URL: https://github.com/callumalpass/tasknotes

評価: タスクを1件1Markdownノートとして扱う、本格タスクCRM向け候補。

特徴:

- 各タスクが個別のMarkdownノート
- YAML frontmatterでstatus、priority、due、projectなどを管理できる
- Obsidian BasesのビューでTask List / Kanban / Calendar / Agendaを表現する
- データがMarkdownのまま残る

向いている用途:

- タスク1件ごとに詳細なメモ、ログ、成果物リンクを持ちたい
- CRMのようにタスク履歴を管理したい
- 将来的にAIエージェント実行結果を各タスクノートへ紐づけたい

注意:

- 通常の `- [ ]` タスクより構造が重い
- MVPでは後回しでもよい

### 6位: Mermaid 標準機能

URL: https://obsidian.md/help/advanced-syntax  
Mermaid Gantt: https://mermaid.ai/open-source/syntax/gantt.html

評価: プラグイン不要で図を出すなら最初に使うべき。

特徴:

- Obsidian標準でMermaidコードブロックを表示できる
- flowchart、sequence diagram、timelineなどに対応
- Mermaid側にはGantt記法がある

向いている用途:

- WBSの依存関係をflowchartで表示する
- プロジェクト工程をGanttで表示する
- AIがMarkdown内に図を自動生成する

注意:

- インタラクティブなドラッグ操作はできない
- 大きなガントは見づらくなる可能性がある

### 7位: Day Planner

URL: https://community.obsidian.md/plugins/obsidian-day-planner

評価: 1日の時間割・タイムライン確認に向く。

特徴:

- Daily Notes、Obsidian Tasks、Online calendars、Dataview clock propertiesを表示できる
- サイドバーにタイムライン表示できる
- 今日の実行計画との相性がよい

向いている用途:

- Daily Noteの予定を時間軸で見たい
- 今日の作業ブロックを視覚化したい
- Google Calendar連携前のローカル時間割に使う

注意:

- WBSや長期プロジェクト管理の主役ではない

### 8位: Kanban

URL: https://github.com/obsidian-community/obsidian-kanban

評価: シンプルなカンバン運用には便利だが、長期的には注意。

特徴:

- Markdown-backed Kanban boards
- カードを列で管理できる
- 軽く始めやすい

向いている用途:

- Inbox / Doing / Done の簡易管理
- 目視で作業状態を動かしたい

注意:

- GitHub上では新しいメンテナーを探している状態
- 本格WBSやガントには別ツールが必要

## 推奨構成パターン

### パターンA: 安定重視のMVP

```text
Tasks + Dataview + Mermaid
```

用途:

- まず壊れにくく始める
- Markdownチェックボックスを正本にする
- AIスクリプト側でWBSと進捗率を生成する

### パターンB: WBS/ガントを視覚化したい

```text
Tasks + Dataview + Project Manager
```

用途:

- WBS、依存関係、ガント、カンバンをObsidian上で見たい
- プロジェクト管理UIを重視する

### パターンC: AI生成しやすいガントが欲しい

```text
Tasks + Dataview + Markwhen
```

用途:

- AIがテキストでガント表現を生成する
- スケジュール全体をMarkdown風に保存する

### パターンD: CRM化を強めたい

```text
TaskNotes + Dataview/Datacore + Project Manager
```

用途:

- タスク1件ごとに履歴や成果物を残す
- エージェント実行結果を各タスクへ紐づける
- 長期的な個人CRMに近づける

## このプロジェクトでの採用方針

初期実装では、特定プラグインに依存しすぎない。

正本は以下のような普通のMarkdownにする。

```md
- [ ] 要件定義を作る 📅 2026-05-15 ⏱ 1h #wbs #dev
```

この形式なら、以下のすべてに展開できる。

- Tasksで検索・完了管理
- Dataviewで集計
- Mermaidで簡易図解
- Markwhenでガント表示
- Project Managerへfrontmatter変換
- Google Calendarへ登録
- Telegramへ配信

## インストール優先順位

まず入れるもの:

1. Tasks
2. Dataview

次に必要に応じて入れるもの:

3. Project Manager
4. Markwhen
5. Day Planner

上級構成で検討するもの:

6. TaskNotes
7. Datacore
