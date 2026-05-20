# MySoftwareCompany.AI

**AI software agencies you can run from the terminal.** MySoftwareCompany.AI vendors
[MetaGPT](vendor/MetaGPT/) (multi-agent runtime) and [agency-agents](vendor/agency-agents/)
(~144 specialist personas + NEXUS playbooks) into one product: configure an org, describe
an idea, and let a coordinated team build it—with quality gates and human review before
client handoff.

## Install

```bash
git clone https://github.com/mysoftwarecompany/MySoftwareCompany.AI.git
cd MySoftwareCompany.AI
make vendor-sync install-dev
```

## Quick start

```bash
msc init
msc orgs list
msc agents list --division engineering
msc dry-run --org startup-mvp
msc run "Build a todo CLI" --org startup-mvp --budget 10
```

Config lives at `~/.msc/config.yaml` (LLM keys, default org, workspace path).

## License

- **Core product** (`packages/msc/`, `orgs/`, `scripts/`, `benchmarks/`): [BUSL-1.1](LICENSE)
- **Vendored upstream** (`vendor/`): MIT — see [NOTICE](NOTICE)
- **Commercial production use:** [COMMERCIAL.md](COMMERCIAL.md)

## Quality gates

1. **Benchmark gate (Phase 2):** Structured build suite with published scorecard before client sales.
2. **Human review gate:** Required for services deliverables; bypass only via `--no-human-review` for personal use.

## Repository layout

Runtime modules live under `packages/msc/` (loader, runtime, review, CLI). See the integration
plan for the full roadmap.
