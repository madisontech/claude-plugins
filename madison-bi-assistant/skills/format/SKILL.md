---
description: Branded deliverable production — XLSX, DOCX, PPTX with MGE brand standards.
---

You are producing a branded deliverable for Madison Group Enterprises.

**Boot:** Read `../../CLAUDE.md`, `../../context.md`, `../../references/output-standards.md`.
If querying data, also load `../../references/query-patterns.md`.
Load `../../references/schema-inventory.md` on demand.

**Default:** XLSX. Always produce a branded file, never markdown as a deliverable.
Use existing query results from the conversation when available; query fresh if needed.

## Workflow

1. **Assess** (internal) — What data exists in context? What format is requested?
2. **Query** (internal, if needed) — Get the data. Save query to `scratch/queries/`.
3. **Build** (internal) — Generate with Python (openpyxl/python-docx/python-pptx) per output-standards.md.
4. **Verify** (internal) — Formatting, number alignment, brand compliance, data accuracy.
5. **Deliver** (visible) — File path and a brief summary of what's in it.

Write deliverables to `deliverables/`.
