---
name: write-handoff
description: Close out a session by writing a handoff note that another agent can pick up later. Use only when the user asks for a handoff.
disable-model-invocation: true
argument-hint: "<2-4 word topic>"
---

# Writing a handoff note

Write one Markdown file that lets another agent, starting cold, continue this session's work
without asking the user anything they already answered.

## File

- Path: `.claude/scratch/HANDOFF-<YYYY-MM-DD>-<topic>.md` (seen from the REMIND root). Date = today.
  `<topic>` = the user's words after the command, else 2-4 words you choose; lowercase, joined
  with `-` (e.g. `HANDOFF-2026-11-12-damdef-nonconvergence.md`).
- If that file exists, add `-2`, `-3`, … Never overwrite or delete a handoff note.
- The folder is gitignored: the note stays on this machine.

## Content

Write for an agent, not a person: exact paths, `path:line`, commands with their key output,
numbers with units. No greetings, no story of the session. Keep it under about 80 lines.

```markdown
# Handoff: <topic>

<date> · REMIND <git rev-parse --short HEAD> · <cluster | laptop> · run: output/<run folder, if any>

## Goal
<what the user wants, in one or two sentences, in their terms>

## Where things stand
<one short paragraph: the current conclusion or state, and how sure it is>

## Established (with evidence)
- <fact> (`path:line`, or command → result)

## Ruled out
- <hypothesis> because <evidence>

## Open questions
- <question>, and what would settle it

## Next steps
1. <concrete action: the command or file to read first>

## Files
- <files read or written this session, incl. scripts in .claude/scratch/>

## Environment
<tools that were missing or behaved differently (piam tools, pandas, gdxdump path), workarounds used>

## User preferences and decisions
- <anything the user decided or asked for that the next agent must respect>
```

Leave a section out if it has nothing. Don't invent content to fill one.

## After writing

Tell the user the file's path in one line. Don't delete or move scratch files as part of the handoff.
