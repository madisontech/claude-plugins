# Finance Query Patterns

> Plugin v3.3.0. All patterns tested and returning reasonable results.
> Substitute `{fiscal_year}` with `YEAR(ADD_MONTHS(CURRENT_DATE(), -6))` for current FY.

## Budget vs GL Variance — By Account Category

Core pattern. Budget and GL share dimension keys (Division, Cost Centre, Account).
GL aggregated to monthly via calendar Month Key to match Budget Period Key.

```sql
WITH gl_monthly AS (
    SELECT
        c.`Month Key` AS period_key,
        gl.`Division Key`,
        gl.`Cost Centre Key`,
        gl.`Account Key`,
        SUM(gl.`Actual Amount`) AS actual_amount
    FROM datawarehouse.fact.generalledger gl
    JOIN datawarehouse.dim.calendar c
        ON gl.`Accounting Date Key` = c.`Date Key`
    JOIN datawarehouse.dim.account a
        ON gl.`Account Key` = a.`Account Key`
    WHERE c.`Month Key` BETWEEN {start_period} AND {end_period}  -- YYYYMM, e.g. 202407 AND 202506
      AND gl.`Division Key` = 1  -- MGE only (only division with budget data)
      AND a.`Account Type` = 'P & L'  -- Budget is P&L only; GL P&L nets to meaningful totals
    GROUP BY c.`Month Key`, gl.`Division Key`, gl.`Cost Centre Key`, gl.`Account Key`
)
SELECT
    a.`Account Group Level 1` AS category,
    SUM(b.`Budgeted Amount`) AS budget,
    SUM(g.actual_amount) AS actual,
    SUM(g.actual_amount) - SUM(b.`Budgeted Amount`) AS variance,
    CASE WHEN SUM(b.`Budgeted Amount`) <> 0
         THEN ROUND((SUM(g.actual_amount) - SUM(b.`Budgeted Amount`))
              / ABS(SUM(b.`Budgeted Amount`)) * 100, 1)
         ELSE NULL END AS variance_pct
FROM datawarehouse.fact.budget b
LEFT JOIN gl_monthly g
    ON b.`Budget Period Key` = g.period_key
    AND b.`Division Key` = g.`Division Key`
    AND b.`Cost Centre Key` = g.`Cost Centre Key`
    AND b.`Account Key` = g.`Account Key`
LEFT JOIN datawarehouse.dim.account a ON b.`Account Key` = a.`Account Key`
WHERE b.`Budget Period Key` BETWEEN {start_period} AND {end_period}
GROUP BY a.`Account Group Level 1`
ORDER BY ABS(SUM(g.actual_amount) - SUM(b.`Budgeted Amount`)) DESC
```

**Sign convention:** Revenue is negative (credit side). Expenses are positive (debit side).
A positive variance on revenue means revenue shortfall (less negative = less revenue).
A negative variance on expenses means underspend (favourable).

**Account Group Level 1 values:**
- Revenue
- Sales & Marketing Expenses
- Administrative & Personnel Expenses
- Interest, Tax, Depreciation & Amortisation

**Account Group Level 2 values (for drill-down):**
- Gross Sales, Discounts, Other Income (under Revenue)
- Cost of Goods Sold, Fulfilment Costs, Selling Expenses, Margin Adjustments (under S&M)
- Staff Costs (under Admin)

---

## Budget vs GL Variance — Monthly Trend

Same CTE, grouped by period instead of account category.

```sql
-- (gl_monthly CTE as above)
SELECT
    b.`Budget Period Key` AS period,
    cal.`Calendar Month Short Name` AS month_name,
    SUM(b.`Budgeted Amount`) AS budget,
    SUM(g.actual_amount) AS actual,
    SUM(g.actual_amount) - SUM(b.`Budgeted Amount`) AS variance,
    CASE WHEN SUM(b.`Budgeted Amount`) <> 0
         THEN ROUND((SUM(g.actual_amount) - SUM(b.`Budgeted Amount`))
              / ABS(SUM(b.`Budgeted Amount`)) * 100, 1)
         ELSE NULL END AS variance_pct
FROM datawarehouse.fact.budget b
LEFT JOIN gl_monthly g
    ON b.`Budget Period Key` = g.period_key
    AND b.`Division Key` = g.`Division Key`
    AND b.`Cost Centre Key` = g.`Cost Centre Key`
    AND b.`Account Key` = g.`Account Key`
LEFT JOIN (
    SELECT DISTINCT `Month Key`, `Calendar Month Short Name`
    FROM datawarehouse.dim.calendar
) cal ON b.`Budget Period Key` = cal.`Month Key`
WHERE b.`Budget Period Key` BETWEEN {start_period} AND {end_period}
GROUP BY b.`Budget Period Key`, cal.`Calendar Month Short Name`
ORDER BY b.`Budget Period Key`
```

---

## Budget vs GL Variance — By Cost Centre

Same CTE, grouped by cost centre. Shows which departments drive the variance.

```sql
-- (gl_monthly CTE as above)
SELECT
    cc.`Cost Centre Name`,
    SUM(b.`Budgeted Amount`) AS budget,
    SUM(g.actual_amount) AS actual,
    SUM(g.actual_amount) - SUM(b.`Budgeted Amount`) AS variance,
    CASE WHEN SUM(b.`Budgeted Amount`) <> 0
         THEN ROUND((SUM(g.actual_amount) - SUM(b.`Budgeted Amount`))
              / ABS(SUM(b.`Budgeted Amount`)) * 100, 1)
         ELSE NULL END AS variance_pct
FROM datawarehouse.fact.budget b
LEFT JOIN gl_monthly g
    ON b.`Budget Period Key` = g.period_key
    AND b.`Division Key` = g.`Division Key`
    AND b.`Cost Centre Key` = g.`Cost Centre Key`
    AND b.`Account Key` = g.`Account Key`
LEFT JOIN datawarehouse.dim.costcentre cc ON b.`Cost Centre Key` = cc.`Cost Centre Key`
WHERE b.`Budget Period Key` BETWEEN {start_period} AND {end_period}
GROUP BY cc.`Cost Centre Name`
ORDER BY ABS(SUM(g.actual_amount) - SUM(b.`Budgeted Amount`)) DESC
```

---

## Materiality Filter

Apply to any variance decomposition to surface only material items.
Default thresholds: >10% AND >$50K absolute variance.

```sql
-- Add as HAVING clause to any of the above patterns:
HAVING ABS(SUM(g.actual_amount) - SUM(b.`Budgeted Amount`)) > 50000
   AND ABS(CASE WHEN SUM(b.`Budgeted Amount`) <> 0
                THEN (SUM(g.actual_amount) - SUM(b.`Budgeted Amount`))
                     / ABS(SUM(b.`Budgeted Amount`)) * 100
                ELSE NULL END) > 10
```

---

## Key Facts

- **Budget scope:** Division 1 (MGE) only. Current budget FY (202407-202506 = FY2025). ~75 P&L accounts, 26 cost centres.
- **GL scope:** Post-May 2024. 1.97M rows. All divisions. Filter to `Account Type = 'P & L'` for variance.
- **Period join:** `fact.budget.Budget Period Key` (INT YYYYMM) = `dim.calendar.Month Key` (INT YYYYMM).
- **Dimension joins:** Budget and GL share `Division Key`, `Cost Centre Key`, `Account Key` (all INT -> BIGINT dims, implicit coercion).
- **Account hierarchy:** `dim.account.Account Group Level 1` and `Level 2` are populated. P&L Group columns (1-4) are all NULL.
- **GL nets to zero:** Full GL balanced by design. Always filter to P&L accounts for meaningful variance totals.

---

## AR Ageing (Computed)

AR fact has no pre-computed ageing columns. Compute from `Due Date` (STRING, YYYYMMDD).

```sql
SELECT
    c.`Customer Name`,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), TO_DATE(ar.`Due Date`, 'yyyyMMdd')) <= 0
             THEN ar.`AUD Amount` END) AS current_,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), TO_DATE(ar.`Due Date`, 'yyyyMMdd')) BETWEEN 1 AND 30
             THEN ar.`AUD Amount` END) AS days_30,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), TO_DATE(ar.`Due Date`, 'yyyyMMdd')) BETWEEN 31 AND 60
             THEN ar.`AUD Amount` END) AS days_31_60,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), TO_DATE(ar.`Due Date`, 'yyyyMMdd')) BETWEEN 61 AND 90
             THEN ar.`AUD Amount` END) AS days_61_90,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), TO_DATE(ar.`Due Date`, 'yyyyMMdd')) > 90
             THEN ar.`AUD Amount` END) AS days_90_plus,
    SUM(ar.`AUD Amount`) AS total
FROM datawarehouse.fact.accountsreceivable ar
LEFT JOIN datawarehouse.dim.customer c
    ON ar.`Customer Key` = CAST(c.`Customer Key` AS STRING)
WHERE ar.`Division Key` = 1
GROUP BY c.`Customer Name`
ORDER BY total DESC
```

## AP Ageing — Net Balance (Accurate)

**AP is double-entry:** invoices are negative `AUD Amount`, payments/credits are positive (blank
`Payment Term`). Gross ageing is wildly misleading (gross is 10-20x net outstanding).
Always compute net balance per supplier-invoice first, then age the residual.

```sql
WITH invoice_net AS (
    SELECT
        ap.`Supplier Key`,
        ap.`Supplier Invoice Number`,
        MIN(ap.`Due Date`) AS due_date,
        MIN(NULLIF(ap.`Payment Term`, '')) AS payment_term,
        SUM(ap.`AUD Amount`) AS net_balance
    FROM datawarehouse.fact.accountspayable ap
    WHERE ap.`Division Key` = 1
      AND ap.`Payment Status` = '0'  -- Open entries
    GROUP BY ap.`Supplier Key`, ap.`Supplier Invoice Number`
    HAVING SUM(ap.`AUD Amount`) < -1  -- Net outstanding only
)
SELECT
    s.`Supplier Name`,
    CASE
        WHEN DATEDIFF(CURRENT_DATE(), TO_DATE(n.due_date, 'yyyyMMdd')) <= 0 THEN 'Not Yet Due'
        WHEN DATEDIFF(CURRENT_DATE(), TO_DATE(n.due_date, 'yyyyMMdd')) BETWEEN 1 AND 30 THEN '1-30 Days'
        WHEN DATEDIFF(CURRENT_DATE(), TO_DATE(n.due_date, 'yyyyMMdd')) BETWEEN 31 AND 60 THEN '31-60 Days'
        WHEN DATEDIFF(CURRENT_DATE(), TO_DATE(n.due_date, 'yyyyMMdd')) BETWEEN 61 AND 90 THEN '61-90 Days'
        ELSE '90+ Days'
    END AS ageing_bucket,
    COUNT(*) AS invoice_count,
    ROUND(SUM(n.net_balance), 2) AS net_outstanding
FROM invoice_net n
LEFT JOIN datawarehouse.dim.supplier s
    ON n.`Supplier Key` = CAST(s.`Supplier Key` AS STRING)
GROUP BY s.`Supplier Name`,
    CASE
        WHEN DATEDIFF(CURRENT_DATE(), TO_DATE(n.due_date, 'yyyyMMdd')) <= 0 THEN 'Not Yet Due'
        WHEN DATEDIFF(CURRENT_DATE(), TO_DATE(n.due_date, 'yyyyMMdd')) BETWEEN 1 AND 30 THEN '1-30 Days'
        WHEN DATEDIFF(CURRENT_DATE(), TO_DATE(n.due_date, 'yyyyMMdd')) BETWEEN 31 AND 60 THEN '31-60 Days'
        WHEN DATEDIFF(CURRENT_DATE(), TO_DATE(n.due_date, 'yyyyMMdd')) BETWEEN 61 AND 90 THEN '61-90 Days'
        ELSE '90+ Days'
    END
ORDER BY net_outstanding ASC
```

**Orientation:** Majority (~80%+) of net AP is typically not yet due. Run the query for current figures.

---

## Weighted Average DPO

DPO = weighted by invoice value, using invoice-to-due gap. Excludes date outliers.

```sql
SELECT
    CASE
        WHEN ap.`Payment Term` LIKE 'N%' THEN 'Net'
        WHEN ap.`Payment Term` LIKE 'M%' THEN 'Month-end'
        WHEN ap.`Payment Term` LIKE 'S%' THEN 'Statement'
        WHEN ap.`Payment Term` IN ('COD', 'C1') THEN 'Immediate'
        ELSE 'Unknown'
    END AS term_type,
    COUNT(DISTINCT ap.`Supplier Key`) AS suppliers,
    COUNT(*) AS invoice_lines,
    ROUND(SUM(ap.`AUD Amount`), 2) AS total_aud,
    ROUND(
        SUM(DATEDIFF(TO_DATE(ap.`Due Date`, 'yyyyMMdd'), TO_DATE(ap.`Invoice Date`, 'yyyyMMdd')) * ABS(ap.`AUD Amount`))
        / SUM(ABS(ap.`AUD Amount`))
    , 1) AS weighted_avg_dpo
FROM datawarehouse.fact.accountspayable ap
WHERE ap.`Division Key` = 1
  AND ap.`AUD Amount` < 0  -- Invoices only
  AND ap.`Payment Term` <> ''
  AND ap.`Payment Term` IS NOT NULL
  AND DATEDIFF(TO_DATE(ap.`Due Date`, 'yyyyMMdd'), TO_DATE(ap.`Invoice Date`, 'yyyyMMdd')) BETWEEN -30 AND 365
GROUP BY
    CASE
        WHEN ap.`Payment Term` LIKE 'N%' THEN 'Net'
        WHEN ap.`Payment Term` LIKE 'M%' THEN 'Month-end'
        WHEN ap.`Payment Term` LIKE 'S%' THEN 'Statement'
        WHEN ap.`Payment Term` IN ('COD', 'C1') THEN 'Immediate'
        ELSE 'Unknown'
    END
ORDER BY total_aud ASC
```

**Orientation:** DPO typically 38-55 days weighted. Net terms dominate (~80% of spend). Statement terms add ~14 days beyond nominal. Run the query for current figures.

---

## Payment Term Decoding

Extract nominal days from term codes. No discount terms exist — all codes are Net/Month-end/Statement/Cash/COD.

```sql
-- Decode payment term to type and nominal days
CASE
    WHEN `Payment Term` LIKE 'N%' THEN 'Net'
    WHEN `Payment Term` LIKE 'M%' THEN 'Month-end'
    WHEN `Payment Term` LIKE 'S%' THEN 'Statement'
    WHEN `Payment Term` = 'COD' THEN 'Cash on Delivery'
    WHEN `Payment Term` = 'C1' THEN 'Cash'
    ELSE 'Unknown'
END AS term_type,
CASE
    WHEN `Payment Term` IN ('COD', 'C1') THEN 0
    WHEN `Payment Term` RLIKE '^[NMS][0-9]+$' THEN CAST(REGEXP_EXTRACT(`Payment Term`, '[0-9]+', 0) AS INT)
    ELSE NULL
END AS nominal_days
```

**28 non-blank term codes across 4 types:**
- **Net (N):** N00, N07, N7, N10, N14, N15, N20, N21, N25, N30, N60, N75, N90
- **Statement (S):** S7, S14, S15, S28, S30, S45, S60, S90
- **Month-end (M):** M00, M07, M14, M30, M45
- **Immediate:** COD, C1

Statement terms add ~14 days beyond nominal (e.g. S30 averages 44 days actual).
Month-end terms add ~10 days beyond nominal.

---

## Term Extension Opportunities

Suppliers on short terms (<=14 days nominal) with material annual spend.
Cash flow benefit = spend * (target_days - current_days) / 365.

```sql
SELECT
    s.`Supplier Name`,
    s.`Supplier Country`,
    ap.`Payment Term`,
    CASE
        WHEN ap.`Payment Term` IN ('COD', 'C1', 'N00', 'M00') THEN 0
        WHEN ap.`Payment Term` RLIKE '^[NMS][0-9]+$' THEN CAST(REGEXP_EXTRACT(ap.`Payment Term`, '[0-9]+', 0) AS INT)
        ELSE NULL
    END AS nominal_days,
    COUNT(*) AS invoice_count,
    ROUND(SUM(ABS(ap.`AUD Amount`)), 2) AS annual_spend,
    ROUND(
        SUM(ABS(ap.`AUD Amount`)) *
        (30 - COALESCE(
            CASE
                WHEN ap.`Payment Term` IN ('COD', 'C1', 'N00', 'M00') THEN 0
                WHEN ap.`Payment Term` RLIKE '^[NMS][0-9]+$' THEN CAST(REGEXP_EXTRACT(ap.`Payment Term`, '[0-9]+', 0) AS INT)
            END, 0)
        ) / 365
    , 2) AS cash_flow_benefit_to_n30
FROM datawarehouse.fact.accountspayable ap
LEFT JOIN datawarehouse.dim.supplier s
    ON ap.`Supplier Key` = CAST(s.`Supplier Key` AS STRING)
WHERE ap.`Division Key` = 1
  AND ap.`AUD Amount` < 0
  AND ap.`Payment Term` IS NOT NULL
  AND ap.`Payment Term` <> ''
  AND (ap.`Payment Term` IN ('COD', 'C1', 'N00', 'M00', 'N7', 'N07', 'N10', 'N14', 'M07', 'M14', 'S7', 'S14', 'S15'))
GROUP BY s.`Supplier Name`, s.`Supplier Country`, ap.`Payment Term`,
    CASE WHEN ap.`Payment Term` IN ('COD', 'C1', 'N00', 'M00') THEN 0
         WHEN ap.`Payment Term` RLIKE '^[NMS][0-9]+$' THEN CAST(REGEXP_EXTRACT(ap.`Payment Term`, '[0-9]+', 0) AS INT)
         ELSE NULL END
HAVING SUM(ABS(ap.`AUD Amount`)) > 50000
ORDER BY cash_flow_benefit_to_n30 DESC
```

**Usage:** Run with current data to identify top candidates. Focus on suppliers with >$50K annual spend on short terms (<=14 days).

---

## Payment Predictor — Cash Flow Pipeline

Forward-looking cash flow by lifecycle stage and week. 5 buckets from PO to AP unpaid.

```sql
SELECT
    pp.`week start`,
    pp.`Bucket Label`,
    pp.`Sort Order`,
    COUNT(*) AS line_count,
    COUNT(DISTINCT pp.`Supplier Key`) AS suppliers,
    ROUND(SUM(pp.`Amount FC`), 2) AS total_fc
FROM datawarehouse.fact.paymentpredictor pp
WHERE pp.`week start` >= CURRENT_DATE() - INTERVAL 7 DAYS
GROUP BY pp.`week start`, pp.`Bucket Label`, pp.`Sort Order`
ORDER BY pp.`week start`, pp.`Sort Order`
```

**Pipeline buckets (by Sort Order):**
| Sort | Code | Label | Description |
|------|------|-------|-------------|
| 10 | OPEN_SENT | Open PO Sent | Purchase orders dispatched to supplier |
| 20 | OPEN_CONFIRMED | Open PO's Confirmed | Supplier-confirmed orders |
| 30 | SHIP_ADVISED | Shipment Advised | In transit |
| 40 | GRNI | GRNI | Goods received, not yet invoiced |
| 99 | AP_UNPAID | AP Unpaid | Invoiced but unpaid — immediate cash pressure |

Run the query for current pipeline totals. AP_UNPAID is typically the largest bucket.

---

## AP Key Facts

- **Double-entry structure:** Invoices = negative `AUD Amount` with `Payment Term` populated. Payments = positive amounts with blank `Payment Term`. Both stay at `Payment Status` = '0'.
- **Payment Status:** 0 = Open (includes both invoices and their offset payments), 1 = Partial (72 rows), 4 = Closed (1,035 rows).
- **No early payment discounts:** All 28 payment terms are pure Net/Month-end/Statement/Cash/COD.
- **Supplier Key CAST:** `ap.Supplier Key` (STRING) joins `dim.supplier.Supplier Key` (BIGINT) via `CAST(s.Supplier Key AS STRING)`.
- **Date columns are STRING:** `Invoice Date`, `Due Date`, `Entry Date` — all STRING YYYYMMDD. Use `TO_DATE(col, 'yyyyMMdd')` for date arithmetic.
- **Data from May 2024 only.** Large transactional table for Division 1 (roughly even split of invoices and payment offsets, plus some partial/closed).

---

## Supplier Concentration (Pareto Analysis)

Net AP exposure ranked by supplier with cumulative percentage. Identifies concentration risk.

```sql
WITH invoice_net AS (
    SELECT
        ap.`Supplier Key`,
        ap.`Supplier Invoice Number`,
        SUM(ap.`AUD Amount`) AS net_balance
    FROM datawarehouse.fact.accountspayable ap
    WHERE ap.`Division Key` = 1
      AND ap.`Payment Status` = '0'
    GROUP BY ap.`Supplier Key`, ap.`Supplier Invoice Number`
    HAVING SUM(ap.`AUD Amount`) < -1
),
supplier_totals AS (
    SELECT
        n.`Supplier Key`,
        s.`Supplier Name`,
        COUNT(*) AS open_invoices,
        ROUND(SUM(ABS(n.net_balance)), 2) AS abs_outstanding
    FROM invoice_net n
    LEFT JOIN datawarehouse.dim.supplier s
        ON n.`Supplier Key` = CAST(s.`Supplier Key` AS STRING)
    GROUP BY n.`Supplier Key`, s.`Supplier Name`
)
SELECT
    `Supplier Name`,
    open_invoices,
    abs_outstanding,
    ROUND(abs_outstanding / SUM(abs_outstanding) OVER () * 100, 2) AS pct_of_total,
    ROUND(SUM(abs_outstanding) OVER (ORDER BY abs_outstanding DESC ROWS UNBOUNDED PRECEDING)
          / SUM(abs_outstanding) OVER () * 100, 2) AS cumulative_pct,
    ROW_NUMBER() OVER (ORDER BY abs_outstanding DESC) AS rank_
FROM supplier_totals
ORDER BY abs_outstanding DESC
```

**Orientation:** Supplier concentration is high — top 5 suppliers typically account for ~60% of net outstanding, top 10 ~80%. Run the query for current figures.

---

## Monthly DPO Trend

Weighted DPO by accounting month — tracks whether payment terms are lengthening or shortening.

```sql
SELECT
    c.`Month Key` AS period,
    c.`Calendar Month Short Name` AS month_name,
    COUNT(*) AS invoice_lines,
    COUNT(DISTINCT ap.`Supplier Key`) AS suppliers,
    ROUND(SUM(ABS(ap.`AUD Amount`)), 2) AS monthly_spend,
    ROUND(
        SUM(DATEDIFF(TO_DATE(ap.`Due Date`, 'yyyyMMdd'), TO_DATE(ap.`Invoice Date`, 'yyyyMMdd')) * ABS(ap.`AUD Amount`))
        / NULLIF(SUM(ABS(ap.`AUD Amount`)), 0)
    , 1) AS weighted_dpo
FROM datawarehouse.fact.accountspayable ap
JOIN datawarehouse.dim.calendar c
    ON ap.`Accounting Date Key` = c.`Date Key`
WHERE ap.`Division Key` = 1
  AND ap.`AUD Amount` < 0  -- Invoices only
  AND ap.`Payment Term` IS NOT NULL
  AND ap.`Payment Term` <> ''
  AND DATEDIFF(TO_DATE(ap.`Due Date`, 'yyyyMMdd'), TO_DATE(ap.`Invoice Date`, 'yyyyMMdd')) BETWEEN -30 AND 365
GROUP BY c.`Month Key`, c.`Calendar Month Short Name`
ORDER BY c.`Month Key`
```

**Caveat:** Monthly DPO susceptible to single-supplier skew — one large late-booked invoice can spike a month. Always exclude the current partial month. Typical range: 38-55 days.

---

## 90+ Overdue Supplier Detail

Net outstanding for suppliers with invoices 90+ days past due. Includes days-overdue range.

```sql
WITH invoice_net AS (
    SELECT
        ap.`Supplier Key`,
        ap.`Supplier Invoice Number`,
        MIN(ap.`Due Date`) AS due_date,
        SUM(ap.`AUD Amount`) AS net_balance
    FROM datawarehouse.fact.accountspayable ap
    WHERE ap.`Division Key` = 1
      AND ap.`Payment Status` = '0'
    GROUP BY ap.`Supplier Key`, ap.`Supplier Invoice Number`
    HAVING SUM(ap.`AUD Amount`) < -1
)
SELECT
    s.`Supplier Name`,
    COUNT(*) AS overdue_invoices,
    ROUND(SUM(ABS(n.net_balance)), 2) AS overdue_amount,
    MIN(DATEDIFF(CURRENT_DATE(), TO_DATE(n.due_date, 'yyyyMMdd'))) AS min_days_overdue,
    MAX(DATEDIFF(CURRENT_DATE(), TO_DATE(n.due_date, 'yyyyMMdd'))) AS max_days_overdue
FROM invoice_net n
LEFT JOIN datawarehouse.dim.supplier s
    ON n.`Supplier Key` = CAST(s.`Supplier Key` AS STRING)
WHERE DATEDIFF(CURRENT_DATE(), TO_DATE(n.due_date, 'yyyyMMdd')) > 90
GROUP BY s.`Supplier Name`
ORDER BY overdue_amount DESC
```

**Orientation:** Intercompany suppliers (Kallipr, Madison Connectivity, CtrlOps) typically dominate 90+ overdue by dollar value. Exclude intercompany for external risk assessment. Run the query for current figures.

---

## GL vs Subledger — Narrow Reconciliation

Compares single GL control account activity to subledger activity by month. Use Account Key 313
(12100 Trade Debtors - External) for AR, Account Key 444 (21100 Trade Creditors - External) for AP.

```sql
-- AR: GL 12100 vs AR subledger
WITH gl_control AS (
    SELECT
        c.`Month Key` AS period,
        ROUND(SUM(gl.`Actual Amount`), 2) AS gl_amount
    FROM datawarehouse.fact.generalledger gl
    JOIN datawarehouse.dim.calendar c ON gl.`Accounting Date Key` = c.`Date Key`
    WHERE gl.`Account Key` = 313  -- 12100 Trade Debtors - External
      AND gl.`Division Key` = 1
    GROUP BY c.`Month Key`
),
subledger AS (
    SELECT
        c.`Month Key` AS period,
        ROUND(SUM(ar.`AUD Amount`), 2) AS sub_amount
    FROM datawarehouse.fact.accountsreceivable ar
    JOIN datawarehouse.dim.calendar c ON ar.`Accounting Date Key` = c.`Date Key`
    WHERE ar.`Division Key` = 1
    GROUP BY c.`Month Key`
)
SELECT
    COALESCE(g.period, s.period) AS period,
    g.gl_amount,
    s.sub_amount,
    ROUND(COALESCE(g.gl_amount, 0) - COALESCE(s.sub_amount, 0), 2) AS difference,
    ROUND(ABS(COALESCE(g.gl_amount, 0) - COALESCE(s.sub_amount, 0))
          / NULLIF(ABS(s.sub_amount), 0) * 100, 2) AS diff_pct
FROM gl_control g
FULL OUTER JOIN subledger s ON g.period = s.period
WHERE COALESCE(g.period, s.period) >= 202405  -- Subledger start
ORDER BY period
```

**For AP:** Replace `Account Key = 313` with `444`, `fact.accountsreceivable` with `fact.accountspayable`, and `ar.AUD Amount` with `ap.AUD Amount`.

**Orientation:**
- AR: Near-exact match most months (typically <$15K, <1%). Differences = intercompany entries (12110).
- AP: Larger variance (typically <$100K). Sources: manual journals, timing, intercompany.

---

## GL vs Subledger — Reconciling Items Breakdown

When a difference exists, break down the full GL account group to identify which sub-accounts
explain the variance. Uses `Account Group Level 2` to capture all related accounts.

```sql
-- Reconciling items for AR (Trade Receivables group)
SELECT
    c.`Month Key` AS period,
    a.`Account Code`,
    a.`Account Name`,
    ROUND(SUM(gl.`Actual Amount`), 2) AS gl_amount
FROM datawarehouse.fact.generalledger gl
JOIN datawarehouse.dim.calendar c ON gl.`Accounting Date Key` = c.`Date Key`
JOIN datawarehouse.dim.account a ON gl.`Account Key` = a.`Account Key`
WHERE a.`Account Group Level 2` = 'Trade Receivables'  -- or 'Trade Payables' for AP
  AND gl.`Division Key` = 1
  AND a.`Account Code` <> 12100  -- Exclude the control account (already reconciled)
  AND c.`Month Key` = {target_period}  -- YYYYMM
GROUP BY c.`Month Key`, a.`Account Code`, a.`Account Name`
HAVING ABS(SUM(gl.`Actual Amount`)) > 0.01
ORDER BY ABS(SUM(gl.`Actual Amount`)) DESC
```

**Common reconciling item accounts:**

| Group | Code | Name | Typical Monthly Impact |
|-------|------|------|----------------------|
| AR | 12165 | AR POS Clearing | $20K-$230K (high variance) |
| AR | 12169 | Web/Cash Sale Clearing | $3K-$300K |
| AR | 12170 | Inter Division Clearing | $1K-$153K |
| AR | 12110 | Trade Debtors - Intercompany | $0.3K-$15K |
| AR | 12180 | AR Unrealised FX | $1K-$9K |
| AP | 21150 | AP Suspense Account | $2K-$120K |
| AP | 21140 | CC Staff Clearing | $2K-$410K (Feb 2026 outlier) |
| AP | 21180 | AP Unrealised FX | $5K-$97K |
| AP | 21145 | CC Company Clearing | $0-$11K |

---

## GL Control Account Reference

| Ledger | Account Key | Code | Name | Subledger Match Quality |
|--------|-------------|------|------|------------------------|
| AR | 313 | 12100 | Trade Debtors - External | Excellent (<$15K, often exact) |
| AR | 314 | 12110 | Trade Debtors - Intercompany | No subledger equivalent |
| AP | 444 | 21100 | Trade Creditors - External | Good ($0-$260K, typically <$80K) |
| AP | 445 | 21110 | Trade Creditors - Intercompany | No subledger equivalent |
