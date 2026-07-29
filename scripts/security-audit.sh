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

unresolved=true
if pip-audit "${requirements[@]}" --desc 2>&1 | tee "$report"; then
  unresolved=false
fi

emit unresolved "$unresolved"
emit_report
echo "advisories unresolved: $unresolved"
