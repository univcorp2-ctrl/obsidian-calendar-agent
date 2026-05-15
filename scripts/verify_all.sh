#!/usr/bin/env bash
set -euo pipefail

python -m compileall obsidian_calendar_agent scripts
python scripts/smoke_test.py
pytest -q
python -m obsidian_calendar_agent.cli roadmap-weekly --start-date 2026-05-11 --weeks 4 --json >/tmp/roadmap-weekly.json
python - <<'PY'
import json
from pathlib import Path
payload = json.loads(Path('/tmp/roadmap-weekly.json').read_text())
assert len(payload['weekly_targets']) == 4
assert payload['weekly_targets'][0]['target_date'] == '2026-05-15'
print('roadmap-weekly CLI smoke ok')
PY
python - <<'PY'
from pathlib import Path
root = Path.cwd()
required = [
    root / 'CLAUDE.md',
    root / '.claude' / 'commands' / 'verify.md',
    root / '.claude' / 'commands' / 'fix-ci.md',
    root / '.claude' / 'commands' / 'roadmap-weekly.md',
    root / '.claude' / 'commands' / 'docker-smoke.md',
]
missing = [str(path) for path in required if not path.exists()]
assert not missing, missing
print('claude-code support files ok')
PY
