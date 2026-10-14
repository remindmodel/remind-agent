# remind-context

AI-assistant context for the [REMIND](https://github.com/remindmodel/remind) model: a lean
always-on `CLAUDE.md` plus four Claude Code **skills** that auto-load by task.

## What's in here

- [`CLAUDE.md`](CLAUDE.md) — always-on base: HPC/safety rules, data hygiene (native-tools-first),
  and a compact REMIND orientation. Everything else loads only when a task calls for it.
- [`skills/`](skills/) — four task skills, each a `SKILL.md` + its own `reference/` docs + `scripts/`:
  - `debug-remind-run` — diagnose a failed/non-converged run (Cases A–F, non-convergence, TIRF,
    climate). Scripts: `nash_converge.py`, `tirf_lst.py`.
  - `inspect-remind-gdx` — inspect a gdx / verify a gdx writer change. Script: `gdx_inspect.R`.
  - `configure-remind-scenarios` — author/review scenario configs. Script: `scenario_switches.py`.
  - `edit-remind-code` — read/change GAMS/R code, compile-after-edit, pik-piam/renv.
- [`commands/`](commands/) — optional `/shortcuts` that force a specific playbook when you don't
  want to wait for a skill to auto-trigger.

## Deployment

`remind-context` lives inside each REMIND checkout as an untracked clone. Symlink its pieces into
the places Claude Code discovers them (so `git pull` keeps the deployed context current), and keep
them out of REMIND's git. From the REMIND checkout root:

```bash
git clone https://github.com/tonnrueter/remind-context.git remind-context

# always-on base (or append its contents to an existing CLAUDE.md)
ln -s remind-context/CLAUDE.md CLAUDE.md

# skills + commands
mkdir -p .claude/skills .claude/commands
for s in remind-context/skills/*/; do ln -s "../../$s" ".claude/skills/$(basename "$s")"; done
for c in remind-context/commands/*.md; do ln -s "../../$c" ".claude/commands/$(basename "$c")"; done

# keep all of it out of REMIND's git
printf 'remind-context/\nCLAUDE.md\n.claude/\n' >> .git/info/exclude
```

Skills are discovered at `.claude/skills/<name>/SKILL.md` — verify that path against your Claude
Code version before relying on the exact symlink commands above.

Optional companion: [remind-rag](https://github.com/tonnrueter/remind-rag), a local search index
over the REMIND source served as MCP tools. The context works without it.

## Scope

This repo is **REMIND-only**. Cross-project, machine-specific skills (e.g. madrat development,
general R dev) are personal — keep them in your own `~/.claude/skills/`, not here.

## Scratch

Agent temp files, intermediate outputs, and scratch scripts go in `scratch/` (gitignored). Delete
them when the task is done; move a report you want to keep out of `scratch/`.

## Updating

```bash
git -C remind-context pull    # symlinked deployments pick it up automatically
```
