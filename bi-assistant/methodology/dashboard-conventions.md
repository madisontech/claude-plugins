# Dashboard & Report Conventions

> Standards for visual outputs. Consistency builds trust.

## Every Output Must Have

1. **Title** — what this shows
2. **Subtitle** — time period, scope, any filters applied
3. **Data source** — where the numbers come from
4. **Last refreshed** — when the data was pulled
5. **Author/owner** — who to ask questions

## Layout Principles

- Information hierarchy: most important metric top-left
- Group related metrics together
- White space is not wasted space — density without clutter
- Mobile-friendly unless told otherwise (stakeholders read on phones)

## Colour

- Colour for meaning, not decoration
- Green = good/growth, Red = bad/decline, Grey = neutral/baseline
- Colourblind-safe palettes (avoid red-green only distinctions)
- Maximum 5-7 colours per chart
- Consistent colours for consistent categories across all reports

## Charts

- Bar charts for comparison
- Line charts for trends over time
- Tables for precise values
- Avoid: pie charts (unless exactly 2-3 segments), 3D anything, dual axes unless clearly labelled

## Numbers

- Currency: $ with commas, 2 decimal places for precision, 0 for summary
- Percentages: 1 decimal place unless integer precision is sufficient
- Large numbers: use K, M, B suffixes in dashboards, full numbers in detail tables
- Always show comparison: vs prior period, vs target, vs benchmark

## Interactivity (HTML dashboards)

- Filters at top, always visible
- Default view should answer the most common question
- Drill-down available but not required to understand the headline
- Loading states for any async data
- Export option where feasible
