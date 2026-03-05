---
description: Discrepancy debugging — trace data issues through the lakehouse, identify root causes.
---

You are investigating a data discrepancy for Madison Group Enterprises.

**Boot:** Read `../../CLAUDE.md`, `../../context.md`, `../../references/query-patterns.md`,
`../../references/investigation.md`. For unfamiliar tables, use `DESCRIBE TABLE` to discover columns.

## Workflow

1. **Observe** (internal) — Reproduce the discrepancy against `datawarehouse.*` views.
2. **Hypothesise** (internal) — Rank likely causes. Use `int.maincontroltable` to understand ETL logic (tracing/debugging only — never for primary analysis).
3. **Trace** (internal) — Follow data through layers. Intermediate layers for tracing only.
4. **Confirm** (internal) — Isolate affected records. Quantify impact in rows and dollars.
5. **Report** (visible) — Plain language: what happened, why, how big the impact is, what to do about it.

Save investigation queries to `scratch/queries/` and findings to `scratch/analysis/`.
