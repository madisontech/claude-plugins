# Madison BI Assistant — Context (v4.0.0)

> Loaded at boot. Contains rules and business logic that cannot be discovered from
> the database schema. For column names and data types, use DESCRIBE TABLE.

## Lakehouse Layer Model

Three layers with different conventions. Rules in this file default to `datawarehouse.*`
unless stated otherwise.

| Rule | datawarehouse.* (views) | gold.* (tables) | silver/bronze |
|------|------------------------|-----------------|---------------|
| Column naming | Space-separated, backtick-quoted (`` `Product Key` ``) | PascalCase, no backticks (`ProductKey`) | Source system naming (varies) |
| CONO / deleted | Not present (pre-filtered) | Not present (pre-filtered) | Must filter: `WHERE CONO = 100 AND deleted = FALSE` |
| Join casting | See casting rules below | Same rules apply | N/A (raw keys, no dim joins) |
| Backtick quoting | Required on every column | Not required | Not required |

For analysis: query `datawarehouse.fact.*` and `datawarehouse.dim.*`.
For investigation: trace through `gold.*` for transformation logic, `silver/bronze` for lineage.
When switching layers, state which and adjust column conventions accordingly.

## Schema Discovery

When querying a table for the first time in a session, or when unsure of column names,
run `DESCRIBE TABLE datawarehouse.fact.<table>` to get current columns and types. Do not
rely on memorised column names — verify against the live schema. This works at any layer:
`DESCRIBE TABLE gold.fact.invoices` returns PascalCase columns.

### Table Directory

Purpose and primary joins only. Use DESCRIBE TABLE for column details.

| Table | Purpose | Primary Joins |
|-------|---------|---------------|
| `fact.invoices` | Revenue, margin, rebates | Product Key, Customer Key, Employee Key, Invoice Date Key |
| `fact.salesorders` | Orders, pipeline, fulfilment | Product Key, Customer Key, Employee Key |
| `fact.purchaseorders` | Inbound supply | Product Key, Supplier Key, Warehouse Key |
| `fact.itembalance` | Stock on hand (bin-level) | Product Key, Warehouse Key, Location Key |
| `fact.itemwarehouse` | Inventory health (ageing, turnover) | Product Key, Warehouse Key |
| `fact.inventoryhistory` | Inventory snapshots (historical) | Product Key, Division (STRING), Record Date (DATE) |
| `fact.generalledger` | GL entries (post May 2024) | Account Key, Division Key (INT surrogate), Accounting Date Key |
| `fact.budget` | Budget by period/account | Account Key, Division Key, Budget Period Key (= Month Key) |
| `fact.accountsreceivable` | AR open items (post May 2024) | Customer Key, Division Key, Currency Key |
| `fact.accountspayable` | AP open items (post May 2024) | Supplier Key, Division Key, Currency Key |
| `fact.salestargets` | Sales targets by employee/month | Employee Key, Fiscal Year Month Key (INT YYYYMM) |
| `fact.paymentpredictor` | Cash flow lifecycle (rolling ~1K rows) | Supplier Key |
| `dim.product` | Product master (M3+SF merged) | Product Key (LONG) |
| `dim.customer` | Customer master (M3+SF merged) | Customer Key (LONG) |
| `dim.employee` | Salespeople + BU attribution | Employee Key (LONG) |
| `dim.calendar` | Date dimension (FY July start) | Date Key (INT YYYYMMDD) |
| `dim.supplier` | Supplier master | Supplier Key (BIGINT) |
| `dim.warehouse` | Warehouse/facility reference | Warehouse Key, Division (STRING) |
| `dim.supersessions` | Product replacement bridge | Product Key (new), Superseded Key (old) |

## SQL Rules

### Join Casting by Source System

| Source System | Facts | Rule |
|--------------|-------|------|
| M3 Core | invoices, salesorders, purchaseorders, deliverynotes, pickslips, preallocations, creditnotes, quotedmargin | `CAST(dim.Key AS STRING)` |
| M3 Inventory | inventoryhistory, inventoryhistorybymonth, itembalance, itemwarehouse | `CAST(dim.Key AS STRING)` |
| GL/Budget | generalledger, budget | No cast needed (INT coerces to LONG) |
| AR/AP | accountsreceivable, accountspayable | `CAST(dim.Key AS STRING)` |
| Salesforce | opportunities, opportunitylineitem, quote | No cast needed (LONG = LONG) |

If a join returns zero rows, check the CAST first. Omitting it silently returns empty results.

### Sentinel Values

Every fact-to-dim lookup uses `COALESCE(..., -1)`. No dimension has a -1 row.
- Use LEFT JOIN by default — INNER JOIN silently drops unmatched records
- `Product Key = -1` on invoices = Project Sales (invoice with Project Code, no Product Code). Expected behaviour. Exclude from product analysis, include in revenue totals.
- Cost centre: 72% of GL entries are -1 (by design)
- Opportunity Product Key: 54.6% NULL (SF line items often missing product link)

### Date Keys

Format: INT YYYYMMDD. Join to `dim.calendar.`Date Key``.

Exceptions:
- `invoices.`Invoice Date Key`` — DECIMAL type. Joins correctly, some NULLs.
- `generalledger.`Accounting Date Key`` — not named `Date Key`. Do not use `Date Key` on GL.
- `inventoryhistory.`Record Date`` — DATE type (not INT). Use date comparison, not calendar join. Use `MAX(`Record Date`)` per month partition, not `LAST_DAY()` (returns weekends with no snapshot).

### SQL Style

CTEs over subqueries. One clause per line. Comments explain WHY, not WHAT.
Test with LIMIT before running full queries on large tables.

## Output Rules

Do not return surrogate keys in analysis output. Resolve to business identifiers:
Division → `Division Code`/`Division Name`, Product → `Product Number`/`Product Name`,
Customer → `Customer Code`/`Customer Name`, Supplier → `Supplier Code`/`Supplier Name`,
Employee → `Full Name`, Account → `Account Code`/`Account Name`.

## Scope Discipline

Before writing any query, resolve internally:
- **Division:** 100 (MGE — all BUs), 5xx (Kallipr), or specific entity
- **Business Unit:** MAV, MT, MEX, MCS, KPR, or all — via attribution path
- **Time Period:** FY year or date range (YYYYMMDD)
- **Filters:** Additional constraints
- **Future date cap:** `Date Key <= today` for period totals

Confirm scope in one plain-English sentence. Do not change scope without approval.

## Business Context

### Fiscal Calendar

July–June fiscal year. `Fiscal Year` is INT (2025). `Fiscal Year Label` = "2024-2025".
```
FiscalYear  = YEAR(ADD_MONTHS(date, -6))    -- FY25 = Jul 2024 – Jun 2025
FiscalMonth = MONTH(ADD_MONTHS(date, -6))   -- 1=July, 12=June
```

Future date exclusion — cap at today. There is no `Is Future Date` column.
```sql
WHERE c.`Fiscal Year` = YEAR(ADD_MONTHS(CURRENT_DATE(), -6))
  AND c.`Date Key` <= CAST(DATE_FORMAT(CURRENT_DATE(), 'yyyyMMdd') AS INT)
```

### Division = Legal Entity

Division is the legal entity / company code. Does not map 1:1 to Business Units.

| Code | Entity | Notes |
|------|--------|-------|
| 100 | Madison Group Enterprises | Primary — contains MAV, MEX, MT, MCS |
| 200 | Madison Technologies Limited | — |
| 300 | Madison Connectivity Pty Ltd | MCS split from 100, Sept 2025 |
| 999 | MGE Consolidation | Always exclude |

Division 100 is the default. MCS split: from Sept 2025, MCS activity in both Div 100
and 300. Use Employee BU attribution for complete MCS picture.

Division column varies by fact table:
- `fact.invoices`, `fact.inventoryhistory`: `Division` (STRING)
- `fact.salesorders`: `DIVI` (DECIMAL)
- GL, Budget, AR, AP: `Division Key` (INT surrogate — JOIN `dim.division` for code)

### Attribution Model

| Path | Column | Coverage | Use For |
|------|--------|----------|---------|
| **Facility** | `Facility` on fact table | 100% | Division attribution (inventory/operations) |
| **Employee BU** | `dim.employee.Business Unit` | ~95% | Revenue attribution (TRIM required) |
| **Product BU** | `dim.product.Product Business Unit` | 47% Unknown | BU drill-down within Div 100 only |
| **Customer BU** | `dim.customer.Business Unit` | 54% NULL | Not reliable for primary attribution |

Always state which attribution path is used. Do not use Product BU for division attribution.

### Revenue & Margin

```
Margin = TotalValue - TotalCost - RebateAmount
```
`RebateAmount` = customer rebate accrual (4-tier waterfall). `TotalCost` already nets
supplier rebate. Omitting `RebateAmount` overstates margin.

Cost field: use `UCDCOS` (delivery cost). `UCUCOS` is stale.

### FX Conversion

`LocalAmount = ForeignAmount / ExchangeRate` — divide, not multiply.
Rate = foreign currency units per 1 AUD.

### UOM Conversions

Purchase/delivery tables have raw and converted quantities. Use `*_Converted` fields
for stock impact analysis (e.g., `Order Qty Converted`, `Delivered Qty Converted`).

### Universal Exclusions

Apply to every M3-sourced query:
- Division 999: `Division <> '999'`
- Credit card surcharges: `Product Number NOT LIKE 'MCC%' AND NOT LIKE 'KCC%'`
- Valid salesperson: code contains hyphen (`LIKE '%-%'`)

### Data Boundaries

| Constraint | Impact |
|-----------|--------|
| GL/AR/AP: post-2024-05-01 only | No historical financials before May 2024 |
| AR: positive amounts only | Credit notes excluded |
| Calendar: 2017-07-01 to 2026-12-31 | Date keys outside range won't join |
| Legacy ERP backfill | Pattern breaks near migration date may be artefact |
| Refresh: hourly 10am-8pm AEST Mon-Fri | Weekend data not refreshed until Monday |

### Customer State Normalisation

`dim.customer.State` is truncated to 2 chars. Map: NS→NSW, VI→VIC, QL→QLD, TA→TAS,
AC→ACT. NZ = New Zealand (country, not state). 32% have no state.

## Schema Gotchas

Things that look correct but aren't. Cannot be discovered via DESCRIBE TABLE.

### Broken / Phantom Tables

- `dim.paymentterms` — does not exist. Payment terms are STRING fields on dim.customer and dim.supplier
- `fact.supplierpayments` — does not exist. Use fact.accountspayable
- `fact.aropenitems` — does not exist. Use fact.accountsreceivable
- `fact.targets` — does not exist. Use fact.salestargets
- `fact.codeliveries` — exists but 0 rows (broken ETL)
- `fact.inventoryprojection` — exists but disabled (performance issues)

### Broken Columns

- `dim.product.Superseded By` — always NULL. Use `dim.supersessions` bridge table
- AR has no `Aging Bucket` or `Open Amount` — compute ageing from `Due Date` (STRING YYYYMMDD) via DATEDIFF
- AP has no pre-computed ageing — same DATEDIFF pattern. AP dates are STRING YYYYMMDD
- `fact.itembalance` — column is `On Hand` (not `On Hand Qty`), `OnHand Value` (not `On Hand Value`)
- `fact.purchaseorders` — no `Exchange Rate` column. FX via `dim.currency` on `Currency Key` (compound: "USD100")
- `fact.inventoryhistory` — has own `Division` column (STRING). No need to join warehouse for division

### Value Enumerations

- **Product Status:** 10=Preliminary, 20=Active, 50=Phase Out, 80=Old, 90=Discontinued
- **Employee BU:** MAV, MT, MEX, MCS, KPR (ignore system values: ZZZ, 0, Slobs, MCT, MGE, KLL, COP, MNZ)
- **Product BU actual strings:** `<Unknown>` (47%), `MadisonAV`, `Madison Technologies`, `Madison Express`, `Madison Connectivity Solutions` (not 'MCS')
- **PO Currency Key:** compound format "USD100" (currency+division), not plain ISO code
- **GL Account grouping:** first digit = type (1=Assets, 2=Liabilities, 3=Equity, 4=Revenue, 5+=Expenses)

### Key Derivations

**Product Supersession** — `dim.supersessions` is the only reliable mechanism. Flat topology
(no recursion). Many-to-one possible. Superseded products keep selling. When joining,
aggregate to avoid fan-out: first replacement + count per superseded product.

**AP Double-Entry** — invoices are negative `AUD Amount`, payments/credits positive (blank
`Payment Term`). Gross ageing is 10-20x net. Compute net balance per supplier-invoice first.

**Sales Targets** — monthly grain (not daily). `Fiscal Year Month Key` is INT YYYYMM.
Aggregate invoices to monthly before joining.

## Bulk Data Extraction

For result sets >500 rows, use `tools/dbx-extract.py` to write directly to CSV.

## Few-Shot Anti-Pattern Examples

<anti_pattern_examples>

<example name="M3 join without CAST">
<wrong>
SELECT p.`Product Name`, SUM(i.`Total Value`)
FROM datawarehouse.fact.invoices i
JOIN datawarehouse.dim.product p ON i.`Product Key` = p.`Product Key`
GROUP BY p.`Product Name`
</wrong>
<result>Zero rows. No error.</result>
<why>fact.invoices stores Product Key as STRING, dim.product stores it as LONG.</why>
<correct>
JOIN datawarehouse.dim.product p ON i.`Product Key` = CAST(p.`Product Key` AS STRING)
</correct>
</example>

<example name="GL filtered by Division string">
<wrong>
SELECT SUM(gl.`Signed Amount`)
FROM datawarehouse.fact.generalledger gl
WHERE gl.`Division` = '100'
</wrong>
<result>Zero rows. GL has no Division column — it uses Division Key (INT surrogate).</result>
<correct>
JOIN datawarehouse.dim.division d ON gl.`Division Key` = d.`Division Key`
WHERE d.`Division Code` = '100'
</correct>
</example>

<example name="INNER JOIN drops sentinel records">
<wrong>
SELECT SUM(i.`Total Value`)
FROM datawarehouse.fact.invoices i
INNER JOIN datawarehouse.dim.product p ON i.`Product Key` = CAST(p.`Product Key` AS STRING)
</wrong>
<result>Total lower than actual — Product Key -1 records (Project Sales) silently dropped.</result>
<correct>
LEFT JOIN datawarehouse.dim.product p ON i.`Product Key` = CAST(p.`Product Key` AS STRING)
</correct>
</example>

<example name="Employee BU without TRIM">
<wrong>WHERE e.`Business Unit` = 'MT'</wrong>
<result>Misses 14 MT employees whose BU value is 'MT ' (trailing space).</result>
<correct>WHERE TRIM(e.`Business Unit`) = 'MT'</correct>
</example>

<example name="Margin without RebateAmount">
<wrong>SELECT SUM(i.`Total Value` - i.`Total Cost`) AS Margin</wrong>
<result>Margin overstated — customer rebate accrual not deducted.</result>
<correct>SELECT SUM(i.`Total Value` - i.`Total Cost` - i.`Rebate Amount`) AS Margin</correct>
</example>

</anti_pattern_examples>
