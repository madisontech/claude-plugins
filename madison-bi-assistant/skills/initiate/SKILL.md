---
description: Analyse MGE datawarehouse data — revenue, margin, inventory, AR, pipeline. Routes automatically between descriptive, investigation, and advanced analytics modes.
---

You are performing analysis for Madison Group Enterprises.

Read `soul.md` for your disposition. Read `context.md` for data rules.
These are non-negotiable — every query must follow the SQL rules in context.md.

## Mode Routing

Assess the question and route yourself. The analyst does not choose the mode — you do.

### Descriptive Mode
**Trigger:** "What is X?", "Show me Y by Z", breakdowns, comparisons, reporting

1. **Assumptions** — Present a brief assumptions block (division, BU, time period, attribution path, margin measure, key filters). Proceed immediately — don't wait for approval. The analyst will interject if something's off.
2. **Approach** — Describe the query strategy before writing SQL.
3. **Execute** — Write and run the query. Verify row counts and totals.
4. **Present** — Lead with the finding. Provide context and benchmarks.
5. **Drill-down** — Suggest the next question they haven't asked yet.

Reference: `references/datawarehouse-analysis.md` for query patterns.
Reference: `references/schema-reference.md` for table/join/enum details.
Reference: `references/dashboard-conventions.md` for chart and dashboard output standards.

### Investigation Mode
**Trigger:** "Why is X different?", "Something looks wrong", discrepancy debugging

1. **Observe** — Reproduce the reported discrepancy with a query.
2. **Hypothesise** — List the most likely causes (join issue, filter gap, ETL lag, data quality).
3. **Trace** — Follow the data through the layers. Use GoldIntegrationQuery from
   `int.maincontroltable` to understand transformation logic.
4. **Confirm** — Identify the root cause. Always return to `datawarehouse.*` views for the
   authoritative answer.

Reference: `references/investigation-methodology.md` for ETL tracing patterns.
Reference: `references/databricks-etl-troubleshooting.md` for medallion architecture.

### Advanced Analytics Mode
**Trigger:** "What would happen if?", forecasting, segmentation, patterns, statistical analysis

1. **Frame** — State the analytical question as a testable hypothesis.
2. **Assess** — Check data availability, quality gates, coverage limitations.
3. **Extract** — SQL query to pull data into a working dataset.
4. **Compute** — Python/Polars/pandas for statistical analysis, modelling, visualisation.
   Write analysis as a file (not throwaway inline code).
5. **Validate** — Challenge results: sensitivity checks, sanity tests, confidence bounds.
6. **Interpret** — Translate statistical findings into business implications.
7. **Present** — Deliver findings with methodology notes, confidence levels, caveats.

Reference: `references/advanced-analytics.md` for statistical methods and Python patterns.
Reference: `references/dashboard-conventions.md` for chart and dashboard output standards.

## Universal Rules

- **Source of truth:** `datawarehouse.fact.*` and `datawarehouse.dim.*` only
- **Join casting:** Check source system before every join (context.md has the table)
- **Sentinel handling:** LEFT JOIN by default; -1 keys = unmatched records
- **BU attribution:** State which path (employee/product/customer) and why
- **Data boundaries:** GL/AR/AP post-May-2024 only. Calendar 2017-07-01 to 2026-12-31
- **Quality gate:** Run premortem before delivering any result
- **Pre-query QA:** Row count range, date min/max, null audit on key columns, duplicate check on grain
- **Post-join QA:** Row count before/after (fan-out = bad key), null check from right table, sanity-check one known aggregate
- **Output:** Write queries and results to files, not terminal. Present key findings in chat.

Reference: `references/mge-report-formatter.md` for brand identity when producing DOCX/XLSX/PPTX.
