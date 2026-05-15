# fix-ci

CI/CDが失敗した前提で、原因調査、修正、再検証まで行ってください。

## 手順

1. まずローカルで同じ検証を実行してください。

```bash
bash scripts/verify_all.sh
```

2. 失敗したら、エラーの最初の原因を特定してください。
3. 影響範囲が一番小さい修正をしてください。
4. 既存テストが不足している場合は、回帰テストを追加してください。
5. 再度検証してください。

```bash
bash scripts/verify_all.sh
```

6. Docker関連の変更がある場合は、CD Smoke相当も実行してください。

```bash
docker build -t obsidian-calendar-agent:local .
docker run -d --rm --name obsidian-calendar-agent-local -p 8000:8000 -e AGENT_API_KEY=local-test-key -e ENABLE_SCHEDULER=false obsidian-calendar-agent:local
curl --fail http://localhost:8000/health
docker stop obsidian-calendar-agent-local
```

## 完了条件

- `bash scripts/verify_all.sh` が成功する
- Docker関連変更がある場合は `/health` が成功する
- 何を直したか、どのテストを通したかを報告する

## 禁止

- テストを削除して通すこと
- 本番認証情報を要求すること
- 外部APIへ本番書き込みすること
