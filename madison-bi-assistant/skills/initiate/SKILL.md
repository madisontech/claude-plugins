---
description: Analyse MGE datawarehouse data — routes to the right mode for revenue, margin, inventory, AR, pipeline, finance, investigation, and advanced analytics.
---

You are performing analysis for Madison Group Enterprises. This is the catch-all entry point.

**Boot:** Read `../../CLAUDE.md`, `../../context.md`, `../../references/query-patterns.md`.
For unfamiliar tables, use `DESCRIBE TABLE datawarehouse.fact.<table>` to discover columns.

## Mode Routing (internal — never shown)

Assess the question and route silently:

| Mode | Trigger | Additional Read |
|------|---------|-----------------|
| **Query** | Breakdowns, comparisons, reporting | None |
| **Investigation** | Discrepancies, debugging, "why is X different?" | `../../references/investigation.md` |
| **Analytics** | Forecasting, segmentation, stats, "what would happen if?" | `../../references/advanced-analytics.md` |
| **Format** | Explicit deliverable request | `../../references/output-standards.md` |
| **Finance** | Budget, AP ageing, DPO, supplier payments, GL recon | `../../references/query-patterns-finance.md` |

Then follow that mode's workflow. The user sees the conversation, not the routing.
