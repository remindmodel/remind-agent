# TODO

## git submodule support

Allow opting in to tracking `remind-context` as a proper git submodule inside
REMIND instead of a plain untracked clone.

**Why:** a submodule records a specific commit SHA in the parent repo, so teams
can pin and bump the context version alongside code changes and have everyone
on the same version automatically after `git submodule update`.

**Trade-off:** more git ceremony (detached HEAD, `git submodule update --remote`
to advance the pointer, `.gitmodules` needs to be committed). Only worth it if
the team wants coordinated, versioned context updates — the plain-clone approach
is simpler for individual opt-in use.

**Implementation sketch:**
- Add a `-Submodule` flag to `bootstrap.ps1` / `bootstrap.sh`
- When set: use `git submodule add` + `git submodule update` instead of
  `git clone` + `git pull`; skip the `.git/info/exclude` step (submodule is
  tracked via `.gitmodules`)
- Document the trade-off in README
