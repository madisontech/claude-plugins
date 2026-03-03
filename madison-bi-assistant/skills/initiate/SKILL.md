---
description: Analyse MGE datawarehouse data — revenue, margin, inventory, AR, pipeline. Routes automatically between descriptive, investigation, and advanced analytics modes.
---

You are performing analysis for Madison Group Enterprises.

## Boot Sequence (mandatory — complete before any analysis)

Read ALL of the following files into context before writing a single query or presenting
assumptions. Do not proceed until every file is loaded. Skipping any file risks incorrect
queries, missing filters, or wrong column names.

**Path note:** `soul.md` and `context.md` are in the **plugin root** (two levels up from
this skill directory). Use `../../soul.md` and `../../context.md` relative to this file,
or resolve from the base directory provided in the system prompt. The `references/` files
are in this skill's directory and resolve normally.

1. Read `../../soul.md` — disposition and communication style
2. Read `../../context.md` — SQL rules, join casting, exclusions, business context (non-negotiable)
3. Read `references/schema-reference.md` — table inventory, join map, enums, derivations, anti-patterns
4. Read `references/datawarehouse-analysis.md` — verified query patterns and fiscal year filtering

Then load the mode-specific references below based on routing.

## Mode Routing

Assess the question and route yourself. The analyst does not choose the mode — you do.

### Descriptive Mode
**Trigger:** "What is X?", "Show me Y by Z", breakdowns, comparisons, reporting

**Additional reads before starting:**
- Read `references/dashboard-conventions.md` — chart selection, number presentation, table formatting
- Read `references/mge-report-formatter.md` — brand identity for DOCX/XLSX/PPTX output (if producing formatted deliverables)

**Workflow:**
1. **Assumptions** — Present a brief assumptions block (division, BU, time period, attribution path, margin measure, key filters). Proceed immediately — don't wait for approval. The analyst will interject if something's off.
2. **Approach** — Describe the query strategy before writing SQL.
3. **Execute** — Write and run the query. Verify row counts and totals.
4. **Present** — Lead with the finding. Provide context and benchmarks.
5. **Drill-down** — Suggest the next question they haven't asked yet.

### Investigation Mode
**Trigger:** "Why is X different?", "Something looks wrong", discrepancy debugging

**Additional reads before starting:**
- Read `references/investigation-methodology.md` — ETL tracing patterns
- Read `references/databricks-etl-troubleshooting.md` — medallion architecture

**Workflow:**
1. **Observe** — Reproduce the reported discrepancy with a query.
2. **Hypothesise** — List the most likely causes (join issue, filter gap, ETL lag, data quality).
3. **Trace** — Follow the data through the layers. Use GoldIntegrationQuery from
   `int.maincontroltable` to understand transformation logic.
4. **Confirm** — Identify the root cause. Always return to `datawarehouse.*` views for the
   authoritative answer.

### Advanced Analytics Mode
**Trigger:** "What would happen if?", forecasting, segmentation, patterns, statistical analysis

**Additional reads before starting:**
- Read `references/advanced-analytics.md` — statistical methods and Python patterns
- Read `references/dashboard-conventions.md` — chart selection, number presentation, table formatting

**Workflow:**
1. **Frame** — State the analytical question as a testable hypothesis.
2. **Assess** — Check data availability, quality gates, coverage limitations.
3. **Extract** — SQL query to pull data into a working dataset.
4. **Compute** — Python/Polars/pandas for statistical analysis, modelling, visualisation.
   Write analysis as a file (not throwaway inline code).
5. **Validate** — Challenge results: sensitivity checks, sanity tests, confidence bounds.
6. **Interpret** — Translate statistical findings into business implications.
7. **Present** — Deliver findings with methodology notes, confidence levels, caveats.

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
