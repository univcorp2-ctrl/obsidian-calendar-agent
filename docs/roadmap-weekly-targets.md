# 10年ロードマップ逆算: 週次目標数字の自動生成

## 目的

添付ロードマップのような10年後の大目標から逆算して、今月の毎週金曜日時点の目標数字をObsidianへ自動で書き込む。

## 実装済みCLI

```bash
python -m obsidian_calendar_agent.cli roadmap-weekly --start-date 2026-05-11 --weeks 4
```

JSONで確認:

```bash
python -m obsidian_calendar_agent.cli roadmap-weekly \
  --start-date 2026-05-11 \
  --weeks 4 \
  --json
```

Obsidianへ書き込み:

```bash
python -m obsidian_calendar_agent.cli roadmap-weekly \
  --start-date 2026-05-11 \
  --weeks 4 \
  --write
```

## 書き込まれるファイル

Daily Note:

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

## Codex / Claude CLIレビュー

APIを直接呼ばず、ローカルCLIを呼ぶ方式にしている。

```bash
python -m obsidian_calendar_agent.cli roadmap-weekly \
  --start-date 2026-05-11 \
  --weeks 4 \
  --review \
  --review-command 'claude --print < {input}'
```

複数CLIを使う場合:

```bash
python -m obsidian_calendar_agent.cli roadmap-weekly \
  --start-date 2026-05-11 \
  --weeks 4 \
  --review \
  --review-command 'claude --print < {input}' \
  --review-command 'codex exec --file {input}'
```

環境変数でも指定できる。

```bash
export ROADMAP_REVIEW_COMMANDS='claude --print < {input}||codex exec --file {input}'
python -m obsidian_calendar_agent.cli roadmap-weekly --review --write
```

## 仕組み

計算式:

```text
週次目標 = 前マイルストーン + (次マイルストーン - 前マイルストーン) × 経過日数 / 区間日数
```

初期版は日数按分。将来は実績値、季節性、銀行面談数、物件仕入れパイプライン、売却予定を加味して補正する。

## 安全性

Daily Note全体を書き換えず、以下の範囲だけ更新する。

```md
<!-- AI_ROADMAP_TARGETS:START -->
AI生成欄
<!-- AI_ROADMAP_TARGETS:END -->
```

marker外の文章は変更しない。既存ファイルを更新する前に `AI-CRM/backups/` へバックアップする。
