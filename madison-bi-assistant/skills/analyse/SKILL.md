---
description: Advanced analytics — forecasting, segmentation, statistical patterns, hypothesis testing.
---

You are performing advanced analytics for Madison Group Enterprises.

## Boot Sequence (mandatory)

Read these files before starting any analysis. Do not proceed until all are loaded.

1. Read `../../CLAUDE.md` — disposition, communication style, quality gate
2. Read `../../context.md` — SQL rules, join casting, exclusions, business context
3. Read `../../references/query-patterns.md` — verified SQL templates
4. Read `../../references/advanced-analytics.md` — statistical methods, Python patterns, validation

If you encounter a table not covered in context.md, load `../../references/schema-inventory.md`.

## Mode Declaration

```
Mode:    Analytics
Scope:   [Division, BU, Time Period, Key Filters]
Output:  Python analysis (files in scratch/)
Loading: CLAUDE.md, context.md, query-patterns.md, advanced-analytics.md
```

## Workflow

1. **Frame** — State the analytical question as a testable hypothesis.
2. **Assess** — Check data availability, quality gates, coverage limitations.
3. **Extract** — SQL query to pull data into a working dataset. Save to `scratch/queries/`.
4. **Compute** — Python/Polars/pandas for statistical analysis, modelling, visualisation. Write as a script file in `scratch/scripts/`, not throwaway inline code.
5. **Validate** — Challenge results: sensitivity checks, sanity tests, confidence bounds.
6. **Interpret** — Translate statistical findings into business implications.
7. **Present** — Deliver findings with methodology notes, confidence levels, caveats. Save to `scratch/analysis/`.

For a branded deliverable, follow up with `/madison-bi-assistant:format`.

## Rules

- Source of truth: `datawarehouse.fact.*` and `datawarehouse.dim.*` only
- Check source system before every join — CAST rules are in context.md
- LEFT JOIN by default; -1 keys = unmatched records
- File-first: all scripts and analysis output written to files, not terminal
- Multi-stage validation: never present unvalidated statistical results
- State assumptions, confidence intervals, and caveats explicitly
