---
description: Analyse MGE datawarehouse data — revenue, margin, inventory, AR, pipeline. Loads query patterns and available views.
---

You are performing datawarehouse analysis for Madison Group Enterprises.

Before writing any query:
1. State the scope explicitly (division, business unit, time period, filters)
2. Describe your query approach
3. Use the correct attribution model (employee BU for revenue, product BU for operations)

After results:
1. Present with context and benchmarks
2. Flag any anomalies
3. Suggest drill-downs or follow-up analyses

Read `references/datawarehouse-analysis.md` for available views and standard query patterns.

All core data rules from the plugin context apply — `datawarehouse.fact.*` and `datawarehouse.dim.*` only,
correct join casting, TRIM on Business Unit, fiscal year conventions.
