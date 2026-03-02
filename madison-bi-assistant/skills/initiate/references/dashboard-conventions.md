# Dashboard & Visual Output Conventions

> Standards for charts, tables, and data visualisations. Brand execution details
> are in `mge-report-formatter.md` — this file covers what to show and how to structure it.

## Output Metadata (mandatory)

Every visual output includes:

1. **Title** — what this shows (concise, specific)
2. **Subtitle** — time period, scope, filters applied
3. **Data source** — table/view name or "Databricks datawarehouse"
4. **Last refreshed** — when the data was pulled (DD/MM/YYYY HH:MM)
5. **Author** — who produced this / who to contact

## Layout Principles

- **Information hierarchy:** Most important metric top-left, supporting detail flows down-right
- **Group related metrics** — don't scatter KPIs across unrelated sections
- **Whitespace is structure** — density without clutter; let the data breathe
- **One key message per view** — if you need more, add a page or tab
- **Mobile awareness:** Stakeholders read on phones — test at narrow widths if HTML

## Chart Selection

| Purpose | Use | Avoid |
|---------|-----|-------|
| Compare categories | Bar chart (horizontal or vertical) | Pie chart (unless 2–3 segments) |
| Trend over time | Line chart | Area chart (unless stacked composition) |
| Part-to-whole | Stacked bar or treemap | 3D pie, donut with >4 segments |
| Correlation | Scatter plot | Bubble chart (hard to read) |
| Precise values | Table with conditional formatting | Chart alone without supporting table |
| Single KPI | Big number with trend indicator | Gauge / speedometer (wastes space) |

### Chart Rules

- **Axis labels:** Readable, never rotated beyond 45 degrees
- **Gridlines:** Minimal — horizontal only, light grey, no vertical
- **Legend:** Only when >1 series; position top or right
- **Data labels:** On bars when <10 items; avoid on line charts (use tooltips)
- **Sort order:** Meaningful — largest to smallest, or chronological. Never alphabetical unless categorical
- **Zero baseline:** Always start Y-axis at zero for bar charts. Line charts may truncate if clearly labelled

## Colour Usage

- **Colour communicates data, not decoration** — every colour choice has a reason
- **Positive / neutral:** Connect Grey. **Negative / decline:** Accent Red
- **Sequential data:** Light-to-dark tints of Connect Grey
- **Categorical data:** Follow chart colour sequence from brand palette
- **Accessibility:** Never rely on colour alone — pair with shape, pattern, or label
- **Maximum 5–7 colours** per chart; consolidate small categories into "Other"

## Number Presentation

| Context | Approach | Example |
|---------|----------|---------|
| Summary / dashboard | No decimals, K/M/B suffixes | $1.2M |
| Detail / drill-down | Full precision, comma separated | $1,234,567.89 |
| Variance | Signed with +/- prefix | +5.2%, -$12K |
| Percentages | 1 decimal unless integer sufficient | 12.3% |

### Comparison Context

Numbers without context are meaningless. Always show at least one:

- vs prior period (MoM, QoQ, YoY)
- vs target / budget
- vs benchmark or peer group
- Include both absolute and percentage variance where space permits

## Table Formatting

- **Alignment:** Text left, numbers right, headers match their data alignment
- **Sorting:** Default to most useful order — largest value or most recent date
- **Conditional formatting:** Subtle — Accent Red text for negative, not garish cell fills
- **Row density:** Enough rows to tell the story; link to detail if >25 rows
- **Totals:** Bottom row, visually separated, bold

## Interactivity (HTML / embedded)

- Filters at top, always visible — never hidden behind a menu
- Default view answers the most common question without any interaction
- Drill-down available but headline readable without it
- Loading states for async data — never show stale numbers without indication
- Export option (CSV/XLSX) where feasible
- Hover tooltips for additional context on chart elements
