# Jedox Reporting Reference

> Condensed from Claude.ai Skill `jedox-reporting`. For detailed Jedox API docs, see the group
> claude repo: `C:\Users\jamesf\OneDrive - MADISON GROUP ENTERPRISES PTY LTD\Documents\GitHub\claude\docs\api\jedox\`

## When to Use

Any task involving Jedox: report design, PALO formulas, dashboards, DynaRanges, charts,
macros (PHP), form elements, Views, splashing/planning, Canvas, Dynatables, subset definitions.

## Connection Details

| System | Endpoint | Auth |
|--------|----------|------|
| Jedox OLAP API | `https://olap.live-madisongroup.cloud.jedox.com` | `api_claude` from `.env` |
| Jedox Cloud UI | `https://live-madisongroup.cloud.jedox.com` | SSO (browser only) |

## Critical Rules

### Colour
- Chart sequence: Purple `#9B69DD` → Aqua `#47C1BF` → Orange `#F5A623`
- NEVER green/red in charts (reserved for trend indicators)
- NEVER blue in charts (reserved for interactive elements)
- Links/buttons: `#057ACE`
- Primary text: `#212A36`
- Input cells: `#F5F5F8`

### Layout
- Header: 45px height
- Resolution: 1280×720px (no responsive)
- Numbers: ALWAYS right-align data AND headers
- Cell padding: 5px blank columns/rows (no native padding)
- Data row height: 30px

### Formulas
- `PALO.DATAV` — read performance (array, no writeback)
- `PALO.DATA` — single-cell read with writeback
- `PALO.DATAC` — no nesting, no cyclic calcs
- Max rows: 65,536 | Max columns: 256 | A1 refs only

### Components
- Buttons are STATIC (don't work in DynaRanges)
- Action + Macro on same element = NOT supported
- Max 2 nested DynaRanges same direction
- No merged cells in DynaRanges

## API Authentication

```python
import requests
from urllib.parse import quote
from dotenv import load_dotenv
import os

load_dotenv()
username = os.environ['JEDOX_USERNAME']  # api_claude
password = os.environ['JEDOX_PASSWORD']

url = f"https://olap.live-madisongroup.cloud.jedox.com/server/login?user={quote(username)}&extern_password={quote(password)}"
response = requests.get(url)
sid = response.text.strip().split(';')[0]
```

## Known Issues

| Error | Fix |
|-------|-----|
| `EOF when reading a line` | Script uses `input()` — use `.env` only |
| `Database not found` | Call `/server/databases` first; names are case-sensitive |
| `400 Bad Request` on login | Use `api_claude`, not SSO creds |
| `1019 worker auth failed` | Check `JEDOX_USERNAME=api_claude` (not email) |
| Attributes empty after reload | `/dimension/clear` wipes attribute cube — export first |
| `#` in cube names | URL-encode as `%23` |
| Element not found in attribute cube | Check dimension order via `/cube/info` |
| Default language element | Use `~` not `en` in `#_LANGUAGE` dimension |

## Detailed Documentation

For full reference including design system, planning formulas, and report building patterns,
see the group claude repo Jedox docs:
- `docs/api/jedox/OLAP_API.md` — Full API reference
- `docs/api/jedox/JEDOX_DEV_WORKFLOW.md` — Development workflow and checklists
- `docs/specs/Jedox_ProjectScope.md` — Project scope and decisions
