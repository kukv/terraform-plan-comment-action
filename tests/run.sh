#!/usr/bin/env bash
# Compare the generated comment against the expected markdown for each fixture.
# Shell + python only, to avoid adding dependencies.
set -euo pipefail
cd "$(dirname "$0")/.."

COMMIT_SHA=0123456789abcdef0123456789abcdef01234567
RUN_URL=https://github.com/kukv/terraform-plan-comment-action/actions/runs/1
export COMMIT_SHA RUN_URL

fail=0

golden() { # golden <name> <exitcode> [VAR=value...]
  local name=$1 exitcode=$2
  shift 2
  local expected="tests/fixtures/$name/expected.md"
  local out rc=0

  out=$(env EXITCODE="$exitcode" "$@" python3 scripts/build_comment.py) || rc=$?
  if [ "$rc" != 0 ]; then
    echo "NG: $name -> exit $rc (expected 0)"
    fail=1
    return
  fi
  if ! diff -u "$expected" <(printf '%s\n' "$out"); then
    echo "NG: $name -> output differs from $expected"
    fail=1
    return
  fi
  echo "OK: $name"
}

expect_error() { # expect_error <description> <exitcode> [VAR=value...]
  local description=$1 exitcode=$2
  shift 2
  local rc=0

  env EXITCODE="$exitcode" "$@" python3 scripts/build_comment.py >/dev/null 2>&1 || rc=$?
  if [ "$rc" != 1 ]; then
    echo "NG: $description -> exit $rc (expected 1)"
    fail=1
    return
  fi
  echo "OK: $description"
}

golden no-changes 0
golden changes 2 \
  PLAN_JSON=tests/fixtures/changes/plan.json \
  PLAN_TEXT=tests/fixtures/changes/plan.txt
golden failed 1 ERROR_MESSAGE='Error: Invalid resource type

  on main.tf line 1, in resource "github_nope" "x":
   1: resource "github_nope" "x" {'

expect_error "missing plan files when exitcode is 2" 2

exit $fail
