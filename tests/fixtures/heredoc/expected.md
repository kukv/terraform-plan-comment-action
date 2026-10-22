### 🏗 Terraform Plan

| ➕ Add | 🔄 Change | ♻️ Replace | ➖ Destroy | 📥 Import | 📦 Move |
|:--:|:--:|:--:|:--:|:--:|:--:|
| 1 | 1 | 0 | 0 | 0 | 0 |

- 🔄 `terraform_data.x`
- ➕ `terraform_data.z`

<details>
<summary>Plan details</summary>

```diff

Terraform used the selected providers to generate the following execution
plan. Resource actions are indicated with the following symbols:
+   create
~   update in-place

Terraform will perform the following actions:

  # terraform_data.x will be updated in-place
~   resource "terraform_data" "x" {
        id     = "3536c7a5-62d7-37e2-7da2-9cd409adbf50"
~       input  = <<-EOT
            keep
            - dash line
            + plus line
-           old
+           new
        EOT
~       output = <<-EOT
            keep
            - dash line
            + plus line
            old
        EOT -> (known after apply)
    }

  # terraform_data.z will be created
+   resource "terraform_data" "z" {
+       id     = (known after apply)
+       input  = {
+           script = <<-EOT
                echo hi
                - not a destroy
                ~ not an update
            EOT
        }
+       output = (known after apply)
    }

Plan: 1 to add, 1 to change, 0 to destroy.
```

</details>

<sub>commit `0123456` · [workflow run](https://github.com/kukv/terraform-plan-comment-action/actions/runs/1)</sub>
