# Schema Inventory — Madison Data Warehouse

> Plugin v3.3.0. Source: schema audit TASK-002 through TASK-006.
> Column names are from `datawarehouse.*` views (space-separated, backtick-quoted).
> The underlying `gold.*` tables use PascalCase — do not mix conventions.
> Load this file on demand — core tables and query rules are in context.md.

---

## 1. Table Inventory

### Dimensions (20 tables)

| Table | Rows | Purpose |
|-------|------|---------|
| `dim.account` | 530 | GL account chart (GROUP by first digit: 1=Assets, 2=Liabilities, 3=Equity, 4=Revenue, 5+=Expenses) |
| `dim.brand` | ~600 | Brand master. Key for rebate analysis: `Brand Key`, `Brand`, `Rebate Brand Group`, `Brand Group`. Note: agreement brand groups (JBL, AKG, etc.) don't map 1:1 to `Rebate Brand Group` — see IS-3706 for mapping |
| `dim.calendar` | 3,471 | Date dimension 2017-07-01 to 2026-12-31. FY July start. Key: `Date Key` (INT YYYYMMDD) |
| `dim.case` | 5,741 | SF case records (support tickets) |
| `dim.costcentre` | 72 | Cost centre lookup. 72% of GL entries have -1 (no cost centre) — by design |
| `dim.currency` | 29 | ISO currency reference. `Currency Key` (STRING ISO code), `Currency Name`. Used by fact.currencyhistory for FX rates. AUD is base |
| `dim.customer` | ~10K | Customer master (M3+SF merged). Key fields: `Customer Key` (LONG), `Customer Code`, `Customer Name`, `Payment Terms`, `Delivery Terms`, `Credit Limit1`/`2`/`3`, `Customer Stop`, `Wholesale Group`, `Wholesale Branch`, `City`, `State`, `Country`, `Postcode`, `Account Owner`, `Business Unit`, `Is Active` |
| `dim.customerpo` | 295,064 | Customer PO cross-reference (denormalised, large) |
| `dim.division` | 10 | Legal entities. Codes 100-560 + 999 (dummy) |
| `dim.employee` | 349 | Salespeople. `Employee Key` (LONG), `Business Unit` (TRIM required — "MT " trailing space) |
| `dim.itemsupplier` | 36,445 | Item-supplier assignment |
| `dim.location` | 2,107 | Warehouse bin locations |
| ~~`dim.paymentterms`~~ | — | **Does not exist.** Payment terms are STRING fields on `dim.customer` and `dim.supplier` |
| `dim.pricelist` | 104,771 | Customer price list (large, denormalised) |
| `dim.product` | 72,479 | Product master (M3+SF merged). `Product Key` (LONG), `Product Number`, `Business Unit` (47% Unknown) |
| `dim.sfaccount` | 18,758 | Raw SF accounts (many without M3 match) |
| `dim.supersessions` | ~2.5K | Product replacement bridge. `Product Key` (new) <-> `Superseded Key` (old). Only reliable mechanism |
| `dim.supplier` | ~2K | Supplier master. Key fields: `Supplier Key` (BIGINT), `Supplier Code`, `Supplier Name`, `Supplier Country`, `Supplier Division`, `Supplier Status`, `Payment Terms`, `Delivery Terms`, `Is Active` |
| `dim.supplierpricelist` | 153,891 | Supplier price list (large, denormalised) |
| `dim.warehouse` | 51 | Warehouse/facility reference. Columns: `Warehouse Key`, `Warehouse`, `Warehouse Description`, `Division` (STRING — maps warehouse to division code), `Is Active`. 27 active across 6 divisions |

### Facts (39 tables)

| Table | Rows | Purpose | Date Range |
|-------|------|---------|-----------|
| `fact.accountspayable` | 54,768 | AP open items | 2024-05-01+ |
| `fact.accountsreceivable` | 41,498 | AR open items (positive only) | 2024-05-01+ |
| `fact.allocations` | 94,662 | Stock allocation to orders | Current snapshot |
| `fact.budget` | 269,613 | Budget data (full history) | 2018+ |
| `fact.case` | 5,741 | SF support cases | 2020+ |
| `fact.cashflow` | 16,654 | Net cash position by week/div/currency | Rolling forecast |
| `fact.codeliveries` | 0 | **Empty — broken ETL** | N/A |
| `fact.creditnotes` | 83,929 | Credit notes issued | 2017+ |
| `fact.currencyhistory` | 6,497 | FX rate history. DateKey is STRING (needs CAST for calendar join) | 2017+ |
| `fact.deliverynotes` | 1,154,389 | Delivery/receipt notes | 2017+ |
| `fact.distributionorders` | 7,143 | Internal warehouse transfers | Current |
| `fact.forecasts` | 36,637 | Demand forecasts | Rolling |
| `fact.generalledger` | 1,978,427 | GL entries | **2024-05-01+ only** |
| `fact.goodsreceipts` | 6,556 | PO receipts | Recent |
| `fact.historicaldemand` | 1,109,760 | Historical demand by item/warehouse | 2017+ |
| `fact.inventoryhistory` | 3,433,127 | Inventory snapshots (historical) | 2022+ |
| `fact.inventoryhistorybymonth` | 565,627 | Monthly inventory aggregation | 2022+ |
| `fact.inventoryprojection` | 5,095,600 | **Disabled — complex, performance issues** | N/A |
| `fact.invoices` | 1,661,403 | Revenue, margin, rebates (core) | 2017+ (includes legacy ERP backfill) |
| `fact.itembalance` | 19,524 | Stock on hand (bin-level) | Current snapshot |
| `fact.itemfacility` | 38,761 | Facility-level cost/valuation | Current snapshot |
| `fact.itemwarehouse` | 372,326 | Inventory health (ageing, turnover, pareto) | Current snapshot |
| `fact.opportunities` | 27,523 | SF opportunities | 2017+ |
| `fact.opportunitylineitem` | 61,414 | SF opp line items (54.6% NULL Product Key) | 2017+ |
| `fact.paymentpredictor` | ~1K | Cash flow lifecycle projection (rolling snapshot — 5 lifecycle buckets from PO to AP unpaid) | Rolling |
| `fact.pickslips` | 502,779 | Warehouse pick operations | 2020+ |
| `fact.preallocations` | 20,193 | Reserved against incoming supply | Current |
| `fact.purchaseorders` | 379,367 | Inbound supply (POs + DOs) | 2017+ |
| `fact.quote` | 45,474 | SF quotes. **Breaks medallion:** joins datawarehouse.dim.product | 2020+ |
| `fact.quotedmargin` | 385,671 | Quote vs invoice margin comparison | 2020+ |
| `fact.receiptpredictor` | 47,048 | Cash-in forecast (AR + open SOs). Gold-to-gold dependency | Rolling |
| `fact.salesorders` | 1,021,233 | Orders, pipeline, fulfilment (core) | 2017+ (includes legacy ERP backfill) |
| `fact.salestargets` | 6,455 | Sales targets by employee/month | 2023+ |
| `fact.stocktransactions` | 890,237 | Stock movements (receipts, issues, adjustments) | 2017+ |
| ~~`fact.supplierpayments`~~ | — | **Does not exist.** Use `fact.accountspayable` for supplier payment analysis | — |
| `fact.customerpayments` | 68,195 | Payments from customers | 2024+ |
| `fact.projectiondates` | 11,367 | Projection date reference | Current |
| `fact.rebateclaims` | 2,891 | Rebate claims filed | 2024+ |
| `fact.shipments` | 189,402 | Shipment tracking | 2020+ |

---

## 2. Join Map

### M3 Core Facts -> Dimensions (CAST required)

```sql
-- Pattern: CAST(dim.Key AS STRING) for all M3 surrogate key joins
fact.invoices i
  JOIN dim.product p      ON i.`Product Key`  = CAST(p.`Product Key` AS STRING)
  JOIN dim.customer c     ON i.`Customer Key` = CAST(c.`Customer Key` AS STRING)
  JOIN dim.employee e     ON i.`Employee Key` = CAST(e.`Employee Key` AS STRING)
  JOIN dim.warehouse w    ON i.`Warehouse Key` = CAST(w.`Warehouse Key` AS STRING)
  JOIN dim.calendar cal   ON i.`Invoice Date Key` = cal.`Date Key`
```

**Applies to:** invoices, salesorders, purchaseorders, deliverynotes, pickslips,
preallocations, creditnotes, quotedmargin, inventoryhistory, inventoryhistorybymonth

### GL/Budget Facts -> Dimensions (no CAST)

```sql
-- INT keys coerce implicitly to LONG
fact.generalledger gl
  JOIN dim.account a      ON gl.`Account Key` = a.`Account Key`
  JOIN dim.costcentre cc  ON gl.`Cost Centre Key` = cc.`Cost Centre Key`  -- 72% orphan rate (by design)
  JOIN dim.division d     ON gl.`Division Key` = d.`Division Key`
  JOIN dim.calendar cal   ON gl.`Accounting Date Key` = cal.`Date Key`  -- GL uses Accounting Date Key, NOT Date Key
```

### Salesforce Facts -> Dimensions (no CAST)

```sql
-- LONG = LONG, native match
fact.opportunities o
  JOIN dim.customer c     ON o.`Customer Key` = c.`Customer Key`
  JOIN dim.employee e     ON o.`Employee Key` = e.`Employee Key`
  JOIN dim.calendar cal   ON o.`Close Date Key` = cal.`Date Key`
```

**Applies to:** opportunities, opportunitylineitem, quote

### Inventory Facts -> Dimensions

```sql
-- itembalance: STRING keys, CAST required
fact.itembalance ib
  JOIN dim.product p      ON ib.`Product Key` = CAST(p.`Product Key` AS STRING)
  JOIN dim.warehouse w    ON ib.`Warehouse Key` = CAST(w.`Warehouse Key` AS STRING)
  JOIN dim.location l     ON ib.`Location Key` = CAST(l.`Location Key` AS STRING)

-- itemwarehouse: STRING keys, CAST required
fact.itemwarehouse iw
  JOIN dim.product p      ON iw.`Product Key` = CAST(p.`Product Key` AS STRING)
  JOIN dim.warehouse w    ON iw.`Warehouse Key` = CAST(w.`Warehouse Key` AS STRING)
```

---

## 3. Enum Registry (Verified Values)

### dim.employee.`Business Unit`
Valid: `MAV`, `MT`, `MEX`, `MCS`, `KPR`, `Other`, `Unknown`
Invalid/system: `ZZZ`, `0`, `Slobs`, `MCT`, `MGE`, `KLL`, `COP`, `MNZ`
**Critical:** `MT ` (with trailing space) exists on 14 employees. Always `TRIM()`.

### dim.product.`Business Unit`
Values: `<Unknown>` (34K, 47%), `MadisonAV`, `Madison Technologies`, `Madison Express`,
`Kallipr Pty Ltd`, `MCS` (3 variants), `KPR` (2 variants), `BLANK` (literal string)
**Unreliable for precise BU filtering** — use employee BU for revenue attribution.

### dim.customer.`Business Unit`
Values: `NULL` (54%), `MAV`, `MEX`, `MT`, `MCS`, `OTHER`, `UnMapped`
**Majority NULL.** Not suitable as primary attribution.

### dim.customer.`State`
Truncated non-standard: `NS` (not NSW), `VI` (not VIC), `QL` (not QLD), `WA`, `SA`, `TA`, `NT`, `AC`, `OT`, `ON`
`NZ` is country not state. 32% empty.

### dim.calendar.`Fiscal Year`
Type: INT. Values: 2017-2026. (NOT string "FY25" — that's `Fiscal Year Label`)

### dim.division
10 rows: 100/MAV, 200/MT, 300/TPM, 400/KPR, 500/MGE, 505/MEX, 520/MEX, 550/MCS, 560/MNZ, 999/ZZZ

### dim.currency.`Currency Key`
29 ISO codes: AUD, USD, EUR, NZD, GBP, SGD, JPY, HKD, CNY, THB, MYR, IDR, PHP, TWD, KRW, INR, VND, FJD, PGK, WST, TOP, SBD, VUV, XPF, CHF, SEK, DKK, NOK, CAD

---

## 4. Key Derivations

### 4a. Order Status (fact.salesorders — 16 levels)
Priority-ordered CASE expression:
1. Shortage (01) -> 2. Awaiting PO (02) -> 3. Awaiting DO (03) -> 4. PO/DO Pending (04)
5. Ready to Pick (05) -> 6. Part Picked (06) -> 7. Fully Picked (07)
8. Part Packed (08) -> 9. Fully Packed (09) -> 10. Awaiting Dispatch (11)
11. Part Delivered (10) -> 12. Delivered (12)
13. Part Invoiced (13) -> 14. Invoiced (15)
15. Cancelled (99)

Statuses 01-04 = supply-constrained. 05-11 = warehouse operations. 12-15 = finance.

### 4b. Product Supersession CTE Pattern

```sql
WITH product_family AS (
  SELECT p.`Product Key`, p.`Product Number`, p.`Product Name`,
         'Current' as product_role
  FROM datawarehouse.dim.product p
  WHERE p.`Product Number` = '{product_number}'

  UNION ALL

  SELECT p_old.`Product Key`, p_old.`Product Number`, p_old.`Product Name`,
         'Superseded' as product_role
  FROM datawarehouse.dim.supersessions s
  JOIN datawarehouse.dim.product p_old ON s.`Superseded Key` = p_old.`Product Key`
  JOIN datawarehouse.dim.product p_curr ON s.`Product Key` = p_curr.`Product Key`
  WHERE p_curr.`Product Number` = '{product_number}'
)
SELECT pf.product_role, pf.`Product Number`, ...
FROM product_family pf
JOIN datawarehouse.fact.invoices i ON CAST(pf.`Product Key` AS STRING) = i.`Product Key`
...
```

Note: fact.invoices stores Product Key as STRING, dim stores as LONG.
When joining FROM dim TO fact: `CAST(pf.`Product Key` AS STRING) = i.`Product Key``

### 4c. Inventory Valuation
```
UnitCost = CASE M9VAMT
  WHEN 0 THEN 0 (no valuation)
  WHEN 1 THEN standard cost (UCOS bucket 6)
  WHEN 4 THEN weighted average cost (9 MCKOST buckets)
  ELSE appraised value
END
OnHand Value = On Hand Qty x UnitCost
```
WAC = sum(qty x cost_bucket) / sum(qty) across 9 MCKOST buckets at facility level.

### 4d. Allocation Chain
```
Ordered - Allocated - Supply = Unfulfilled (shortage)
Supply = PreAllocated + PO qty + DO qty
Pipeline Original Currency = outstanding unallocated value
```
