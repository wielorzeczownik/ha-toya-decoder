---
title: Unresolved security advisories
labels: security advisory
---

`pip-audit` reports advisories against the locked dependencies in `uv.lock`.
Renovate only proposes version bumps on its own schedule, so these need a
deliberate bump in `pyproject.toml` or a refreshed `uv.lock`.

{{ env.AUDIT_REPORT }}
