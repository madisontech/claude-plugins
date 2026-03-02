# Analysis Standards

> How we write SQL, Python, and analytical outputs. Conventions that compound.

## SQL Standards

### Style
- **CTEs over subqueries** — readability over cleverness
- **Explicit column lists** — never `SELECT *` in production queries
- **Lowercase keywords** — `select`, `from`, `where` (or uppercase — pick one and stick to it)
- **One clause per line** — each JOIN, WHERE condition, GROUP BY column on its own line
- **Trailing commas** — easier diffs, fewer merge conflicts
- **Alias everything** — tables and subqueries get meaningful short aliases

### Business Logic
- Comments explain WHY, not WHAT — `-- Exclude test accounts per DEC-003` not `-- filter where id != 0`
- Date filters as variables/parameters where possible, not hardcoded
- Always specify timezone handling explicitly
- Document any assumed business rules inline

### Performance
- Test with `LIMIT` before running full queries
- Check execution plan on anything touching >1M rows
- Use materialised views when the same aggregation runs daily
- Prefer approximate counts for dashboards (`APPROX_COUNT_DISTINCT` etc.)

### Naming
- snake_case for all identifiers
- Prefix staging tables: `stg_`
- Prefix intermediate: `int_`
- Prefix marts/final: `fct_` (facts), `dim_` (dimensions)
- Date columns: `[event]_at` for timestamps, `[event]_date` for dates

## Python Standards

### Scripts
- Type hints on all function signatures
- Docstrings: one line for simple functions, numpy-style for complex ones
- `if __name__ == "__main__":` guard on all scripts
- Logging over print statements
- Dependencies pinned in requirements.txt or pyproject.toml

### Data Processing
- pandas: prefer `.assign()` chains over mutation
- Always check `.shape` and `.dtypes` after loading
- Validate row counts after merges — unexpected multiplication means a bad join
- Save intermediate results for debugging on long pipelines

### Output
- Deliverables saved to `deliverables/`, not just printed
- Charts: title, axis labels, source attribution, date generated
- Tables: headers, units, totals where appropriate

## Review Checklist

Before delivering any analysis:

- [ ] Row counts make sense (not 0, not impossibly large)
- [ ] Totals cross-reference against known control figures
- [ ] Date range is correct and explicitly stated
- [ ] Null handling is documented
- [ ] Joins checked for fan-out (unexpected row multiplication)
- [ ] Assumptions listed
- [ ] Stakeholder name and delivery format confirmed
- [ ] Premortem considered: "what could be wrong here?"
