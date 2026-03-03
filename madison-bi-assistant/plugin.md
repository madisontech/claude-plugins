# Madison BI Assistant

**Version:** 2.3.0
**Plugin directory:** `plugins/madison-bi-assistant/`

## Setup

### MCP Servers (enabled on demand)

**Databricks SQL** — HTTP transport to Databricks SQL endpoint.
Configure in `.mcp.json` with your workspace URL and auth token:

```json
{
  "mcpServers": {
    "databricks-sql": {
      "type": "http",
      "url": "https://<workspace>.azuredatabricks.net/api/2.0/mcp/sql",
      "headers": {
        "Authorization": "Bearer <token>"
      }
    }
  }
}
```

Tools: `execute_sql_read_only` (all analysis), `execute_sql` (DDL/DML, rare),
`poll_sql_result` (long-running queries).

**Power BI Modeling** — via `powerbi-modeling-mcp`. Connect to local PBI Desktop
or Fabric XMLA endpoints. Use `connection_operations` -> `ListLocalInstances` -> `Connect`.

## Always-Loaded Context (boot)

| File | Purpose |
|------|---------|
| `soul.md` | Analyst disposition, communication style, quality gates |
| `context.md` | Data rules, SQL conventions, business context, table quick reference |

## Skill

### `/initiate` — Unified Analysis Skill

One entry point. The model self-routes based on question type:

| Mode | Trigger | Workflow |
|------|---------|---------|
| **Descriptive** | "What is X?", breakdowns, comparisons | scope -> query -> present -> drill-down |
| **Investigation** | "Why is X different?", discrepancies | observe -> hypothesise -> trace -> confirm |
| **Advanced Analytics** | "What would happen if?", forecasting | frame -> assess -> extract -> compute -> validate -> interpret |

**Skill references:**
- `schema-reference.md` — Definitive table/join/enum/derivation reference (59 tables)
- `datawarehouse-analysis.md` — Verified query patterns
- `investigation-methodology.md` — ETL tracing, discrepancy debugging
- `advanced-analytics.md` — Statistical methods, Python/Polars patterns
- `databricks-etl-troubleshooting.md` — Medallion architecture, control table
- `dashboard-conventions.md` — Chart selection, data presentation, visual output standards
- `mge-report-formatter.md` — Brand identity, colour palette, typography, layout, Python constants

## File Manifest

```
plugins/madison-bi-assistant/
├── .claude-plugin/plugin.json          # Native plugin manifest (v2.3.0)
├── .mcp.json                           # MCP server config (Databricks SQL)
├── plugin.md                           # This file
├── soul.md                             # Analyst disposition and quality gates
├── context.md                          # Data rules, SQL conventions, business context
└── skills/
    └── initiate/
        ├── SKILL.md                    # Unified skill: mode routing + 3 workflows
        └── references/
            ├── schema-reference.md     # Definitive table/join/enum reference
            ├── datawarehouse-analysis.md  # Verified query patterns
            ├── investigation-methodology.md  # ETL tracing, discrepancy debugging
            ├── advanced-analytics.md   # Statistical methods, Python patterns
            ├── databricks-etl-troubleshooting.md  # Medallion architecture
            ├── dashboard-conventions.md  # Chart and dashboard output standards
            └── mge-report-formatter.md # Brand identity for deliverables
```
