---
description: Descriptive analysis — revenue, margin, inventory, AR, pipeline breakdowns and comparisons.
---

You are performing descriptive analysis for Madison Group Enterprises.

**Boot:** Read `../../CLAUDE.md`, `../../context.md`, `../../references/query-patterns.md`.
For unfamiliar tables, use `DESCRIBE TABLE datawarehouse.fact.<table>` to discover columns.

## Workflow

1. **Scope** (visible — one sentence) — Confirm what you're answering. Proceed immediately.
2. **Approach** (internal) — Plan joins, casts, exclusions, attribution path.
3. **Execute** (internal) — Write and run the query. Save to `scratch/queries/`.
4. **Present** (visible) — Lead with the finding, not the table. Save detail to `scratch/analysis/` if >10 rows.
5. **Drill-down** (visible) — Suggest the next question naturally.
