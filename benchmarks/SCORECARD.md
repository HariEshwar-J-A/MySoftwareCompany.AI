# MySoftwareCompany.AI Benchmark Scorecard

Phase 2 **hard gate** before client sales.

## Pass threshold (locked)
- Avg requirements met (0–3) ≥ **0.67**
- Median polish hours ≤ **8h**

**Status:** INCOMPLETE

Human scores required (2/6 scored). Run `msc benchmark gate --preliminary` for a partial read once ≥2 are scored.

| Build | Compiles | Tests | Req | Polish (h) | LLM $ | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Python Todo CLI | 0 | 0 | 1 | 0.5 | 0.02 | todo.py written with add/list/complete/delete structure but f-string syntax error on line 41 (unmatched bracket). Retry loop fired correctly. One-line fix to pass. |
| Static Landing Page | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | Fill after human review. |
| FastAPI CRUD API | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | Fill after human review. |
| React SPA with Auth | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | Fill after human review. |
| CLI 2048 Game | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | NEEDS_HUMAN_SCORE | Fill after human review. |
| CSV Transform Script | 1 | 1 | 2 | 2.0 | 0.03 | csv_aggregator.py compiles clean. filter+aggregate+sum+average all work. sample.csv and test1.sh included. CLI arg names differ from README examples (underscore vs dash) - minor UX fix needed. Run crashed mid-refinement due to transient OpenRouter SSE error, not code quality. |

## Dry-run (CI, no API keys)
```bash
msc benchmark run --dry-run
msc benchmark report
msc benchmark gate
```

## Full runs
Set API keys, merge Phase 1 runtime + vendor/MetaGPT, then `msc benchmark run`.
Score each `benchmarks/runs/<id>/result.json` after human review.

_Generated 2026-05-23 23:05 UTC_
