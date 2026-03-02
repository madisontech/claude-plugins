# Investigation Methodology

> Use when a value looks wrong, a report doesn't match, or a discrepancy needs root-causing.
> Always start and finish with `datawarehouse.*` views — intermediate layers are for tracing only.

## Workflow

### 1. Observe — Reproduce the Discrepancy

Before investigating, confirm the problem exists:

```sql
-- Get the actual value from the authoritative source
SELECT SUM(`Total Value`) AS Revenue
FROM datawarehouse.fact.invoices i
LEFT JOIN datawarehouse.dim.calendar c ON i.`Invoice Date Key` = c.`Date Key`
WHERE c.`Fiscal Year` = 2025
  AND i.`Division` <> '999'
```

Compare to the reported value. If they match, the problem is downstream (Power BI, Excel, Jedox).
If they differ, the problem is in the data.

### 2. Hypothesise — Rank Likely Causes

Common root causes (in order of frequency):

| Cause | Symptom | Check |
|-------|---------|-------|
| **Join mismatch** | Zero or inflated rows | Check CAST rules per source system. M3 facts need `CAST(dim.Key AS STRING)` |
| **Filter gap** | Missing records | Check CONO=100, deleted=FALSE, Division<>999, credit card exclusions |
| **Date boundary** | Missing history | GL/AR/AP only from May 2024. Calendar range 2017-07 to 2026-12 |
| **BU attribution path** | Different totals | Employee BU vs Product BU vs Customer BU give different answers |
| **Sentinel orphans** | Lower totals with INNER JOIN | -1 keys dropped by INNER JOIN. Use LEFT JOIN |
| **Trailing spaces** | Missing BU segment | "MT " vs "MT" on dim.employee. Always TRIM |
| **ETL lag** | Recent data missing | Check watermark in GoldIntegrationBehaviorSettings |
| **Disabled query** | Stale data | inventoryprojection and codeliveries are disabled |
| **Rebate inclusion** | Margin overstatement | Margin = TotalValue - TotalCost - RebateAmount |
| **FX direction** | Inverted amounts | Division not multiplication (amount / rate) |

### 3. Trace — Follow the Data Through Layers

**Layer 1: Datawarehouse views** (authoritative)
```
datawarehouse.fact.* / datawarehouse.dim.*
```

**Layer 2: Gold tables** (structure reference)
```
gold.fact.* / gold.dim.* — same data, different namespace
```

**Layer 3: ETL logic** (transformation reference)
```sql
SELECT GoldIntegrationQuery
FROM int.maincontroltable
WHERE GoldObjectSettings LIKE '%{table_name}%'
  AND GoldIntegrationEnabled = true
```

**Layer 4: Silver/Bronze** (raw source, last resort)
```
*_silver.* / *_bronze.* — lineage verification only
```

### Key ETL Patterns to Check

**Gold-to-gold dependencies:** Some fact tables read other fact tables:
- `fact.receiptpredictor` reads `fact.salesorders` + `fact.accountsreceivable`
- `fact.paymentpredictor` reads `fact.purchaseorders` + `fact.accountspayable`
- `fact.cashflow` reads both predictors
- Refresh order matters — stale upstream = stale downstream

**Incremental watermarks:** Most M3 tables use `__ts` column for incremental loads.
Exceptions: `salestargets` (full load), `calendar` (generated), `case` (full load).

**Identity columns (key resolution):**
The ETL resolves natural keys to surrogate keys via dimension lookups, then wraps in
`COALESCE(..., -1)`. If a natural key doesn't match any dimension record, the surrogate
key becomes -1. This is by design, not an error — but it means INNER JOIN drops these records.

### 4. Confirm — Isolate and Verify

Once you've identified the likely cause:

1. Write a targeted query that isolates the specific records affected
2. Quantify the impact (how many rows, what dollar value)
3. Determine if it's a data issue (ETL bug, source system) or a query issue (wrong join, wrong filter)
4. **Return to `datawarehouse.*` views** for the corrected authoritative number

### 5. Report

Structure the finding as:
- **Discrepancy:** What was reported vs what is correct
- **Root cause:** Why they differ (specific technical detail)
- **Impact:** Rows affected, dollar impact, which reports/dashboards are wrong
- **Fix:** What needs to change (ETL, query, report, or data source)

## Common Traps

- **Don't trust intermediate layers for reporting.** Gold queries can have bugs.
  The `datawarehouse.*` views are the contract.
- **Don't assume joins are correct.** The audit found all 3 query patterns in the
  previous context.md were broken (wrong column names, missing CAST).
- **Check the calendar range.** Date keys outside 20170701–20261231 won't join.
  Historical data from legacy ERP may have dates from 2006-2007.
- **Verify table names.** `fact.aropenitems` doesn't exist (it's `fact.accountsreceivable`).
  `fact.targets` doesn't exist (it's `fact.salestargets`).
