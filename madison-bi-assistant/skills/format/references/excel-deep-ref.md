# Excel Deep Reference — openpyxl Edge Cases & Advanced Features

> Load this file when you need to go beyond what `mge_excel.py` handles:
> combination charts, conditional formatting, structured tables, data validation,
> row/column grouping, sheet protection, hyperlinks, CellRichText, or print edge cases.
>
> **Do not duplicate what the scripts handle.** For standard tables, title blocks,
> print setup, auto-fit, freeze panes, single-type charts, and negative highlighting,
> use `mge_excel.py` directly.

---

## Combination Charts (Bar + Line with Secondary Axis)

The classic board chart — revenue bars with margin % line on a secondary axis.

```python
from openpyxl.chart import BarChart, LineChart, Reference

# Primary chart: revenue bars
c1 = BarChart()
c1.style = None  # CRITICAL: prevent theme colour leakage
c1.type = "col"
c1.y_axis.title = "Revenue ($)"
c1.add_data(data_ref, titles_from_data=True)
c1.set_categories(cat_ref)

# Colour series — brand palette
for si, s in enumerate(c1.series):
    s.graphicalProperties.solidFill = brand.CHART_COLOURS[si % len(brand.CHART_COLOURS)].hex

# Secondary chart: margin % line
c2 = LineChart()
c2.style = None
c2.y_axis.axId = 200              # unique axis ID (primary defaults to 100)
c2.y_axis.title = "Margin %"
c2.y_axis.numFmt = '0.0%'
c2.add_data(pct_ref, titles_from_data=True)

# Colour line series Accent Red
for s in c2.series:
    s.graphicalProperties.line.solidFill = brand.ACCENT_RED.hex
    s.graphicalProperties.line.width = 25400  # 2pt in EMU
    s.graphicalProperties.noFill = True        # no area fill under line

# Combine: push secondary axis to right side
c1.y_axis.crosses = "max"  # set on PRIMARY axis, not secondary
c1 += c2

ws.add_chart(c1, "B20")
```

**Compatible combinations:** Bar+Line, Bar+Bar, Line+Line, Bar+Scatter, Area+Line.
**Cannot combine:** Pie with anything. 3D with 2D.

**Manual axis scaling** — set `c1.y_axis.scaling.min/max` and `c2.y_axis.scaling.min/max`
independently. Without this, Excel auto-scales each axis, which can mislead.

---

## Individual Data Point Colouring

Highlight specific bars (e.g. negative values in Accent Red, one bar as the focus):

```python
from openpyxl.chart.series import DataPoint

series = chart.series[0]
for idx in negative_indices:  # 0-based index into the series
    pt = DataPoint(idx=idx)
    pt.graphicalProperties.solidFill = brand.ACCENT_RED.hex
    series.data_points.append(pt)
```

For pie/doughnut charts, colour every slice individually via DataPoint — otherwise
Excel applies theme colours.

---

## Conditional Formatting

### Colour Scales (heatmaps)

```python
from openpyxl.formatting.rule import ColorScaleRule

# White → Connect Grey gradient
rule = ColorScaleRule(
    start_type='min', start_color='FFFFFFFF',
    end_type='max',   end_color='FF3F5364',
)
ws.conditional_formatting.add('C6:C50', rule)

# 3-colour: white → Satin Grey → Connect Grey
rule = ColorScaleRule(
    start_type='min',        start_color='FFFFFFFF',
    mid_type='percentile',   mid_value=50, mid_color='FFE4E5E6',
    end_type='max',          end_color='FF3F5364',
)
```

**⚠ Colour format:** Use 8-char aRGB (`'FF3F5364'`) for conditional formatting —
6-char strings get `'00'` alpha prepended (technically transparent, but Excel ignores alpha).

### Data Bars (in-cell sparkline substitute)

```python
from openpyxl.formatting.rule import DataBarRule

rule = DataBarRule(
    start_type='min', end_type='max',
    color='FF3F5364',
    minLength=0, maxLength=100,
    showValue=True,  # False hides the number, showing only the bar
)
ws.conditional_formatting.add('D6:D50', rule)
```

**Limitations:** Always gradient fill (solid not configurable). Single colour only —
no separate colour for negative values. These are OOXML 1st edition constraints.

### Icon Sets (arrows, traffic lights)

```python
from openpyxl.formatting.rule import IconSetRule

# Up/down arrows for positive/negative
rule = IconSetRule(
    icon_style='3Arrows',
    type='num',
    values=[0, 0, 1],  # down < 0, middle = 0, up >= 1
    showValue=True,
)
ws.conditional_formatting.add('E6:E50', rule)
```

17 built-in styles available (3/4/5-icon variants). Cannot mix icons across sets.
Cannot show only subset of icons — set thresholds to make unwanted range impossibly narrow.

### Cell/Formula Rules (row highlighting)

```python
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import PatternFill, Font
from openpyxl.styles.differential import DifferentialStyle

# Highlight cells < 0 with Accent Red background
rule = CellIsRule(
    operator='lessThan', formula=['0'],
    fill=PatternFill(start_color='FFCF152D', end_color='FFCF152D', fill_type='solid'),
    font=Font(color='FFFFFF'),
)
ws.conditional_formatting.add('C6:C50', rule)

# Row-level highlight where column E = "Overdue"
# Use $E (absolute col) with relative row — applied across full row range
diff = DifferentialStyle(
    fill=PatternFill(bgColor='FFFCE8EA'),  # Red 10% — NOTE: bgColor only for DifferentialStyle
    font=Font(color='CF152D'),
)
rule = FormulaRule(formula=['$E6="Overdue"'], dxf=diff)
ws.conditional_formatting.add('B6:H50', rule)
```

**⚠ PatternFill gotcha:** Convenience functions (`CellIsRule`, `FormulaRule`) use
full `PatternFill(start_color=..., end_color=..., fill_type='solid')`.
`DifferentialStyle` uses only `PatternFill(bgColor=...)`. Mixing them produces
invisible or incorrect formatting.

**Priority:** `Rule.priority` — lower number = higher precedence. `stopIfTrue=True`
skips lower-priority rules for matching cells.

---

## Structured Tables

openpyxl cannot create custom table styles. Two approaches:

### Approach 1: Built-in Style (quick, imperfect brand match)

```python
from openpyxl.worksheet.table import Table, TableStyleInfo

table = Table(displayName="tblRevenue", ref="B5:H25")
style = TableStyleInfo(
    name="TableStyleMedium7",  # grey header, grey/white banding — closest to brand
    showRowStripes=True,
    showFirstColumn=False, showLastColumn=False, showColumnStripes=False,
)
table.tableStyleInfo = style
ws.add_table(table)
```

### Approach 2: Invisible Table + Manual Formatting (brand-perfect)

```python
# Create table with no visible style — keeps structured references and autofilter
table = Table(displayName="tblRevenue", ref="B5:H25")
style = TableStyleInfo(name=None)  # invisible
table.tableStyleInfo = style
ws.add_table(table)

# Then format cells with brand NamedStyles as usual (mge_header, mge_body, etc.)
```

**Totals row:** Set `totalsRowCount=1` on Table. Each `TableColumn` supports
`totalsRowFunction` (`'sum'`, `'average'`, `'count'`, `'min'`, `'max'`, `'custom'`)
and `totalsRowLabel`. The `ref` range must include the totals row.

**⚠ Gotchas:**
- `displayName` must be unique across the workbook (case-insensitive), no spaces
- Column names within a table must be unique — duplicates corrupt the file
- Auto-filter is mandatory when `headerRowCount >= 1` — cannot disable
- Table `ref` is a static string — does not auto-expand when rows are added

---

## Data Validation (Dropdowns)

```python
from openpyxl.worksheet.datavalidation import DataValidation

# Dropdown list — inner double quotes are REQUIRED by OOXML spec
dv = DataValidation(
    type="list",
    formula1='"Finance,HR,IT,Marketing"',  # note the inner double quotes
    showErrorMessage=True,   # 3.1+ defaults to False — always set explicitly
    showInputMessage=True,   # 3.1+ defaults to False
    errorTitle="Invalid",
    error="Select from the list.",
    promptTitle="Department",
    prompt="Choose a department.",
)
ws.add_data_validation(dv)
dv.add("C6:C50")

# Cell-range source for longer lists (> 256 chars)
dv2 = DataValidation(type="list", formula1="Lookups!$A$1:$A$100")
```

**⚠ showDropDown inversion:** `showDropDown=True` **HIDES** the dropdown arrow.
Use `hide_drop_down=True` if you want to hide it. Leave both unset to show the dropdown.

**Inline list limit:** 256 total characters including commas and quotes. For longer
lists, reference a cell range on a (possibly hidden) sheet.

---

## Row/Column Grouping (Collapsible Sections)

```python
# Group rows 6-15 (detail rows) under a summary at row 16
ws.row_dimensions.group(6, 15, outline_level=1, hidden=True)

# CRITICAL: set collapsed flag on the summary row (first row AFTER the group)
ws.row_dimensions[16].collapsed = True

# Nested groups: increase outline_level (max 7)
ws.row_dimensions.group(7, 10, outline_level=2, hidden=True)
ws.row_dimensions[11].collapsed = True

# Column grouping uses letters
ws.column_dimensions.group('D', 'F', hidden=True)

# Summary row position — default is below detail
# Change to above: ws.sheet_properties.outlinePr.summaryBelow = False
```

**⚠ The collapsed flag must be set manually.** `.group()` sets `hidden=True` on
rows but does NOT set `collapsed` on the summary row. Without it, expand/collapse
buttons may not render correctly.

Use `SUBTOTAL(109, range)` in summary cells — it respects both filters and collapsed
groups (109 = SUM ignoring hidden rows).

---

## Sheet Protection

```python
from openpyxl.styles import Protection

# 1. Unlock input cells FIRST (all cells are locked by default)
for row in ws.iter_rows(min_row=6, max_row=50, min_col=3, max_col=5):
    for cell in row:
        cell.protection = Protection(locked=False)

# 2. Enable sheet protection — allows sort/filter on protected sheet
ws.protection.sheet = True
ws.protection.password = 'boardpack'  # trivially bypassable — accidental edit prevention only
ws.protection.sort = False           # ⚠ True = BLOCKED, False = ALLOWED (counterintuitive)
ws.protection.autoFilter = False     # allow filtering
ws.protection.formatCells = True     # block cell formatting changes
ws.protection.insertRows = True      # block row insertion

# Workbook structure protection (prevent sheet add/delete/rename)
wb.security.lockStructure = True
wb.security.workbookPassword = 'structure'
```

**⚠ Semantics are inverted:** `True` means the operation is **blocked**, not allowed.
**Password security is negligible** — 16-bit XOR hash, trivially bypassable. This is
for preventing accidental edits in board-distributed workbooks, not data security.

---

## Hyperlinks (Cross-Sheet Navigation)

```python
# Internal link to another sheet (# prefix required)
cell = ws.cell(row=6, column=2, value="→ See Detail")
cell.hyperlink = "#'Revenue Detail'!A1"  # quote sheet names with spaces
cell.font = Font(name='Arial', color=brand.CONNECT_GREY.hex, underline='single')

# External URL
cell.hyperlink = "https://example.com"
cell.hyperlink.tooltip = "Open in browser"

# Named range target
cell.hyperlink = "#my_named_range"
```

**openpyxl does NOT auto-apply blue underline** — you must style the cell explicitly.
This is an advantage: use brand Connect Grey instead of default blue.

Hyperlinks on merged cells must be set on the **top-left cell** only.

---

## CellRichText (Mixed Formatting in a Single Cell)

```python
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont

# KPI cell: "Revenue: $12.4M" with label in CG and value in bold
cell.value = CellRichText(
    TextBlock(InlineFont(rFont='Arial', sz=18, color='FF3F5364'), "Revenue: "),
    TextBlock(InlineFont(rFont='Arial', sz=18, b=True, color='FF243747'), "$12.4M"),
)
```

**⚠ Limitations:**
- Rich text cells become **string type** — no formulas, no number formatting
- `InlineFont` uses `rFont` (not `name`), `sz` in half-points (`sz=18` = 9pt)
- Colour uses aRGB 8-char format
- Requires openpyxl **3.1.3+** (earlier versions have save bugs without lxml)
- Loading rich text: `load_workbook('file.xlsx', rich_text=True)` — otherwise flattened

Use for display-only cells: dashboard KPIs, annotated headers, mixed-format labels.
Not suitable for computed data cells.

---

## Print Edge Cases

### Multiple Print Areas

```python
# Each range prints as a separate page section
ws.print_area = 'B1:H25,B27:H50'  # or as list: ['B1:H25', 'B27:H50']
```

### Page Breaks

```python
from openpyxl.worksheet.pagebreak import Break

# Insert page break BEFORE row 25
ws.row_breaks.append(Break(id=25))

# Column break before column E
ws.col_breaks.append(Break(id=5))
```

**⚠ Always pass explicit Break(id=N).** Calling `append()` without one creates a
Break at `id=self.count+1`, which is almost always the wrong row.

### Headers/Footers with Colour

```python
# Colour uses 6-char hex — no # prefix, validated against ^[A-Fa-f0-9]{6}$
ws.oddFooter.left.text = "Madison Group Enterprises"
ws.oddFooter.left.font = "Arial,Regular"
ws.oddFooter.left.size = 8
ws.oddFooter.left.color = "9FA9B2"  # CG 50%

ws.oddFooter.right.text = "Page &[Page] of &[Pages]"
ws.oddFooter.right.font = "Arial,Regular"
ws.oddFooter.right.size = 8
ws.oddFooter.right.color = "9FA9B2"
```

**Field codes:** `&[Page]`/`&P`, `&[Pages]`/`&N`, `&[Date]`/`&D`, `&[Tab]`/`&A`,
`&[File]`/`&F`. Raw formatting: `&"FontName,Style"`, `&nn` (size), `&KRRGGBB` (colour).

**⚠ Images in headers/footers are NOT supported** by openpyxl. Place logos on the
sheet in the header area using `ws.add_image()` as a workaround.

**Different first page:** Set `ws.headerFooter.differentFirst = True` explicitly —
openpyxl does not auto-detect when `firstHeader`/`firstFooter` content is set.

### Sheet View Presets

```python
# Open file in page break preview for print verification
ws.sheet_view.view = 'pageBreakPreview'
ws.sheet_view.zoomScale = 85
```

---

## Hex Colour Format Quick Reference

| Context | Format | Example | Notes |
|---------|--------|---------|-------|
| `PatternFill` (fgColor) | 6-char or 8-char | `'3F5364'` or `'FF3F5364'` | Both work for cell fills |
| Conditional formatting | 8-char aRGB | `'FF3F5364'` | 6-char gets `'00'` alpha — still works but 8-char is safer |
| Chart series fills | 6-char RRGGBB | `'3F5364'` | No `#` prefix |
| Chart line fills | 6-char RRGGBB | `'CF152D'` | Same as series |
| Header/footer colour | 6-char RRGGBB | `'9FA9B2'` | Validated against `^[A-Fa-f0-9]{6}$` |
| `Font` colour | 6-char RRGGBB | `'3F5364'` | openpyxl auto-prepends alpha |
| `Border` Side colour | 6-char RRGGBB | `'3F5364'` | Same as Font |

---

## Unit Quick Reference

| Unit | Per Inch | Per Point | Per cm | Use |
|------|----------|-----------|--------|-----|
| EMU | 914,400 | 12,700 | 360,000 | Chart dimensions, line widths, offsets |
| CharacterProperties `sz` | — | 100 | — | Chart title/axis font sizes (1400 = 14pt) |
| Rotation | — | — | — | 60,000ths of degree (-5,400,000 = -90°) |
| Column width | — | — | — | Character-width units of Normal style font |

---

## Common Error Patterns

| Symptom | Cause | Fix |
|---------|-------|-----|
| Fit-to-page not working | Missing `pageSetUpPr.fitToPage = True` | Use `setup_print()` from mge_excel.py |
| Default blue/green on charts | `chart.style` not set to `None` | Set `chart.style = None` before adding data |
| Negative values in Excel red, not brand red | `[Red]` in number format string | Use colourless format + font colour override |
| NamedStyle "already exists" error | Duplicate registration attempt | Check `wb.named_styles` before adding |
| NamedStyle changes not reflected | Modified after registration | Define all properties before `add_named_style()` |
| Conditional formatting fill invisible | Wrong PatternFill pattern for context | Convenience functions: full PatternFill. DifferentialStyle: bgColor only |
| Table corrupts on open | Duplicate column names in Table | Ensure all column headers are unique |
| Dropdown hidden despite creating validation | `showDropDown=True` hides it | Leave unset or use `hide_drop_down=False` |
| Group expand/collapse button missing | `collapsed` flag not set on summary row | Manually set `ws.row_dimensions[N].collapsed = True` |
| Shapes/images lost on re-save | openpyxl strips unrecognised drawing objects | Only affects round-trip files, not new workbooks |
| Sparklines disappeared | openpyxl does not support sparklines | Use DataBarRule conditional formatting instead |
