# Commercial Licensing — MySoftwareCompany.AI

## License overview

MySoftwareCompany.AI is distributed under the **Business Source License 1.1 (BUSL-1.1)**.
See [LICENSE](LICENSE) for full terms.

| Use case | License required |
|----------|------------------|
| Evaluation, learning, local dev, non-production experiments | Included (Additional Use Grant) |
| Production deployment or paid client deliverables | Commercial license from MySoftwareCompany.AI |
| Modifying and redistributing the BUSL-covered core | Subject to BUSL terms; converts to Apache-2.0 on Change Date |

On **May 20, 2030** (or four years after first public distribution of a given version,
whichever is earlier), each version converts to **Apache License 2.0**.

Contact: **licensing@mysoftwarecompany.ai**

## CLI (`mscai` / `msc`)

- **PyPI package name:** `mscai`
- **Console entry points:** `mscai` and `msc` (alias)
- Non-production use is permitted under BUSL without a separate fee.
- Commercial production use requires a paid license.

## Marketplace (premium org packs)

Premium organization packs are sold separately. Purchasers receive a license key that
unlocks signed, encrypted org definitions. Marketplace terms of service apply at purchase.

## Services SLA

Custom software builds delivered by MySoftwareCompany.AI include a **mandatory human review
gate** before any artifact is handed to a client. This is contractual.

- Client-facing runs **must not** use `--no-human-review`.
- The `--no-human-review` flag exists for personal experimentation only; it prints a
  stderr warning and records `no_human_review=true` in workspace metadata.

## Vendored open source

MetaGPT and agency-agents remain **MIT-licensed** in `vendor/`. See [NOTICE](NOTICE).
