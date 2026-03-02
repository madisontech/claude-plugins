# MGE Report Formatter — Brand Identity Reference

> Loaded from Claude.ai Skill `mge-report-formatter`. Reference before generating any DOCX/XLSX/PPTX.

## Colour Palette

### Primary

| Role | Name | HEX | RGB | Usage |
|------|------|-----|-----|-------|
| Primary | Connect Grey | `#3F5364` | 63, 83, 100 | Logos, headings, headers/footers, block panels |
| Accent | Accent Red | `#CF152D` | 200, 16, 46 | Sparingly — accents, bullets, status indicators |
| Light BG | Satin Grey | `#E4E5E6` | 228, 229, 230 | Background panels, alternating rows, section breaks |
| Dark | Dark Grey | `#243747` | 35, 55, 70 | Extra contrast headings, dark backgrounds |
| Mid | 50% Connect Grey | `#9FA9B2` | 159, 169, 178 | Secondary text, borders, dividers |

### Derived Tints

| Name | HEX | Usage |
|------|-----|-------|
| Connect Grey 20% | `#D9DDE1` | Alternating table rows (light) |
| Connect Grey 10% | `#ECEEF0` | Subtle zebra stripe |
| Accent Red 20% | `#F8D0D5` | Negative variance highlight |
| Accent Red 10% | `#FCE8EA` | Subtle alert background |

### Chart Colour Sequence

1. Connect Grey `#3F5364`
2. Accent Red `#CF152D`
3. 50% Connect Grey `#9FA9B2`
4. Satin Grey `#E4E5E6`
5. Dark Grey `#243747`

Positive = Connect Grey, Negative = Accent Red.

## Typography

Always use **Arial** (Hurme Geometric Sans unavailable in automated environments).

| Element | Size (pt) |
|---------|-----------|
| Document title | 24–28 |
| Heading 1 | 18–20 |
| Heading 2 | 14–16 |
| Heading 3 | 12–13 |
| Body text | 10–11 |
| Table content | 9–10 |
| Footnotes | 8 |

## Layout — Documents (DOCX)

- A4 (11906 × 16838 DXA), 1 inch margins
- Header: Connect Grey rule line
- Footer: page number right, title left, in 50% Connect Grey
- Headings: Connect Grey for H1/H2, Dark Grey for H3+
- Red: callout boxes, bullet markers, status indicators only — never headings
- Tables: Connect Grey header with white text, alternating Satin Grey / Connect Grey 10%

## Layout — Spreadsheets (XLSX)

- Header row: Connect Grey fill, white bold Arial 10pt
- Alternating rows: White / Connect Grey 10%
- Total rows: Satin Grey fill, bold
- Negative values: Accent Red text
- Borders: 50% Connect Grey thin
- Numbers: Australian conventions (comma thousands, period decimal)

## Python Constants (openpyxl)

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
    WHITE            = "FFFFFFFF"
    BLACK            = "FF000000"

MGE_HEADER_FONT  = Font(name="Arial", bold=True, size=10, color=MGE.WHITE)
MGE_HEADER_FILL  = PatternFill("solid", fgColor=MGE.CONNECT_GREY)
MGE_BODY_FONT    = Font(name="Arial", size=10, color=MGE.BLACK)
MGE_ALT_FILL     = PatternFill("solid", fgColor=MGE.CONNECT_GREY_10)
MGE_TOTAL_FILL   = PatternFill("solid", fgColor=MGE.SATIN_GREY)
MGE_TOTAL_FONT   = Font(name="Arial", bold=True, size=10, color=MGE.BLACK)
MGE_NEG_FONT     = Font(name="Arial", size=10, color=MGE.ACCENT_RED)
MGE_THIN_BORDER  = Border(
    left=Side(style="thin", color=MGE.CONNECT_GREY_50),
    right=Side(style="thin", color=MGE.CONNECT_GREY_50),
    top=Side(style="thin", color=MGE.CONNECT_GREY_50),
    bottom=Side(style="thin", color=MGE.CONNECT_GREY_50),
)
```

## Checklist Before Delivery

1. Font: Arial throughout
2. Colours: Brand palette only — no default blue
3. Headings: Connect Grey, not black
4. Red: Accent only, never dominant
5. Tables: Branded header, alternating rows
6. Page size: A4
7. Numbers: Australian conventions
