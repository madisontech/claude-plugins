---
description: Branded deliverable production — XLSX, DOCX, PPTX with MGE brand standards. Use when producing Excel workbooks, Word documents, or formatted reports for stakeholders.
---

You are producing a branded deliverable for Madison Group Enterprises. Every output
must look like it was produced by a professional design agency — board-ready, print-safe,
brand-compliant. You achieve this by using the bundled Python scripts and following the
brand rules below.

## Boot Sequence

1. Read `../../CLAUDE.md` and `../../context.md` (plugin identity and domain rules)
2. If querying data: also read `../../references/query-patterns.md`
3. For unfamiliar tables: `DESCRIBE TABLE` to discover columns

The brand rules and script API below are self-contained for common cases.
Load `references/design-system.md` only when you need detail beyond what's here
(unusual layouts, deep colour accessibility, cover page variants, KPI card sizing).

## Format Selection

| Request | Format | When |
|---------|--------|------|
| Data table, analysis extract | **XLSX** (default) | Numbers, drill-down, pivot-ready data |
| Narrative report, executive summary | **DOCX** | Prose with embedded tables and findings |
| Board pack | **Both** | XLSX workbook + DOCX executive summary |
| Presentation | **PPTX** | Slide deck (use python-pptx — brand rules apply) |

Default is XLSX. Always produce a branded file — never markdown as a deliverable.

## Workflow

All steps are internal except Deliver. Do not show the user boilerplate, query text,
or verification steps — they see the finished product and a brief summary.

1. **Assess** — What data exists in context? What format? What audience?
2. **Query** (if needed) — Get the data via Databricks SQL. Save to `scratch/queries/`.
3. **Build** — Generate with Python using the scripts below. Write to `deliverables/`.
4. **Verify** — Run the delivery checklist. Fix any failures before presenting.
5. **Deliver** — File path and a concise summary of what's in it.

## Scripts

Three bundled Python scripts in `scripts/` handle all branding mechanics.
Import `mge_brand` for constants; use `mge_excel` and `mge_word` for document creation.

### mge_brand.py — Constants & Utilities (available now)

```python
import sys
sys.path.insert(0, 'plugins/madison-bi-assistant/skills/format/scripts')
import mge_brand as brand

# Colours — each has .hex, .rgb (tuple), .argb (openpyxl string)
brand.CONNECT_GREY.hex    # "3F5364"
brand.CONNECT_GREY.argb   # "FF3F5364"
brand.CONNECT_GREY.rgb    # (63, 83, 100)
brand.ACCENT_RED           # Accent only — negatives, alerts
brand.SATIN_GREY           # Light backgrounds, total row fills
brand.DARK_GREY            # Deep contrast, cover pages
brand.CONNECT_GREY_50      # Borders/decoration ONLY — fails WCAG for text
brand.CONNECT_GREY_10      # Zebra stripe fill
brand.CHART_COLOURS        # [CG, Red, CG50, Satin, Dark, CG30]

# Number formats — no [Red] colour codes (apply colour via font, not format)
brand.NUM_FMT_CURRENCY          # '$#,##0'
brand.NUM_FMT_CURRENCY_DETAIL   # '$#,##0.00'
brand.NUM_FMT_CURRENCY_NEG      # '$#,##0;($#,##0)'
brand.NUM_FMT_PCT               # '0.0%'
brand.NUM_FMT_VARIANCE_PCT      # '+0.0%;(0.0%);"-"'
brand.NUM_FMT_DATE_DISPLAY      # 'DD MMM YYYY'
brand.NUM_FMT_CURRENCY_DYNAMIC  # Auto K/M suffix

# Column width estimation (font-metric-based, ~6% error)
brand.estimate_column_width(["$1,234,567", "$987"], header="Revenue", font_size=9)

# Logo path resolution — returns Path or None if file missing
brand.logo_path("mge")          # Colour logo
brand.logo_path("mge-wide")     # Horizontal logo (cover pages)
brand.logo_path("mav", grey=True)  # Grey variant (headers on white)

# Trend indicators
brand.TREND_UP    # "▲"
brand.TREND_DOWN  # "▼"
brand.TREND_FLAT  # "—"
```

### mge_excel.py — Workbook Builder

```python
import mge_excel as xl

# Create branded workbook with all styles registered
wb, ws = xl.create_branded_workbook("Sheet Title", "Subtitle — Date Range")

# Write a data table (header row + data with zebra stripes)
end_row, end_col = xl.write_data_table(ws, headers=["Region", "Revenue", "Margin %"],
                                        data=rows, start_row=5, start_col=2)

# Total row — write values first, then apply styling (function sets label + formatting only)
for col, val in zip(range(3, end_col + 1), total_values):
    ws.cell(row=end_row + 1, column=col, value=val)
xl.write_total_row(ws, end_row + 1, start_col=2, end_col=end_col, label="Total", style="grand")

# KPI cards for dashboards
xl.write_kpi_cards(ws, metrics=[{"label": "Revenue", "value": "$12.4M", "change": "▲ +5.2%"}],
                   start_row=2, start_col=2)

# Auto-fit columns using font metrics
xl.auto_fit_columns(ws, start_col=2, end_col=end_col, start_row=5, end_row=end_row)

# Negative highlighting — Accent Red on negative values
xl.apply_negative_highlighting(ws, start_row=6, end_row=end_row, cols=[3, 4])

# Print setup (explicit — the #1 gotcha source)
xl.setup_print(ws, orientation="landscape", fit_to_width=1, repeat_header_row=5)

# Freeze panes and autofilter
xl.freeze_panes(ws, row=5, col=2)  # freezes below header row 5
xl.add_autofilter(ws, start_row=5, start_col=2, end_col=end_col)

# High-level convenience: build_sheet() composes all the above in one call
xl.build_sheet(wb, "Summary", title="Revenue Summary", subtitle="FY2026",
               headers=["Region", "Revenue"], data=rows)
```

### mge_word.py — Document Builder

```python
import mge_word as wd

# Create branded document with cover page, styles, headers/footers
doc = wd.create_branded_document("Inventory Board Pack", subtitle="March 2026",
                                  include_cover=True)

# Headings with red full stop (H1/H2 only — auto-appended)
wd.add_heading(doc, "Executive Summary", level=1)
doc.add_paragraph("Body text here.", style="MGE Body")

# Data table (primary: CG header, alternating rows)
wd.add_data_table(doc, headers=["Metric", "Value", "Change"],
                  rows=[["Revenue", "$12.4M", "▲ +5.2%"]])

# KPI panel (side-by-side metric cards)
wd.add_kpi_panel(doc, metrics=[{"label": "Revenue", "value": "$12.4M", "change": "+5.2%"}])

# Callout box (note/warning/insight)
wd.add_callout(doc, "Key Finding", "Revenue declined 12% driven by...", style="note")

# Landscape section for wide tables
wd.add_section_break(doc, orientation="landscape")
```

## Brand Rules (Quick Reference)

These rules are sufficient for producing correct output without loading design-system.md.

### Colours

| Role | Colour | HEX | Use |
|------|--------|-----|-----|
| Primary | Connect Grey | `#3F5364` | Headings, headers, chart primary, borders |
| Accent | Accent Red | `#CF152D` | Negatives, alerts, red full stop — never dominant |
| Background | Satin Grey | `#E4E5E6` | Light panels, total row fill |
| Deep | Dark Grey | `#243747` | Cover pages, H3+ headings |
| Secondary | CG 50% | `#9FA9B2` | Borders, footer text — **never body text** |
| Zebra | CG 10% | `#ECEEF0` | Alternating table rows |
| Alert bg | Red 10% | `#FCE8EA` | Subtle negative background |

**Colour rules:** 60% white/light, 30% grey, 10% max red. No green. No default blue.
Positive = CG or black. Negative = Accent Red. Max 3 red elements per page.

### Typography

**Font:** Arial throughout — no exceptions, no theme fonts.

**Word scale:** Title 28pt → H1 20pt → H2 16pt → H3 13pt → Body 10.5pt → Caption 9pt → Footnote 8pt. All in Connect Grey (H3+ in Dark Grey). Line spacing 1.15× body, 1.0× headings.

**Excel scale:** Title 14pt → Section 11pt → Header 9pt Bold (white on CG fill) → Data 9pt → Notes 8pt.

**Red full stop:** H1 and H2 headings end with a period in Accent Red. Not H3 and below. Omit if heading already ends with punctuation.

**Case:** Title Case for titles, H1, H2, table headers, KPI labels. Sentence case for H3+, body.

### Tables

- **Header:** CG fill, white bold text, centre-aligned
- **Data:** Alternating white / CG 10%, text left, numbers right
- **Total:** Satin Grey fill, bold, single line above + double line below (accounting convention)
- **Borders:** Horizontal rules only (default). Vertical only for 10+ column tables
- **Minimum border weight:** 0.5pt (print survival)

### Numbers

Australian conventions: comma thousands, period decimal, DD/MM dates.

| Context | Format |
|---------|--------|
| Summary currency | `$#,##0` |
| Detail currency | `$#,##0.00` |
| Negative currency | `$#,##0;($#,##0)` — parentheses, no [Red] code |
| Percentage | `0.0%` |
| Variance | `+0.0%;(0.0%);"-"` |
| Date | `DD MMM YYYY` |

**Critical:** Never use `[Red]` in Excel format strings — it overrides cell font colour
with Excel's built-in red, not brand Accent Red. Apply negative colour via font colour.

### Layout

**Excel:** Row 1 blank, Column A blank. Title in Row 2 (merged, CG Bold 14pt).
Subtitle Row 3. Blank Row 4. Headers Row 5+. Freeze panes below header.
Row height: data 18-20pt, header 24pt. Gridlines off on formatted sheets.

**Word:** A4 portrait, 1-inch margins. Header: CG rule line. Footer: title left,
page X of Y right, CG 50% 8pt. Cover page: separate section, no header/footer.

### Print (Mandatory for Excel)

Every worksheet must have explicit print setup:
1. Paper size A4, orientation set
2. Margins defined (left/right 0.7", top/bottom 0.75")
3. Fit-to-width: `fitToWidth=1, fitToHeight=0`
4. **`ws.sheet_properties.pageSetUpPr.fitToPage = True`** ← the #1 gotcha
5. Print area set to data range
6. Repeat header rows via `print_title_rows`
7. Footer: company name left, page numbers right

### Charts

- Brand colour sequence only — zero default Excel blue/green
- Axis labels: readable, never rotated >45°
- Gridlines: horizontal only, CG 10%
- Legend: only when >1 series, position top or right
- Zero baseline on bar charts
- Sort: meaningful order (largest first or chronological), never alphabetical

### Logos

13 PNGs in `assets/logos/`, 300 DPI, RGBA. Use `brand.logo_path()` to resolve.
Available: mge, mge-wide, mav, mex, mt, mcs, kallipr (colour and grey variants).
Always handle missing files gracefully — placeholder text, never crash.

## Delivery Checklist

Run before presenting any deliverable. Every item must pass.

- [ ] **Font:** Arial throughout — no Calibri, no theme fonts
- [ ] **Colours:** Brand palette only — no default blue, no unbranded colours
- [ ] **Headings:** Connect Grey (H1/H2) or Dark Grey (H3+) — never black, never red
- [ ] **Red full stop:** Present on H1/H2 headings in Word documents
- [ ] **Accent Red:** Used only for negatives/alerts — never dominant, never in totals
- [ ] **Tables:** CG header fill, alternating rows, text left / numbers right
- [ ] **Totals:** Accounting convention — single line above, double line below
- [ ] **Numbers:** Australian format, no [Red] colour codes in format strings
- [ ] **Page size:** A4. Correct orientation for content width
- [ ] **Spacing:** Blank Row 1 + Column A (Excel). 1-inch margins (Word)
- [ ] **Freeze panes:** Header row locked in all worksheets
- [ ] **Print setup:** Explicit on every worksheet (margins, fit-to-page, repeat rows)
- [ ] **Gridlines:** Off on formatted sheets
- [ ] **Data accuracy:** Totals verified, no phantom rows, column headers match data
- [ ] **File location:** Written to `deliverables/`

## Reference Loading (On Demand)

The scripts and rules above handle standard deliverables. Load a reference file
only when the task requires something the scripts don't provide.

### `references/excel-deep-ref.md` — load when:
- Building a **combination chart** (bar + line with secondary axis)
- Applying **conditional formatting** (colour scales, data bars, icon sets, row highlighting)
- Colouring **individual data points** differently (e.g. one red bar among grey)
- Creating a **structured table** (ListObject with totals row and auto-filter)
- Adding **data validation** dropdowns
- Building **collapsible grouped rows** (drill-down sections)
- Applying **sheet protection** for board-distributed workbooks
- Adding **cross-sheet hyperlinks** for navigation
- Using **CellRichText** for mixed formatting in a single cell
- Handling **print edge cases** (multiple print areas, page breaks, header/footer colour)

### `references/word-deep-ref.md` — load when:
- Inserting a **table of contents**
- Creating **numbered or bulleted lists** (especially restarting numbering)
- Adding a **watermark** (DRAFT, CONFIDENTIAL)
- Positioning a **floating image** at specific page coordinates
- Using **paragraph borders** for simple callout panels (not the table-based callout)
- Adjusting **document settings** (zoom, spell check, compatibility mode, font embedding)
- Setting **custom document properties** (metadata beyond core properties)
- Configuring **outline levels** on custom heading styles for navigation pane
- Making **table header rows repeat** across printed pages

### `references/design-system.md` — load when:
- Unusual layouts, accessibility detail, cover page variants, KPI card sizing, border tier system

### `../../references/output-standards.md` — load when:
- Chart selection matrix, number presentation rules (shared with other skills)
