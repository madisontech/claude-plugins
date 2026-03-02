---
description: Work with Jedox OLAP cubes — report design, PALO formulas, dashboards, DynaRanges, macros, planning.
---

You are working with the Jedox reporting and planning platform for MGE.

Critical rules:
- Chart colours: Purple #9B69DD, Aqua #47C1BF, Orange #F5A623 in sequence
- NEVER green/red in charts (reserved for trend indicators)
- NEVER blue in charts (reserved for interactive elements)
- Numbers ALWAYS right-aligned (data AND headers)
- Resolution: 1280x720px, no responsive design
- Buttons are STATIC — they do not work inside DynaRanges
- Use `PALO.DATAV` for read performance, `PALO.DATA` for writeback cells

Read `references/jedox-reporting.md` for full API authentication, component rules,
known issues, and links to detailed documentation.

Authenticate via OLAP API using `api_claude` credentials from `.env`, never SSO credentials.
