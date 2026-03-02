---
description: Debug data discrepancies between Power BI and Databricks. Traces transformation logic through the medallion architecture.
---

You are troubleshooting a data discrepancy in the MGE datawarehouse.

Workflow:
1. First verify the actual value in `datawarehouse.fact.*` or `datawarehouse.dim.*`
2. Extract the GoldIntegrationQuery from `int.maincontroltable` for the relevant table
3. Review join logic, cost allocation, and formula calculations
4. Identify which transformation step produces the discrepancy
5. **Return to datawarehouse views** for the authoritative answer — GoldIntegrationQuery is for learning/debugging only

Read `references/databricks-etl-troubleshooting.md` for the medallion architecture reference,
control table structure, and gold tables inventory.

Never report values from intermediate layers (bronze, silver, gold) as authoritative.
Always confirm final numbers against `datawarehouse.*` views.
