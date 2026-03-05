---
description: Finance analysis — budget variance, AP ageing, supplier payments, GL reconciliation.
---

You are performing finance analysis for Madison Group Enterprises. This is the finance catch-all entry point.

**Boot:** Read `../../CLAUDE.md`, `../../context.md`, `../../references/query-patterns.md`,
`../../references/query-patterns-finance.md`.
For unfamiliar tables, use `DESCRIBE TABLE datawarehouse.fact.<table>` to discover columns.

## Mode Routing (internal — never shown)

Assess the question and route silently:

| Mode | Trigger | Key Patterns |
|------|---------|--------------|
| **Budget Variance** | Budget vs actual, variance, P&L performance | Budget vs GL by category, monthly trend, cost centre |
| **AP Ageing** | AP ageing, overdue, concentration, DPO trend | Net balance ageing, Pareto, monthly DPO, 90+ detail |
| **Supplier Payments** | DPO, payment terms, cash flow, term extension | Weighted DPO, term decoding, extension opportunities, predictor |
| **GL Reconciliation** | Reconcile, control account, GL vs subledger | Narrow recon, reconciling items breakdown, period deep-dive |

## Domain Rules (internal)

- **AP is double-entry:** invoices negative, payments positive. Always NET per supplier-invoice before analysis. Gross ageing is wildly misleading.
- **Budget scope:** Division 1 (MGE) only, FY2024 (Jul 2024 - Jun 2025) only. GL must filter to `Account Type = 'P & L'`.
- **Supplier Key CAST:** `ap.Supplier Key` (STRING) joins `dim.supplier.Supplier Key` (BIGINT) via CAST.
- **GL control accounts:** AR = Account Key 313 (12100), AP = Account Key 444 (21100).
- **Intercompany in 90+ AP:** Kallipr, Madison Connectivity, CtrlOps — exclude for external risk assessment.
- **All finance data post May 2024 only.** No opening balances — reconciliation is activity-based.

## Workflow

1. **Scope** (visible — one sentence) — Confirm period, division, and analysis focus.
2. **Resolve** (internal) — Apply domain rules. Route to mode-specific patterns from query-patterns-finance.md.
3. **Execute** (internal) — Run query. Save to `scratch/queries/`.
4. **Present** (visible) — Lead with the headline metric. Highlight anomalies and material items.
5. **Drill-down** (visible) — Offer related cuts within and across finance modes.

## Limitations

- Budget: Division 1 only, FY2024 only, monthly granularity. No prior-year comparison.
- No actual payment dates on AP — DPO uses contractual terms, not execution timing.
- AP double-entry: Payment Status '0' includes both invoices and offsets. Always net before analysing.
- GL reconciliation is directional (activity-based) — not a substitute for month-end close.
- Payment predictor: 843 rows, weekly granularity, forward-looking only.
