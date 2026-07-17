---
name: meeting-summarizer
description: Turns raw meeting notes or a transcript into a clean summary with decisions and action items. Use when the user shares meeting notes / a transcript and asks to "summarize this meeting", "pull out the action items", "what did we decide", or "write up the meeting".
---

# meeting-summarizer

Turns messy meeting notes or a transcript into a concise, structured write-up: what was
decided, who owns what, and what's still open.

## When to use
- The user pastes meeting notes or a transcript and wants a summary.
- They ask for the action items, owners, or decisions from a meeting.

## How to produce the summary
1. **Read the whole thing first** to understand the goal of the meeting.
2. Produce the output in this structure:
   - **TL;DR** — 1–2 sentences on the outcome.
   - **Decisions** — bullet list of what was agreed.
   - **Action items** — a checklist, each as `- [ ] <action> — <owner> (<due date if mentioned>)`.
   - **Open questions** — anything unresolved.
3. **Only use what's in the notes.** Don't invent owners, dates, or decisions. If an owner
   or due date isn't stated, leave it blank rather than guessing.
4. Keep it tight — a reader should grasp the meeting in under a minute.
