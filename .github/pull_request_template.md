**A pull request that does not fill this in is closed without review.** See
[CONTRIBUTING.md](https://github.com/kukv/terraform-plan-comment-action/blob/main/CONTRIBUTING.md)
before opening one. Commits use a `feat:` / `fix:` / `docs:` / `chore:` / `ci:` prefix; CI must
pass.

## What and why

<!-- What changes, and why. "Why" is required — a diff without a reason is closed. -->

## Verification

<!-- The exact commands you ran (e.g. `./tests/run.sh`, `actionlint`) and what they printed.
     "I tested it" is not enough on its own. -->

## Scope

<!-- `scripts/build_comment.py` uses the standard library only, reads everything from environment
     variables (no `${{ }}`), keeps the three branches of `exitcode` intact, and never runs
     `terraform`. Confirm this change stays inside that line, or say why it needs to cross it.
     If you touched a workflow, confirm any new or changed action is pinned to a full commit SHA
     with a `# vX.Y.Z` comment. -->

## Comment output (delete this section if unchanged)

<!-- Every change to the generated comment needs a fixture: the updated or added
     `tests/fixtures/<case>/expected.md`, in this same pull request. Paste the diff of the
     expected markdown — that is what consumers will see. -->

## Documentation (delete this section if unchanged)

<!-- Changes to inputs or behavior update both `README.md` and `README.ja.md`. -->

## Release notes label

<!-- Which label from .github/release.yaml applies to this change, so the maintainer can attach
     it: Kind: Feature, Kind: Bug Fix, Kind: Enhancement, Impact: Breaking, or Kind: Dependencies. -->

## AI use (verified?)

<!-- If AI assisted this submission, confirm per
     [Use of AI](https://github.com/kukv/terraform-plan-comment-action/blob/main/CONTRIBUTING.md#use-of-ai)
     that you've read, verified and can defend the output. -->
