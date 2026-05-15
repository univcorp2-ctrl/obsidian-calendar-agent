# docker-smoke

CD Smoke相当のDocker起動確認を実行してください。

## 実行

```bash
docker build -t obsidian-calendar-agent:local .
docker run -d --rm --name obsidian-calendar-agent-local -p 8000:8000 -e AGENT_API_KEY=local-test-key -e ENABLE_SCHEDULER=false obsidian-calendar-agent:local
for i in {1..20}; do
  if curl --fail --silent http://localhost:8000/health; then
    docker stop obsidian-calendar-agent-local
    exit 0
  fi
  sleep 1
done
docker logs obsidian-calendar-agent-local
docker stop obsidian-calendar-agent-local
exit 1
```

## 完了条件

- Docker image buildが成功する
- FastAPIが起動する
- `/health` が `{"status":"ok"}` を返す

## 注意

- 実際のGoogle CalendarやTelegramには接続しない。
- `AGENT_API_KEY=local-test-key`、`ENABLE_SCHEDULER=false` で起動する。
