#!/usr/bin/env bash
set -uo pipefail

: "${GITHUB_OUTPUT:?GITHUB_OUTPUT is required}"

report="${REPORT_FILE:-audit-report.txt}"
requirements=(--requirement requirements_dev.txt --requirement requirements_lint.txt)

emit() {
  echo "$1=$2" >>"$GITHUB_OUTPUT"
}

emit_report() {
  {
    echo 'report<<AUDIT_REPORT_EOF'
    if [[ -s "$report" ]]; then
      cat "$report"
    else
      echo 'pip-audit produced no output, see the workflow logs.'
    fi
    echo 'AUDIT_REPORT_EOF'
  } >>"$GITHUB_OUTPUT"
}

if pip-audit "${requirements[@]}" --desc 2>&1 | tee "$report"; then
  emit changed false
  emit unresolved false
  emit_report
  exit 0
fi

echo "Advisories found, attempting pip-audit --fix"
pip-audit "${requirements[@]}" --fix || echo "pip-audit --fix could not resolve everything"

changed=false
if ! git diff --quiet -- requirements_dev.txt requirements_lint.txt; then
  changed=true
fi

unresolved=true
if pip-audit "${requirements[@]}" --desc 2>&1 | tee "$report"; then
  unresolved=false
fi

emit changed "$changed"
emit unresolved "$unresolved"
emit_report
echo "requirements changed: $changed, advisories unresolved: $unresolved"
