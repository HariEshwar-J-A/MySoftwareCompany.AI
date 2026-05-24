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
make install-dev            # venv, vendors, editable msc + MetaGPT
msc init                    # creates .env from .env.example, ~/.msc, ~/.metagpt
# Edit .env — set OPENROUTER_API_KEY (https://openrouter.ai/keys)
msc init --env-only         # sync key into ~/.metagpt/config2.yaml
msc dry-run --org startup-mvp
msc run "Build a todo CLI" --org startup-mvp --budget 10 --rounds 20
```

First-time clone with vendors + website deps: `msc init --full`. Publishing: [docs/PUBLISHING.md](docs/PUBLISHING.md).

## Configuration (`msc init`)

| Command | What it does |
|---------|----------------|
| `msc init` | `.env` (if missing), `~/.msc/config.yaml`, `~/.metagpt/config2.yaml`, `workspace/` |
| `msc init --env-only` | After editing `.env`, sync `OPENROUTER_API_KEY` → MetaGPT config |
| `msc init --force` | Overwrite existing MSC + MetaGPT config files |
| `msc init --full` | Above + `vendor_sync` + `website` npm ci |

Repo-root [`.env`](.env.example) is the only file you edit for secrets. MSC applies tier models (DeepSeek Flash / Gemma / Kimi K2.6 on OpenRouter). Never commit `.env`.

**Logging:** console defaults to **WARNING** (no INFO lines); details still go to `vendor/MetaGPT/logs/` at **INFO**. Show INFO on stderr: `msc --info run …`. More: `msc --verbose` (DEBUG). Less: `msc --quiet` (ERROR only). Override: `MSC_LOG_LEVEL` in `.env`.

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
