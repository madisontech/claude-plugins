# Output & Formatting Standards

> Load when producing charts, tables, reports, or branded deliverables.
> Combines data presentation rules with MGE brand identity.

## Default Output Behaviour

- Any `/format` invocation produces a branded deliverable. Default format: **XLSX**.
- Markdown tables are for chat-only responses (via `/query`), not deliverables.
- When `/format` is invoked standalone with a data request, run the query first, then format.
- Australian conventions throughout: comma = thousands, period = decimal, DD/MM date order.

## Output Metadata (mandatory)

Every deliverable includes:

1. **Title** — what this shows (concise, specific)
2. **Subtitle** — time period, scope, filters applied
3. **Data source** — table/view name or "Databricks datawarehouse"
4. **Last refreshed** — when the data was pulled (DD/MM/YYYY HH:MM)
5. **Author** — who produced this / who to contact

## Chart Selection

| Purpose | Use | Avoid |
|---------|-----|-------|
| Compare categories | Bar chart (horizontal or vertical) | Pie chart (unless 2-3 segments) |
| Trend over time | Line chart | Area chart (unless stacked composition) |
| Part-to-whole | Stacked bar or treemap | 3D pie, donut with >4 segments |
| Correlation | Scatter plot | Bubble chart (hard to read) |
| Precise values | Table with conditional formatting | Chart alone without supporting table |
| Single KPI | Big number with trend indicator | Gauge / speedometer (wastes space) |

### Chart Rules

- **Axis labels:** Readable, never rotated beyond 45 degrees
- **Gridlines:** Minimal — horizontal only, light grey, no vertical
- **Legend:** Only when >1 series; position top or right
- **Data labels:** On bars when <10 items; avoid on line charts
- **Sort order:** Meaningful — largest to smallest, or chronological. Never alphabetical unless categorical
- **Zero baseline:** Always start Y-axis at zero for bar charts

## Colour Usage

- **Colour communicates data, not decoration** — every colour choice has a reason
- **Positive / neutral:** Connect Grey. **Negative / decline:** Accent Red
- **Sequential data:** Light-to-dark tints of Connect Grey
- **Categorical data:** Follow chart colour sequence from brand palette
- **Accessibility:** Never rely on colour alone — pair with shape, pattern, or label
- **Maximum 5-7 colours** per chart; consolidate small categories into "Other"

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

## Layout Principles

- **Information hierarchy:** Most important metric top-left, supporting detail flows down-right
- **Group related metrics** — don't scatter KPIs across unrelated sections
- **Whitespace is structure** — density without clutter; let the data breathe
- **One key message per view** — if you need more, add a page or tab

---

## Brand Identity — MGE

### Typography

**Brand font:** Hurme Geometric Sans (Semibold headers, Regular body).
**Automated output font:** Arial — use in all programmatic output.

| Element | Weight | Size (pt) |
|---------|--------|-----------|
| Document title | Bold | 24-28 |
| H1 section heading | Bold | 18-20 |
| H2 sub-heading | Bold | 14-16 |
| H3 sub-sub-heading | Bold | 12-13 |
| Body text | Regular | 10-11 |
| Table header | Bold | 10 |
| Table content | Regular | 9-10 |
| Footnotes / captions | Regular | 8 |

Line spacing: 1.15 for body text. Paragraph spacing: 6pt after.

### Colour Palette

#### Primary

| Role | Name | HEX | RGB | Usage |
|------|------|-----|-----|-------|
| Primary | Connect Grey | `#3F5364` | 63, 83, 100 | Headings, headers/footers, chart primary |
| Accent | Accent Red | `#CF152D` | 200, 16, 46 | Sparingly — accents, negative values |
| Background | Satin Grey | `#E4E5E6` | 228, 229, 230 | Background panels, alternating rows |
| Dark | Dark Grey | `#243747` | 35, 55, 70 | Extra contrast headings |
| Secondary | 50% Connect Grey | `#9FA9B2` | 159, 169, 178 | Secondary text, borders, dividers |

#### Derived Tints

| Name | HEX | Usage |
|------|-----|-------|
| Connect Grey 20% | `#D9DDE1` | Alternating table rows (light) |
| Connect Grey 10% | `#ECEEF0` | Subtle zebra stripe |
| Accent Red 20% | `#F8D0D5` | Negative variance background |
| Accent Red 10% | `#FCE8EA` | Subtle alert background |

#### Colour Rules

- Brand palette only — never default blue, never unbranded colours
- Accent Red is an accent: never dominant, never for headings, never for large fills
- Positive values = Connect Grey. Negative values = Accent Red text
- Green is NOT in the brand palette — use Connect Grey for positive indicators

#### Chart Colour Sequence

1. Connect Grey `#3F5364`
2. Accent Red `#CF152D`
3. 50% Connect Grey `#9FA9B2`
4. Satin Grey `#E4E5E6`
5. Dark Grey `#243747`

### Brand Elements

**Corner device:** Small L-shaped accent, top-right corner of covers/title slides.
Accent Red on light, White on dark. 8mm small, 15mm A4.

**Circle pattern:** Dotted halftone background texture. Decorative — not required on every output.

## Layout — Documents (DOCX)

- **Page size:** A4 portrait, 1-inch margins all sides
- **Header:** Connect Grey rule line; document title left in 50% Connect Grey 9pt
- **Footer:** Page number right, title left, in 50% Connect Grey 8pt
- **Heading colour:** Connect Grey for H1/H2, Dark Grey for H3+. Never black, never red
- **Tables:** Connect Grey header row (white bold text), alternating CG10%/white, CG50% thin borders
- **Callout boxes:** Satin Grey background with Connect Grey left border

## Layout — Spreadsheets (XLSX)

### Sheet Structure

- **Row 1:** Blank (breathing room)
- **Row 2:** Report title — Connect Grey bold 14pt, merged across data columns
- **Row 3:** Subtitle / date range — 50% Connect Grey 10pt
- **Row 4:** Blank (separator)
- **Row 5+:** Header row, then data
- **Column A:** Blank (left margin)

### Cell Formatting

- **Header row:** Connect Grey fill, white bold Arial 10pt, centre-aligned
- **Data rows:** Alternating white / Connect Grey 10%
- **Total/summary rows:** Satin Grey fill, bold, separated by heavier bottom border
- **Text:** Left-aligned
- **Numbers:** Right-aligned
- **Negative values:** Accent Red font colour
- **Borders:** 50% Connect Grey thin — horizontal only for clean look, all sides for dense tables
- **Column width:** Auto-fit with 2-character padding minimum
- **Freeze panes:** Lock header row and any left-hand label columns

### Number Formats

| Type | Format | Example |
|------|--------|---------|
| Currency (summary) | `$#,##0` | $1,234,567 |
| Currency (detail) | `$#,##0.00` | $1,234.56 |
| Percentage | `0.0%` | 12.3% |
| Integer | `#,##0` | 1,234 |
| Date | `DD/MM/YYYY` | 03/03/2026 |

## Layout — Presentations (PPTX)

- **Slide size:** 16:9 widescreen
- **Title slides:** Connect Grey background, white text, Accent Red corner device top-right
- **Content slides:** White background, Connect Grey headings, Dark Grey body text
- **Charts:** Brand colour sequence, clean axis labels, minimal gridlines

## Python Constants

### openpyxl (XLSX)

```python
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

class MGE:
    CONNECT_GREY     = "FF3F5364"
    ACCENT_RED       = "FFCF152D"
    SATIN_GREY       = "FFE4E5E6"
    DARK_GREY        = "FF243747"
    CONNECT_GREY_50  = "FF9FA9B2"
    CONNECT_GREY_20  = "FFD9DDE1"
    CONNECT_GREY_10  = "FFECEEF0"
    ACCENT_RED_20    = "FFF8D0D5"
    ACCENT_RED_10    = "FFFCE8EA"
    WHITE            = "FFFFFFFF"
    BLACK            = "FF000000"

# Fonts
MGE_TITLE_FONT    = Font(name="Arial", bold=True, size=14, color=MGE.CONNECT_GREY)
MGE_SUBTITLE_FONT = Font(name="Arial", size=10, color=MGE.CONNECT_GREY_50)
MGE_HEADER_FONT   = Font(name="Arial", bold=True, size=10, color=MGE.WHITE)
MGE_BODY_FONT     = Font(name="Arial", size=10, color=MGE.BLACK)
MGE_TOTAL_FONT    = Font(name="Arial", bold=True, size=10, color=MGE.BLACK)
MGE_NEG_FONT      = Font(name="Arial", size=10, color=MGE.ACCENT_RED)
MGE_FOOTER_FONT   = Font(name="Arial", size=8, color=MGE.CONNECT_GREY_50)

# Fills
MGE_HEADER_FILL   = PatternFill("solid", fgColor=MGE.CONNECT_GREY)
MGE_ALT_FILL      = PatternFill("solid", fgColor=MGE.CONNECT_GREY_10)
MGE_TOTAL_FILL    = PatternFill("solid", fgColor=MGE.SATIN_GREY)

# Alignment
MGE_TEXT_ALIGN     = Alignment(horizontal="left", vertical="center")
MGE_NUM_ALIGN      = Alignment(horizontal="right", vertical="center")
MGE_HEADER_ALIGN   = Alignment(horizontal="center", vertical="center")

# Borders
MGE_THIN_BORDER = Border(
    left=Side(style="thin", color=MGE.CONNECT_GREY_50),
    right=Side(style="thin", color=MGE.CONNECT_GREY_50),
    top=Side(style="thin", color=MGE.CONNECT_GREY_50),
    bottom=Side(style="thin", color=MGE.CONNECT_GREY_50),
)

# Number formats
MGE_CURRENCY_FMT        = '$#,##0'
MGE_CURRENCY_DETAIL_FMT = '$#,##0.00'
MGE_PCT_FMT             = '0.0%'
MGE_DATE_FMT            = 'DD/MM/YYYY'
MGE_NUM_FMT             = '#,##0'
```

### python-docx (DOCX)

```python
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

class MGEDoc:
    CONNECT_GREY = RGBColor(63, 83, 100)
    ACCENT_RED   = RGBColor(200, 16, 46)
    SATIN_GREY   = RGBColor(228, 229, 230)
    DARK_GREY    = RGBColor(35, 55, 70)
    GREY_50      = RGBColor(159, 169, 178)
    WHITE        = RGBColor(255, 255, 255)

    MARGIN       = Inches(1)
    FONT_NAME    = "Arial"
    BODY_SIZE    = Pt(10)
    LINE_SPACING = 1.15
    SPACE_AFTER  = Pt(6)
```

## Delivery Checklist

1. **Font:** Arial throughout
2. **Colours:** Brand palette only — no default blue, no unbranded colours
3. **Headings:** Connect Grey — never black, never red
4. **Red:** Accent only — bullets, negative values, alerts. Never dominant
5. **Tables:** Branded header, alternating rows, text left / numbers right
6. **Page size:** A4 for documents, 16:9 for presentations
7. **Numbers:** Australian conventions (DD/MM, comma thousands, period decimal)
8. **Spacing:** Blank Row 1 + Column A in spreadsheets; 1.15 line spacing in documents
9. **Freeze panes:** Header row locked in all spreadsheets
10. **Corner device:** Accent Red top-right on cover pages and title slides
