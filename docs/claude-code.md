# Claude Code運用ガイド

## 目的

このリポジトリをClaude Codeでも迷わず扱えるようにする。

## 追加済みファイル

```text
CLAUDE.md
.claude/commands/verify.md
.claude/commands/fix-ci.md
.claude/commands/roadmap-weekly.md
.claude/commands/docker-smoke.md
.claude/settings.example.json
```

## Claude Codeで最初にやること

リポジトリ直下でClaude Codeを起動する。

```bash
claude
```

その後、まず以下を依頼する。

```text
CLAUDE.mdを読んで、このプロジェクトの作業ルールを把握して。
```

## よく使うClaude Codeコマンド

Claude Code内で `/` を入力すると、プロジェクトコマンドを選べる。

### /verify

全検証を実行する。

```bash
bash scripts/verify_all.sh
```

### /fix-ci

CI/CD失敗を前提に、原因調査、修正、再検証まで行う。

### /roadmap-weekly

10年ロードマップから週次金曜日目標を生成する。

```bash
python -m obsidian_calendar_agent.cli roadmap-weekly --start-date 2026-05-11 --weeks 4
```

### /docker-smoke

CD Smoke相当のDocker build / health checkを実行する。

## Claude Codeで修正するときのルール

1. まず `docs/requirements.md` と `docs/architecture.md` を読む。
2. 変更する前に、修正方針とテスト方針を短く書く。
3. 修正する。
4. `bash scripts/verify_all.sh` を実行する。
5. 失敗したら、テストを消さずに原因を直す。
6. 成功したら、変更点とテスト結果を報告する。

## ローカル修正ループ

Claude Code以外のClaude CLI / Codex CLIでも、失敗ログを渡して修正ループを回せる。

```bash
export REPAIR_COMMAND='claude --print < {log}'
bash scripts/ci_repair_loop.sh
```

Codex CLI例:

```bash
export REPAIR_COMMAND='codex exec --file {log}'
bash scripts/ci_repair_loop.sh
```

## 注意

- `.env`, `credentials.json`, `token.json` はコミット禁止。
- Google Calendar / Telegramへの本番送信は、ユーザーが明示したときだけ行う。
- Obsidian Daily Noteはmarker内だけ更新する。
- GitHub Actions上でAIが勝手に本番修正・本番送信する構成にはしない。
