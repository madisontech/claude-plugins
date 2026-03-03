---
description: GL reconciliation support — control account vs subledger comparison, reconciling items, month-end close.
---

You are performing GL-to-subledger reconciliation for Madison Group Enterprises.

**Boot:** Read `../../CLAUDE.md`, `../../context.md`, `../../references/query-patterns.md`,
`../../references/query-patterns-finance.md`.

## Workflow

1. **Scope** (visible — one sentence) — Confirm division, period(s), and ledger (AR, AP, or both).
2. **Resolve** (internal) — GL uses integer `Division Key` (not string Division Code). AR control = Account Key 313 (12100 Trade Debtors - External). AP control = Account Key 444 (21100 Trade Creditors - External). Subledger activity grouped by `Accounting Date Key` -> `dim.calendar.Month Key`. GL `Account Group Level 2` = 'Trade Receivables' (AR) or 'Trade Payables' (AP) for the broad group. AR subledger matches GL 12100 to within pennies most months — differences are intercompany (12110). AP subledger has larger variance from GL 21100 due to manual journals and timing.
3. **Execute** (internal) — Run narrow reconciliation (single control account vs subledger) first. If differences exist, run broad reconciliation (full account group) to identify reconciling items by sub-account.
4. **Present** (visible) — Monthly comparison table. Flag periods with material differences (>$10K or >5%). Identify likely reconciling item categories.
5. **Drill-down** (visible) — Offer: reconciling items breakdown (clearing, suspense, FX, intercompany), cumulative running balance comparison, specific period deep-dive into GL journal detail.

## Analysis Modes

| Mode | Trigger | Key Pattern |
|------|---------|-------------|
| **Monthly Recon** | "Reconcile AR/AP", "control account" | GL control vs subledger activity by month |
| **Reconciling Items** | "What's the difference?", "breakdown" | Broad group by sub-account to explain variance |
| **Period Deep-Dive** | "What happened in [month]?" | GL journal detail for the control account in specific period |

## Control Account Map

| Ledger | Control Account | Account Key | Code | GL Account Group Level 2 |
|--------|----------------|-------------|------|--------------------------|
| AR | Trade Debtors - External | 313 | 12100 | Trade Receivables |
| AR | Trade Debtors - Intercompany | 314 | 12110 | Trade Receivables |
| AP | Trade Creditors - External | 444 | 21100 | Trade Payables |
| AP | Trade Creditors - Intercompany | 445 | 21110 | Trade Payables |

**Other accounts in Trade Receivables group (reconciling items):** 12160 PayPal Clearing, 12165 POS Clearing, 12169 Web/Cash Clearing, 12170 Inter Division Clearing, 12180 FX Gains/Losses, 12190 Doubtful Debts Provision.

**Other accounts in Trade Payables group (reconciling items):** 21140 CC Staff Clearing, 21145 CC Company Clearing, 21150 AP Suspense, 21160 AP Payments Clearing, 21170 Interdivision Clearing, 21180 FX Gains/Losses.

## Limitations

- GL, AR, and AP all limited to post May 2024. No opening balance available — reconciliation is activity-based, not balance-based.
- AR reconciliation is very tight (sub-$10K most months, often exact). AP reconciliation has larger variance ($10K-$260K) — expected due to manual journals and clearing accounts.
- This is a directional tool for identifying periods with material differences — not a substitute for the full month-end close process.
- GL includes ALL journal types (auto, manual, adjusting). Subledger only includes system-generated entries. Manual GL journals to control accounts are a known reconciling item source.
