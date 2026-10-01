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

## Deployment model

`remind-context` lives **inside** each REMIND checkout as a plain untracked
clone. A one-line `CLAUDE.md` in the REMIND root points to it; Claude Code
reads `CLAUDE.md` (not `AGENT.md`) and resolves `@`-imports transitively:

```
<remind>/
├── CLAUDE.md          <- one line: @remind-context/AGENT.md
├── remind-context/    <- this repo
│   ├── AGENT.md
│   ├── instructions/
│   ├── prompts/
│   └── scripts/
└── ...
```

Both stay out of REMIND's git status via `.git/info/exclude`. A pointer, not a
copy, so pulling this repo updates the context.

## Install

In the root of each REMIND checkout:

```bash
git clone https://github.com/tonnrueter/remind-context.git remind-context
echo '@remind-context/AGENT.md' > CLAUDE.md
printf 'remind-context/\nCLAUDE.md\n' >> .git/info/exclude
```

If the checkout already has a `CLAUDE.md`, add the `@remind-context/AGENT.md`
line to it instead of overwriting it.

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
