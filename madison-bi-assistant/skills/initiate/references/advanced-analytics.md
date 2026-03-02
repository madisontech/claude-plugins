# Advanced Analytics Methodology

> Use when the question requires statistical analysis, forecasting, segmentation,
> what-if scenarios, or any computation beyond descriptive SQL aggregation.

## Principles

1. **File-first execution** — All analyses written as Python/SQL files before execution.
   Preserves auditability and reproducibility. Never run throwaway inline code for
   analytical outputs.

2. **Multi-stage validation** — Challenge your own findings before presenting them.
   Run sensitivity checks, sanity tests, and confidence bounds.

3. **Transparency** — Document reasoning at every step. Verbose workings, concise conclusions.

4. **Hybrid SQL + Python** — SQL for extraction and aggregation (use the lakehouse).
   Python/Polars/pandas for statistical computation, visualisation, and modelling.
   Polars preferred over pandas for performance on larger datasets.

## Workflow

```
1. FRAME    — State the analytical question as a testable hypothesis
2. ASSESS   — Check data availability, quality gates, coverage limitations
3. EXTRACT  — SQL query to pull relevant data into a working dataset
4. COMPUTE  — Python/Polars for statistical analysis, modelling, visualisation
5. VALIDATE — Challenge results: sensitivity checks, sanity tests, confidence bounds
6. INTERPRET — Translate statistical findings into business implications
7. PRESENT  — Deliver with methodology notes, confidence levels, caveats
```

## Data Quality Gates (Pre-Modelling Checklist)

Before any advanced analysis, verify these coverage constraints:

| Check | Known Issue | Impact |
|-------|------------|--------|
| Employee BU null/invalid rate | "MT " trailing space (14 employees, $131M) | Always TRIM |
| Product BU coverage | 47% `<Unknown>` | Cannot segment by product BU reliably |
| Customer BU coverage | 54% NULL | Cannot use as primary attribution |
| GL/AR/AP date range | Post-May-2024 only (~2 years) | Insufficient for long time series |
| Calendar range | 2017-07-01 to 2026-12-31 | Legacy dates outside range won't join |
| Opportunity Product Key | 54.6% NULL | SF opp line items often missing product link |
| Sentinel keys (-1) | No -1 rows in dims | INNER JOIN silently drops unknowns |
| Currency history DateKey | STRING type | Needs CAST to INT for calendar joins |
| Legacy ERP backfill | Pattern breaks near migration | May be system artefact, not business |

**If any gate fails, disclose it.** Do not proceed with analysis that would be
materially affected by a coverage gap without the analyst's informed consent.

## Analytical Techniques

| Category | Methods | When to Use |
|----------|---------|------------|
| **Descriptive** | Aggregation, segmentation, cohort analysis, funnel analysis | Understanding current/historical state |
| **Diagnostic** | Variance decomposition, root cause trees, contribution analysis, anomaly detection | Explaining why metrics moved |
| **Predictive** | Time series forecasting (Prophet, ARIMA), regression, classification, survival analysis | Projecting future outcomes |
| **Prescriptive** | What-if scenarios, sensitivity analysis, optimisation, Monte Carlo simulation | Recommending actions |
| **Statistical** | Hypothesis testing, confidence intervals, correlation matrices, distribution analysis | Validating findings with rigour |

## Business Metric Formulas (Verified from ETL)

### Revenue and Margin
```
Margin = TotalValue - TotalCost - RebateAmount
```
- TotalValue = InvoiceValue + HeaderChargeValue + LineChargeValue
- RebateAmount includes 4 tiers + conditional surcharges (FREDON 5%, MI Retail 4%)
- **Do not compute margin as TotalValue - TotalCost** — this overstates by the rebate amount

### Weighted Average Cost
```
WAC = sum(qty x cost_bucket) / sum(qty) across 9 MCKOST buckets
```
At facility level (`fact.itemfacility`). Depends on M9VAMT valuation method.

### FX Conversion
```
LocalAmount = ForeignAmount / ExchangeRate
```
Rate = foreign currency per 1 AUD. **Division, not multiplication.**

### Inventory Turns
```
Turns = Cost of Goods Sold / Average Inventory Value
```
COGS from fact.invoices (`TotalCost`), inventory from fact.itembalance (`OnHand Value`).

### Days Sales Outstanding
```
DSO = (AR Balance / Revenue) x Days in Period
```
AR from fact.accountsreceivable (post-May-2024 only). Revenue from fact.invoices.

## Python Environment

- Windows venv: `C:\Users\jamesf\AppData\Local\Claude\Claude`
- Packages: pandas, numpy, polars (preferred), sqlalchemy, databricks-sql-connector, openpyxl
- For Databricks direct: use `databricks-sql-connector` with `.env` credentials
- Output to: `scratch/analysis/` (working) or `deliverables/` (final)

## File Output Standards

| Output Type | Write To | Chat Contains |
|-------------|----------|---------------|
| SQL extraction queries | `scratch/queries/*.sql` | Path + 1-line purpose |
| Working datasets | `scratch/analysis/*.csv` | Path + shape + key stats |
| Analysis scripts | `scratch/scripts/*.py` | Path + what it does |
| Visualisations | `scratch/analysis/*.png` | Path + key finding |
| Final deliverables | `deliverables/*` | Path + summary |

## Validation Checklist

Before presenting advanced analytical results:

- [ ] Sample size sufficient for the method used
- [ ] Confidence intervals or uncertainty ranges provided
- [ ] Results robust to reasonable parameter changes (sensitivity test)
- [ ] Business interpretation makes intuitive sense (sanity check)
- [ ] Data quality limitations disclosed
- [ ] Methodology documented in the output file
- [ ] At least one control figure cross-referenced against known truth
- [ ] Premortem: "What would make this finding wrong?"
