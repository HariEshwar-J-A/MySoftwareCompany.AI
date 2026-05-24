# MySoftwareCompany.AI

**AI software agencies you can run from the terminal.** MySoftwareCompany.AI vendors
[MetaGPT](vendor/MetaGPT/) (multi-agent runtime) and [agency-agents](vendor/agency-agents/)
(~144 specialist personas + NEXUS playbooks) into one product: configure an org, describe
an idea, and let a coordinated team build it—with quality gates and human review before
client handoff.

**Version:** 0.1.0 · **Website:** [mysoftwarecompany.ai](https://mysoftwarecompany.ai) (see [`website/`](website/)) · **Changelog:** [CHANGELOG.md](CHANGELOG.md)

## Install

### From PyPI (CLI package)

The published wheel includes the `msc` Python package. Full agency runs still need this repo for vendored MetaGPT, org YAML, and agent catalogs:

```bash
pip install mscai==0.1.0
msc --version
```

### From source (recommended for development)

```bash
git clone https://github.com/mysoftwarecompany/MySoftwareCompany.AI.git
cd MySoftwareCompany.AI
make vendor-sync install-dev
```

Publishing steps for maintainers: [docs/PUBLISHING.md](docs/PUBLISHING.md).

## Quick start

```bash
msc init
msc orgs list
msc agents list --division engineering
msc dry-run --org startup-mvp
msc run "Build a todo CLI" --org startup-mvp --budget 10
```

Config: copy `config.example.yaml` to `~/.msc/config.yaml` (paths, default org). **API keys**
go in `~/.metagpt/config2.yaml` only — never in the repo.

## Benchmark gate

Phase 2 **hard gate** before client sales. Current scorecard: **[PASS](benchmarks/SCORECARD.md)** (avg requirements ≥ 0.67, median polish ≤ 8h).

```bash
msc benchmark run --dry-run   # CI-safe, no API keys
msc benchmark report
msc benchmark gate
```

## Marketplace

Premium org packs (MSC1 license tokens, Stripe checkout on the website):

```bash
msc marketplace orgs
msc marketplace login --token "<MSC1 token from purchase>"
```

Browse packs and buy at `/marketplace` on the marketing site. See [website/README.md](website/README.md) for Stripe env vars.

## Website

The Phase 5 Next.js site lives in [`website/`](website/):

```bash
cd website && npm ci && npm run dev
```

Pages: Home, Services, Marketplace (Stripe checkout), Pricing, Contact. Demo embed: set `NEXT_PUBLIC_DEMO_VIDEO_URL` (see [docs/DEMO.md](docs/DEMO.md) for a recording script).

## License

- **Core product** (`packages/msc/`, `orgs/`, `scripts/`, `benchmarks/`, `website/`): [BUSL-1.1](LICENSE)
- **Vendored upstream** (`vendor/`): MIT — see [NOTICE](NOTICE)
- **Commercial production use:** [COMMERCIAL.md](COMMERCIAL.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Run `make ci` and `cd website && npm run build` before opening a PR.

## Repository layout

| Path | Role |
|------|------|
| `packages/msc/` | CLI, loader, runtime, marketplace, benchmarks |
| `orgs/` | Org templates (OSS + premium) |
| `benchmarks/` | Standard suite + scorecard |
| `website/` | Marketing site and Stripe APIs |
| `vendor/` | MetaGPT + agency-agents (MIT) |
