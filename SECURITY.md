# Security Policy

## Supported versions

Only the latest release is supported. Users are expected to pin this action to a
commit SHA (`uses: kukv/terraform-plan-comment-action@<commit sha> # vX.Y.Z`) and to
update that pin when a new release is published; fixes are not backported to older tags.

## Reporting a vulnerability

Report privately through GitHub: open the **Security** tab of this repository and
choose **Report a vulnerability**. Please do not open a public issue, and do not
attach a working payload to anything public.

Include the workflow snippet and the plan output that reproduce the problem, and the
version (commit SHA) you ran.

## What counts as a security issue

- **Anything in the plan output that can affect the runner or the comment beyond its own
  text.** The action reads files produced by `terraform show` and passes them through a
  shell; a resource name or attribute value that causes command execution, or that escapes
  the comment body to reach the token or the workflow, is a vulnerability.
- **Leakage of the token passed as `github-token`**, including into the comment body or the
  job log.

Not a security issue:

- A comment that renders oddly (broken tables, a truncated diff). Open an ordinary issue.
- Secrets that appear in the plan output itself. Terraform writes them there; keep them out
  of the plan with `sensitive` variables and outputs.

## Handling

Reports are acknowledged and triaged by the maintainer. Once a fix is released, the
advisory is published with credit to the reporter unless anonymity is requested.
