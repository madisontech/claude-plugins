# Investigation Methodology

> Use when a value looks wrong, a report doesn't match, or a discrepancy needs root-causing.
> Always start and finish with `datawarehouse.*` views — intermediate layers are for tracing only.
> Query rules (join casting, sentinels, exclusions) are in context.md. When tracing through
> gold or silver/bronze layers, adjust column naming and filtering per the Lakehouse Layer
> Model in context.md: gold uses PascalCase (no backticks), silver/bronze needs CONO/deleted filters.

## Workflow

### 1. Observe — Reproduce the Discrepancy

Before investigating, confirm the problem exists with a query against `datawarehouse.*` views.
Compare to the reported value. If they match, the problem is downstream (Power BI, Excel, Jedox).
If they differ, the problem is in the data.

### 2. Hypothesise — Rank Likely Causes

| Cause | Symptom | Check |
|-------|---------|-------|
| **Join mismatch** | Zero or inflated rows | Check CAST rules per source system (context.md) |
| **Filter gap** | Missing records | Division<>999, credit card exclusions |
| **Date boundary** | Missing history | GL/AR/AP only from May 2024. Calendar 2017-07 to 2026-12 |
| **BU attribution path** | Different totals | Employee BU vs Product BU vs Customer BU give different answers |
| **Sentinel orphans** | Lower totals with INNER JOIN | -1 keys dropped. Use LEFT JOIN |
| **Trailing spaces** | Missing BU segment | "MT " vs "MT" on dim.employee. Always TRIM |
| **ETL lag** | Recent data missing | Check watermark in GoldIntegrationBehaviorSettings |
| **Disabled query** | Stale data | inventoryprojection and codeliveries are disabled |
| **Rebate inclusion** | Margin overstatement | Margin = TotalValue - TotalCost - RebateAmount |
| **FX direction** | Inverted amounts | Division not multiplication (amount / rate) |

### 3. Trace — Follow the Data Through Layers

```
datawarehouse.fact.* / datawarehouse.dim.* <-- QUERY FOR ANALYSIS (Power BI connected)
     ^ (views built on)
gold.fact.* / gold.dim.* <-- Gold tables (structure reference only)
     ^ (populated by)
int.maincontroltable <-- GoldIntegrationQuery (transformation logic)
     ^ (sourced from)
*_silver.* / *_bronze.* <-- Lineage verification only
```

**GoldIntegrationQuery is for learning/debugging only — never for primary analysis.**

#### Extract Transformation Logic

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

#### Control Table Columns

| Column | Use |
|--------|-----|
| GoldObjectSettings | JSON: table name, schema, key columns, SCD type |
| GoldIntegrationQuery | Delta merge SQL showing transformation logic |
| GoldIntegrationBehaviorSettings | JSON: load type, watermark, dependencies |
| GoldIntegrationEnabled | Active/inactive flag |

### 4. Confirm — Isolate and Verify

1. Write a targeted query that isolates the specific records affected
2. Quantify the impact (how many rows, what dollar value)
3. Determine if it's a data issue (ETL bug, source system) or a query issue (wrong join, filter)
4. **Return to `datawarehouse.*` views** for the corrected authoritative number

### 5. Report

Structure the finding as:
- **Discrepancy:** What was reported vs what is correct
- **Root cause:** Why they differ (specific technical detail)
- **Impact:** Rows affected, dollar impact, which reports/dashboards are wrong
- **Fix:** What needs to change (ETL, query, report, or data source)

## ETL Patterns (from 61 Gold Queries)

| # | Pattern | Detail |
|---|---------|--------|
| 1 | **Silver -> Gold dim lookup** (dominant) | Natural keys to surrogates, `COALESCE(..., -1)` for unmatched |
| 2 | **M3 compound keys** | `CONO` + `ORNO` + `PONR`. Filtered `CONO=100`, `deleted=FALSE` in silver |
| 3 | **CSYTAB enrichment** | `ITTY` = item type, `CFI3` = product BU, `SMCD` = employee BU (first 3 chars) |
| 4 | **Salesforce joins** | 18-char string IDs. No CONO, no deleted. LONG keys in gold |
| 5 | **Gold-to-gold dependencies** | receiptpredictor reads salesorders+AR; paymentpredictor reads purchaseorders+AP; cashflow reads both predictors; quotedmargin reads invoices. Refresh order matters |
| 6 | **MoPro WMS joins** | `CONCAT('MI', mopro.SKU)` maps to M3 ProductNumber |
| 7 | **Rebate joins** | spsales.rebates + brand groups. R1 (exclusive) -> R2 (non-exclusive) -> R3 (wholesale) -> R4 (member). +FREDON 5%, +MI Retail 4% |

## Disabled/Broken Tables

- **`fact.inventoryprojection`** — Complex multi-CTE query, performance issues. Disabled.
- **`fact.codeliveries`** — Missing silver table prefix. 0 rows. Broken.
- **`fact.quote`** — Joins to `datawarehouse.dim.product` (breaks medallion convention).

## Common Traps

- Don't trust intermediate layers for reporting. `datawarehouse.*` views are the contract.
- Don't assume joins are correct — always verify CAST rules.
- Check the calendar range (20170701–20261231). Legacy dates may fall outside.
- Verify table names: `fact.aropenitems` doesn't exist (use `fact.accountsreceivable`),
  `fact.targets` doesn't exist (use `fact.salestargets`).
