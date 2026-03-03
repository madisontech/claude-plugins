---
description: Discrepancy debugging — trace data issues through the lakehouse, identify root causes.
---

You are investigating a data discrepancy for Madison Group Enterprises.

## Boot Sequence (mandatory)

Read these files before starting any investigation. Do not proceed until all are loaded.

1. Read `../../CLAUDE.md` — disposition, communication style, quality gate
2. Read `../../context.md` — SQL rules, join casting, exclusions, business context
3. Read `../../references/query-patterns.md` — verified SQL templates
4. Read `../../references/investigation.md` — ETL tracing, medallion architecture, control table

If you encounter a table not covered in context.md, load `../../references/schema-inventory.md`.

## Mode Declaration

```
Mode:    Investigation
Scope:   [Division, BU, Time Period, Key Filters]
Output:  narrative (investigation report)
Loading: CLAUDE.md, context.md, query-patterns.md, investigation.md
```

## Workflow

1. **Observe** — Reproduce the reported discrepancy with a query against `datawarehouse.*` views. Compare to the reported value.
2. **Hypothesise** — Rank likely causes: join mismatch, filter gap, date boundary, BU attribution path, sentinel orphans, trailing spaces, ETL lag, disabled queries, rebate inclusion, FX direction.
3. **Trace** — Follow data through layers. Use `int.maincontroltable` GoldIntegrationQuery to understand transformation logic. Intermediate layers are for tracing only.
4. **Confirm** — Isolate affected records. Quantify impact (rows, dollar value). Determine if data issue or query issue.
5. **Report** — Structure as: Discrepancy (reported vs correct), Root cause (specific detail), Impact (rows, dollars, affected reports), Fix (ETL, query, report, or source).

Always return to `datawarehouse.*` views for the corrected authoritative number.

## Rules

- Source of truth: `datawarehouse.fact.*` and `datawarehouse.dim.*` only
- GoldIntegrationQuery is for learning/debugging — never for primary analysis
- Check source system before every join — CAST rules are in context.md
- LEFT JOIN by default; -1 keys = unmatched records
- Save investigation queries to `scratch/queries/` and findings to `scratch/analysis/`
