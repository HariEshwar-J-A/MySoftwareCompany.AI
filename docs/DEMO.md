# Demo video script (outline)

Use this outline when recording the v0.1.0 launch demo. Set `NEXT_PUBLIC_DEMO_VIDEO_URL` on the marketing site to the published YouTube or Vimeo URL when ready.

## Target length

5–7 minutes.

## Act 1 — Problem (30s)

- Single chatbot vs coordinated agency: roles, playbooks, gates.
- Show [mysoftwarecompany.ai](https://mysoftwarecompany.ai) home hero (optional B-roll).

## Act 2 — Install & init (60s)

```bash
pip install mscai==0.1.0
msc init
msc --version
msc orgs list
```

- Mention `~/.msc/config.yaml` and keys in `~/.metagpt/config2.yaml`.

## Act 3 — Dry run & agents (90s)

```bash
msc agents list --division engineering
msc dry-run --org startup-mvp
msc run "Build a todo CLI" --org startup-mvp --budget 10
```

- Highlight phased output, evidence paths, human-review reminder for client work.

## Act 4 — Benchmark gate (45s)

```bash
msc benchmark gate
```

- Open [benchmarks/SCORECARD.md](../benchmarks/SCORECARD.md): **PASS**, thresholds 0.67 req avg / 8h polish median.

## Act 5 — Marketplace (60s)

```bash
msc marketplace orgs
```

- Website: `/marketplace` → Stripe test checkout → success page with MSC1 token and `msc marketplace login`.

## Act 6 — CTA (30s)

- PyPI: `pip install mscai`
- Repo README, services contact, commercial license pointer.

## Production notes

- Terminal: large font, dark theme, no secrets on screen.
- Blur or use test Stripe keys only.
- Export 1080p; upload unlisted until launch day.
