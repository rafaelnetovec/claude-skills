---
name: pdf-reader
description: Reads and extracts text, tables, and metadata from PDF files, and answers questions about their contents. Tuned for VEC reports and internal documents (quarterly updates, guides, handbooks, partnering and research docs). Use when the user shares a .pdf file (or a path to one) and asks to "read this PDF", "extract the text/tables", "summarize this PDF", "what does this document say", or asks any question that requires opening a PDF.
---

# pdf-reader

Open a PDF file, pull out its contents (text, tables, and metadata), and use them to
answer the user's question or produce the requested output. This skill is tuned for
**VEC's reports and internal documents** — quarterly updates, process guides, handbooks
(e.g. the IC-PJ Handbook), partnering decks, and research PDFs — while still handling any
other PDF the user shares.

## When to use

- The user shares a `.pdf` file or a path to one and wants its contents.
- The user asks to **extract text or tables** from a PDF.
- The user asks to **summarize** a PDF, list its sections, or find something in it.
- The user asks a question that can only be answered by reading a PDF.

Do **not** use this for creating or editing PDFs, or for non-PDF documents (Word,
spreadsheets, images) — this skill only reads.

## Language

- **Always respond in English**, even when the source PDF is in Brazilian Portuguese.
  VEC's reporting language is English, so summaries, answers, and extracted narrative
  should be delivered in English.
- When you translate Portuguese content, keep the **original term in parentheses** the
  first time it matters (e.g. "onboarding guide (*guia de integração*)"), and preserve
  proper nouns, project names, and defined terms verbatim.
- Tables, figures, numbers, dates, and monetary values are reproduced as-is — only
  surrounding prose is translated.

## Steps

1. **Locate the file.** Confirm the PDF path. If the user referred to a file without a
   clear path, ask for it (or the file itself) before proceeding. VEC PDFs often live in
   Google Drive or Slack — if the user points there, retrieve the file first.
2. **Read the PDF.** Use the Read tool with the `pages` parameter to open the PDF
   directly — it renders text and layout. For a PDF over 10 pages, `pages` is required;
   read at most 20 pages per request and page through the rest in ranges (e.g. `"1-20"`,
   then `"21-40"`).
3. **Extract what was asked.**
   - *Text*: read through and return the relevant passages verbatim or paraphrased (in
     English).
   - *Tables*: reconstruct them as Markdown tables, preserving row/column structure.
   - *Metadata* (title, author, page count, creation date): report what the document
     exposes.
4. **Report-oriented structure.** For VEC reports and internal docs, favor a structured
   read the reader can act on:
   - Lead with a short **summary** of what the document is and its purpose.
   - Pull out **key points, decisions, figures, and dates** as a bullet list.
   - Preserve the document's own **section headings** so the reader can navigate.
   - If the doc defines a process or policy (e.g. a handbook or guide), summarize it as
     clear steps or rules rather than a wall of prose.
5. **Handle scanned / image-only PDFs.** If a page has no selectable text (a scan), say
   so — it needs OCR, which is outside this skill's scope. Point the user to an OCR step
   rather than guessing at the contents.
6. **Answer or deliver.** Use the extracted content to answer the question or produce
   the requested output. Cite page numbers (`p. 3`) so the user can verify.

## Guardrails

- **Never invent content.** If a page is unreadable or a value is ambiguous, say so
  instead of filling the gap.
- **Respect length.** For long reports, summarize section by section rather than dumping
  the whole document.
- **Confidentiality.** VEC documents are often internal or client-confidential (e.g.
  files marked "Confidential Project"). Do not send their contents to external services
  or third parties, and don't repost them outside the requested destination without the
  user's OK.
- **Copyright.** Do not reproduce large copyrighted passages wholesale; summarize and
  quote sparingly with page attribution.
