# MySoftwareCompany.AI Benchmark Scorecard

Phase 2 **hard gate** before client sales.

## Pass threshold (locked)
- Avg requirements met (0–3) ≥ **0.67**
- Median polish hours ≤ **8h**

**Status:** INCOMPLETE

Human scores required (NEEDS_HUMAN_SCORE).

| Build | Compiles | Tests | Req | Polish (h) | LLM $ | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Python Todo CLI | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | Fill after human review. |
| Static Landing Page | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | Fill after human review. |
| FastAPI CRUD API | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | Fill after human review. |
| React SPA with Auth | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | Fill after human review. |
| CLI 2048 Game | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | Fill after human review. |
| CSV Transform Script | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | Fill after human review. |

## Dry-run (CI, no API keys)
```bash
msc benchmark run --dry-run
msc benchmark report
msc benchmark gate
```

## Full runs
Set API keys, merge Phase 1 runtime + vendor/MetaGPT, then `msc benchmark run`.
Score each `benchmarks/runs/<id>/result.json` after human review.

_Generated 2026-05-20 04:41 UTC_
