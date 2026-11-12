# remind-agent

AI-assistant context for the [REMIND](https://github.com/remindmodel/remind) model, packaged as a
self-contained **`.claude/`** bundle: a lean always-on `CLAUDE.md` plus four task skills that
auto-load by task, their reference docs and scripts, and optional slash-command shortcuts.

## What's in here

- `CLAUDE.md` — always-on base: HPC/safety rules, data hygiene (native-tools-first), and a compact
  REMIND orientation.
- `skills/` — four task skills, each a `SKILL.md` + `reference/` + (where useful) `scripts/`:
  - `debug-remind-run` — diagnose a failed/non-converged run (Cases A–F, non-convergence, TIRF).
  - `inspect-remind-gdx` — inspect a gdx / verify a gdx writer change.
  - `configure-remind-scenarios` — author/review scenario configs.
  - `edit-remind-code` — read/change GAMS/R code, compile-after-edit, pik-piam/renv.
- `commands/` — optional `/shortcuts` that jump straight into a skill's playbook.
- `scratch/` — working dir for agent temp files (contents gitignored).

## Deployment

The repo **is** the `.claude/` directory. From the root of a REMIND checkout:

```bash
git clone https://github.com/remindmodel/remind-agent.git .claude
printf '.claude/\n' >> .git/info/exclude     # keep it out of REMIND's git
rm -f CLAUDE.md                              # drop any stale root CLAUDE.md pointer, if present
```

That's the whole install — Claude Code discovers `.claude/CLAUDE.md`, `.claude/skills/`, and
`.claude/commands/` natively. No symlinks, no `@`-imports.

Optional: browse the bundle under a friendlier name with a **cosmetic** alias (tools still read the
real `.claude/`, so it never sits in a discovery path):

```bash
ln -s .claude remind-agent
```

Do **not** do the reverse (`ln -s remind-agent .claude`): a symlinked `.claude` currently breaks
skill invocation in Claude Code (`/skill` → `Unknown skill`).

## Updating

```bash
git -C .claude pull
```

## Portability (other agents)

The content is tool-neutral. **opencode** already reads `.claude/skills/` natively, so the skills
work there with no change — add a root `AGENTS.md` (or an `opencode.json` instructions entry
pointing at `.claude/CLAUDE.md`) for its always-on memory. **qwen-code** reads `AGENTS.md` / `QWEN.md`
the same way. The always-on file is kept as `CLAUDE.md` because it always loads; `AGENTS.md` is the
portable alternative but only loads on Claude Code ≥2.1.277 and is suppressed by any `CLAUDE.md`
above it.

## Scope

REMIND-only. Cross-project, machine-specific skills (madrat development, general R dev) are
personal — keep them in your own `~/.claude/skills/`, not in this shared bundle.
