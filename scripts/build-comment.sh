#!/usr/bin/env bash
#
# Build the pull request comment body from a Terraform plan result and write it
# to stdout. Posting is the caller's job.
#
# Reads from the environment:
#   EXITCODE      exit code of the plan run (0 = no changes, 2 = changes, other = failure)
#   PLAN_JSON     path to `terraform show -json <planfile>` output (required when EXITCODE is 2)
#   PLAN_TEXT     path to `terraform show -no-color <planfile>` output (required when EXITCODE is 2)
#   ERROR_MESSAGE message to show on failure
#   COMMIT_SHA    commit the plan ran against
#   RUN_URL       URL of the workflow run

set -euo pipefail

footer="<sub>commit \`${COMMIT_SHA:0:7}\` · [workflow run](${RUN_URL})</sub>"

# Count the resource changes matching a jq select expression.
count() {
  jq "[.resource_changes[]? | select($1)] | length" "$PLAN_JSON"
}

# One bullet per changed resource, prefixed with an icon for what happens to it.
list_changes() {
  jq -r '.resource_changes[]?
         | select(.change.actions != ["read"])
         | .change.actions as $a
         | ((if .change.importing != null then "📥" else "" end)
            + (if .previous_address != null then "📦" else "" end)
            + (if $a == ["create"] then "➕"
               elif $a == ["update"] then "🔄"
               elif $a == ["delete"] then "➖"
               elif $a == ["no-op"] then ""
               else "♻️" end)) as $icon
         | select($icon != "")
         | "- " + $icon + " `"
           + (if .previous_address != null
              then .previous_address + "` → `" + .address
              else .address end)
           + "`"' "$PLAN_JSON"
}

no_changes() {
  echo '### 🏗 Terraform Plan'
  echo
  echo 'No infrastructure changes.'
}

changes() {
  local added changed deleted replaced imported moved

  added=$(count '.change.actions == ["create"]')
  changed=$(count '.change.actions == ["update"]')
  deleted=$(count '.change.actions == ["delete"]')
  replaced=$(count '.change.actions | length > 1')
  imported=$(count '.change.importing != null')
  moved=$(count '.previous_address != null')

  echo '### 🏗 Terraform Plan'
  echo
  echo '| ➕ Add | 🔄 Change | ♻️ Replace | ➖ Destroy | 📥 Import | 📦 Move |'
  echo '|:--:|:--:|:--:|:--:|:--:|:--:|'
  echo "| $added | $changed | $replaced | $deleted | $imported | $moved |"
  echo
  list_changes
  echo
  echo '<details>'
  echo '<summary>Plan details</summary>'
  echo
  echo '```diff'
  # Terraform indents the action marker; move it to the start of the line so the
  # diff block colours the change.
  sed -E 's/^([[:space:]]*)([-+~])/\2\1/' "$PLAN_TEXT"
  echo '```'
  echo
  echo '</details>'
}

failed() {
  echo '### ❌ Terraform Plan: failed'
  echo
  echo '```'
  printf '%s\n' "$ERROR_MESSAGE"
  echo '```'
}

case "$EXITCODE" in
  0)
    no_changes
    ;;
  2)
    if [ -z "$PLAN_JSON" ] || [ -z "$PLAN_TEXT" ]; then
      echo "::error::plan-json and plan-text are both required when exitcode is 2" >&2
      exit 1
    fi
    changes
    ;;
  *)
    failed
    ;;
esac

echo
echo "$footer"
