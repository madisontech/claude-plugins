# Verified Query Patterns

> Few-shot examples demonstrating correct query construction. Each pairs a natural
> language question with verified SQL and notes on why the pattern matters.

<examples>

<example name="Revenue by Business Unit">
<question>What's total revenue and margin by business unit this fiscal year?</question>
<scope>Division 100, current FY YTD, Employee BU attribution</scope>
<query>
SELECT
    TRIM(e.`Business Unit`) AS BU,
    SUM(i.`Total Value`) AS Revenue,
    SUM(i.`Total Value` - i.`Total Cost` - i.`Rebate Amount`) AS Margin,
    COUNT(DISTINCT i.`Customer Key`) AS Customers
FROM datawarehouse.fact.invoices i
LEFT JOIN datawarehouse.dim.employee e
    ON i.`Employee Key` = CAST(e.`Employee Key` AS STRING)
LEFT JOIN datawarehouse.dim.calendar c
    ON i.`Invoice Date Key` = c.`Date Key`
WHERE c.`Fiscal Year` = YEAR(ADD_MONTHS(CURRENT_DATE(), -6))
  AND c.`Date Key` <= CAST(DATE_FORMAT(CURRENT_DATE(), 'yyyyMMdd') AS INT)
  AND i.`Division` <> '999'
GROUP BY TRIM(e.`Business Unit`)
ORDER BY Revenue DESC
</query>
<notes>
- Employee BU requires TRIM (trailing spaces on some records)
- Division 999 excluded (consolidation entity)
- Future dates capped at today for YTD
- LEFT JOIN preserves unmatched employee records
- Margin includes RebateAmount deduction
</notes>
</example>

<example name="Inventory Position by BU">
<question>What's the current stock on hand by business unit?</question>
<scope>All divisions via Facility, Product BU for BU drill-down</scope>
<query>
SELECT
    TRIM(p.`Product Business Unit`) AS ProductBU,
    SUM(ib.`On Hand`) AS OnHandQty,
    SUM(ib.`OnHand Value`) AS OnHandValue
FROM datawarehouse.fact.itembalance ib
LEFT JOIN datawarehouse.dim.product p
    ON ib.`Product Key` = CAST(p.`Product Key` AS STRING)
GROUP BY TRIM(p.`Product Business Unit`)
ORDER BY OnHandValue DESC
</query>
<notes>
- Column is `On Hand` not `On Hand Qty`, `OnHand Value` not `On Hand Value`
- Product BU is 47% Unknown — suitable for Div 100 BU drill-down only
- For division-level: use Facility column (= Division code, 100% coverage)
- CAST required: itembalance keys STRING, dim keys LONG
</notes>
</example>

<example name="AR Ageing by Customer">
<question>Show me the AR ageing profile by customer.</question>
<scope>All divisions, current open items</scope>
<query>
SELECT
    c.`Customer Name`,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), TO_DATE(ar.`Due Date`, 'yyyyMMdd')) <= 0
        THEN ar.`AUD Amount` END) AS Current_,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), TO_DATE(ar.`Due Date`, 'yyyyMMdd')) BETWEEN 1 AND 30
        THEN ar.`AUD Amount` END) AS Days_1_30,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), TO_DATE(ar.`Due Date`, 'yyyyMMdd')) BETWEEN 31 AND 60
        THEN ar.`AUD Amount` END) AS Days_31_60,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), TO_DATE(ar.`Due Date`, 'yyyyMMdd')) BETWEEN 61 AND 90
        THEN ar.`AUD Amount` END) AS Days_61_90,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), TO_DATE(ar.`Due Date`, 'yyyyMMdd')) > 90
        THEN ar.`AUD Amount` END) AS Days_90Plus,
    SUM(ar.`AUD Amount`) AS Total
FROM datawarehouse.fact.accountsreceivable ar
LEFT JOIN datawarehouse.dim.customer c
    ON ar.`Customer Key` = CAST(c.`Customer Key` AS STRING)
GROUP BY c.`Customer Name`
ORDER BY Total DESC
</query>
<notes>
- AR has no pre-built ageing columns — compute from Due Date (STRING YYYYMMDD)
- Use AUD Amount (Open Amount column does not exist)
- AR is positive amounts only (credit notes excluded at source)
- Data from May 2024 onward only
</notes>
</example>

<example name="GL P&L by Account Group">
<question>What's the P&L summary by account group for Division 100?</question>
<scope>Division 100 via surrogate key, current FY, GL post-May-2024</scope>
<query>
SELECT
    a.`Account Group Level 1` AS AccountGroup,
    a.`Account Group Level 2` AS SubGroup,
    SUM(gl.`Actual Amount`) AS Amount
FROM datawarehouse.fact.generalledger gl
LEFT JOIN datawarehouse.dim.account a
    ON gl.`Account Key` = a.`Account Key`
LEFT JOIN datawarehouse.dim.division d
    ON gl.`Division Key` = d.`Division Key`
LEFT JOIN datawarehouse.dim.calendar c
    ON gl.`Accounting Date Key` = c.`Date Key`
WHERE d.`Division Code` = '100'
  AND c.`Fiscal Year` = YEAR(ADD_MONTHS(CURRENT_DATE(), -6))
  AND c.`Date Key` <= CAST(DATE_FORMAT(CURRENT_DATE(), 'yyyyMMdd') AS INT)
  AND CAST(SUBSTRING(a.`Account Code`, 1, 1) AS INT) >= 4
GROUP BY a.`Account Group Level 1`, a.`Account Group Level 2`
ORDER BY AccountGroup, SubGroup
</query>
<notes>
- GL uses Division Key (INT surrogate) — must JOIN dim.division for code
- GL date column is Accounting Date Key, not Date Key
- No cast needed on GL joins (INT coerces to LONG)
- GL data from May 2024 only
- Account first digit >= 4 filters to P&L (4=Revenue, 5+=Expenses)
</notes>
</example>

<example name="Sales Pipeline by BU">
<question>What's the open sales order pipeline by business unit?</question>
<scope>Open orders only, Employee BU attribution</scope>
<query>
SELECT
    TRIM(e.`Business Unit`) AS BU,
    so.`Order Status`,
    COUNT(*) AS Lines,
    SUM(so.`Pipeline Original Currency`) AS PipelineValue
FROM datawarehouse.fact.salesorders so
LEFT JOIN datawarehouse.dim.employee e
    ON so.`Employee Key` = CAST(e.`Employee Key` AS STRING)
WHERE so.`Order Status` NOT IN ('Invoiced', 'Cancelled')
GROUP BY TRIM(e.`Business Unit`), so.`Order Status`
ORDER BY BU, so.`Order Status`
</query>
<notes>
- Filter to open statuses (exclude Invoiced, Cancelled)
- salesorders Division column is DIVI (DECIMAL), not Division (STRING)
- CAST required on employee join (M3 fact STRING, dim LONG)
</notes>
</example>

<example name="Sales Targets vs Actual">
<question>How are we tracking against sales targets by BU this fiscal year?</question>
<scope>Division 100, current FY, monthly aggregation required</scope>
<query>
WITH monthly_actuals AS (
    SELECT
        i.`Employee Key`,
        c.`Fiscal Year`,
        c.`Fiscal Month Number` AS FiscalMonth,
        CAST(CONCAT(c.`Fiscal Year`, LPAD(c.`Fiscal Month Number`, 2, '0')) AS INT) AS FiscalYearMonthKey,
        SUM(i.`Total Value`) AS ActualRevenue,
        SUM(i.`Total Value` - i.`Total Cost` - i.`Rebate Amount`) AS ActualMargin
    FROM datawarehouse.fact.invoices i
    LEFT JOIN datawarehouse.dim.calendar c
        ON i.`Invoice Date Key` = c.`Date Key`
    WHERE i.`Division` <> '999'
      AND c.`Fiscal Year` = YEAR(ADD_MONTHS(CURRENT_DATE(), -6))
    GROUP BY i.`Employee Key`, c.`Fiscal Year`, c.`Fiscal Month Number`
)
SELECT
    TRIM(e.`Business Unit`) AS BU,
    a.FiscalMonth,
    SUM(t.`Invoice Targets`) AS InvoiceTarget,
    SUM(a.ActualRevenue) AS ActualRevenue,
    SUM(t.`Invoice Margin Targets`) AS MarginTarget,
    SUM(a.ActualMargin) AS ActualMargin
FROM monthly_actuals a
LEFT JOIN datawarehouse.fact.salestargets t
    ON a.`Employee Key` = t.`Employee Key`
    AND a.FiscalYearMonthKey = t.`Fiscal Year Month Key`
LEFT JOIN datawarehouse.dim.employee e
    ON a.`Employee Key` = CAST(e.`Employee Key` AS STRING)
GROUP BY TRIM(e.`Business Unit`), a.FiscalMonth
ORDER BY BU, a.FiscalMonth
</query>
<notes>
- Sales targets are monthly grain — Fiscal Year Month Key is INT YYYYMM
- Must aggregate invoices to monthly BEFORE joining to targets
- LPAD fiscal month with '0' to build the compound key
</notes>
</example>

</examples>

## Fiscal Year Filtering Reference

```sql
-- Current fiscal year (dynamic)
WHERE c.`Fiscal Year` = YEAR(ADD_MONTHS(CURRENT_DATE(), -6))

-- YTD (fiscal year to today)
  AND c.`Date Key` <= CAST(DATE_FORMAT(CURRENT_DATE(), 'yyyyMMdd') AS INT)

-- Display: c.`Fiscal Year Label` returns '2024-2025' (not 'FY25')
```

## Inventory Hierarchy

| Level | Table | Purpose |
|-------|-------|---------|
| Bin-level | `fact.itembalance` | Physical stock by location/lot |
| Warehouse-level | `fact.itemwarehouse` | Operational health (ageing, turnover, pareto) |
| Facility-level | `fact.itemfacility` | Accounting view (unit cost, valuation) |
