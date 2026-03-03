# Madison BI Assistant

**Version:** 3.0.0-trial
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
| `CLAUDE.md` | Plugin identity, disposition, communication style, quality gates |
| `context.md` | Canonical SQL rules, join casting, exclusions, business context, 14 core tables |

## Skills

### `/query` — Descriptive Analysis
"What is X?", breakdowns, comparisons, reporting.
Loads: CLAUDE.md + context.md + query-patterns.md (~9k tokens).
Output: chat table with key findings.

### `/investigate` — Discrepancy Debugging
"Why is X different?", data quality issues, ETL tracing.
Loads: CLAUDE.md + context.md + query-patterns.md + investigation.md (~12k tokens).
Output: investigation narrative with root cause analysis.

### `/analyse` — Advanced Analytics
Forecasting, segmentation, statistical patterns, hypothesis testing.
Loads: CLAUDE.md + context.md + query-patterns.md + advanced-analytics.md (~10k tokens).
Output: Python analysis with files in scratch/.

### `/format` — Branded Deliverables
XLSX, DOCX, PPTX production with MGE brand standards.
Loads: CLAUDE.md + context.md + output-standards.md (~15k tokens with query).
Output: branded file in deliverables/. Default: XLSX. Works standalone or as post-processing.

### `/initiate` — Catch-All Router
Any question that doesn't obviously map to a specific skill.
Loads: CLAUDE.md + context.md + query-patterns.md, then additional refs after routing.
Output: depends on mode selected.

## Shared References (on-demand)

| File | Purpose | Loaded By |
|------|---------|-----------|
| `references/query-patterns.md` | Verified SQL templates | query, investigate, analyse, initiate |
| `references/schema-inventory.md` | Full 59-table inventory (on demand) | Any skill when needed |
| `references/investigation.md` | ETL tracing, medallion architecture | investigate, initiate |
| `references/advanced-analytics.md` | Statistical methods, Python patterns | analyse, initiate |
| `references/output-standards.md` | Brand identity, chart rules, XLSX/DOCX/PPTX layout | format, initiate |

## File Manifest

```
plugins/madison-bi-assistant/
├── .claude-plugin/plugin.json          # Native plugin manifest (v3.0.0-trial)
├── .mcp.json                           # MCP server config (Databricks SQL)
├── plugin.md                           # This file — setup guide, skill index
├── CLAUDE.md                           # Plugin identity, disposition, quality gates
├── context.md                          # Canonical SQL rules, business context, 14 core tables
├── references/
│   ├── query-patterns.md               # Verified SQL templates
│   ├── schema-inventory.md             # Full 59-table inventory (on demand)
│   ├── investigation.md                # ETL tracing, medallion architecture, control table
│   ├── advanced-analytics.md           # Statistical methods, Python patterns
│   └── output-standards.md             # Brand identity, chart rules, deliverable layout
└── skills/
    ├── query/SKILL.md                  # Descriptive analysis
    ├── investigate/SKILL.md            # Discrepancy debugging
    ├── analyse/SKILL.md                # Advanced analytics
    ├── format/SKILL.md                 # Branded deliverable production
    └── initiate/SKILL.md               # Catch-all router
```
