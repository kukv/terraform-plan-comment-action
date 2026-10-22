### 🏗 Terraform Plan

| ➕ Add | 🔄 Change | ♻️ Replace | ➖ Destroy | 📥 Import | 📦 Move |
|:--:|:--:|:--:|:--:|:--:|:--:|
| 1 | 0 | 0 | 0 | 0 | 1 |

- ➕ ``terraform_data.addr["k` @octocat [fake](https://example.invalid) `"]``
- 📦 ``terraform_data.old["`"]`` → ```terraform_data.new["``"]```

<details>
<summary>Plan details</summary>

````diff
Terraform will perform the following actions:

  # terraform_data.addr["k` @octocat [fake](https://example.invalid) `"] will be created
+   resource "terraform_data" "addr" {
+       input = <<-EOT
            line1
            
```
<!-- hidden
injected-outside-fence
        EOT
    }

Plan: 1 to add, 0 to change, 0 to destroy.
````

</details>

<sub>commit `0123456` · [workflow run](https://github.com/kukv/terraform-plan-comment-action/actions/runs/1)</sub>
