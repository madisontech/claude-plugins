# Databricks ETL Troubleshooting Reference

> Use when debugging data discrepancies. Understand the transformation logic, then return
> to `datawarehouse.*` views for authoritative answers.
> **GoldIntegrationQuery is for learning/debugging only — never for primary analysis.**

## Medallion Architecture

```
datawarehouse.fact.* / datawarehouse.dim.* <-- QUERY FOR ANALYSIS (Power BI connected)
     ^ (views built on)
gold.fact.* / gold.dim.* <-- Gold tables (structure reference only)
     ^ (populated by)
int.maincontroltable <-- GoldIntegrationQuery (transformation logic)
     ^ (sourced from)
*_silver.* / *_bronze.* <-- Lineage verification only
```

## Control Table

**Table:** `int.maincontroltable`

| Column | Use |
|--------|-----|
| GoldObjectSettings | JSON: table name, schema, key columns, SCD type |
| GoldIntegrationQuery | Delta merge SQL showing transformation logic |
| GoldIntegrationBehaviorSettings | JSON: load type, watermark, dependencies |
| GoldIntegrationEnabled | Active/inactive flag |

### Extract Transformation Logic

```sql
SELECT
    JSON_EXTRACT_SCALAR(GoldObjectSettings, '$.tableName') AS table_name,
    JSON_EXTRACT_SCALAR(GoldObjectSettings, '$.schemaName') AS schema_name,
    GoldIntegrationQuery,
    JSON_EXTRACT_SCALAR(GoldIntegrationBehaviorSettings, '$.integrationType') AS load_type,
    JSON_EXTRACT_SCALAR(GoldIntegrationBehaviorSettings, '$.watermarkColumnName') AS watermark_col
FROM int.maincontroltable
WHERE GoldObjectSettings LIKE '%{table_name}%'
  AND GoldIntegrationEnabled = true
```

## ETL Patterns (Mined from 61 Gold Queries)

### Pattern 1: Silver -> Gold Dim Lookup (Dominant)
Every fact joins dims via natural keys to get surrogate keys, wrapped in `COALESCE(..., -1)`.
Unmatched = -1 sentinel. No dimension has a -1 row.

### Pattern 2: Silver-to-Silver M3 Compound Keys
M3 joins use composite keys: `CONO` + `ORNO` + `PONR` (multi-column).
Always filtered by `CONO = 100` and `deleted = FALSE`.

### Pattern 3: CSYTAB Dimension Enrichment
Codes resolved via `m3_silver.CSYTAB` constant values table:
- `ITTY` = item type
- `CFI3` = product business unit
- `SMCD` = employee sales district (first 3 chars = BU)

### Pattern 4: Salesforce Joins
String IDs (18-char). No CONO filter. No deleted flag.
Keys are natively LONG in gold — no CAST needed for SF-sourced facts.

### Pattern 5: Gold-to-Gold Dependencies (Breaks Medallion)
Some facts read other facts:
- `fact.receiptpredictor` reads `fact.salesorders` + `fact.accountsreceivable`
- `fact.paymentpredictor` reads `fact.purchaseorders` + `fact.accountspayable`
- `fact.cashflow` reads both predictors
- `fact.quotedmargin` reads `fact.invoices`
**Refresh order matters** — stale upstream = stale downstream.

### Pattern 6: MoPro WMS Joins
SKU prefix: `CONCAT('MI', mopro.SKU)` maps to M3 ProductNumber.

### Pattern 7: Rebate Joins (External)
`spsales.rebates` + brand groups + accruals. 4-tier logic:
R1 (exclusive brand) -> R2 (non-exclusive brand) -> R3 (wholesale group) -> R4 (member accrual)
Plus: FREDON +5%, MI Retail +4% (conditional surcharges).

## Gold Tables Inventory (61 queries)

**Dimensions (20):** Calendar, Month, Customer, Employee, Warehouse, Product, Supplier,
ItemWarehouse, Location, SalesRep, PriceList, PaymentTerms, Division, BusinessUnit,
ItemSupplier, CustomerPriceList, SupplierPriceList, ProductCategory, ProductSubCategory,
CustomerClassification

**Facts (39):** SalesOrders, Invoices, ItemBalance, PurchaseOrders, GoodsReceipts,
StockTransactions, CustomerPayments, SupplierPayments, Quotes, CreditNotes,
AccountsReceivable, AccountsPayable, PaymentPredictor, ReceiptPredictor, CashFlow,
Budget, SalesTargets, Forecasts, InventoryHistory, InventoryHistoryByMonth,
ItemWarehouse, ItemFacility, Allocations, PreAllocations, PickSlips, DeliveryNotes,
DistributionOrders, HistoricalDemand, QuotedMargin, Opportunities, OpportunityLineItem,
Case, CurrencyHistory, Shipments, RebateClaims, Supersessions, ProjectionDates,
InventoryProjection (disabled), CoDeliveries (broken/empty)

## Disabled/Broken Tables

- **`fact.inventoryprojection`** — Complex multi-CTE query with performance issues. Disabled.
- **`fact.codeliveries`** — Missing silver table prefix in ETL. 0 rows. Broken.
- **`fact.quote`** — Joins to `datawarehouse.dim.product` (breaks medallion convention).
