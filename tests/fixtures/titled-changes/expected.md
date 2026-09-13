### 🏗 Terraform Plan (zone-b8m.app)

| ➕ Add | 🔄 Change | ♻️ Replace | ➖ Destroy | 📥 Import | 📦 Move |
|:--:|:--:|:--:|:--:|:--:|:--:|
| 1 | 1 | 1 | 1 | 1 | 1 |

- ➕ `github_repository.added`
- 🔄 `github_repository.changed`
- ➖ `github_repository.deleted`
- ♻️ `github_repository.replaced`
- 📥 `github_repository.imported`
- 📦 `github_repository.moved_from` → `github_repository.moved_to`

<details>
<summary>Plan details</summary>

```diff
Terraform used the selected providers to generate the following execution
plan. Resource actions are indicated with the following symbols:
+   create
~   update in-place
-   destroy

Terraform will perform the following actions:

  # github_repository.added will be created
+   resource "github_repository" "added" {
+       name       = "added"
+       visibility = "public"
    }

  # github_repository.changed will be updated in-place
~   resource "github_repository" "changed" {
        name        = "changed"
~       description = "old" -> "new"
    }

  # github_repository.deleted will be destroyed
-   resource "github_repository" "deleted" {
-       name = "deleted" -> null
    }

Plan: 1 to add, 1 to change, 1 to destroy.
```

</details>

<sub>commit `0123456` · [workflow run](https://github.com/kukv/terraform-plan-comment-action/actions/runs/1)</sub>
