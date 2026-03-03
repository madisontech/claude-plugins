---
description: Supplier payment optimisation — DPO analysis, AP ageing, term extension opportunities, cash flow projection.
---

You are performing supplier payment optimisation analysis for Madison Group Enterprises.

**Boot:** Read `../../CLAUDE.md`, `../../context.md`, `../../references/query-patterns.md`,
`../../references/query-patterns-finance.md`.

## Workflow

1. **Scope** (visible — one sentence) — Confirm division, time window, and analysis focus (DPO overview, overdue AP, term extension opportunities, or cash flow projection).
2. **Resolve** (internal) — AP is double-entry: invoices are negative `AUD Amount`, payments/credits are positive (blank `Payment Term`). Always compute NET balances per supplier-invoice combination. `Supplier Key` STRING joins `dim.supplier.Supplier Key` BIGINT via CAST. Payment terms decoded from code prefix: N=Net, M=Month-end, S=Statement, COD/C1=Immediate. No early payment discount terms exist in current data.
3. **Execute** (internal) — Run the appropriate pattern from query-patterns-finance.md. Save to `scratch/queries/`.
4. **Present** (visible) — Lead with the metric: overall weighted DPO (51.6 days baseline, May 2024 onward), net AP outstanding by ageing bucket, or cash flow pipeline by lifecycle stage. Top suppliers ranked by impact.
5. **Drill-down** (visible) — Offer related analysis: from DPO overview, suggest overdue suppliers or term extension candidates; from ageing, suggest payment predictor pipeline; from term extension, suggest cash flow impact modelling.

## Analysis Modes

| Mode | Trigger | Key Pattern |
|------|---------|-------------|
| **DPO Overview** | "What's our DPO?", payment terms | Weighted avg DPO by term type, supplier tier |
| **Overdue AP** | "What's overdue?", ageing | Net balance ageing by supplier-invoice (not gross) |
| **Term Extension** | "Where can we free up cash?", optimisation | Short-term suppliers (<=14 days) with material spend |
| **Cash Flow Projection** | "What's coming due?", pipeline | Payment predictor lifecycle buckets by week |

## Limitations

- AP data from May 2024 only. No prior-period trending available.
- No actual payment dates on AP — DPO uses invoice-to-due gap (contractual terms), not payment execution timing.
- Payment Status codes (0=Open, 1=Partial, 4=Closed) but most items stay Status 0 with offsetting entries.
- No early payment discount terms in current data — all 28 terms are Net/Month-end/Statement/Cash/COD.
- Payment predictor has 843 rows (small dataset), weekly granularity, forward-looking only.
- AP ageing must use net balances per supplier-invoice; gross ageing is wildly misleading due to double-entry structure.
