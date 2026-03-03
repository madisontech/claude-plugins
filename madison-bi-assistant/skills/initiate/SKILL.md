---
description: Analyse MGE datawarehouse data — routes to the right mode for revenue, margin, inventory, AR, pipeline, investigation, and advanced analytics.
---

You are performing analysis for Madison Group Enterprises. This is the catch-all entry point.

## Boot Sequence (mandatory)

Read these files before doing anything. Do not proceed until all are loaded.

1. Read `../../CLAUDE.md` — disposition, communication style, quality gate
2. Read `../../context.md` — SQL rules, join casting, exclusions, business context
3. Read `../../references/query-patterns.md` — verified SQL templates

Then load additional references based on mode routing below.

If you encounter a table not covered in context.md, load `../../references/schema-inventory.md`.

## Mode Routing

Assess the question and select the mode. The analyst does not choose — you do.

### Query Mode
**Trigger:** "What is X?", "Show me Y by Z", breakdowns, comparisons, reporting
**No additional reads required.**

Workflow: Scope → Approach → Execute → Present → Drill-down

Output: chat table with key findings. For branded deliverables, suggest `/madison-bi-assistant:format`.

### Investigation Mode
**Trigger:** "Why is X different?", "Something looks wrong", discrepancy debugging
**Additional read:** `../../references/investigation.md`

Workflow: Observe → Hypothesise → Trace → Confirm → Report

Output: investigation narrative with root cause analysis.

### Analytics Mode
**Trigger:** "What would happen if?", forecasting, segmentation, patterns, statistical analysis
**Additional read:** `../../references/advanced-analytics.md`

Workflow: Frame → Assess → Extract → Compute → Validate → Interpret → Present

Output: Python analysis with files in `scratch/`.

### Format Mode
**Trigger:** "Make that into a spreadsheet", "Format as XLSX", explicit deliverable request
**Additional read:** `../../references/output-standards.md`

Workflow: Assess → Query (if needed) → Build → Verify → Deliver

Output: branded XLSX (default) / DOCX / PPTX in `deliverables/`.

## Mode Declaration (mandatory before analysis)

```
Mode:    [Query | Investigation | Analytics | Format]
Scope:   [Division, BU, Time Period, Key Filters]
Output:  [chat table | branded XLSX | narrative | Python analysis]
Loading: [additional reference files being loaded]
```

## Rules

- Source of truth: `datawarehouse.fact.*` and `datawarehouse.dim.*` only
- Check source system before every join — CAST rules are in context.md
- LEFT JOIN by default; -1 keys = unmatched records
- State BU attribution path (employee/product/customer) and why
- TRIM employee BU always
- Run premortem before delivering any result
- Write queries and results to files, not terminal. Present key findings in chat.
