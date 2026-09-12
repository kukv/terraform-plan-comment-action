# terraform-plan-comment-action

Terraform の実行計画を Pull Request にコメントする composite action。

この action は `terraform` を実行しない。計画の実行は呼び出し側に任せ、その結果
（終了コードと `terraform show` の出力ファイル）を受け取って整形・投稿するだけ。
呼び出し側で使っているバージョンとの差異が生まれないようにするため。

依存するのは `terraform show -json` の JSON スキーマ（`format_version` 1.x）のみ。
OpenTofu の `tofu show -json` の出力も渡せる。

ランナーに `gh` と `jq` があることを前提とする（GitHub-hosted runner には両方入っている）。

## inputs

| input | 必須 | デフォルト | 説明 |
|---|---|---|---|
| `exitcode` | ✓ | — | 計画の終了コード（`-detailed-exitcode` 付きで実行したときの値）。`0` = 変更なし、`2` = 変更あり、それ以外 = 失敗 |
| `plan-json` | — | `''` | `terraform show -json <planfile>` の出力ファイルパス。`exitcode` が `2` のときのみ参照される |
| `plan-text` | — | `''` | `terraform show -no-color <planfile>` の出力ファイルパス。同上 |
| `error-message` | — | `''` | 失敗時にコメントへ載せる文字列 |
| `github-token` | ✓ | — | コメント投稿に使うトークン。`pull-requests: write` が必要 |
| `pr-number` | — | `github.event.pull_request.number` | コメント先の PR 番号 |

`plan-json` / `plan-text` のパスは **ワークスペースルートからの相対パスか絶対パス**。
composite action 内のステップは `$GITHUB_WORKSPACE` を作業ディレクトリとして実行され、
呼び出し側ジョブの `defaults.run.working-directory` は効かない。
`${{ runner.temp }}` 配下の絶対パスに書き出して渡すのが確実。

`exitcode` が `2` 以外のときは計画ファイルが存在せず `terraform show` を実行できないため、
`plan-json` / `plan-text` は必須にしていない。呼び出し側の `terraform show` ステップには
`if: steps.<plan step id>.outputs.exitcode == '2'` を付けること。

## outputs

なし。

## 責務の範囲

失敗時に job を失敗させるのは呼び出し側の責務。この action はコメントするだけで、
自身は異常終了しない（inputs の指定ミスを除く）。

## 使用例

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

`steps.plan.outputs.exitcode` と `steps.plan.outputs.stderr` は
`hashicorp/setup-terraform` のラッパーが提供する出力。ラッパーを無効にしている場合は
自前で終了コードを拾って渡す。

上の例では読みやすさのためタグ表記にしているが、実際に使うときは commit SHA で
ピンすることを推奨する。
