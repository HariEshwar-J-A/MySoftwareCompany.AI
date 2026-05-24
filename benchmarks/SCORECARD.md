# MySoftwareCompany.AI Benchmark Scorecard

Phase 2 **hard gate** before client sales.

## Pass threshold (locked)
- Avg requirements met (0–3) ≥ **0.67**
- Median polish hours ≤ **8h**

**Status:** PASS

Meets Phase 2 gate threshold.

| Build | Compiles | Tests | Req | Polish (h) | LLM $ | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Python Todo CLI | 1 | 1 | 2 | 1.0 | 0.02 | 5/5 tests pass; add/list/complete/delete work |
| Static Landing Page | 0 | 0 | 1 | 6.0 | 0.05 | All 5 sections drafted with Tailwind responsive classes. Hero.js has JSX syntax errors; no package.json/build scaffold — not runnable. |
| FastAPI CRUD API | 1 | 1 | 2 | 2.0 | 0.06 | Full CRUD routes, SQLite/SQLAlchemy, pytest test_create_item passes. Deprecation warnings; only one test. |
| React SPA with Auth | 0 | 0 | 0 | 8.0 | 0.05 | Run failed in 21s; empty workspace. TeamLeader planned PRD→arch→tasks→code chain, never assigned implementation; waited on Alice indefinitely. |
| CLI 2048 Game | 1 | 0 | 1 | 2.0 | 0.04 | 2048 logic present for up/left/down/right but game loop passes w/a/s/d — moves have no effect. ~1 line key-map fix to be playable. |
| CSV Transform Script | 1 | 0 | 1 | 4.0 | 0.03 | Compiles and passthrough CSV works. README filter/aggregate examples fail: all values coerced to str (age>25 errors), aggregate eval lacks column scope (sum(salary) undefined). Works only with int(age)>25 and int(row['salary']). Uses eval(); errors print but still writes unfiltered data. README+sample_data present, no automated tests. |

## Dry-run (CI, no API keys)
```bash
msc benchmark run --dry-run
msc benchmark report
msc benchmark gate
```

## Full runs
Set API keys, merge Phase 1 runtime + vendor/MetaGPT, then `msc benchmark run`.
Score each `benchmarks/runs/<id>/result.json` after human review.

_Generated 2026-05-24 18:24 UTC_
