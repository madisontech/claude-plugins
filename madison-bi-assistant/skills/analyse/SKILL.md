---
description: Advanced analytics — forecasting, segmentation, statistical patterns, hypothesis testing.
---

You are performing advanced analytics for Madison Group Enterprises.

**Boot:** Read `../../CLAUDE.md`, `../../context.md`, `../../references/query-patterns.md`,
`../../references/advanced-analytics.md`. For unfamiliar tables, use `DESCRIBE TABLE` to discover columns.

## Workflow

1. **Frame** (visible — one sentence) — State what you're testing or exploring, in plain English.
2. **Assess** (internal) — Check data availability, quality, coverage limitations.
3. **Extract** (internal) — SQL to pull the working dataset. Save to `scratch/queries/`.
4. **Compute** (internal) — Python analysis, modelling, visualisation. Scripts to `scratch/scripts/`.
5. **Validate** (internal) — Sensitivity checks, sanity tests, confidence bounds.
6. **Interpret** (visible) — Business implications. Lead with insight, support with evidence. State confidence and caveats in plain language.
7. **Present** (visible) — Charts, tables, narrative. Save to `scratch/analysis/`.

For branded deliverables, follow up with `/madison-bi-assistant:format`.
