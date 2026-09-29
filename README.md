# remind-context

AI-assistant context files for the [REMIND](https://github.com/remindmodel/remind)
codebase. Consumed by **GitHub Copilot** (VS Code) and **Claude Code**.

## What's in here

- [`AGENT.md`](AGENT.md) — **single source of truth**: repo-wide instructions
  (model overview, HPC environment, debugging protocol, renv workflow, …).
  Imports the topic files below via `@`-references.
- [`instructions/`](instructions/) — topic-specific deep dives
  (`gams.md`, `r.md`, `cicd.md`, `gdx.md`).
- [`prompts/`](prompts/) — on-demand task prompts
  ([`triage-failed-run.md`](prompts/triage-failed-run.md),
  [`inspect-verify-gdx.md`](prompts/inspect-verify-gdx.md)). **Not** auto-loaded;
  invoked explicitly as slash commands when needed.
- [`scripts/`](scripts/) — reusable tools referenced by the prompts (e.g.
  [`gdx_inspect.R`](scripts/gdx_inspect.R), a context-safe GDX inspector).
- `bootstrap.sh` / `bootstrap.ps1` — one-shot installer for REMIND checkouts.

## Deployment model

`remind-context` lives **inside** each REMIND checkout as a plain untracked
subdirectory — not committed, not a submodule, just a local clone:

```
<remind>/
├── .git/
├── .github/
│   └── copilot-instructions.md  <- pointer: @../remind-context/AGENT.md
├── AGENT.md                     <- pointer: @remind-context/AGENT.md
├── remind-context/              <- this repo (untracked, in .git/info/exclude)
│   ├── AGENT.md
│   ├── instructions/
│   ├── prompts/
│   └── scripts/
└── ...
```

Both Copilot and Claude Code resolve `@`-imports transitively, so the two
one-line pointer files pull in the full context without duplication.

**Multiple REMIND checkouts:** run bootstrap once per checkout — each gets its
own `remind-context/` clone. Update each independently with
`git -C remind-context pull`.

## Install

### 1. Clone this repo into your REMIND checkout

```bash
cd /path/to/remind
git clone https://github.com/tonnrueter/remind-context.git remind-context
```

### 2. Run the bootstrap script

#### Linux / macOS

```bash
bash remind-context/bootstrap.sh
```

#### Windows

```powershell
remind-context\bootstrap.ps1
```

The script:

1. Pulls the latest context (or clones if `remind-context/` isn't there yet).
2. Adds `remind-context/` to `.git/info/exclude` so it stays out of git status.
3. Writes `AGENT.md` and `.github/copilot-instructions.md` pointer files
   (only if they don't already exist).

## Updating

Pull the latest context into a checkout:

```bash
git -C remind-context pull
```

## Editing context

```bash
cd remind-context
git checkout main
# edit AGENT.md / instructions/*.md / prompts/*.md
git commit -am "..."
git push
```

## Invoking prompts

Prompts in [`prompts/`](prompts/) are **on-demand**, not auto-loaded.

- **Copilot Chat**: place a `.prompt.md` copy under `.github/prompts/` in
  REMIND, then run via `/<name>` in chat or the *Chat: Run Prompt* command.
- **Claude Code**: shim under `.claude/commands/<name>.md` containing
  `@../../remind-context/prompts/<name>.md`, invoked as `/<name>`.

(Neither shim is created by `bootstrap` — add it manually if you want prompt
parity, otherwise just open the prompt file and paste.)
