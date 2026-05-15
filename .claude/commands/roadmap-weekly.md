# roadmap-weekly

10年ロードマップから、今週・来週・再来週・4週間後の金曜日目標を生成してください。

## まず確認するファイル

- `data/roadmap_targets_10yr.json`
- `obsidian_calendar_agent/crm/roadmap.py`
- `docs/roadmap-weekly-targets.md`

## 実行例

```bash
python -m obsidian_calendar_agent.cli roadmap-weekly --start-date 2026-05-11 --weeks 4
```

JSONで確認する場合:

```bash
python -m obsidian_calendar_agent.cli roadmap-weekly --start-date 2026-05-11 --weeks 4 --json
```

Obsidianへ書き込む場合:

```bash
python -m obsidian_calendar_agent.cli roadmap-weekly --start-date 2026-05-11 --weeks 4 --write
```

Claude/Codex CLIレビューを入れる場合:

```bash
python -m obsidian_calendar_agent.cli roadmap-weekly \
  --start-date 2026-05-11 \
  --weeks 4 \
  --review \
  --review-command 'claude --print < {input}' \
  --write
```

## 注意

- `--write` は実Vaultへ書き込むため、ユーザーが明示したときだけ実行する。
- 通常確認は `--json` またはMarkdown出力だけにする。
- marker外のDaily Note本文は変更しない。
