# CI/CD と失敗時修正ループ

## CI

GitHub Actionsの `CI` は、push / pull request / manual run で動く。

実行内容:

```bash
bash scripts/verify_all.sh
```

中身:

```bash
python -m compileall obsidian_calendar_agent scripts
python scripts/smoke_test.py
pytest -q
python -m obsidian_calendar_agent.cli roadmap-weekly --start-date 2026-05-11 --weeks 4 --json
```

## CD Smoke

`CD Smoke` はCI成功後に動く。

実行内容:

```bash
docker build -t obsidian-calendar-agent:ci .
docker run ... obsidian-calendar-agent:ci
curl http://localhost:8000/health
```

本番デプロイはまだしない。まずDockerで起動できることだけを確認する。

## 失敗したら修正する仕組み

完全自動でGitHub Actionsが勝手にコードを書き換える方式は危険なので、初期版ではローカルCLI修正ループを提供する。

```bash
export REPAIR_COMMAND='claude --print < {log}'
bash scripts/ci_repair_loop.sh
```

Codex CLI例:

```bash
export REPAIR_COMMAND='codex exec --file {log}'
bash scripts/ci_repair_loop.sh
```

動き:

```text
1. テストを実行
2. 失敗したら .repair/last_failure.log に保存
3. Claude/Codex CLIへ失敗ログを渡す
4. CLIが修正した後、再テスト
5. 成功するまで MAX_REPAIR_ATTEMPTS 回繰り返す
```

回数指定:

```bash
export MAX_REPAIR_ATTEMPTS=3
bash scripts/ci_repair_loop.sh
```

## GitHub Actionsで完全自動修正したい場合

将来的には以下を追加できる。

- Claude Code GitHub Action
- Codex系GitHub Action
- `workflow_run` failure trigger
- 修正ブランチ自動作成
- PR自動作成

ただし、その場合はGitHub SecretsにAI実行用の認証情報を入れる必要があるため、MVPでは入れない。
