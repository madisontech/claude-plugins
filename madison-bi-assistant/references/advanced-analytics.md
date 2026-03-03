# Advanced Analytics Methodology

> Use when the question requires statistical analysis, forecasting, segmentation,
> what-if scenarios, or any computation beyond descriptive SQL aggregation.
> Query rules and data boundaries are in context.md. Do not restate them here.

## Principles

1. **File-first execution** — All analyses written as Python/SQL files before execution.
   Preserves auditability and reproducibility. Never run throwaway inline code.
2. **Multi-stage validation** — Challenge your own findings before presenting them.
3. **Transparency** — Document reasoning at every step. Verbose workings, concise conclusions.
4. **Hybrid SQL + Python** — SQL for extraction and aggregation (use the lakehouse).
   Python/Polars/pandas for statistical computation, visualisation, and modelling.
   Polars preferred over pandas for performance on larger datasets.

## Workflow

```
1. FRAME    — State the analytical question as a testable hypothesis
2. ASSESS   — Check data availability and coverage (see context.md Data Boundaries)
3. EXTRACT  — SQL query to pull relevant data into a working dataset
4. COMPUTE  — Python/Polars for statistical analysis, modelling, visualisation
5. VALIDATE — Challenge results: sensitivity checks, sanity tests, confidence bounds
6. INTERPRET — Translate statistical findings into business implications
7. PRESENT  — Deliver with methodology notes, confidence levels, caveats
```

## Analytical Techniques

| Category | Methods | When to Use |
|----------|---------|------------|
| **Descriptive** | Aggregation, segmentation, cohort analysis, funnel analysis | Understanding current/historical state |
| **Diagnostic** | Variance decomposition, root cause trees, contribution analysis, anomaly detection | Explaining why metrics moved |
| **Predictive** | Time series forecasting (Prophet, ARIMA), regression, classification, survival analysis | Projecting future outcomes |
| **Prescriptive** | What-if scenarios, sensitivity analysis, optimisation, Monte Carlo simulation | Recommending actions |
| **Statistical** | Hypothesis testing, confidence intervals, correlation matrices, distribution analysis | Validating findings with rigour |

## Python Environment

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
