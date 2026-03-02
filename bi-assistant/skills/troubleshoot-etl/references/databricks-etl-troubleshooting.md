# Databricks ETL Troubleshooting Reference

> Loaded from Claude.ai Skill `databricks-etl-analysis`. Use when debugging data discrepancies.

## Purpose

When a `datawarehouse.*` value seems wrong, use this to understand the transformation logic.
**GoldIntegrationQuery is for learning/debugging only — never for primary analysis.**

## Medallion Architecture

```
datawarehouse.fact.* / datawarehouse.dim.* ← QUERY FOR ANALYSIS (Power BI connected)
     ↑ (views built on)
fact.* / dim.* ← Gold tables (structure reference only)
     ↑ (populated by)
int.maincontroltable ← GoldIntegrationQuery (transformation logic)
     ↑ (sourced from)
*_silver.* / *_bronze.* ← Lineage verification only
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
    GoldIntegrationQuery,
    JSON_EXTRACT_SCALAR(GoldIntegrationBehaviorSettings, '$.integrationType') AS load_type
FROM int.maincontroltable
WHERE GoldObjectSettings LIKE '%invoices%'
  AND GoldIntegrationEnabled = true
```

## Troubleshooting Workflow

1. Query `datawarehouse.fact.*` to verify the actual value
2. Extract `GoldIntegrationQuery` for the relevant gold table
3. Review join logic, cost allocation, formula calculations
4. Identify which transformation step produces the discrepancy
5. **Return to datawarehouse views** for authoritative reporting

## Gold Tables Inventory (61 tables)

**Dimensions:** Calendar, Month, Customer, Employee, Warehouse, Product, Supplier,
ItemWarehouse, Location, SalesRep, PriceList, PaymentTerms, Division, BusinessUnit,
ItemSupplier, CustomerPriceList, SupplierPriceList, ProductCategory, ProductSubCategory,
CustomerClassification

**Facts:** SalesOrders, Invoices, ItemBalance, PurchaseOrders, GoodsReceipts,
StockTransactions, CustomerPayments, SupplierPayments, Quotes, CreditNotes,
AROpenItems, APOpenItems, PaymentPredictor, ReceiptPredictor
