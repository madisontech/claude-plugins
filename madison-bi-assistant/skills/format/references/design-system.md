# MGE Design System — Visual Language Reference

> Load on demand when SKILL.md instructions are insufficient for a specific
> design question. This is the comprehensive reference; SKILL.md carries the
> essentials for common cases.

## 1. Colour System

### Palette

| Token | HEX | RGB | Role |
|-------|-----|-----|------|
| Connect Grey | `#3F5364` | 63, 83, 100 | Primary. Headings, headers, chart primary, structural borders |
| Accent Red | `#CF152D` | 207, 21, 45 | Accent only. Negatives, alerts, red full stop, corner device |
| Satin Grey | `#E4E5E6` | 228, 229, 230 | Light backgrounds, summary row fills, section panels |
| Dark Grey | `#243747` | 35, 55, 70 | Deep contrast. Cover pages, H3+ headings |
| CG 50% | `#9FA9B2` | 159, 169, 178 | Borders, dividers, footer text. **Never text — fails WCAG (2.39:1)** |

### Derived Tints

| Token | HEX | Usage |
|-------|-----|-------|
| CG 30% | `#B9C1C8` | Disabled/muted states, 6th chart series |
| CG 20% | `#D9DDE1` | Alternating rows (medium), subtotal fills, decorative borders |
| CG 10% | `#ECEEF0` | Zebra stripes (subtle), section backgrounds |
| CG 05% | `#F5F6F7` | Ultra-subtle background, input cell fill |
| Red 30% | `#F2B5BC` | Warning highlight (medium) |
| Red 20% | `#F8D0D5` | Negative variance background (light) |
| Red 10% | `#FCE8EA` | Subtle alert background |

### Accessibility

| Combination | Ratio | WCAG AA | AAA |
|-------------|-------|---------|-----|
| CG on White | 7.96:1 | Pass all | Pass all |
| White on CG | 7.96:1 | Pass all | Pass all |
| Red on White | 5.53:1 | Pass all | Large text only |
| CG on CG 10% | 6.85:1 | Pass all | Large text only |
| **CG 50% on White** | **2.39:1** | **Fail all** | **Fail all** |

**Rule:** CG 50% is decoration only — borders, divider lines, disabled icons with adjacent labels. Never body text, never table data.

### Colour Rules

- 60/30/10 allocation: 60% white/light, 30% grey tones, 10% max red
- Accent Red is never dominant — max 3 red elements per page
- Positive = Connect Grey (or black). Negative = Accent Red text
- No green in the palette — grey signals "normal/good", red signals "exception"
- No browser-default blue anywhere (hyperlinks use Connect Grey underlined)
- White text only on Connect Grey, Dark Grey, or Accent Red fills

### Chart Colours

Cycle in order: CG → Red → CG 50% → Satin → Dark Grey → CG 30%.
Binary: CG = positive/actual, Red = negative. Target/actual: CG 50% = target (muted), CG = actual.

## 2. Typography

### Font

**Arial** for all programmatic output. Hurme Geometric Sans is the brand font for manual design work only — unavailable in automated environments. Arial's large x-height means it appears visually larger than serif fonts at equivalent point sizes.

### Word Type Scale (Major Third 1.25 ratio, 10pt body)

| Element | Size | Weight | Colour | Spacing Before/After |
|---------|------|--------|--------|---------------------|
| Title | 28pt | Bold | CG | 0 / 12pt |
| Subtitle | 16pt | Regular | CG 50% | 0 / 24pt |
| H1 | 20pt | Bold | CG | 24 / 8pt |
| H2 | 16pt | Bold | CG | 18 / 6pt |
| H3 | 13pt | Bold | Dark Grey | 14 / 4pt |
| H4 | 11pt | Bold | Dark Grey | 10 / 4pt |
| Body | 10.5pt | Regular | Black | 0 / 6pt |
| Body Small | 9.5pt | Regular | Black | 0 / 4pt |
| Caption | 9pt | Regular | CG 50% | 4 / 2pt |
| Footnote | 8pt | Regular | CG 50% | 0 / 2pt |

Line spacing: 1.15× for body text, 1.0× for headings and table cells.

### Excel Type Scale (1.2 ratio, 9pt body)

| Element | Size | Weight | Colour |
|---------|------|--------|--------|
| Sheet title | 14pt | Bold | CG |
| Section header | 11pt | Bold | Dark Grey |
| Column header | 9pt | Bold | White (on CG fill) |
| Data | 9pt | Regular | Black |
| Notes/footer | 8pt | Regular | CG 50% |

### The Red Full Stop

H1 and H2 headings end with a period rendered in Accent Red while heading text is Connect Grey. This is a distinctive MGE brand element from the governance PDF.

- Apply to H1 and H2 only — not H3 and below
- If heading already ends with punctuation (? : !), do not add
- In python-docx: split into two runs — text run in CG, period run in Red

### Capitalisation

| Element | Case |
|---------|------|
| Title, H1, H2 | Title Case |
| H3, H4 | Sentence case |
| Table headers, KPI labels | Title Case |
| Body text | Sentence case |

## 3. Table Design

### Standard Data Table

| Property | Header | Even Rows | Odd Rows | Total Row |
|----------|--------|-----------|----------|-----------|
| Fill | CG | White | CG 10% | Satin Grey |
| Text | White Bold 10pt | Black 9.5pt | Black 9.5pt | Black Bold 10pt |
| Alignment | Centre | Left/Right | Left/Right | Left/Right |
| Top border | — | 0.5pt CG 50% | 0.5pt CG 50% | 1.5pt CG |
| Bottom border | 1pt Dark Grey | 0.5pt CG 50% | 0.5pt CG 50% | Double CG |

**Alignment rule:** Text left, numbers right, headers match their data. Centre alignment only for spanner headers spanning sub-columns.

### Total Row Convention (Accounting Standard)

Board directors expect the accounting convention:
- Single line above = "sum of items above"
- **Double line below = "this is the final figure"**
- Use "Double Accounting Underline" (edge-to-edge), not text underline
- Accent Red never appears in total rows

### Borders

Three tiers: decorative (CG 20%, cell dividers), structural (CG 50%, section separators), emphatic (CG, totals/headers). Horizontal rules only is the default — vertical lines only for dense 10+ column tables. Minimum 0.5pt for print survival.

### Zebra Stripes

Use CG 10% alternating with white (~5-6% luminance difference). Recommended for tables with 7+ columns. For narrow tables, generous row height may suffice. If no stripes, row dividers are required.

## 4. KPI Presentation

### Big Number Cards

A reader should grasp the story from KPI cards in under 5 seconds. Each card has exactly four elements:

1. **Metric value** (hero number) — 24-36pt Bold CG
2. **Label** — 9pt Regular CG 50%
3. **Trend/change** — 10pt Bold, CG (positive) or Red (negative)
4. **Period** (optional) — 8pt Regular muted grey

**Layout:** 3 cards across portrait (52mm each, 8mm gap), 4 across landscape (58mm each). All cards in a row must have identical dimensions.

**In Excel:** Merged cell blocks (e.g. B2:D6), white background, 0.5pt CG 20% border, 2pt bottom accent in CG. Gridlines off on dashboard sheets.

**In Word:** Single-row table with 3-4 cells, even widths, 2pt bottom border in CG as visual anchor.

### Trend Indicators

| Condition | Symbol | Colour | Weight |
|-----------|--------|--------|--------|
| Positive | ▲ (U+25B2) | CG | Bold |
| Flat | — (U+2014) | Muted grey | Regular |
| Negative | ▼ (U+25BC) | Red | Bold |

Format: `▲ +12.4% YoY` — arrow first, signed value, comparison basis. Always show + sign for positive.

## 5. Whitespace & Layout

### Word Documents

- A4 portrait, 1-inch (2.54cm) margins all sides
- Content width: 159mm (9026 DXA)
- Line length: ~65 characters at 10pt Arial (optimal 60-75 range)
- 40-60% of a well-designed page should be whitespace

**Spacing rhythm** (base unit 6pt):
H1: 24pt before / 8pt after. H2: 18/6. H3: 14/4. Body: 0/6. Table: 12pt before and after.

### Excel Worksheets

- Row 1 blank, Column A blank (breathing room)
- Row 2: title (CG Bold 14pt, merged). Row 3: subtitle. Row 4: blank. Row 5+: data
- Row heights: data 18-20pt, header 24pt, title 30pt, spacer 6pt
- Column widths: auto-fit + 2-4 character padding (use font metrics)
- Gridlines off on formatted sheets

### Cover Pages (Word)

**External/formal:** Dark Grey full page, white title at ~40% from top, CG 50% subtitle below, Accent Red corner device top-right (15mm), "conduct.connect" at bottom.

**Internal/working:** White background, CG 3pt rule at ~33% from top, CG title above rule, metadata below. Simpler, appropriate for weekly reports.

Cover page is always a separate section with no header/footer.

## 6. Print Considerations

### Font Size Floors

Board directors (typically 50+) need larger text. 10pt body is the minimum for tables; 11pt recommended for Word body text. Never go below 8pt except for footnotes/legal disclaimers.

### Border Weight Floors

- 0.5pt: absolute minimum for print survival
- 0.75pt: safe default for structural borders
- 1pt: important separators (header rules, total lines)
- "hair" style unreliable in print — use "thin" minimum

### Orientation Decision

| Columns | Strategy |
|---------|----------|
| ≤8 | Portrait A4 |
| 9-12 | Landscape A4 |
| 13-15 | Landscape, narrow margins, reduce font 1pt |
| >15 | Split tables or abbreviate headers |

### Excel Print Setup (Mandatory)

Every worksheet must define: orientation, paper size (A4), margins, print area, fit-to-width (fitToWidth=1, fitToHeight=0), **pageSetUpPr.fitToPage=True** (the #1 gotcha — without this, fit-to-page is silently ignored), repeat header rows.

### Headers & Footers

**Word:** Header has CG rule line (0.5pt bottom border). Footer has CG 50% rule line (top border), title left, "Page X of Y" right, both 8pt CG 50%.

**Excel:** Left footer: "Madison Group Enterprises". Right footer: "Page &P of &N". Header: sheet name (&A).

## 7. Brand Elements

### Corner Device

Small L-shaped accent, top-right corner of covers/title slides. Accent Red on light backgrounds, white on dark. Dimensions: 15mm on A4, 8mm on smaller formats. Implemented as a positioned image or two short lines.

### Circle Pattern

Dotted halftone background texture. Decorative — not required on every output. Use sparingly on cover pages or section dividers.

### Red Bullets

Top-level bullet points use Accent Red (distinctive brand element). Nested bullets revert to CG 50%. Character: • (U+2022) for top level, – (en dash) for nested.
