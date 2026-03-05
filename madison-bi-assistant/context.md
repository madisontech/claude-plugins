# Madison BI Assistant — Context (v3.3.0)

> Loaded at boot. Full table inventory: `references/schema-inventory.md` (load on demand, not at boot).

## Source of Truth

**Always query:** `datawarehouse.fact.*` and `datawarehouse.dim.*` (reporting views)
**Never query:** `gold.*`, `fact.*`, `dim.*`, `*_silver.*`, `*_bronze.*` (intermediate layers)

The `datawarehouse.*` views use **space-separated column names** (backtick-quoted: `` `Product Key` ``).
The underlying `gold.*` tables use PascalCase without spaces (`ProductKey`). All column names
in this document and query patterns reference the `datawarehouse.*` view layer.

Full table inventory in `references/schema-inventory.md`.

## Output Rules

**Never return surrogate keys in analysis output.** Keys like `Division Key`, `Product Key`,
`Customer Key`, `Warehouse Key` are internal database identifiers — meaningless to stakeholders.
Always resolve to business identifiers:
- Division: `Division Code` (100, 300, 520) or `Division Name`
- Product: `Product Number` + `Product Name`
- Customer: `Customer Code` + `Customer Name`
- Warehouse: `Warehouse` code + `Warehouse Description`
- Supplier: `Supplier Code` + `Supplier Name`
- Employee: `Full Name` via dim.employee
- Account: `Account Code` + `Account Name`

## SQL Rules (Critical — Queries Fail Without These)

### Column Names
All columns on `datawarehouse.*` views use **space-separated names with backtick quoting**:
`` `Invoice Date Key` ``, `` `Product Key` ``, `` `Product Business Unit` ``. Never snake_case.
Every column reference must be backtick-quoted.

### Join Casting by Source System

| Source System | Fact Key Type | Dim Key Type | Rule |
|--------------|--------------|-------------|------|
| **M3 Core** (invoices, salesorders, purchaseorders, deliverynotes, pickslips, preallocations, creditnotes, quotedmargin) | STRING | LONG | `CAST(dim.Key AS STRING)` |
| **M3 Inventory** (inventoryhistory, inventoryhistorybymonth, inventoryprojection) | STRING | LONG | `CAST(dim.Key AS STRING)` |
| **GL/Budget** (generalledger, budget) | INT | LONG | No cast needed (implicit coercion) |
| **AR/AP** (accountsreceivable, accountspayable) | STRING | LONG | `CAST(dim.Key AS STRING)` — same as M3 Core |
| **Salesforce** (opportunities, opportunitylineitem, quote) | LONG | LONG | No cast needed |
| **Other** (historicaldemand) | STRING | STRING | No cast needed |

**If a join returns zero rows, check the CAST first.** M3 facts store surrogate keys as STRING;
dimensions store them as LONG. Omitting the CAST silently returns empty results.

### GL Division Key Cross-Reference

The GL fact table (`fact.generalledger`) uses `Division Key` — an integer surrogate key that
maps to `dim.division.`Division Key``, **not** the string division code used in M3 invoice/order
facts. Filtering GL with `WHERE Division = '100'` returns zero rows.

Known mapping (from `datawarehouse.dim.division`). If querying a division not in this table,
JOIN `dim.division` dynamically to resolve:

| Division Key | Division Code | Division Name |
|---|---|---|
| 1 | 100 | Madison Group Enterprises Pty Ltd |
| 2 | 200 | Madison Technologies Limited |
| 3 | 500 | Kallipr Holdings Pty Ltd |
| 4 | 505 | Kallipr IP Pty Ltd |
| 5 | 520 | Kallipr Pty Ltd |
| 6 | 550 | Kallipr Regional Pty Ltd |
| 7 | 999 | MGE Consolidation |
| 8 | 560 | Kallipr Americas LLC |
| 9 | 300 | Madison Connectivity Pty Ltd |
| 10 | 400 | CtrlOps Pty Ltd |

To filter GL by division, either JOIN to the dimension or use the verified surrogate key:
```sql
-- Option A: JOIN to dim.division
JOIN datawarehouse.dim.division d ON gl.`Division Key` = d.`Division Key`
WHERE d.`Division Code` = '100'

-- Option B: Use verified surrogate key directly
WHERE gl.`Division Key` = 1  -- Division 100 (MGE Operating)
```

### Sentinel Values
Every fact-to-dim lookup wraps in `COALESCE(..., -1)`. No dimension has a -1 row.
- **INNER JOIN** silently drops unmatched records (invoices have thousands of customer orphans; GL has >1M cost centre orphans)
- **LEFT JOIN** preserves them — use LEFT JOIN by default, filter -1 only when deliberate
- **Product Key = -1 on invoices:** These are Project Sales — invoices with a Project Code but no Product Code. Expected behaviour, not a data quality issue. Exclude from product-level analysis; include in total revenue/division analysis.

### Date Keys
Format: INT `YYYYMMDD` (e.g., `20260303`). Join to `dim.calendar.`Date Key``.
Exception: `invoices.`Invoice Date Key`` is DECIMAL — still joins correctly but has some NULLs.
Exception: `generalledger.`Accounting Date Key`` — NOT named `Date Key`. Do not use `Date Key` on GL.

### SQL Style
- CTEs over subqueries; one clause per line; trailing commas
- Comments explain WHY, not WHAT: `-- Exclude test accounts per DEC-003`
- Test with LIMIT before running full queries on large tables
- Use APPROX_COUNT_DISTINCT for dashboard-level counts

## Scope Discipline (Internal Checklist)

Before writing any query, resolve these five dimensions internally:

- **Division:** 100 (MGE operating — all BUs), 5xx (Kallipr), or specific entity code. This is the legal entity filter.
- **Business Unit:** MAV, MT, MEX, MCS, KPR, or all — via attribution path (Employee BU for revenue, Product BU for operations within Div 100). This isolates BUs *within* a division.
- **Time Period:** FY year or date range (YYYYMMDD format)
- **Filters:** Any additional constraints (product line, customer segment, etc.)
- **Future date cap:** Apply `Date Key <= today` for period totals (see Fiscal Calendar section)

Then confirm the scope to the user in one plain-English sentence. Never render this
checklist as a code block. Never change scope without the analyst's approval.

## Business Context

### Fiscal Calendar
July–June fiscal year. `Fiscal Year` is INT (2025, not "FY25"). `Fiscal Year Label` = "2024-2025" (not "FY25").
```
FiscalYear  = YEAR(add_months(date, -6))    -- FY25 = Jul 2024 – Jun 2025
FiscalMonth = MONTH(add_months(date, -6))   -- 1=July, 12=June
```

**Future Date Exclusion:** When calculating period totals (MTD, QTD, YTD), always cap at
today's date to exclude uncommitted future data. Current FY = `YEAR(ADD_MONTHS(CURRENT_DATE(), -6))`.
```sql
-- YTD capped at today
WHERE c.`Fiscal Year` = YEAR(ADD_MONTHS(CURRENT_DATE(), -6))
  AND c.`Date Key` <= CAST(DATE_FORMAT(CURRENT_DATE(), 'yyyyMMdd') AS INT)
```
There is **no** `Is Future Date` column on dim.calendar — always use the date cap method above.

### Division = Legal Entity

Division is the legal entity / company code in M3. It does **not** map 1:1 to Business Units
for analysis purposes.

| Code | Entity | Abbrev |
|------|--------|--------|
| 100 | Madison Group Enterprises Pty Ltd | MGE |
| 200 | Madison Technologies Limited | MT |
| 300 | Madison Connectivity Pty Ltd | MCS |
| 400 | CtrlOps Pty Ltd | — |
| 500 | Kallipr Holdings Pty Ltd | KPR |
| 505 | Kallipr IP Pty Ltd | KPR |
| 520 | Kallipr Pty Ltd | KPR |
| 550 | Kallipr Regional Pty Ltd | KPR |
| 560 | Kallipr Americas LLC | KPR |
| 999 | MGE Consolidation | ZZZ — always exclude |

**Division 100 is the primary operating division** and the default for all analysis unless
otherwise stated. When filtering to Division 100, you get ALL four business units (MAV, MEX,
MT, MCS). To isolate a specific BU within Division 100, use the attribution path (Employee BU
for revenue, Product BU for BU drill-down on operations), not the division code.

**MCS Division Split (September 2025):** MCS split from Division 100 into Division 300
(Madison Connectivity Pty Ltd). First Division 300 invoice: 2025-09-09. Sales still come through
both Division 100 and Division 300 for MCS. When analysing MCS, check both divisions or use
Employee BU attribution to capture the full picture.

Standard MGE filters:
- `WHERE Division = '100'` — for M3 invoice/order facts (all BUs, but note MCS split)
- `WHERE TRIM(e.`Business Unit`) = 'MT'` — to isolate a specific BU within Division 100
- `WHERE Division IN ('100', '300')` — when you need MCS activity from both entities

### Attribution Model

**Division attribution (inventory/operations):** Use `Facility` on the fact table — this is the
M3 item/facility code and equals the Division code. 100% coverage, structurally guaranteed.
`dim.warehouse.Division` provides the same mapping via `Warehouse Key`. **Do not use
`Product Business Unit` for division attribution** — it has ~50% Unknown overall and is
completely BLANK for Division 520 (Kallipr).

**BU drill-down within Division 100:** Use `Product Business Unit` on `dim.product` to isolate
MAV/MEX/MT/MCS within Division 100 only. Coverage is good for Div 100; not applicable for
other divisions.

**Revenue attribution:** Employee BU via `dim.employee.Business Unit` (TRIM required — "MT "
has trailing spaces). Values: MAV, MT, MEX, MCS, KPR.

**Division column varies by fact table:**

| Fact Table | Division Column | Type | Notes |
|-----------|----------------|------|-------|
| `fact.invoices` | `Division`, `Facility` | STRING | Both available |
| `fact.inventoryhistory` | `Division`, `Facility` | STRING | Both available |
| `fact.salesorders` | `DIVI` | DECIMAL | No `Division` or `Facility` column |
| `fact.generalledger` | `Division Key` | INT (surrogate) | Must JOIN dim.division for code |
| `fact.budget` | `Division Key` | INT (surrogate) | Must JOIN dim.division for code |
| `fact.accountsreceivable` | `Division Key` | INT (surrogate) | Must JOIN dim.division for code |
| `fact.accountspayable` | `Division Key` | INT (surrogate) | Must JOIN dim.division for code |

Other BU attribution paths (for reference, not primary):

| Path | Coverage | Notes |
|------|----------|-------|
| **Product BU** | ~50% `<Unknown>` | Name-based: "MadisonAV", "Madison Technologies", "Madison Express". 3 MCS variants, 2 KPR variants. BU drill-down only, not for division |
| **Customer BU** | ~50% NULL | SF Account Owner department. Unreliable for primary attribution |

Always state which attribution path is used.

### Revenue Composition (Invoice Anatomy)

```
InvoiceValue  = qty x unit price              (OINVOL type '31')
+ HeaderCharge = header-level charges           (type '60')
+ LineCharge   = line-level charges             (type '67')
= TotalValue   (revenue recognised)

TotalCost     = standard cost - supplier rebate + COGS charge
Margin        = TotalValue - TotalCost - RebateAmount
```

`RebateAmount` is the **customer rebate accrual** (from the 4-tier waterfall below). `TotalCost`
already nets the **supplier rebate**. These are distinct — not double-counted.

**Margin includes rebate deductions.** The 4-tier rebate waterfall:
1. Exclusive brand rebate (customer-brand-specific)
2. Non-exclusive brand rebate (brand-level)
3. Wholesale group accrual rate
4. Rebate member accrual rate
Plus: +5% FREDON surcharge, +4% MI Retail surcharge (conditional)

Querying `TotalValue - TotalCost` without `RebateAmount` **overstates margin**.

**Cost field:** When querying item-level cost, use `UCDCOS` (delivery cost from MITBAL).
`UCUCOS` is a stale unit cost that may not reflect current pricing. The pre-calculated
`Total Cost` on `fact.invoices` already uses the correct cost basis.

### FX Conversion
`LocalAmount = ForeignAmount / ExchangeRate` — **division, not multiplication.**
Rate = foreign currency units per 1 AUD.

### Unit of Measure Conversions

Purchase and delivery quantities have two representations:

| Fact Table | Raw Fields | Converted Fields | Rule |
|-----------|-----------|-----------------|------|
| `fact.purchaseorders` | `Order Qty` | `Order Qty Converted` | Use Converted for stock impact analysis |
| `fact.deliverynotes` | `Delivered Qty`, `Received Qty` | `Delivered Qty Converted`, `Received Qty Converted` | Use Converted for inventory reconciliation |
| `fact.salesorders`, `fact.invoices`, `fact.itembalance` | Single qty fields | — | Already in stock UOM |

Conversions between purchase units (RO, BOX, BAG) and stock units (EA, M) are applied
during ETL. Always use the **Converted** quantity when assessing stock impact, supply chain
metrics, or comparing purchase to sales volumes.

## Universal Exclusions

Apply to every M3-sourced query:
- Division 999 excluded from invoices (`Division <> '999'`)
- Credit card surcharges excluded (join to dim.product, filter `Product Number NOT LIKE 'MCC%' AND NOT LIKE 'KCC%'`)
- Valid salesperson: code contains hyphen (`LIKE '%-%'`)

**Gold-layer note:** `CONO` and `deleted` columns exist on silver/bronze layers but are
pre-filtered in the gold `datawarehouse.fact.*` views. Do not include `WHERE CONO = 100`
or `AND deleted = FALSE` in queries against gold-layer fact tables — these columns do not exist there.

## Data Boundaries and Coverage Gaps

### Refresh Schedule
Sales, Finance, and Operations semantic models refresh hourly from 10:00 AM to 8:00 PM AEST,
Monday to Friday. Data queried outside this window or before the first refresh reflects the
previous business day's final state. Weekend data is not refreshed until Monday morning.

| Constraint | Impact |
|-----------|--------|
| **GL/AR/AP: post-2024-05-01 only** | `generalledger WHERE EGACDT > 20240430`, same for AR/AP. No historical financials before May 2024 |
| **AR: positive amounts only** | Credit notes excluded (`ESCUAM > 0`) |
| **Calendar range: 2017-07-01 to 2026-12-31** | Date keys outside this range won't join to calendar |
| **Customer BU: ~50% NULL** | Majority of customers have no BU via SF Account Owner path |
| **Product BU: ~50% Unknown** | `<Unknown>` is the most common value in dim.product.`Business Unit` |
| **Opportunity Product Key: ~55% NULL** | SF opportunity line items often missing product link |
| **Customer State: truncated** | See state normalisation mapping below |
| **Legacy ERP backfill** | fact.invoices and fact.salesorders contain backfilled data from pre-M3. Pattern breaks near migration date may be system artefact, not business shift |

**Customer State Normalisation:** `dim.customer.State` is truncated to 2 characters. Apply
this mapping for reporting:
```sql
CASE TRIM(State)
  WHEN 'NS' THEN 'NSW'
  WHEN 'VI' THEN 'VIC'
  WHEN 'QL' THEN 'QLD'
  WHEN 'WA' THEN 'WA'
  WHEN 'SA' THEN 'SA'
  WHEN 'TA' THEN 'TAS'
  WHEN 'NT' THEN 'NT'
  WHEN 'AC' THEN 'ACT'
  WHEN 'NZ' THEN 'NZ'   -- Country, not state
  ELSE State
END AS State_Normalised
```
32% of customer records have no state. `NZ` indicates New Zealand (country), not a state.

## Product Supersession

`dim.supersessions` is the **only reliable** supersession mechanism.
`dim.product.`Superseded By`` is structurally broken (always NULL). Do not use it.

When analysing product performance where continuity matters, use the supersession CTE pattern
documented in `references/schema-inventory.md` section 4c. Always ask whether the user wants to include
superseded products when the target product has bridge table entries.

Key facts: flat topology (no recursion needed), many-to-one possible, superseded products
keep selling after replacement.

## Multi-System Integration

| System | Key Format | Filters | Notes |
|--------|-----------|---------|-------|
| M3 / CloudSuite | Composite keys, CONO=100 | `deleted = FALSE`, YYYYMMDD dates | Primary ERP |
| Salesforce | 18-char string IDs | No CONO, no deleted flag | CRM — commercial metadata |
| MoPro | SKU -> `CONCAT('MI', SKU)` | WMS operations data | Warehouse management |
| Jedox | Division/product codes, period strings | OLAP planning data | Not queried via this assistant |
| spsales | Brand group + date range | Rebate rates | External rebate system |

**Dual system of record:** Products split M3 (transactional: cost, pricing, item type) and
SF (commercial: supersession, pareto, product line manager). Customers split M3 (master record)
and SF (account owner, BU, industry). `dim.product` and `dim.customer` merge both sources.

## Key Tables (Quick Reference)

### Core Facts
| Table | Purpose | Key Joins |
|-------|---------|-----------|
| `fact.invoices` | Revenue, margin, rebates | Product, Customer, Employee, Calendar |
| `fact.salesorders` | Open/fulfilled orders, pipeline | Product, Customer, Employee, Calendar |
| `fact.purchaseorders` | Inbound supply | Product, Supplier, Warehouse |
| `fact.itembalance` | Stock on hand (bin-level) | Product, Warehouse, Location |
| `fact.itemwarehouse` | Inventory health (ageing, turnover) | Product, Warehouse |
| `fact.generalledger` | GL entries (post May 2024) | Account, CostCentre, Division, Calendar |
| `fact.budget` | Budget by period/account (current budget FY, Division 100) | Account, CostCentre, Division, Calendar (via `Budget Period Key` = `Month Key`) |
| `fact.accountsreceivable` | AR open items (post May 2024) | Customer, Currency, Calendar |
| `fact.accountspayable` | AP open items (post May 2024) | Supplier, Currency, Calendar |
| `fact.paymentpredictor` | Cash flow lifecycle projection (rolling snapshot, ~1K rows) | Supplier, Calendar |
| `fact.salestargets` | Sales targets by employee/month | Employee, Calendar |

### Core Dimensions
| Table | Purpose | Key Fields |
|-------|---------|------------|
| `dim.product` | Product master (M3+SF merged) | `Product Key`, `Product Number`, `Product Business Unit` |
| `dim.customer` | Customer master (M3+SF merged) | `Customer Key`, `Customer Code`, `Customer Name`, `Payment Terms`, `Delivery Terms`, `Credit Limit1/2/3`, `Customer Stop`, `Wholesale Group` |
| `dim.employee` | Salespeople + BU attribution | `Employee Key`, `Business Unit` (TRIM!) |
| `dim.calendar` | Date dimension (FY Jul start) | `Date Key`, `Fiscal Year`, `Fiscal Year Label` |
| `dim.supplier` | Supplier master | `Supplier Key` (BIGINT), `Supplier Code`, `Supplier Name`, `Supplier Division`, `Payment Terms`, `Delivery Terms` |
| `dim.warehouse` | Warehouse/facility reference | `Warehouse Key`, `Warehouse`, `Warehouse Description`, `Division` |
| `dim.supersessions` | Product replacement links | `Product Key` (new), `Superseded Key` (old) |

## Bulk Data Extraction

For result sets too large for the context window (>~500 rows), use `tools/dbx-extract.py`
to write directly to CSV. See `references/python-environment.md` for invocation and setup.

## Common Anti-Patterns

| Anti-Pattern | Consequence | Correct Approach |
|-------------|-------------|-----------------|
| Omit CAST on M3 fact->dim joins | Zero rows returned silently | `CAST(dim.Key AS STRING)` |
| INNER JOIN fact to dim | Silently drops orphan records | LEFT JOIN, filter -1 explicitly |
| Use `dim.product.`Superseded By`` | Always NULL (broken) | Use `dim.supersessions` bridge table |
| Query GL/AR/AP before May 2024 | No data exists | Use fact.invoices or fact.budget |
| Use `Fiscal Year` as string "FY25" | Wrong type — it's INT 2025 | Use `Fiscal Year Label` for display |
| Filter employee BU = 'MT' without TRIM | Misses 14 employees | `TRIM(`Business Unit`) = 'MT'` |
| Multiply FX rate | Inverts conversion | `amount / rate` |
| Include CONO or deleted on gold tables | Column doesn't exist | These are pre-filtered in gold layer |
| Use `fact.aropenitems` or `fact.targets` | Tables don't exist | `fact.accountsreceivable`, `fact.salestargets` |
| Use `fact.supplierpayments` or `dim.paymentterms` | Tables don't exist | Use `fact.accountspayable` + `fact.paymentpredictor`. Payment terms: `dim.customer.`Payment Terms`` and `dim.supplier.`Payment Terms`` (STRING codes) |
| Reference AR `Aging Bucket` or `Open Amount` | Columns don't exist | Compute ageing from `Due Date` (STRING) via `DATEDIFF(CURRENT_DATE(), TO_DATE(due_date, 'yyyyMMdd'))`. Use `AUD Amount` for balances |
| Reference AP ageing columns | No pre-computed ageing on AP | Same computed DATEDIFF pattern. AP dates (`Due Date`, `Invoice Date`) are STRING YYYYMMDD |
| Display `Fiscal Year Label` as "FY25" | Actual format is "2024-2025" | Use `Fiscal Year Label` for display; `Fiscal Year` (INT) for filtering |
| Filter GL with `Division = '100'` (string code) | Zero rows — GL uses integer surrogate `Division Key` | JOIN `dim.division` on `Division Key`, filter on `Division Code`, or use verified surrogate key |
| Use `On Hand Qty` on itembalance | Column is `On Hand` (no Qty suffix) | `` `On Hand` `` for quantity, `` `OnHand Value` `` for value |
| Use `LAST_DAY()` on inventoryhistory dates | Returns weekend/holiday with no snapshot row | `MAX(`Record Date`)` per year/month partition |
| Join dim.supersessions without aggregation | Fan-out: one-to-many produces duplicate product rows | CTE: `FIRST(replacement) + COUNT(*)` per superseded product |
| Assume PO has Exchange Rate column | Column doesn't exist on purchaseorders | FX via `dim.currency` join on `Currency Key` (compound format: "USD100") |
| Use `'MCS'` for `Product Business Unit` filter | Silent miss — actual value is `'Madison Connectivity Solutions'` | Use full string or CASE WHEN mapping |
| Assume inventoryhistory needs warehouse join for division | Unnecessary complexity | Table has own `Division` column (STRING) — filter directly |
