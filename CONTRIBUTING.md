# Contributing

Thanks for taking the time to improve terraform-plan-comment-action.

## Getting started

There are two files. `scripts/build_comment.py` turns a plan result into a markdown comment on
stdout, reading everything it needs from the environment. `action.yml` declares the inputs, runs
that script, and posts the output with `gh`. The script uses the **standard library only** —
nothing to install, nothing to build.

```bash
./tests/run.sh   # compare generated comments against the expected markdown
actionlint       # lint the workflows

# run the script on a plan you have lying around
EXITCODE=2 PLAN_JSON=plan.json PLAN_TEXT=plan.txt \
  COMMIT_SHA=0000000 RUN_URL=https://example.com \
  python3 scripts/build_comment.py
```

Keeping the script free of GitHub Actions specifics is deliberate: it takes plain environment
variables, so you can run it by hand against a real plan and read the result before pushing.

Keep the standard-library-only rule. An action that installs dependencies to format a comment
would make every consumer's workflow slower and its supply chain wider.

Keep the action free of a Terraform dependency. It reads the output of `terraform show`; it must
never run `terraform` itself. A second Terraform version inside the action is exactly the drift
this action exists to avoid.

## Changing the comment

Every change to the output needs a fixture. `tests/fixtures/<case>/expected.md` is the exact
markdown the script must produce; `tests/run.sh` diffs the two. Update the expected file in the
same commit as the change, and read the diff — it is the review of what consumers will see.

1. Keep the three branches of `exitcode` intact: `0` (no changes), `2` (changes), anything else
   (failure). Each one must produce a comment.
2. Only `plan-json` is parsed. The text from `terraform show -no-color` is pasted into a `diff`
   block as-is — do not start parsing it.
3. Stick to the documented fields of the plan JSON (`resource_changes[].change.actions`,
   `.change.importing`, `.previous_address`). They are stable across `format_version` 1.x.
4. Keep `${{ }}` out of the script. `action.yml` maps expressions to environment variables and
   the script reads those, so it stays runnable and lintable on its own.
5. The comment body is English. Keep it that way.
6. Update both `README.md` and `README.ja.md` when inputs or behavior change.

## Pull requests

- CI runs on every pull request: `ci.yml` (the fixture tests) and `security.yml` (gitleaks,
  osv-scanner, zizmor, actionlint). All of them must pass.
- Pin any GitHub Action you add to a full commit SHA with a `# vX.Y.Z` comment, and pin Docker
  images by digest. Renovate follows them through the `# renovate:` annotations.
- Commit messages use a `feat:` / `fix:` / `docs:` / `chore:` / `ci:` prefix.
- Label the pull request so it lands in the right section of the release notes — see the
  categories in `.github/release.yaml` (`Kind: Feature`, `Kind: Bug Fix`, `Kind: Enhancement`,
  `Impact: Breaking`, `Kind: Dependencies`).
- Review by the maintainer (`.github/CODEOWNERS`) is required before merge.

## Releases

Push a `vX.Y.Z` tag on `main`. `on-tag-push.yml` creates the GitHub Release and generates the
notes from the labels of the pull requests included, following `.github/release.yaml`.

```bash
git tag v1.0.0 && git push origin v1.0.0
```

Consumers pin a commit SHA with the tag in a comment (`@<sha> # v1.0.0`), so tags are never
moved once pushed. `feat:` bumps the minor, `fix:` the patch, and anything labelled
`Impact: Breaking` the major.

## Use of AI

AI assistance is fine. Submitting what an AI produced without understanding it is not.

Generating a submission takes seconds; verifying one takes a person's time. Sending
unverified output moves that cost onto the maintainer and takes time away from the review
this project actually needs.

Before you open an issue or a pull request, you are expected to have read the output,
verified it against this repository, and be able to explain and defend it. You are the
author of what you submit, whatever tool helped you write it.

Issues and pull requests that appear to be unreviewed AI output — invented inputs that do not
exist, a diff that does not follow from the description, boilerplate that does not engage with
this project — are **closed without notice and without individual explanation**. That judgment
is the maintainer's, and there is no appeal process; you are welcome to open a new issue or
pull request that shows your own reasoning.

Closing one does not mean the underlying point was worthless. If a closed issue or pull
request contains something useful, the maintainer may take it up — as an issue raised by
the maintainer, or by merging or rewriting the change — without notice and without credit
to the original submitter. Anything you submit is licensed under the
[MIT License](LICENSE), and opening an issue or pull request here means you accept this
handling.

## Reporting problems

- A security-relevant issue: see [SECURITY.md](SECURITY.md).
- Anything else: open an issue with the workflow snippet and the plan output that reproduces it.

By contributing you agree that your contributions are licensed under the
[MIT License](LICENSE).
