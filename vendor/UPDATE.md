# Vendored upstream versions

| Package | SHA | Synced |
|---------|-----|--------|
| MetaGPT | `11cdf466d042aece04fc6cfd13b28e1a70341b1f` | 2026-05-20T04:38Z |
| agency-agents | `783f6a72bfd7f3135700ac273c619d92821b419a` | 2026-05-20T04:38Z |

## Re-vendor

```bash
make vendor-sync
```

Override sources: `METAGPT_SRC`, `AGENCY_SRC`.

## Internal note

`info-sentry/` is excluded at vendor time as out-of-scope upstream content.
