# Data Warehouse Analysis Patterns

> Supplementary reference for query patterns and available views.
> Core rules (source of truth, join casting, data quality) are in `plugins/bi-assistant/context.md`.

## Available Views

### Dimensions (datawarehouse.dim.*)

customer, product, warehouse, supplier, calendar, employee, salesrep,
division, businessunit, paymentterms, productcategory, itemsupplier,
location, itemwarehouse, customerpricelist, supplierpricelist

### Facts (datawarehouse.fact.*)

invoices, salesorders, purchaseorders, itembalance, stocktransactions,
aropentems, apopentems, paymentpredictor, goodsreceipts, customerpayments,
supplierpayments, quotes, creditnotes, receiptpredictor

## Standard Query Patterns

### Sales by Business Unit (Employee attribution)
```sql
SELECT
    TRIM(e.`Business Unit`) AS BU,
    SUM(i.`Total Value`) AS Revenue,
    SUM(i.`Margin`) AS Margin,
    COUNT(DISTINCT i.`Customer Key`) AS Customers
FROM datawarehouse.fact.invoices i
JOIN datawarehouse.dim.employee e
    ON i.`Employee Key` = CAST(e.`Employee Key` AS STRING)
JOIN datawarehouse.dim.calendar c
    ON i.`Invoice Date Key` = c.`Date Key`
WHERE c.`Fiscal Year` = 'FY25'
GROUP BY TRIM(e.`Business Unit`)
ORDER BY Revenue DESC
```

### Inventory by Business Unit (Product attribution)
```sql
SELECT
    TRIM(p.`Business Unit`) AS BU,
    SUM(ib.`On Hand Qty`) AS OnHandQty,
    SUM(ib.`On Hand Value`) AS OnHandValue
FROM datawarehouse.fact.itembalance ib
JOIN datawarehouse.dim.product p
    ON ib.`Product Key` = CAST(p.`Product Key` AS STRING)
GROUP BY TRIM(p.`Business Unit`)
```

### AR Aging
```sql
SELECT
    cu.`Customer Name`,
    SUM(CASE WHEN ar.`Aging Bucket` = 'Current' THEN ar.`Open Amount` END) AS Current_,
    SUM(CASE WHEN ar.`Aging Bucket` = '30 Days' THEN ar.`Open Amount` END) AS Days_30,
    SUM(CASE WHEN ar.`Aging Bucket` = '60 Days' THEN ar.`Open Amount` END) AS Days_60,
    SUM(CASE WHEN ar.`Aging Bucket` = '90+ Days' THEN ar.`Open Amount` END) AS Days_90Plus,
    SUM(ar.`Open Amount`) AS Total
FROM datawarehouse.fact.aropentems ar
JOIN datawarehouse.dim.customer cu
    ON ar.`Customer Key` = CAST(cu.`Customer Key` AS STRING)
GROUP BY cu.`Customer Name`
ORDER BY Total DESC
```

### Fiscal Year Filtering
```sql
-- FY25 = Jul 2024 to Jun 2025
WHERE c.`Fiscal Year` = 'FY25'

-- Current month via date key
WHERE i.`Invoice Date Key` >= 20250201 AND i.`Invoice Date Key` < 20250301

-- YTD (Jul to current month)
WHERE c.`Fiscal Year` = 'FY25'
  AND c.`Date Key` <= CAST(DATE_FORMAT(CURRENT_DATE(), 'yyyyMMdd') AS DECIMAL)
```

