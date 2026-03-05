---
description: First-time setup for the Madison BI Assistant plugin - configures Databricks credentials and verifies connectivity.
---

You are setting up the Madison BI Assistant plugin for first use.

**Boot:** Read `../../plugin.md` for plugin overview. Read `../../.env.example` for credential template.

## What This Does

Configures the Databricks connection so the plugin's MCP server and extraction tools work.
The plugin's `.mcp.json` references `${DATABRICKS_ACCESS_TOKEN}` which must be set in the
user's environment. This skill creates a `.env` file in the project root with the required values.

## Steps

1. **Check prerequisites** - Check for Python and uv:
   ```bash
   python --version 2>/dev/null || python3 --version 2>/dev/null
   uv --version 2>/dev/null
   ```
   - If **Python** is missing: ask the user if you should install it. If yes, install via
     `winget install Python.Python.3.12` (Windows) or `brew install python@3.12` (macOS).
     Detect the OS first.
   - If **uv** is missing: ask the user if you should install it. If yes:
     - Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
     - macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - If both are present, report versions and continue.

2. **Check existing config** - Look for `.env` in the project root (working directory).
   If it already contains `DATABRICKS_ACCESS_TOKEN` with a real value (not a placeholder),
   skip to step 5 (verify).

3. **Collect credentials** - Ask the user for their Databricks Personal Access Token (PAT).
   Tell them where to generate one:
   > Databricks workspace > User Settings > Developer > Access tokens
   >
   > Workspace URL: https://adb-6242187004665047.7.azuredatabricks.net

   The workspace hostname and SQL warehouse HTTP path are shared across the org and
   pre-configured. Only the PAT is unique per user.

4. **Write .env** - Create or update `.env` in the project root with:
   ```
   # Databricks - Madison Group workspace
   DATABRICKS_SERVER_HOSTNAME=adb-6242187004665047.7.azuredatabricks.net
   DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/6e7e26c4f1065740
   DATABRICKS_ACCESS_TOKEN=<the-token-they-provided>
   ```
   If `.env` already exists with other content, append the Databricks section without
   overwriting existing entries.

5. **Verify connection** - Run a test query via the MCP tool:
   ```sql
   SELECT 1 AS connection_test
   ```
   Use `execute_sql_read_only`. If this fails, report the error and suggest:
   - Check the PAT is valid and not expired
   - Check network access to the Databricks workspace
   - The user may need to restart Claude Code for env var changes to take effect

6. **Verify extraction tool** - Run:
   ```bash
   uv run --script plugins/madison-bi-assistant/tools/dbx-extract.py --sql "SELECT 1 AS extraction_test" --output scratch/extracts/setup-test.csv
   ```
   This should work if steps 1 and 4 succeeded. If it fails, report the error.

7. **Report** - Summarise what was configured:
   ```
   Madison BI Assistant - setup complete
   - Python: [version] [installed / already present]
   - uv: [version] [installed / already present]
   - .env: written to project root with Databricks credentials
   - MCP connection: verified (execute_sql_read_only working)
   - Extraction tool: verified (dbx-extract.py working)
   - Ready to use: /initiate, /query, /investigate, /analyse, /finance, /format
   ```

## Rules

- Never log, print, or echo the PAT value
- Never modify `.mcp.json` - it ships with the correct env var references
- If `.env` already has valid credentials, don't ask for them again
- If MCP test fails but .env looks correct, suggest restarting Claude Code
