# Madison BI Assistant

**Version:** 3.2.0
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

### `/finance` — Finance Analysis (Router)
Budget variance, AP ageing, supplier payments, GL reconciliation. Routes to the right finance sub-domain.
Loads: CLAUDE.md + context.md + query-patterns.md + query-patterns-finance.md (~14k tokens).
Output: chat table with headline metrics, anomalies, and drill-down options.

### `/budget-variance-analysis` — Budget vs GL Actuals
Budget vs actual variance with automated decomposition by account category, cost centre, or monthly trend.
Loads: CLAUDE.md + context.md + query-patterns.md + query-patterns-finance.md (~14k tokens).
Output: material variances ranked by impact with favourable/unfavourable classification.

### `/supplier-payment-optimisation` — Supplier Payment Analysis
DPO analysis, AP ageing, term extension opportunities, cash flow projection.
Loads: CLAUDE.md + context.md + query-patterns.md + query-patterns-finance.md (~14k tokens).
Output: payment metrics, term extension candidates, cash flow pipeline.

### `/ap-ageing-analysis` — AP Ageing Analysis
Ageing profile, overdue risk, supplier concentration (Pareto), DPO trends.
Loads: CLAUDE.md + context.md + query-patterns.md + query-patterns-finance.md (~14k tokens).
Output: net balance ageing by bucket, concentration risk, trend anomalies.

### `/gl-reconciliation-support` — GL Reconciliation
GL-to-subledger reconciliation for AR and AP. Control account mapping, reconciling items.
Loads: CLAUDE.md + context.md + query-patterns.md + query-patterns-finance.md (~14k tokens).
Output: monthly comparison with material differences flagged and reconciling item categories.

### `/initiate` — Catch-All Router
Any question that doesn't obviously map to a specific skill.
Loads: CLAUDE.md + context.md + query-patterns.md, then additional refs after routing.
Output: depends on mode selected.

## Shared References (on-demand)

| File | Purpose | Loaded By |
|------|---------|-----------|
| `references/query-patterns.md` | Verified SQL templates (revenue, inventory, AR, pipeline) | query, investigate, analyse, finance, initiate |
| `references/query-patterns-finance.md` | Finance SQL templates (budget, AP, DPO, GL recon) | finance, budget-variance-analysis, supplier-payment-optimisation, ap-ageing-analysis, gl-reconciliation-support, initiate |
| `references/schema-inventory.md` | Full 59-table inventory (on demand) | Any skill when needed |
| `references/investigation.md` | ETL tracing, medallion architecture | investigate, initiate |
| `references/advanced-analytics.md` | Statistical methods, Python patterns | analyse, initiate |
| `references/output-standards.md` | Brand identity, chart rules, XLSX/DOCX/PPTX layout | format, initiate |

## File Manifest

```
plugins/madison-bi-assistant/
├── .claude-plugin/plugin.json          # Native plugin manifest (v3.2.0)
├── .mcp.json                           # MCP server config (Databricks SQL)
├── plugin.md                           # This file — setup guide, skill index
├── CLAUDE.md                           # Plugin identity, disposition, quality gates
├── context.md                          # Canonical SQL rules, business context, 14 core tables
├── references/
│   ├── query-patterns.md               # Verified SQL templates (revenue, inventory, AR, pipeline)
│   ├── query-patterns-finance.md       # Finance SQL templates (budget, AP, DPO, GL recon)
│   ├── schema-inventory.md             # Full 59-table inventory (on demand)
│   ├── investigation.md                # ETL tracing, medallion architecture, control table
│   ├── advanced-analytics.md           # Statistical methods, Python patterns
│   └── output-standards.md             # Brand identity, chart rules, deliverable layout
└── skills/
    ├── query/SKILL.md                  # Descriptive analysis
    ├── investigate/SKILL.md            # Discrepancy debugging
    ├── analyse/SKILL.md                # Advanced analytics
    ├── format/SKILL.md                 # Branded deliverable production
    ├── finance/SKILL.md                # Finance analysis router
    ├── budget-variance-analysis/SKILL.md        # Budget vs GL variance
    ├── supplier-payment-optimisation/SKILL.md   # DPO, term extension, cash flow
    ├── ap-ageing-analysis/SKILL.md              # AP ageing, concentration, DPO trend
    ├── gl-reconciliation-support/SKILL.md       # GL-to-subledger reconciliation
    └── initiate/SKILL.md               # Catch-all router
```
