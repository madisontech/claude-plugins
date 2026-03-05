# Anti-Pattern Reference

> On-demand reference. The top 5 anti-patterns are demonstrated as few-shot examples
> in context.md. This file contains the complete catalogue for investigation/debugging.

| Anti-Pattern | Consequence | Correct Approach |
|-------------|-------------|-----------------|
| Omit CAST on M3 fact→dim joins | Zero rows silently | `CAST(dim.Key AS STRING)` |
| INNER JOIN fact to dim | Drops orphan records | LEFT JOIN, filter -1 explicitly |
| Use `dim.product.Superseded By` | Always NULL | Use `dim.supersessions` bridge table |
| Query GL/AR/AP before May 2024 | No data exists | Use fact.invoices or fact.budget for history |
| Use `Fiscal Year` as string "FY25" | Wrong type (INT 2025) | `Fiscal Year Label` for display |
| Filter employee BU without TRIM | Misses 14 employees | `TRIM(Business Unit) = 'MT'` |
| Multiply FX rate | Inverts conversion | `amount / rate` (divide) |
| Include CONO or deleted on gold/datawarehouse | Column doesn't exist | Pre-filtered — only needed at silver/bronze |
| Use `fact.aropenitems` or `fact.targets` | Tables don't exist | `fact.accountsreceivable`, `fact.salestargets` |
| Use `fact.supplierpayments` or `dim.paymentterms` | Tables don't exist | `fact.accountspayable`. Payment terms on dim.customer/dim.supplier |
| Reference AR `Aging Bucket` or `Open Amount` | Columns don't exist | Compute ageing from `Due Date` via DATEDIFF. Use `AUD Amount` |
| Reference AP ageing columns | No pre-computed ageing | Same DATEDIFF pattern. AP dates are STRING YYYYMMDD |
| Display `Fiscal Year Label` as "FY25" | Format is "2024-2025" | Use `Fiscal Year Label` for display, `Fiscal Year` (INT) for filtering |
| Filter GL with `Division = '100'` | Zero rows — GL uses `Division Key` (INT) | JOIN `dim.division`, filter `Division Code` |
| Use `On Hand Qty` on itembalance | Column is `On Hand` | `` `On Hand` `` for qty, `` `OnHand Value` `` for value |
| Use `LAST_DAY()` on inventoryhistory | Returns weekend with no snapshot | `MAX(Record Date)` per year/month partition |
| Join supersessions without aggregation | Fan-out (one-to-many) | Aggregate: first replacement + count per superseded product |
| Assume PO has Exchange Rate | Column doesn't exist | FX via `dim.currency` join on `Currency Key` (compound "USD100") |
| Use `'MCS'` for Product Business Unit | Silent miss | Actual value is `'Madison Connectivity Solutions'` |
| Assume inventoryhistory needs warehouse join for division | Unnecessary | Table has own `Division` column (STRING) |
| Omit RebateAmount from margin | Overstates margin | `Margin = TotalValue - TotalCost - RebateAmount` |
| Use `UCUCOS` for item cost | Stale unit cost | Use `UCDCOS` (delivery cost) |
| Filter salesorders with `Division` | Column is `DIVI` (DECIMAL) | `WHERE DIVI = 100` not `WHERE Division = '100'` |
| Use `Date Key` on GL | Column is `Accounting Date Key` | GL date column has different name |
