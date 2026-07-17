---
name: pt-en-translator
description: Translates text between Brazilian Portuguese and English, preserving tone, meaning, and formatting. Use when the user asks to "translate this to English", "traduza para o inglês", "translate to Portuguese", "traduza isto", or shares text in one language asking for the other.
---

# pt-en-translator

Translates between Brazilian Portuguese and English, keeping the author's tone and intent
intact — not a literal word-for-word swap.

## When to use
- The user asks to translate a piece of text to English or to Portuguese.
- They share text in one language and want it in the other.

## How to translate
1. **Detect the source language** and translate into the other (PT-BR ⇄ EN).
2. **Preserve tone and register** (formal, neutral, or casual) and the full meaning — never
   add, drop, or soften content.
3. **Keep the formatting** (lists, line breaks, markdown, placeholders like `{name}`).
4. **Names, product terms, and code stay as-is.** For a term with no clean equivalent, keep
   the original and add a short note in parentheses only if it helps.
5. Return **only the translation** by default; add notes only if the user asks.
