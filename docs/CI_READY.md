# ⚙️ CI — READY TO ENABLE (1 minute, web se)

**Status:** file READY, push BLOCKED — Arena ka GitHub App token is
repo par `workflows` scope nahi rakhta, isliye agent khud workflow
file push nahi kar sakta (probed: remote rejected). Operator ise
github.com web UI se add kar sakta hai (phone se bhi).

## Steps (github.com → repo → Add file → Create new file)
1. Path: `.github/workflows/ci.yml`
2. Neeche wala content paste karo
3. "Commit changes" → har push/PR par suite chalega

```yaml
name: ci

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install test deps (pypi only - the sandbox allowlist set)
        run: pip install pytest imageio-ffmpeg numpy
      - name: Suite
        run: python -m pytest tests/ -q
```

**Verified:** yeh exact dep-set fresh venv me 430 passed (CI-parity
check 2026-09-28) — pehli run green hogi.
