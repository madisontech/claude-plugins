# BI Assistant Plugin

**Name:** bi-assistant
**Version:** 1.0.0
**Description:** Business Intelligence analysis for Madison Group Enterprises. Provides
datawarehouse query rules, SQL patterns, scope discipline, business context (fiscal calendar,
divisions, attribution), and reporting conventions.

## Setup

This is a Claude Code native plugin. To install:

1. Copy `plugins/bi-assistant/` into your project
2. Enable the plugin: `claude --plugin-dir ./plugins/bi-assistant` (or add to project settings)
3. Set the required environment variables (see `.env.example`):
   - `DATABRICKS_MCP_ENDPOINT` — your Databricks MCP endpoint URL
   - `DATABRICKS_TOKEN` — your Databricks personal access token
4. Restart Claude Code. The `databricks-sql` MCP server loads automatically.

## MCP Servers (auto-loaded)

| Server | Transport | Purpose |
|--------|-----------|---------|
| `databricks-sql` | HTTP | Datawarehouse queries via DBSQL |

Servers are defined in `.mcp.json` at the plugin root and loaded automatically by Claude Code
when the plugin is enabled. No manual `.mcp.json` editing required.

## Methodology Files

| File | Load When |
|------|-----------|
| `datawarehouse-analysis.md` | Starting any datawarehouse query work |
| `databricks-etl-troubleshooting.md` | Debugging data pipeline or transformation issues |
| `mge-report-formatter.md` | Building Excel/Word deliverables for MGE stakeholders |
| `dashboard-conventions.md` | Creating or modifying Power BI dashboards |
| `analysis-standards.md` | Reviewing or writing analysis methodology |
| `data-quality-checks.md` | Running QA procedures on data |
| `jedox-reporting.md` | Working with Jedox OLAP cubes or PALO formulas |

## Confluence References

Detailed documentation available via Atlassian REST API (not loaded by default):

| Document | Page ID |
|----------|---------|
| Madison BI Guide | 490438657 |
| Measures Reference | 490340372 |
| Schema Reference | 490471425 |
