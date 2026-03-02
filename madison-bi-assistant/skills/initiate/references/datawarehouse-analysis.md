# Data Warehouse Analysis Patterns

> Verified query patterns for the Madison data warehouse. All column names, types, and joins
> confirmed against live endpoint 2026-03-03.
> Core rules in `context.md`. Full table reference in `schema-reference.md`.

## Standard Query Patterns

### Revenue by Business Unit (Employee Attribution)

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

Notes:
- `Fiscal Year` is INT (2025), not string "FY25"
- CAST required on employee join (M3 fact STRING -> dim LONG)
- LEFT JOIN preserves -1 orphan employees
- TRIM handles "MT " trailing space
- Division 999 excluded (dummy)

### Inventory by Business Unit (Product Attribution)

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

Notes:
- 47% of products have `<Unknown>` BU — flag this to the analyst
- `OnHand Value` has a space (verified column name)
- CAST required (M3 inventory fact)

### AR Ageing

```sql
SELECT
    c.`Customer Name`,
    SUM(CASE WHEN ar.`Aging Bucket` = 'Current' THEN ar.`Open Amount` END) AS Current_,
    SUM(CASE WHEN ar.`Aging Bucket` = '30 Days' THEN ar.`Open Amount` END) AS Days_30,
    SUM(CASE WHEN ar.`Aging Bucket` = '60 Days' THEN ar.`Open Amount` END) AS Days_60,
    SUM(CASE WHEN ar.`Aging Bucket` = '90+ Days' THEN ar.`Open Amount` END) AS Days_90Plus,
    SUM(ar.`Open Amount`) AS Total
FROM datawarehouse.fact.accountsreceivable ar
LEFT JOIN datawarehouse.dim.customer c
    ON ar.`Customer Key` = CAST(c.`Customer Key` AS STRING)
GROUP BY c.`Customer Name`
ORDER BY Total DESC
```

Notes:
- Table is `fact.accountsreceivable` (NOT `fact.aropenitems`)
- Data from May 2024 onwards only
- Positive amounts only (credit notes excluded by ETL)
- CAST required (M3 fact)

### Sales Orders Pipeline

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

### Sales Targets vs Actual

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

Notes:
- Table is `fact.salestargets` (NOT `fact.targets`)
- Targets at employee/date granularity

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
SELECT c.`Fiscal Year Label`            -- returns 'FY25'
```

## Inventory Hierarchy

Three granularity levels — choose the right one for the question:

| Level | Table | Purpose | Key |
|-------|-------|---------|-----|
| Bin-level | `fact.itembalance` | Physical stock position by location/lot | `Product Key` + `Warehouse Key` + `Location Key` |
| Warehouse-level | `fact.itemwarehouse` | Operational health (ageing, turnover, pareto, lead times) | `Product Key` + `Warehouse Key` |
| Facility-level | `fact.itemfacility` | Accounting view (unit cost, valuation method) | `Product Key` + `Facility Key` |

Use `itembalance` for "how much stock". Use `itemwarehouse` for "how healthy is inventory".
Use `itemfacility` for "what is it worth".

## GoldIntegrationQuery Extraction

For understanding ETL transformation logic (investigation mode only):

```sql
SELECT
    JSON_EXTRACT_SCALAR(GoldObjectSettings, '$.tableName') AS table_name,
    GoldIntegrationQuery,
    JSON_EXTRACT_SCALAR(GoldIntegrationBehaviorSettings, '$.integrationType') AS load_type
FROM int.maincontroltable
WHERE GoldObjectSettings LIKE '%invoices%'
  AND GoldIntegrationEnabled = true
```

**GoldIntegrationQuery is for learning/debugging only — never for primary analysis.**
