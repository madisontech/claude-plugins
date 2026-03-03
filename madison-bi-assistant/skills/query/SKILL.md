---
description: Descriptive analysis — revenue, margin, inventory, AR, pipeline breakdowns and comparisons.
---

You are performing descriptive analysis for Madison Group Enterprises.

## Boot Sequence (mandatory)

Read these files before writing any query. Do not proceed until all are loaded.

1. Read `../../CLAUDE.md` — disposition, communication style, quality gate
2. Read `../../context.md` — SQL rules, join casting, exclusions, business context
3. Read `../../references/query-patterns.md` — verified SQL templates

If you encounter a table not covered in context.md, load `../../references/schema-inventory.md`.

## Mode Declaration

```
Mode:    Query
Scope:   [Division, BU, Time Period, Key Filters]
Output:  chat table
Loading: CLAUDE.md, context.md, query-patterns.md
```

## Workflow

1. **Scope** — State division, BU, time period, attribution path, filters. Proceed immediately — the analyst will interject if something's off.
2. **Approach** — Describe the query strategy before writing SQL.
3. **Execute** — Write and run the query. Save to `scratch/queries/`. Verify row counts and totals.
4. **Present** — Lead with the finding in chat. Provide context and benchmarks. Save detail to `scratch/analysis/` if >10 rows.
5. **Drill-down** — Suggest the next question they haven't asked yet.

For a branded deliverable (XLSX/DOCX/PPTX), follow up with `/madison-bi-assistant:format`.

## Rules

- Source of truth: `datawarehouse.fact.*` and `datawarehouse.dim.*` only
- Check source system before every join — CAST rules are in context.md
- LEFT JOIN by default; -1 keys = unmatched records
- State BU attribution path (employee/product/customer) and why
- TRIM employee BU always
- Run premortem before delivering any result
