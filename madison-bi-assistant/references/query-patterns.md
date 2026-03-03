# Verified Query Patterns

> All patterns verified against live endpoint 2026-03-03.
> Join rules, exclusions, and business context are in context.md. Patterns here demonstrate
> correct usage — they do not restate the rules.

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
WHERE c.`Fiscal Year` = 2025
  AND i.`Division` <> '999'
GROUP BY TRIM(e.`Business Unit`)
ORDER BY Revenue DESC
```

## Inventory by Business Unit (Product Attribution)

```sql
SELECT
    TRIM(p.`Business Unit`) AS ProductBU,
    SUM(ib.`On Hand Qty`) AS OnHandQty,
    SUM(ib.`OnHand Value`) AS OnHandValue
FROM datawarehouse.fact.itembalance ib
LEFT JOIN datawarehouse.dim.product p
    ON ib.`Product Key` = CAST(p.`Product Key` AS STRING)
GROUP BY TRIM(p.`Business Unit`)
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

```sql
SELECT
    TRIM(e.`Business Unit`) AS BU,
    c.`Fiscal Year`,
    c.`Fiscal Month`,
    SUM(t.`Target Value`) AS Target,
    SUM(i.`Total Value`) AS Actual
FROM datawarehouse.fact.salestargets t
LEFT JOIN datawarehouse.dim.employee e
    ON t.`Employee Key` = CAST(e.`Employee Key` AS STRING)
LEFT JOIN datawarehouse.dim.calendar c
    ON t.`Date Key` = c.`Date Key`
LEFT JOIN (
    SELECT `Employee Key`, `Invoice Date Key`,
           SUM(`Total Value`) AS `Total Value`
    FROM datawarehouse.fact.invoices
    WHERE `Division` <> '999'
    GROUP BY `Employee Key`, `Invoice Date Key`
) i ON t.`Employee Key` = i.`Employee Key`
   AND t.`Date Key` = i.`Invoice Date Key`
WHERE c.`Fiscal Year` = 2025
GROUP BY TRIM(e.`Business Unit`), c.`Fiscal Year`, c.`Fiscal Month`
ORDER BY BU, c.`Fiscal Month`
```

## Fiscal Year Filtering

```sql
-- FY25 = Jul 2024 to Jun 2025
WHERE c.`Fiscal Year` = 2025            -- INT, not 'FY25'

-- Current month via date key
WHERE i.`Invoice Date Key` >= 20250201
  AND i.`Invoice Date Key` < 20250301

-- YTD (fiscal year to today)
WHERE c.`Fiscal Year` = 2025
  AND c.`Date Key` <= CAST(DATE_FORMAT(CURRENT_DATE(), 'yyyyMMdd') AS INT)

-- Display label
SELECT c.`Fiscal Year Label`            -- returns '2024-2025' (not 'FY25')
```

## Inventory Hierarchy

Three granularity levels — choose the right one for the question:

| Level | Table | Purpose | Key |
|-------|-------|---------|-----|
| Bin-level | `fact.itembalance` | Physical stock position by location/lot | Product + Warehouse + Location |
| Warehouse-level | `fact.itemwarehouse` | Operational health (ageing, turnover, pareto) | Product + Warehouse |
| Facility-level | `fact.itemfacility` | Accounting view (unit cost, valuation method) | Product + Facility |
