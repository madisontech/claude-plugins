# Word Deep Reference — python-docx Edge Cases & Advanced Features

> Load this file when you need to go beyond what `mge_word.py` handles:
> table of contents, numbered/bulleted lists, watermarks, floating images,
> paragraph borders, document settings, custom properties, or multi-level outlines.
>
> **Do not duplicate what the scripts handle.** For cover pages, headings with red
> full stop, data tables, KPI panels, callouts, section breaks, headers/footers,
> field codes, and cell shading, use `mge_word.py` directly.

---

## Table of Contents

python-docx has no TOC API. You insert a field code placeholder; Word renders
the actual entries and page numbers when the document is opened.

### Insertion via Complex Field Code (Recommended)

```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

paragraph = doc.add_paragraph()
paragraph.style = doc.styles['MGE Body']  # or 'TOC Heading' if defined

# Begin field
fldChar_begin = OxmlElement('w:fldChar')
fldChar_begin.set(qn('w:fldCharType'), 'begin')
fldChar_begin.set(qn('w:dirty'), 'true')  # request update on open
run1 = paragraph.add_run()
run1._r.append(fldChar_begin)

# Instruction text — TOC switches
instrText = OxmlElement('w:instrText')
instrText.set(qn('xml:space'), 'preserve')  # MANDATORY — field parser needs spaces
instrText.text = ' TOC \\o "1-3" \\h \\z \\u '
# \o "1-3" = heading levels 1-3
# \h       = hyperlinks
# \z       = suppress page numbers in web layout
# \u       = use outline levels (recognises custom heading styles)
run2 = paragraph.add_run()
run2._r.append(instrText)

# Separate field
fldChar_sep = OxmlElement('w:fldChar')
fldChar_sep.set(qn('w:fldCharType'), 'separate')
run3 = paragraph.add_run()
run3._r.append(fldChar_sep)

# Placeholder text (replaced by Word on update)
run4 = paragraph.add_run('Right-click to update table of contents')
run4.font.color.rgb = RGBColor(0x9F, 0xA9, 0xB2)  # CG 50% — subtle hint

# End field
fldChar_end = OxmlElement('w:fldChar')
fldChar_end.set(qn('w:fldCharType'), 'end')
run5 = paragraph.add_run()
run5._r.append(fldChar_end)
```

### Custom Heading Recognition

Built-in Heading 1-9 are recognised automatically. For custom MGE heading styles, use
the `\t` switch to map style names to TOC levels:

```
' TOC \\t "MGE Heading 1,1,MGE Heading 2,2,MGE Heading 3,3" \\h \\z '
```

Or use the `\u` switch and set outline levels on custom styles (see Outline Levels below).

### TOC Styling

TOC entries use `TOC 1`, `TOC 2`, `TOC 3` styles — not the heading styles themselves.
Tab leaders (dot characters connecting titles to page numbers) are controlled via
right-aligned tab stops with dot leaders in these TOC styles. Define these in a template
for consistent appearance.

### Auto-Update on Open

Two mechanisms — both unreliable:
- `w:dirty="true"` on the fldChar begin element (shown above)
- `<w:updateFields w:val="true"/>` in `settings.xml`

Both depend on Word's global "Update automatic links at open" setting. When off, the
TOC shows placeholder text until the user right-clicks → Update Field. No way to
force silent automatic population.

---

## Lists (Numbered and Bulleted)

### The Template Dependency

`doc.add_paragraph('Item', style='List Bullet')` and `style='List Number'` work — but
the underlying `abstractNum` definitions that make numbering work may be absent from
python-docx's default template. Result: `List Number` paragraphs render as plain text.

**Fix:** Use a pre-built template `.docx` that has all list styles properly configured
with their numbering definitions. This eliminates 90% of the complexity.

### Available Built-in List Styles

- `List Bullet`, `List Bullet 2` through `List Bullet 5`
- `List Number`, `List Number 2` through `List Number 5`
- `List Continue`, `List Continue 2` through `List Continue 5` (continuation without bullet)

**⚠ `List Bullet 2` / `List Number 2` are separate sequences**, not sub-levels.
For true multi-level lists, use a single multi-level `abstractNum` with paragraphs
varying only in `w:ilvl` (indent level).

### Restarting Numbered Lists

All paragraphs sharing `List Number` style continue numbering. To restart:

```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# Get the numbering part
numbering_part = doc.part.numbering_part
numbering_elem = numbering_part.element

# Find the abstractNumId used by the existing List Number style
# (typically 0 or 1 — inspect the template)
abstract_num_id = 0

# Create a new numbering instance with a level override to restart at 1
new_num = numbering_elem.add_num(abstract_num_id)
new_num_id = new_num.numId

# Add restart override
lvl_override = new_num.add_lvlOverride(ilvl=0)
lvl_override.add_startOverride(1)

# Apply to the target paragraph
paragraph = doc.add_paragraph('First item of new list', style='List Number')
numPr = paragraph._p.get_or_add_pPr().get_or_add_numPr()
numId = numPr.get_or_add_numId()
numId.val = new_num_id
```

### Custom Bullets

Standard bullet (•, U+2022) and en dash (–, U+2013) work with Arial. Wingdings
characters use font-specific encoding (not Unicode) — avoid unless the template
pre-defines them.

Standard indent: each level adds **720 twips (0.5")** with **360-twip hanging indent**.
For tighter enterprise layouts, use 360 twips per level (0.25" increments).

---

## Watermarks (DRAFT / CONFIDENTIAL)

python-docx has no watermark API. Requires VML shape injection into every header part.

```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn, nsdecls

def add_watermark(doc, text="DRAFT", colour="D9DDE1"):
    """Inject a diagonal text watermark into all active header parts."""
    watermark_xml = f'''
    <w:sdt {nsdecls('w', 'w10', 'v', 'o', 'r')}>
      <w:sdtContent>
        <w:p>
          <w:pPr><w:pStyle w:val="Header"/></w:pPr>
          <w:r>
            <w:rPr><w:noProof/></w:rPr>
            <w:pict>
              <v:shapetype id="_x0000_t136" coordsize="21600,21600"
                o:spt="136" adj="10800"
                path="m@7,l@8,m@5,21600l@6,21600e">
                <v:formulas>
                  <v:f eqn="sum #0 0 10800"/>
                  <v:f eqn="prod #0 2 1"/>
                  <v:f eqn="sum 21600 0 @1"/>
                  <v:f eqn="sum 0 0 @2"/>
                  <v:f eqn="sum 21600 0 @3"/>
                  <v:f eqn="if @0 @3 0"/>
                  <v:f eqn="if @0 21600 @1"/>
                  <v:f eqn="if @0 0 @2"/>
                  <v:f eqn="if @0 @4 21600"/>
                  <v:f eqn="mid @5 @6"/>
                  <v:f eqn="mid @8 @5"/>
                  <v:f eqn="mid @7 @8"/>
                  <v:f eqn="mid @6 @7"/>
                  <v:f eqn="sum @6 0 @5"/>
                </v:formulas>
                <v:path textpathok="t" o:connecttype="custom"
                  o:connectlocs="@9,0;@10,10800;@11,21600;@12,10800"
                  o:connectangles="270,180,90,0"/>
                <v:textpath on="t" fitshape="t"/>
                <v:handles><v:h position="#0,bottomRight" xrange="6629,14971"/></v:handles>
                <o:lock v:ext="edit" text="t" shapetype="t"/>
              </v:shapetype>
              <v:shape id="PowerPlusWaterMarkObject"
                o:spid="_x0000_s2049" type="#_x0000_t136"
                style="position:absolute;margin-left:0;margin-top:0;
                  width:527.85pt;height:131.95pt;rotation:315;
                  z-index:-251658752;
                  mso-position-horizontal:center;
                  mso-position-horizontal-relative:margin;
                  mso-position-vertical:center;
                  mso-position-vertical-relative:margin"
                o:allowincell="f" fillcolor="#{colour}" stroked="f">
                <v:fill opacity=".25"/>
                <v:textpath style="font-family:&quot;Arial&quot;;font-size:1pt"
                  string="{text}"/>
                <w10:wrap type="none"/>
              </v:shape>
            </w:pict>
          </w:r>
        </w:p>
      </w:sdtContent>
    </w:sdt>'''

    watermark_elem = parse_xml(watermark_xml)

    # Inject into every active header
    for section in doc.sections:
        header = section.header
        if header.is_linked_to_previous:
            continue
        header._element.append(deepcopy(watermark_elem))

        # Also inject into first-page header if different first page is enabled
        if section.different_first_page_header_footer:
            first_header = section.first_page_header
            first_header._element.append(deepcopy(watermark_elem))
```

**⚠ Must inject into every active (unlinked) header part.** Multi-section documents
need watermarks in each section's headers unless headers are linked to previous.

Use CG 20% (`D9DDE1`) for subtle watermarks, Accent Red (`CF152D`) for urgent ones.

---

## Floating Images (Positioned Logos)

python-docx only creates inline images. For absolute positioning, add the image inline
then convert its `wp:inline` element to `wp:anchor`:

```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Mm, Emu
from copy import deepcopy

# Add image inline first (creates the image part and relationship)
paragraph = doc.add_paragraph()
run = paragraph.add_run()
inline_shape = run.add_picture('logo.png', width=Mm(50))

# Get the inline element and extract the picture element
inline = inline_shape._inline
pic = inline.find(qn('a:graphic')).find(qn('a:graphicData')).find(qn('pic:pic'))
extent = inline.find(qn('wp:extent'))
docPr = inline.find(qn('wp:docPr'))

# Build anchor element
anchor = OxmlElement('wp:anchor')
anchor.set('distT', '0')
anchor.set('distB', '0')
anchor.set('distL', '114300')  # 0.125" in EMU
anchor.set('distR', '114300')
anchor.set('simplePos', '0')
anchor.set('relativeHeight', '251658240')
anchor.set('behindDoc', '0')  # 1 = behind text
anchor.set('locked', '0')
anchor.set('layoutInCell', '1')
anchor.set('allowOverlap', '1')

# Position relative to page
posH = OxmlElement('wp:positionH')
posH.set('relativeFrom', 'page')
posOffset_h = OxmlElement('wp:posOffset')
posOffset_h.text = str(Emu(Mm(25)))  # 25mm from left page edge
posH.append(posOffset_h)
anchor.append(posH)

posV = OxmlElement('wp:positionV')
posV.set('relativeFrom', 'page')
posOffset_v = OxmlElement('wp:posOffset')
posOffset_v.text = str(Emu(Mm(25)))  # 25mm from top page edge
posV.append(posOffset_v)
anchor.append(posV)

# Copy extent and docPr from inline
anchor.append(deepcopy(extent))
anchor.append(deepcopy(extent))  # effectExtent
anchor.append(OxmlElement('wp:wrapNone'))  # no text wrapping
anchor.append(deepcopy(docPr))

# Re-wrap the graphic
graphic = OxmlElement('a:graphic')
graphicData = OxmlElement('a:graphicData')
graphicData.set('uri', 'http://schemas.openxmlformats.org/drawingml/2006/picture')
graphicData.append(deepcopy(pic))
graphic.append(graphicData)
anchor.append(graphic)

# Replace inline with anchor in the run
drawing = run._r.find(qn('w:drawing'))
drawing.remove(inline)
drawing.append(anchor)
```

**Position reference points** (`relativeFrom`): `page`, `margin`, `column`, `paragraph`.

**EMU conversions:** 1 inch = 914,400 EMU, 1 cm = 360,000 EMU, 1 pt = 12,700 EMU.
Use `Emu()` from `docx.shared` for explicit EMU values.

---

## Paragraph Borders (Simple Callout Panels)

No native API. For simple single-paragraph notes where a left accent border suffices
(without needing the full table-based callout from `mge_word.py`):

```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

paragraph = doc.add_paragraph("Important note here.", style='MGE Body')
pPr = paragraph._p.get_or_add_pPr()

# Create paragraph border element
pBdr = OxmlElement('w:pBdr')

# Left accent border — 3pt Accent Red
left = OxmlElement('w:left')
left.set(qn('w:val'), 'single')
left.set(qn('w:sz'), '24')      # eighths of a point: 24 = 3pt
left.set(qn('w:space'), '8')    # 8pt gap between border and text
left.set(qn('w:color'), 'CF152D')  # Accent Red, no # prefix
pBdr.append(left)

pPr.append(pBdr)

# Add background shading
shd = OxmlElement('w:shd')
shd.set(qn('w:val'), 'clear')
shd.set(qn('w:color'), 'auto')
shd.set(qn('w:fill'), 'ECEEF0')  # CG 10%
pPr.append(shd)
```

**Multi-paragraph grouping:** Consecutive paragraphs with **identical** `w:pBdr` values
are treated as one visual unit — top border on first, bottom on last, sides continuous.
If even one attribute differs, they become separate boxes. Set `w:between val="none"` to
suppress dividers between grouped paragraphs.

**Border width units:** Eighths of a point — 4 = 0.5pt, 8 = 1pt, 12 = 1.5pt, 24 = 3pt.

---

## Document Settings (XML Injection)

`document.settings` exposes only `odd_and_even_pages_header_footer`. Everything else
requires XML manipulation of `word/settings.xml`:

```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

settings = doc.settings._settings  # the lxml element

# Fix zoom level — default template ships with 203% (issue #254)
zoom = settings.find(qn('w:zoom'))
if zoom is None:
    zoom = OxmlElement('w:zoom')
    settings.append(zoom)
zoom.set(qn('w:percent'), '100')

# Suppress spell/grammar check squiggles
for tag in ['w:hideSpellingErrors', 'w:hideGrammaticalErrors']:
    elem = OxmlElement(tag)
    settings.append(elem)

# Set compatibility mode to Word 2013+ (value 15)
compat = settings.find(qn('w:compat'))
if compat is None:
    compat = OxmlElement('w:compat')
    settings.append(compat)
cs = OxmlElement('w:compatSetting')
cs.set(qn('w:name'), 'compatibilityMode')
cs.set(qn('w:uri'), 'http://schemas.microsoft.com/office/word')
cs.set(qn('w:val'), '15')
compat.append(cs)

# Embed TrueType fonts (ensures Arial renders on systems without it)
settings.append(OxmlElement('w:embedTrueTypeFonts'))
settings.append(OxmlElement('w:saveSubsetFonts'))

# Remove personal information on save (for external board documents)
settings.append(OxmlElement('w:removePersonalInformation'))

# Force field update on open (TOC, page numbers)
settings.append(OxmlElement('w:updateFields'))
settings.find(qn('w:updateFields')).set(qn('w:val'), 'true')
```

---

## Multi-Level Heading Outlines (Navigation Pane Visibility)

Custom heading styles need `w:outlineLvl` set for the navigation pane and TOC to
recognise them. No high-level API exists:

```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# Set outline level on a custom heading style (0 = level 1, 1 = level 2, etc.)
style = doc.styles['MGE Heading 1']
pPr = style.element.get_or_add_pPr()
outline = OxmlElement('w:outlineLvl')
outline.set(qn('w:val'), '0')  # level 1
pPr.append(outline)
```

Once set, Word's navigation pane, TOC `\u` switch, and PDF bookmarks all
recognise the style correctly.

---

## Custom Document Properties

No native API (issue #91, open since 2014). Three approaches:

1. **python-docx-oss fork** — `pip install python-docx-oss`, provides `document.custom_properties`
2. **docx-properties package** — standalone with CLI support
3. **Manual XML** — manipulate `docProps/custom.xml` via OPC package internals

For lightweight metadata needs, use the native core properties:
`doc.core_properties.category`, `doc.core_properties.content_status`,
`doc.core_properties.subject` as stand-ins.

---

## Repeating Table Header Rows

```python
from docx.oxml import OxmlElement

# Mark the first row as a repeating header
row = table.rows[0]
trPr = row._tr.get_or_add_trPr()
trPr.append(OxmlElement('w:tblHeader'))

# Multiple header rows — must be contiguous starting from row 0
for i in range(2):  # rows 0 and 1
    trPr = table.rows[i]._tr.get_or_add_trPr()
    trPr.append(OxmlElement('w:tblHeader'))
```

**⚠ Header rows must be contiguous from row 0.** Marking row 2 without rows 0-1
causes Word to silently ignore it. Does not work in nested tables.

Pair with `w:cantSplit` on the same rows to prevent them breaking across pages.

---

## Unit System Quick Reference

| Context | Unit | Per Inch | Notes |
|---------|------|----------|-------|
| Cell margins, row heights | twips/dxa | 1,440 | `w:w`, `w:val` attributes |
| Border widths | eighths of pt | — | 4 = 0.5pt, 8 = 1pt, 24 = 3pt |
| Drawing layer positions | EMU | 914,400 | `wp:posOffset`, image dimensions |
| python-docx `Length` objects | EMU internally | 914,400 | `Pt()`, `Inches()`, `Mm()` convert |
| Table width (percentage) | 1/50th of % | — | 5000 = 100% of available space |

---

## Common Error Patterns

| Symptom | Cause | Fix |
|---------|-------|-----|
| Heading font stays Calibri despite setting Arial | Theme font references override `font.name` | Use `mge_word.py` — it clears theme fonts. Or use custom styles (not built-in Heading 1-9) |
| Landscape section still portrait | Only set `orientation`, not dimensions | Swap `page_width` and `page_height` explicitly |
| Cell shading only appears in last cell | Same OxmlElement appended to multiple cells | Create new `OxmlElement('w:shd')` per cell |
| List Number paragraphs show no numbers | Template lacks `abstractNum` definitions | Use a pre-built template with list styles configured |
| Numbered list doesn't restart | All paragraphs share same `w:num` instance | Create new `w:num` with `w:lvlOverride` restart |
| TOC shows placeholder text | Word hasn't updated fields | Set `w:dirty="true"` on fldChar. User must right-click → Update Field |
| Header content from previous section | `is_linked_to_previous` defaults to `True` | Set `header.is_linked_to_previous = False` |
| Setting `is_linked_to_previous = True` destroyed content | This is by design — irreversible | Keep a copy. Unlink before modifying. |
| `KeyError` accessing built-in style | Style is latent (not written to styles.xml) | Use template with all needed styles activated, or `add_style(name, builtin=True)` |
| 203% zoom on open | Default template zoom setting | Set `<w:zoom w:percent="100"/>` in settings XML |
| `paragraph.text = "..."` destroyed field codes | Replaces all runs including field code runs | Set text via individual `run.text`, not `paragraph.text` |
