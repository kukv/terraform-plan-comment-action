#!/usr/bin/env python3
"""Build the pull request comment body from a Terraform plan result.

Writes markdown to stdout; posting is the caller's job. Standard library only,
so it runs anywhere python3 does and can be exercised by hand:

    EXITCODE=2 PLAN_JSON=plan.json PLAN_TEXT=plan.txt \\
      COMMIT_SHA=0000000 RUN_URL=https://example.com \\
      ./scripts/build_comment.py

Environment:
    EXITCODE      exit code of the plan run (0 = no changes, 2 = changes, other = failure)
    PLAN_JSON     path to `terraform show -json <planfile>` output (required when EXITCODE is 2)
    PLAN_TEXT     path to `terraform show -no-color <planfile>` output (required when EXITCODE is 2)
    ERROR_MESSAGE message to show on failure
    TITLE         name of what was planned, shown in the heading (for matrix jobs)
    COMMIT_SHA    commit the plan ran against
    RUN_URL       URL of the workflow run
"""

import json
import os
import re
import sys

# Terraform indents the action marker; move it to the start of the line so the
# diff block colours the change.
DIFF_MARKER = re.compile(r"^([ \t]*)([-+~])")
# An attribute whose value is a multi-line string, rendered as a heredoc.
HEREDOC_START = re.compile(r"^([ \t]*)([-+~] )?.*<<-?(\w+)$")


def mark_diff(plan_text):
    """Move action markers to the start of their line.

    Inside a heredoc, only Terraform's own per-line markers move (two columns
    right of the attribute name); the string's content stays as it is.
    """
    lines = []
    heredoc = None  # (delimiter, column of the per-line markers)
    for line in plan_text.split("\n"):
        if heredoc is None:
            start = HEREDOC_START.match(line)
            if start:
                name_column = len(start.group(1)) + (2 if start.group(2) else 0)
                heredoc = (start.group(3), name_column + 2)
            lines.append(DIFF_MARKER.sub(r"\2\1", line))
            continue

        delimiter, column = heredoc
        body = line.strip()
        if body == delimiter or body.startswith(delimiter + " "):
            heredoc = None
            lines.append(line)
            continue
        marker = DIFF_MARKER.match(line)
        if marker and len(marker.group(1)) == column:
            line = DIFF_MARKER.sub(r"\2\1", line)
        lines.append(line)
    return "\n".join(lines)


def longest_backtick_run(text):
    return max((len(run) for run in re.findall(r"`+", text)), default=0)


def code_span(text):
    """Wrap text in inline code that no backtick inside it can close."""
    ticks = "`" * (longest_backtick_run(text) + 1)
    if text.startswith("`") or text.endswith("`"):
        text = " {} ".format(text)
    return ticks + text + ticks


def code_block(text, info=""):
    """Fence text so that no line inside it can close the block."""
    fence = "`" * max(3, longest_backtick_run(text) + 1)
    return [fence + info, text, fence]


def headings(title):
    """Return the (normal, failed) headings, scoped by TITLE when it is set."""
    # A line break would end the heading; keep the title on one line.
    title = " ".join(title.split())
    scope = " ({})".format(title) if title else ""
    return (
        "### 🏗 Terraform Plan" + scope,
        "### ❌ Terraform Plan" + scope + ": failed",
    )


def icon(change):
    """Return the icon for a resource change, or "" if it shows nothing."""
    actions = change["change"]["actions"]
    prefix = ""
    if change["change"].get("importing") is not None:
        prefix += "📥"
    if change.get("previous_address") is not None:
        prefix += "📦"

    if actions == ["create"]:
        return prefix + "➕"
    if actions == ["update"]:
        return prefix + "🔄"
    if actions == ["delete"]:
        return prefix + "➖"
    if actions == ["no-op"]:
        return prefix
    return prefix + "♻️"


def changed_resources(plan):
    """Resource changes worth listing, paired with their icon."""
    for change in plan.get("resource_changes") or []:
        if change["change"]["actions"] == ["read"]:
            continue
        mark = icon(change)
        if mark:
            yield mark, change


def summary_counts(plan):
    counts = dict.fromkeys(
        ("added", "changed", "replaced", "deleted", "imported", "moved"), 0
    )
    for change in plan.get("resource_changes") or []:
        actions = change["change"]["actions"]
        if actions == ["create"]:
            counts["added"] += 1
        elif actions == ["update"]:
            counts["changed"] += 1
        elif actions == ["delete"]:
            counts["deleted"] += 1
        elif len(actions) > 1:
            counts["replaced"] += 1
        if change["change"].get("importing") is not None:
            counts["imported"] += 1
        if change.get("previous_address") is not None:
            counts["moved"] += 1
    return counts


def no_changes(heading):
    return [heading, "", "No infrastructure changes."]


def changes(plan, plan_text, heading):
    counts = summary_counts(plan)
    lines = [
        heading,
        "",
        "| ➕ Add | 🔄 Change | ♻️ Replace | ➖ Destroy | 📥 Import | 📦 Move |",
        "|:--:|:--:|:--:|:--:|:--:|:--:|",
        "| {added} | {changed} | {replaced} | {deleted} | {imported} | {moved} |".format(
            **counts
        ),
        "",
    ]

    for mark, change in changed_resources(plan):
        if change.get("previous_address") is not None:
            body = "{} → {}".format(
                code_span(change["previous_address"]), code_span(change["address"])
            )
        else:
            body = code_span(change["address"])
        lines.append("- {} {}".format(mark, body))

    lines += ["", "<details>", "<summary>Plan details</summary>", ""]
    lines += code_block(mark_diff(plan_text.rstrip("\n")), "diff")
    lines += ["", "</details>"]
    return lines


def failed(error_message, heading):
    return [heading, "", *code_block(error_message)]


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def main():
    exitcode = os.environ.get("EXITCODE", "")
    commit_sha = os.environ.get("COMMIT_SHA", "")
    run_url = os.environ.get("RUN_URL", "")
    heading, failed_heading = headings(os.environ.get("TITLE", "").strip())

    if exitcode == "0":
        lines = no_changes(heading)
    elif exitcode == "2":
        plan_json = os.environ.get("PLAN_JSON", "")
        plan_text = os.environ.get("PLAN_TEXT", "")
        if not plan_json or not plan_text:
            print(
                "::error::plan-json and plan-text are both required when exitcode is 2",
                file=sys.stderr,
            )
            return 1
        lines = changes(json.loads(read(plan_json)), read(plan_text), heading)
    else:
        lines = failed(os.environ.get("ERROR_MESSAGE", ""), failed_heading)

    lines += [
        "",
        "<sub>commit `{}` · [workflow run]({})</sub>".format(commit_sha[:7], run_url),
    ]
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
