---
name: pdf-reader
description: Reads and extracts text, tables, and metadata from PDF files, and answers questions about their contents. Use when the user shares a .pdf file (or a path to one) and asks to "read this PDF", "extract the text/tables", "summarize this PDF", "what does this document say", or asks any question that requires opening a PDF.
---

# pdf-reader

Open a PDF file, pull out its contents (text, tables, and metadata), and use them to
answer the user's question or produce the requested output.

## When to use

- The user shares a `.pdf` file or a path to one and wants its contents.
- The user asks to **extract text or tables** from a PDF.
- The user asks to **summarize** a PDF, list its sections, or find something in it.
- The user asks a question that can only be answered by reading a PDF.

Do **not** use this for creating or editing PDFs, or for non-PDF documents (Word,
spreadsheets, images) — this skill only reads.

## Steps

1. **Locate the file.** Confirm the PDF path. If the user referred to a file without a
   clear path, ask for it (or the file itself) before proceeding.
2. **Read the PDF.** Use the Read tool with the `pages` parameter to open the PDF
   directly — it renders text and layout. For a PDF over 10 pages, `pages` is required;
   read at most 20 pages per request and page through the rest in ranges (e.g. `"1-20"`,
   then `"21-40"`).
3. **Extract what was asked.**
   - *Text*: read through and return the relevant passages verbatim or paraphrased.
   - *Tables*: reconstruct them as Markdown tables, preserving row/column structure.
   - *Metadata* (title, author, page count, creation date): report what the document
     exposes.
4. **Handle scanned / image-only PDFs.** If a page has no selectable text (a scan), say
   so — it needs OCR, which is outside this skill's scope. Point the user to an OCR step
   rather than guessing at the contents.
5. **Answer or deliver.** Use the extracted content to answer the question or produce
   the requested output. Cite page numbers (`p. 3`) so the user can verify.

## Guardrails

- **Never invent content.** If a page is unreadable or a value is ambiguous, say so
  instead of filling the gap.
- **Respect length.** For long PDFs, summarize section by section rather than dumping the
  whole document.
- **Copyright.** Do not reproduce large copyrighted passages wholesale; summarize and
  quote sparingly with page attribution.
