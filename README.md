# terraform-plan-comment-action

[日本語](README.ja.md)

A composite action that comments Terraform execution plans on pull requests.

This action never runs `terraform` itself. The caller runs the plan and passes the result —
an exit code and the files written by `terraform show` — and this action formats it and posts
the comment. Keeping execution on the caller's side means there is no second Terraform version
that could drift from the one used to apply.

Its only dependency is the JSON schema of `terraform show -json` (`format_version` 1.x).
The output of OpenTofu's `tofu show -json` works just as well.

The runner is expected to have `gh` and `jq` available (GitHub-hosted runners ship both).

## Inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `exitcode` | ✓ | — | Exit code of the plan run (with `-detailed-exitcode`). `0` = no changes, `2` = changes, anything else = failure |
| `plan-json` | — | `''` | Path to the output of `terraform show -json <planfile>`. Only read when `exitcode` is `2` |
| `plan-text` | — | `''` | Path to the output of `terraform show -no-color <planfile>`. Only read when `exitcode` is `2` |
| `error-message` | — | `''` | Message to include in the comment on failure |
| `github-token` | ✓ | — | Token used to post the comment. Requires `pull-requests: write` |
| `pr-number` | — | `github.event.pull_request.number` | Pull request number to comment on |

Paths given to `plan-json` and `plan-text` are **relative to the workspace root, or absolute**.
Steps inside a composite action run from `$GITHUB_WORKSPACE`, and the calling job's
`defaults.run.working-directory` does not apply to them. Writing the files to an absolute path
under `${{ runner.temp }}` is the reliable way to pass them.

Neither file is required, because when `exitcode` is anything other than `2` there is no plan
file and `terraform show` cannot run. Guard the caller's `terraform show` step with
`if: steps.<plan step id>.outputs.exitcode == '2'`.

## Outputs

None.

## Scope

Failing the job on a failed plan is the caller's responsibility. This action only posts the
comment; it does not exit non-zero (except when its own inputs are inconsistent).

## Usage

```yaml
permissions:
  contents: read

jobs:
  plan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v5
        with:
          persist-credentials: false

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.16.1

      - run: terraform init

      - name: Plan
        id: plan
        continue-on-error: true
        run: terraform plan -no-color -detailed-exitcode -out=tfplan

      - name: Show
        if: steps.plan.outputs.exitcode == '2'
        run: |
          terraform show -json tfplan > "${RUNNER_TEMP}/plan.json"
          terraform show -no-color tfplan > "${RUNNER_TEMP}/plan.txt"

      - name: Comment
        uses: kukv/terraform-plan-comment-action@v1
        with:
          exitcode: ${{ steps.plan.outputs.exitcode }}
          plan-json: ${{ runner.temp }}/plan.json
          plan-text: ${{ runner.temp }}/plan.txt
          error-message: ${{ steps.plan.outputs.stderr }}
          github-token: ${{ secrets.GITHUB_TOKEN }}

      - name: Fail if plan failed
        if: steps.plan.outputs.exitcode != '0' && steps.plan.outputs.exitcode != '2'
        run: exit 1
```

`steps.plan.outputs.exitcode` and `steps.plan.outputs.stderr` come from the
`hashicorp/setup-terraform` wrapper. If you disable the wrapper, capture the exit code yourself
and pass it in.

The example above uses a tag for readability. Pin to a full commit SHA in real use.

## Note on the comment language

The comment body is written in Japanese. There is no input to switch it yet — open an issue if
you need one.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
