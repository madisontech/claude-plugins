# Python Environment Reference

> Loaded on demand when Python execution is needed. Not loaded at boot.

## Execution Model

### Primary: `uv run --script` (recommended)

[uv](https://docs.astral.sh/uv/) auto-provisions Python and dependencies from
[PEP 723](https://peps.python.org/pep-0723/) inline metadata embedded in the script.
No venv activation, no pip install, no Python version management required.

```bash
# Run a plugin tool
uv run --script plugins/madison-bi-assistant/tools/dbx-extract.py --help

# Run any PEP 723 script
uv run --script scratch/scripts/my-analysis.py
```

uv handles:
- Finding a compatible Python (or downloading one if needed)
- Installing declared dependencies into an isolated cache
- Running the script
- Works on Windows, macOS, and Linux

### Fallback: System Python

When `uv` is not available, use system Python directly. Dependencies must already be installed:

```bash
pip install databricks-sql-connector
python tools/dbx-extract.py --help
```

### Installing uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Databricks Credentials

### Required Environment Variables

| Variable | Fallback | Purpose |
|----------|----------|---------|
| `DATABRICKS_SERVER_HOSTNAME` | `DATABRICKS_HOST` | Workspace hostname (e.g., `adb-xxx.azuredatabricks.net`) |
| `DATABRICKS_HTTP_PATH` | — | SQL warehouse path (e.g., `/sql/1.0/warehouses/xxx`) |
| `DATABRICKS_ACCESS_TOKEN` | `DATABRICKS_TOKEN` | Personal access token |

### Credential Resolution Order

1. Environment variables already set in the shell
2. `.env` file in the working directory (auto-loaded, silent if missing)
3. Explicit `--env-file` flag (overrides default .env path)

Existing env vars always take precedence over .env file values.

### `.env` File Template

```bash
# Databricks SQL connection
DATABRICKS_SERVER_HOSTNAME=adb-XXXX.Y.azuredatabricks.net
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/XXXX
DATABRICKS_ACCESS_TOKEN=dapiXXXXXXXXXXXXXXXXXX
```

## Plugin Tools

### `tools/dbx-extract.py` — Bulk Data Extraction

Streams query results directly to CSV. Bounded memory regardless of result size.

```bash
# From SQL string
uv run --script tools/dbx-extract.py \
  --sql "SELECT * FROM datawarehouse.fact.invoices WHERE Division = '100'" \
  --output scratch/extracts/invoices.csv

# From SQL file
uv run --script tools/dbx-extract.py \
  --sql-file scratch/queries/inventory.sql \
  --output scratch/extracts/inventory.csv

# Custom batch size and delimiter
uv run --script tools/dbx-extract.py \
  --sql "SELECT ..." --output output.tsv --delimiter "\t" --batch-size 5000
```

**When to use instead of MCP `execute_sql_read_only`:**
- Result set exceeds ~500 rows (too large for the context window)
- Data needed as a file for downstream processing (XLSX build, pandas analysis)
- Multi-query extraction batches for deliverables

**When to use MCP instead:**
- Quick lookups, profiling, small aggregations (<~500 rows)
- Interactive exploration where results guide the next query
- Anything where the model needs to reason about the data inline

## Writing New Scripts with PEP 723

Embed dependency metadata at the top of any standalone Python script:

```python
# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "openpyxl"]
# ///
"""Description of what this script does."""

import pandas as pd
# ... rest of script
```

Then invoke with `uv run --script my-script.py`. Dependencies are cached after the first
run — subsequent invocations are fast.

## Common Failure Modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| `uv: command not found` | uv not installed | See "Installing uv" above |
| `No module named 'databricks'` | Running with system Python, deps missing | Use `uv run --script` or `pip install databricks-sql-connector` |
| `credential error — missing ...` | Env vars not set, no .env file | Create `.env` from template above |
| Connection timeout | Wrong hostname or network/firewall | Verify `DATABRICKS_SERVER_HOSTNAME` matches your workspace URL |
| Zero rows returned | Often a CAST issue on joins | Check join casting rules in `context.md` |
| `ModuleNotFoundError` inside uv | Corrupt uv cache | Run `uv cache clean` and retry |
