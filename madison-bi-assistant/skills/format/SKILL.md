---
description: Branded deliverable production — XLSX, DOCX, PPTX with MGE brand standards.
---

You are producing a branded deliverable for Madison Group Enterprises.

## Boot Sequence (mandatory)

Read these files before producing any output. Do not proceed until all are loaded.

1. Read `../../CLAUDE.md` — disposition, communication style, quality gate
2. Read `../../context.md` — SQL rules, join casting, exclusions, business context
3. Read `../../references/output-standards.md` — brand identity, chart rules, XLSX/DOCX/PPTX layout, Python constants

If data needs to be queried first (standalone invocation), also load:
4. Read `../../references/query-patterns.md` — verified SQL templates

If you encounter a table not covered in context.md, load `../../references/schema-inventory.md`.

## Mode Declaration

```
Mode:    Format
Scope:   [Division, BU, Time Period, Key Filters]
Output:  branded XLSX (default) | DOCX | PPTX
Loading: CLAUDE.md, context.md, output-standards.md [+ query-patterns.md if querying]
```

## Default Behaviour

**Always produce a branded file.** Default format is XLSX. Never output markdown as a deliverable.

- If conversation already has query results: format them into the branded deliverable
- If no data in context: run the query first (load query-patterns.md), then format
- Write deliverables to `deliverables/`

## Workflow

1. **Assess** — What data exists in context? What format is requested (default XLSX)?
2. **Query** (if needed) — Run SQL to get the data. Save query to `scratch/queries/`.
3. **Build** — Generate the deliverable using Python (openpyxl/python-docx/python-pptx) with MGE brand standards from output-standards.md.
4. **Verify** — Check formatting, number alignment, brand compliance, data accuracy.
5. **Deliver** — Save to `deliverables/`. Present file path and key findings in chat.

## Rules

- Source of truth: `datawarehouse.fact.*` and `datawarehouse.dim.*` only
- Every deliverable includes: title, subtitle, data source, last refreshed date, author
- Brand standards: Connect Grey `#3F5364`, Accent Red `#CF152D`, Arial font
- Australian number conventions: comma thousands, DD/MM/YYYY dates
- Numbers without context are meaningless — always include comparison (YoY, vs target, vs benchmark)
