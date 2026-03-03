---
description: Budget variance analysis — budget vs GL actuals with automated decomposition.
---

You are performing budget variance analysis for Madison Group Enterprises.

**Boot:** Read `../../CLAUDE.md`, `../../context.md`, `../../references/query-patterns.md`,
`../../references/query-patterns-finance.md`.

## Workflow

1. **Scope** (visible — one sentence) — Confirm period (FY / month range), division, and decomposition axis (account category, cost centre, or monthly trend).
2. **Resolve** (internal) — Budget: `Budget Period Key` (YYYYMM) joins `dim.calendar.Month Key`. GL: `Accounting Date Key` (YYYYMMDD) joins `dim.calendar.Date Key`, aggregate to month via `Month Key`. Filter GL to `Account Type = 'P & L'` to match budget scope. Shared dimension keys: Division Key, Cost Centre Key, Account Key.
3. **Execute** (internal) — Run variance query. Apply materiality threshold (default: >10% AND >$50K; user-adjustable). Save to `scratch/queries/`.
4. **Present** (visible) — Lead with the headline variance (total budget vs actual, net position). Then the top material variances ranked by absolute impact. State favourable/unfavourable using sign convention: revenue negative (credit), expenses positive (debit).
5. **Drill-down** (visible) — Offer next axis: if by category, suggest cost centre; if by cost centre, suggest account detail or monthly trend.

## Limitations

- Budget data: Division 1 (MGE) only, FY2024 (Jul 2024 - Jun 2025) only, monthly granularity.
- GL: post-May 2024 only. No historical comparison to prior-year budget periods.
- Account hierarchy via `Account Group Level 1` / `Level 2` (P&L Group columns are NULL).
- GL actuals net to near-zero across all accounts (balanced ledger) — always filter to P&L accounts for meaningful variance.
