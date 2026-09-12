# Contributing

Thanks for taking the time to improve terraform-plan-comment-action.

## Getting started

The whole action is `action.yml`: an input definition and a single bash step that builds the
comment body and posts it with `gh`. There is nothing to install and nothing to build.

```bash
actionlint                          # lint the workflows
yq -r '.runs.steps[0].run' action.yml > /tmp/action-script.sh
shellcheck --shell=bash /tmp/action-script.sh
```

Keep the action free of a Terraform dependency. It reads the output of `terraform show`; it must
never run `terraform` itself. A second Terraform version inside the action is exactly the drift
this action exists to avoid.

## Changing the comment

1. Keep the three branches of `exitcode` intact: `0` (no changes), `2` (changes), anything else
   (failure). Each one must produce a comment.
2. Only `plan-json` is parsed. The text from `terraform show -no-color` is pasted into a `diff`
   block as-is — do not start parsing it.
3. Stick to the documented fields of the plan JSON (`resource_changes[].change.actions`,
   `.change.importing`, `.previous_address`). They are stable across `format_version` 1.x.
4. Pass every expression through `env:` rather than interpolating `${{ }}` into the script body,
   so the script stays valid shell and shellcheck can read it.
5. Update both `README.md` and `README.ja.md` when inputs or behavior change.

## Pull requests

- CI runs `security.yml` on every pull request (gitleaks, osv-scanner, zizmor, actionlint).
  All of it must pass.
- Pin any GitHub Action you add to a full commit SHA with a `# vX.Y.Z` comment, and pin Docker
  images by digest. Renovate follows them through the `# renovate:` annotations.
- Commit messages use a `feat:` / `fix:` / `docs:` / `chore:` / `ci:` prefix.
- Label the pull request so it lands in the right section of the release notes — see the
  categories in `.github/release.yaml` (`Kind: Feature`, `Kind: Bug Fix`, `Kind: Enhancement`,
  `Impact: Breaking`, `Kind: Dependencies`).
- Review by the maintainer (`.github/CODEOWNERS`) is required before merge.

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
