# verify

このプロジェクトの全検証を実行してください。

## 実行すること

```bash
bash scripts/verify_all.sh
```

## 成功した場合

次を報告してください。

- 成功した検証項目
- 変更ファイルがある場合の要約
- 次に人間が確認すべきこと

## 失敗した場合

1. 失敗ログを読み、原因を特定してください。
2. 必要最小限の修正を行ってください。
3. 再度 `bash scripts/verify_all.sh` を実行してください。
4. 成功するまで繰り返してください。

## 注意

- `.env`, `credentials.json`, `token.json` は作らない、編集しない、コミットしない。
- Google CalendarやTelegramに本番送信しない。
- Obsidian書き込みを伴う確認はテスト用tmpディレクトリだけで行う。
