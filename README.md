# remind-context

AI-assistant context files for the [REMIND](https://github.com/remindmodel/remind)
codebase. Consumed by **GitHub Copilot** (VS Code) and **Claude Code**.

## What''s in here

- [``AGENT.md``](AGENT.md) — **single source of truth**: repo-wide instructions
  (model overview, HPC environment, debugging protocol, renv workflow, …).
  Imports the topic files below via ``@``-references.
- [``instructions/``](instructions/) — topic-specific deep dives
  (``gams.md``, ``r.md``, ``cicd.md``).
- [``prompts/``](prompts/) — on-demand task prompts (e.g.
  [``triage-failed-run.md``](prompts/triage-failed-run.md)). **Not** auto-loaded;
  invoked explicitly as slash commands when needed.
- [``copilot-instructions.md``](copilot-instructions.md) — thin shim
  (``@AGENT.md``) so Copilot keeps working if anyone reads this repo directly.
- ``bootstrap.sh`` / ``bootstrap.ps1`` — one-shot installer for REMIND checkouts.

## Deployment model

``remind-context`` is **not** distributed with REMIND. Devs who want AI context
opt in by adding it as a git submodule inside their REMIND checkout:

```
<remind>/
├── .git/
├── .github/
│   └── copilot-instructions.md    <- pointer:  @../remind-context/AGENT.md
├── AGENT.md                        <- pointer:  @remind-context/AGENT.md
├── remind-context/                 <- this repo, as a submodule
│   ├── AGENT.md
│   ├── instructions/
│   └── prompts/
└── ...
```

Both Copilot and Claude Code resolve ``@``-imports transitively, so the two
one-line pointer files pull in the full context without duplication.

The submodule, ``.gitmodules``, and the pointer files stay **untracked in
REMIND** — this is intentional and matches the previous "copy and ignore"
workflow.

## Install in a REMIND checkout

### Linux / macOS

```bash
cd /path/to/remind
/path/to/remind-context/bootstrap.sh
```

### Windows

```powershell
cd C:\path\to\remind
C:\path\to\remind-context\bootstrap.ps1
```

The script:

1. Adds ``remind-context`` as a submodule at ``<remind>/remind-context``.
2. Writes ``<remind>/AGENT.md`` and ``<remind>/.github/copilot-instructions.md``
   pointer files (only if they don''t already exist).

## Updating

Pull the latest context into a REMIND checkout:

```bash
git submodule update --remote remind-context
```

## Editing context (round-trip)

Submodules check out a detached HEAD by default. Move to a branch first:

```bash
cd <remind>/remind-context
git checkout main
# edit AGENT.md / instructions/*.md / prompts/*.md
git commit -am "..."
git push
```

Then either bump the pointer in your REMIND checkout
(``git submodule update --remote remind-context`` from REMIND root) or just
leave it — other devs pull on their own schedule.

## Invoking prompts

Prompts in [``prompts/``](prompts/) are **on-demand**, not auto-loaded.

- **Copilot Chat**: place a ``.prompt.md`` copy under ``.github/prompts/`` in
  REMIND, then run via ``/<name>`` in chat or the *Chat: Run Prompt* command.
- **Claude Code**: shim under ``.claude/commands/<name>.md`` containing
  ``@../../remind-context/prompts/<name>.md``, invoked as ``/<name>``.

(Neither shim is created by ``bootstrap`` — add it manually if you want prompt
parity, otherwise just open the prompt file and paste.)
