# Verified Query Patterns

> Plugin v3.3.0. Join rules, exclusions, and business context are in context.md.
> Patterns demonstrate correct usage — they do not restate the rules.
> Substitute `{fiscal_year}` with `YEAR(ADD_MONTHS(CURRENT_DATE(), -6))` for current FY.

## Revenue by Business Unit (Employee Attribution)

```sql
SELECT
    TRIM(e.`Business Unit`) AS BU,
    SUM(i.`Total Value`) AS Revenue,
    SUM(i.`Margin`) AS Margin,
    COUNT(DISTINCT i.`Customer Key`) AS Customers
FROM datawarehouse.fact.invoices i
LEFT JOIN datawarehouse.dim.employee e
    ON i.`Employee Key` = CAST(e.`Employee Key` AS STRING)
LEFT JOIN datawarehouse.dim.calendar c
    ON i.`Invoice Date Key` = c.`Date Key`
WHERE c.`Fiscal Year` = YEAR(ADD_MONTHS(CURRENT_DATE(), -6))
  AND i.`Division` <> '999'
GROUP BY TRIM(e.`Business Unit`)
ORDER BY Revenue DESC
```

## Inventory by Business Unit (Product Attribution)

```sql
SELECT
    TRIM(p.`Product Business Unit`) AS ProductBU,
    SUM(ib.`On Hand`) AS OnHandQty,
    SUM(ib.`OnHand Value`) AS OnHandValue
FROM datawarehouse.fact.itembalance ib
LEFT JOIN datawarehouse.dim.product p
    ON ib.`Product Key` = CAST(p.`Product Key` AS STRING)
GROUP BY TRIM(p.`Product Business Unit`)
ORDER BY OnHandValue DESC
```

## AR Ageing (Computed — No Pre-Built Ageing Columns)

AR has no `Aging Bucket` or `Open Amount` columns. Compute ageing from `Due Date` (STRING YYYYMMDD).

```sql
SELECT
    c.`Customer Name`,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), TO_DATE(ar.`Due Date`, 'yyyyMMdd')) <= 0 THEN ar.`AUD Amount` END) AS Current_,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), TO_DATE(ar.`Due Date`, 'yyyyMMdd')) BETWEEN 1 AND 30 THEN ar.`AUD Amount` END) AS Days_1_30,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), TO_DATE(ar.`Due Date`, 'yyyyMMdd')) BETWEEN 31 AND 60 THEN ar.`AUD Amount` END) AS Days_31_60,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), TO_DATE(ar.`Due Date`, 'yyyyMMdd')) BETWEEN 61 AND 90 THEN ar.`AUD Amount` END) AS Days_61_90,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), TO_DATE(ar.`Due Date`, 'yyyyMMdd')) > 90 THEN ar.`AUD Amount` END) AS Days_90Plus,
    SUM(ar.`AUD Amount`) AS Total
FROM datawarehouse.fact.accountsreceivable ar
LEFT JOIN datawarehouse.dim.customer c
    ON ar.`Customer Key` = CAST(c.`Customer Key` AS STRING)
GROUP BY c.`Customer Name`
ORDER BY Total DESC
```

## Sales Orders Pipeline

```sql
SELECT
    TRIM(e.`Business Unit`) AS BU,
    so.`Order Status`,
    COUNT(*) AS Lines,
    SUM(so.`Pipeline Original Currency`) AS PipelineValue
FROM datawarehouse.fact.salesorders so
LEFT JOIN datawarehouse.dim.employee e
    ON so.`Employee Key` = CAST(e.`Employee Key` AS STRING)
WHERE so.`Order Status` NOT IN ('Invoiced', 'Cancelled')
GROUP BY TRIM(e.`Business Unit`), so.`Order Status`
ORDER BY BU, so.`Order Status`
```

## Sales Targets vs Actual

Sales targets are **monthly** — `fact.salestargets` uses `Fiscal Year Month Key` (INT, format YYYYMM),
NOT a daily Date Key. Aggregate invoices to monthly before joining.

Key columns on `fact.salestargets`: `Fiscal Year Month Key` (INT), `Employee Key` (STRING),
`Sales Order Targets`, `Invoice Targets`, `Invoice Margin Targets`, `Budget Targets`,
`Budget Margin Targets`, `MOPro Rep ID`.

```sql
WITH monthly_actuals AS (
    SELECT
        i.`Employee Key`,
        c.`Fiscal Year`,
        c.`Fiscal Month Number` AS FiscalMonth,
        CAST(CONCAT(c.`Fiscal Year`, LPAD(c.`Fiscal Month Number`, 2, '0')) AS INT) AS FiscalYearMonthKey,
        SUM(i.`Total Value`) AS ActualRevenue,
        SUM(i.`Margin`) AS ActualMargin
    FROM datawarehouse.fact.invoices i
    LEFT JOIN datawarehouse.dim.calendar c
        ON i.`Invoice Date Key` = c.`Date Key`
    WHERE i.`Division` <> '999'
      AND c.`Fiscal Year` = YEAR(ADD_MONTHS(CURRENT_DATE(), -6))
    GROUP BY i.`Employee Key`, c.`Fiscal Year`, c.`Fiscal Month Number`
)
SELECT
    TRIM(e.`Business Unit`) AS BU,
    a.`Fiscal Year`,
    a.FiscalMonth,
    SUM(t.`Invoice Targets`) AS InvoiceTarget,
    SUM(a.ActualRevenue) AS ActualRevenue,
    SUM(t.`Invoice Margin Targets`) AS MarginTarget,
    SUM(a.ActualMargin) AS ActualMargin
FROM monthly_actuals a
LEFT JOIN datawarehouse.fact.salestargets t
    ON a.`Employee Key` = t.`Employee Key`
    AND a.FiscalYearMonthKey = t.`Fiscal Year Month Key`
LEFT JOIN datawarehouse.dim.employee e
    ON a.`Employee Key` = CAST(e.`Employee Key` AS STRING)
GROUP BY TRIM(e.`Business Unit`), a.`Fiscal Year`, a.FiscalMonth
ORDER BY BU, a.FiscalMonth
```

## Fiscal Year Filtering

```sql
-- Current fiscal year (dynamic — FY = July to June)
WHERE c.`Fiscal Year` = YEAR(ADD_MONTHS(CURRENT_DATE(), -6))  -- INT, not 'FY25'

-- Current month via date key
WHERE i.`Invoice Date Key` >= CAST(DATE_FORMAT(TRUNC(CURRENT_DATE(), 'MM'), 'yyyyMMdd') AS INT)
  AND i.`Invoice Date Key` < CAST(DATE_FORMAT(ADD_MONTHS(TRUNC(CURRENT_DATE(), 'MM'), 1), 'yyyyMMdd') AS INT)

-- YTD (fiscal year to today)
WHERE c.`Fiscal Year` = YEAR(ADD_MONTHS(CURRENT_DATE(), -6))
  AND c.`Date Key` <= CAST(DATE_FORMAT(CURRENT_DATE(), 'yyyyMMdd') AS INT)

-- Display label
SELECT c.`Fiscal Year Label`            -- returns '2024-2025' format (not 'FY25')
```

## Inventory Hierarchy

Three granularity levels — choose the right one for the question:

| Level | Table | Purpose | Key |
|-------|-------|---------|-----|
| Bin-level | `fact.itembalance` | Physical stock position by location/lot | Product + Warehouse + Location |
| Warehouse-level | `fact.itemwarehouse` | Operational health (ageing, turnover, pareto) | Product + Warehouse |
| Facility-level | `fact.itemfacility` | Accounting view (unit cost, valuation method) | Product + Facility |
