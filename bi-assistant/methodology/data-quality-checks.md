# Data Quality Checks

> Standard QA procedures. Run these before trusting any dataset.

## Before Starting Any Analysis

1. **Row count** — is it in the expected range? Compare to yesterday/last week.
2. **Date range** — does min/max date match expectations? Any gaps?
3. **Null audit** — which columns have nulls? Expected or concerning?
4. **Duplicate check** — is the grain what you think it is? `COUNT(*)` vs `COUNT(DISTINCT pk)`.
5. **Schema check** — have columns been added, removed, or renamed since last query?

## After Joins

1. **Row count comparison** — before join vs after. Fan-out means a bad join key.
2. **Null check on join result** — nulls in columns from the right table mean unmatched rows.
3. **Sanity total** — does a known aggregate (total revenue, customer count) still match?

## Before Delivery

1. **Control figure reconciliation** — can you tie at least one number to a known source of truth?
2. **Boundary check** — are there negative values where there shouldn't be? Future dates? Impossible percentages?
3. **Historical comparison** — does the trend look right? Sudden jumps need explanation.
4. **Sample check** — pick 3-5 individual records and trace them through the logic manually.
5. **Stakeholder preview** — if time allows, share a draft with one trusted reviewer.

## Common Traps

| Trap | Symptom | Fix |
|------|---------|-----|
| Timezone mismatch | Counts shift depending on when you run | Standardise to UTC or local, document which |
| Soft deletes ignored | Inflated counts | Add `WHERE deleted_at IS NULL` |
| Duplicate source records | Multiplied totals after join | Deduplicate before joining |
| Currency not normalised | Revenue comparisons are wrong | Convert to base currency with rate at transaction date |
| Test/internal accounts | Metrics skewed by non-real activity | Maintain an exclusion list |
| Changed definitions | YoY comparison is apples-to-oranges | Document definition changes in decisions/ |

## When Something Looks Wrong

1. Don't panic. Don't publish.
2. Isolate: which specific records or time period is affected?
3. Trace: follow one record from source to output.
4. Compare: does the raw source agree with the transformed data?
5. Document: log the finding in `.memory/learnings/` even if it turns out to be nothing.
