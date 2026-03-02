# BI Assistant Plugin

**Name:** bi-assistant
**Version:** 1.1.0
**Description:** Business Intelligence analysis for Madison Group Enterprises. Provides
datawarehouse query rules, SQL patterns, scope discipline, business context (fiscal calendar,
divisions, attribution), and reporting conventions.

## Setup

Install from the madison-tools marketplace:

```
/plugin marketplace add madisontech/claude-plugins
/plugin install bi-assistant@madison-tools
```

Then create `.mcp.json` from `.mcp.json.example` with your Databricks credentials:
- `DATABRICKS_MCP_ENDPOINT` — your Databricks MCP endpoint URL
- `DATABRICKS_TOKEN` — your Databricks personal access token

Restart Claude Code. The `databricks-sql` MCP server loads automatically.

## MCP Servers (auto-loaded)

| Server | Transport | Purpose |
|--------|-----------|---------|
| `databricks-sql` | HTTP | Datawarehouse queries via DBSQL |

## Always-Loaded Context

These files are loaded when the plugin is enabled:

| File | Purpose |
|------|---------|
| `context.md` | Core data rules, business context, key tables, query patterns |
| `references/analysis-standards.md` | SQL style conventions, output standards |
| `references/data-quality-checks.md` | Pre-analysis and pre-delivery QA checklists |
| `references/dashboard-conventions.md` | Visual output and dashboard layout standards |
| `references/mge-report-formatter.md` | Brand colours, typography, document formatting |

## Skills (on-demand)

| Skill | Command | Use When |
|-------|---------|----------|
| Analyse | `/bi-assistant:analyse` | Querying datawarehouse — revenue, margin, inventory, AR, pipeline |
| Troubleshoot ETL | `/bi-assistant:troubleshoot-etl` | Debugging data discrepancies between Power BI and Databricks |
| Jedox | `/bi-assistant:jedox` | Working with Jedox OLAP cubes, PALO formulas, dashboards, planning |

## Confluence References

Detailed documentation available via Atlassian REST API (not loaded by default):

| Document | Page ID |
|----------|---------|
| Madison BI Guide | 490438657 |
| Measures Reference | 490340372 |
| Schema Reference | 490471425 |
