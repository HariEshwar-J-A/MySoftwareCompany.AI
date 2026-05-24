# Changelog

All notable changes to the MySoftwareCompany.AI core product (`mscai` on PyPI) are documented here.

## [0.1.0] - 2026-05-24

First public launch release.

### Added

- **CLI** (`msc` / `mscai`): `init`, `orgs`, `agents`, `dry-run`, `run`, `benchmark`, `marketplace`, resume and review gates.
- **Org templates**: OSS packs under `orgs/` plus premium marketplace packs with MSC1 license tokens.
- **Runtime**: MetaGPT integration, NEXUS playbooks, LLM tier routing, evidence and human-review gates.
- **Benchmark suite**: Six standard builds with Phase 2 hard gate ([benchmarks/SCORECARD.md](benchmarks/SCORECARD.md) — **PASS**).
- **Marketplace**: Entitlements, Stripe webhook stub, encrypted premium org packs.
- **Website**: Next.js marketing site (services, marketplace checkout, pricing, contact) at `website/`.

### Notes

- Vendored upstream (`vendor/MetaGPT`, `vendor/agency-agents`) remains MIT; core is BUSL-1.1 until the Change Date.
- Production client delivery requires a commercial license — see [COMMERCIAL.md](COMMERCIAL.md).

[0.1.0]: https://github.com/mysoftwarecompany/MySoftwareCompany.AI/releases/tag/v0.1.0
