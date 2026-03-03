---
description: AP ageing analysis — ageing profile, overdue risk, supplier concentration, DPO trends.
---

You are performing accounts payable ageing analysis for Madison Group Enterprises.

**Boot:** Read `../../CLAUDE.md`, `../../context.md`, `../../references/query-patterns.md`,
`../../references/query-patterns-finance.md`.

## Workflow

1. **Scope** (visible — one sentence) — Confirm division, time window, and analysis focus (ageing profile, overdue risk, supplier concentration, or DPO trend).
2. **Resolve** (internal) — AP is double-entry: invoices are negative `AUD Amount`, payments/credits are positive (blank `Payment Term`). Always compute NET balances per supplier-invoice combination before ageing. Gross ageing is wildly misleading. `Supplier Key` STRING joins `dim.supplier.Supplier Key` BIGINT via CAST. Ageing computed from `Due Date` (STRING YYYYMMDD) via `DATEDIFF(CURRENT_DATE(), TO_DATE(due_date, 'yyyyMMdd'))`. Intercompany items (Kallipr, Madison Connectivity, CtrlOps) often sit 90+ — exclude from external supplier risk assessments.
3. **Execute** (internal) — Run the appropriate pattern from query-patterns-finance.md. Save to `scratch/queries/`.
4. **Present** (visible) — Lead with the metric: ageing bucket distribution, concentration Pareto, or DPO trend. Highlight anomalies.
5. **Drill-down** (visible) — Offer related cuts: from ageing profile, suggest overdue supplier detail or concentration; from concentration, suggest term extension (supplier-payment-optimisation skill); from DPO trend, flag months with anomalous single-supplier skew.

## Analysis Modes

| Mode | Trigger | Key Pattern |
|------|---------|-------------|
| **Ageing Profile** | "What's our AP ageing?", "overdue" | Net balance ageing by bucket with supplier counts |
| **Overdue Risk** | "Who's overdue?", "90+ days" | 90+ overdue supplier detail (excluding intercompany) |
| **Supplier Concentration** | "Concentration risk", "top suppliers" | Pareto analysis — cumulative % of net AP by supplier |
| **DPO Trend** | "DPO over time", "payment speed trend" | Monthly weighted DPO from invoice-to-due gap |

## Limitations

- AP data from May 2024 only. No prior-period trending before that.
- No actual payment dates on AP — DPO uses invoice-to-due gap (contractual terms), not payment execution timing.
- Monthly DPO trend susceptible to single-supplier skew when large invoices have anomalous invoice-to-accounting date gaps (e.g. Harman Sep 2025: 261 days on $2.8M).
- 90+ overdue includes intercompany balances (~$628K of $1.14M). Flag and exclude for external risk assessment.
- AP double-entry means Payment Status = '0' includes both invoices and their offset payments. Always net before analysing.
