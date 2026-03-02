# Madison BI Assistant — Context

> Loaded at boot. Every rule here is verified against the live datawarehouse as of 2026-03-03.
> Detailed per-table reference: `skills/initiate/references/schema-reference.md`

## Source of Truth

**Always query:** `datawarehouse.fact.*` and `datawarehouse.dim.*`
**Never query:** `fact.*`, `dim.*`, `*_silver.*`, `*_bronze.*` (intermediate layers)

59 live tables: 20 dimensions, 39 facts. Full inventory in schema-reference.md.

## SQL Rules (Critical — Queries Fail Without These)

### Column Names
All columns use **Pascal Case with backtick quoting**: `` `Invoice Date Key` ``, `` `Product Key` ``,
`` `Business Unit` ``. Never snake_case. Every column reference must be backtick-quoted.

### Join Casting by Source System

| Source System | Fact Key Type | Dim Key Type | Rule |
|--------------|--------------|-------------|------|
| **M3 Core** (invoices, salesorders, purchaseorders, deliverynotes, pickslips, preallocations, creditnotes, quotedmargin) | STRING | LONG | `CAST(dim.Key AS STRING)` |
| **M3 Inventory** (inventoryhistory, inventoryhistorybymonth, inventoryprojection) | STRING | LONG | `CAST(dim.Key AS STRING)` |
| **GL/Budget** (generalledger, budget) | INT | LONG | No cast needed (implicit coercion) |
| **Salesforce** (opportunities, opportunitylineitem, quote) | LONG | LONG | No cast needed |
| **Other** (historicaldemand) | STRING | STRING | No cast needed |

**If a join returns zero rows, check the CAST first.** M3 facts store surrogate keys as STRING;
dimensions store them as LONG. Omitting the CAST silently returns empty results.

### Sentinel Values
Every fact-to-dim lookup wraps in `COALESCE(..., -1)`. No dimension has a -1 row.
- **INNER JOIN** silently drops unmatched records (invoices: 3,973 customer orphans; GL: 1.4M cost centre orphans)
- **LEFT JOIN** preserves them — use LEFT JOIN by default, filter -1 only when deliberate

### Date Keys
Format: INT `YYYYMMDD` (e.g., `20260303`). Join to `dim.calendar.`Date Key``.
Exception: `invoices.`Invoice Date Key`` is DECIMAL — still joins correctly but has 187 NULLs.

### SQL Style
- CTEs over subqueries; one clause per line; trailing commas
- Comments explain WHY, not WHAT: `-- Exclude test accounts per DEC-003`
- Test with LIMIT before running full queries on large tables
- Use APPROX_COUNT_DISTINCT for dashboard-level counts

## Scope Discipline

Before any query, state explicitly:

```
Division:      [100 = MAV | 200 = MT | 505/520 = MEX | 550 = MCS | all]
Business Unit: [MAV | MT | MEX | MCS | KPR | all] — specify attribution path
Time Period:   [FY__ or date range YYYYMMDD–YYYYMMDD]
Filters:       [any additional constraints]
```

Never change scope without the analyst's approval.

## Business Context

### Fiscal Calendar
July–June fiscal year. `Fiscal Year` is INT (2025, not "FY25"). `Fiscal Year Label` = "FY25".
```
FiscalYear  = YEAR(add_months(date, -6))    -- FY25 = Jul 2024 – Jun 2025
FiscalMonth = MONTH(add_months(date, -6))   -- 1=July, 12=June
```

### Division = Legal Entity

| Code | Entity | Abbrev |
|------|--------|--------|
| 100 | MadisonAV Pty Ltd | MAV |
| 200 | Madison Technologies (Australia) | MT |
| 300 | Total Product Marketing | TPM |
| 400 | Kallipr Pty Ltd | KPR |
| 500 | Madison Group Enterprises | MGE |
| 505 | Madison Express Holdings | MEX |
| 520 | Madison Express | MEX |
| 550 | Madison Connectivity Solutions | MCS |
| 560 | Madison NZ Ltd | MNZ |
| 999 | Dummy Division | ZZZ — always exclude |

### Dual Attribution Model

Revenue can be attributed three ways — they often disagree:

| Path | Join | Source | Coverage |
|------|------|--------|----------|
| **Employee BU** (revenue) | fact -> `Employee Key` -> dim.employee.`Business Unit` | CSYTAB SMCD (first 3 chars) | Good. Values: MAV, MT, MEX, MCS, KPR. **Warning:** "MT " has trailing space on 14 employees ($131M exposure) — always TRIM |
| **Product BU** (operations) | fact -> `Product Key` -> dim.product.`Business Unit` | CSYTAB CFI3 description | **47% `<Unknown>`**. Name-based: "MadisonAV", "Madison Technologies", "Madison Express". 3 MCS variants, 2 KPR variants |
| **Customer BU** | dim.customer.`Business Unit` | SF Account Owner department | **54% NULL**. Unreliable for primary attribution |

Default: Employee BU for revenue, Product BU for inventory/operations. Always state which.

### Revenue Composition (Invoice Anatomy)

```
InvoiceValue  = qty x unit price              (OINVOL type '31')
+ HeaderCharge = header-level charges           (type '60')
+ LineCharge   = line-level charges             (type '67')
= TotalValue   (revenue recognised)

TotalCost     = standard cost - supplier rebate + COGS charge
Margin        = TotalValue - TotalCost - RebateAmount
```

**Margin includes rebate deductions.** The 4-tier rebate waterfall:
1. Exclusive brand rebate (customer-brand-specific)
2. Non-exclusive brand rebate (brand-level)
3. Wholesale group accrual rate
4. Rebate member accrual rate
Plus: +5% FREDON surcharge, +4% MI Retail surcharge (conditional)

Querying `TotalValue - TotalCost` without `RebateAmount` **overstates margin**.

### FX Conversion
`LocalAmount = ForeignAmount / ExchangeRate` — **division, not multiplication.**
Rate = foreign currency units per 1 AUD.

## Universal Exclusions

Apply to every M3-sourced query:
- `WHERE CONO = 100` — company filter (always)
- `AND deleted = FALSE` — soft-delete from M3 replication
- Division 999 excluded from invoices (`Division <> '999'`)
- Credit card surcharges excluded (`Product NOT LIKE 'MCC%' AND NOT LIKE 'KCC%'`)
- Valid salesperson: code contains hyphen (`LIKE '%-%'`)

## Data Boundaries and Coverage Gaps

| Constraint | Impact |
|-----------|--------|
| **GL/AR/AP: post-2024-05-01 only** | `generalledger WHERE EGACDT > 20240430`, same for AR/AP. No historical financials before May 2024 |
| **AR: positive amounts only** | Credit notes excluded (`ESCUAM > 0`) |
| **Calendar range: 2017-07-01 to 2026-12-31** | Date keys outside this range won't join to calendar |
| **Customer BU: 54% NULL** | Majority of customers have no BU via SF Account Owner path |
| **Product BU: 47% Unknown** | `<Unknown>` is the most common value in dim.product.`Business Unit` |
| **Opportunity Product Key: 54.6% NULL** | SF opportunity line items often missing product link |
| **Customer State: truncated** | NS not NSW, VI not VIC, QL not QLD. 32% empty. NZ is country not state |
| **Legacy ERP backfill** | fact.invoices and fact.salesorders contain backfilled data from pre-M3. Pattern breaks near migration date may be system artefact, not business shift |

## Product Supersession

`dim.supersessions` is the **only reliable** supersession mechanism (2,505 rows).
`dim.product.`Superseded By`` is structurally broken (always NULL). Do not use it.

When analysing product performance where continuity matters, use the supersession CTE pattern
documented in schema-reference.md section 4c. Always ask whether the user wants to include
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
| `fact.accountsreceivable` | AR open items (post May 2024) | Customer, Currency, Calendar |
| `fact.salestargets` | Sales targets by employee/month | Employee, Calendar |

### Core Dimensions
| Table | Purpose | Key Fields |
|-------|---------|------------|
| `dim.product` | Product master (M3+SF merged) | `Product Key`, `Product Number`, `Business Unit` |
| `dim.customer` | Customer master (M3+SF merged) | `Customer Key`, `Customer Code`, `Customer Name` |
| `dim.employee` | Salespeople + BU attribution | `Employee Key`, `Business Unit` (TRIM!) |
| `dim.calendar` | Date dimension (FY Jul start) | `Date Key`, `Fiscal Year`, `Fiscal Year Label` |
| `dim.warehouse` | Warehouse/facility reference | `Warehouse Key`, `Warehouse` |
| `dim.supersessions` | Product replacement links | `Product Key` (new), `Superseded Key` (old) |

## Reporting Standards

When producing formatted deliverables, reference `skills/initiate/references/mge-report-formatter.md` for
brand standards: Connect Grey `#3F5364`, Accent Red `#CF152D`, Arial font, A4 layout,
Australian number conventions.
