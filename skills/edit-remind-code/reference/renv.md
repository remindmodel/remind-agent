# renv architecture (REMIND-specific)

- There is **no `renv.lock` in the repo root**. The main renv library lives at `renv/library/` but
  has no lockfile — it is managed manually.
- Lockfile snapshots are archived in `renv/archive/<timestamp>_renv.lock`.
- At run start, `scripts/start/submit.R` snapshots the current main library into
  `output/<run>/renv.lock`, then calls `renv::restore()` inside the run folder.
- Each run folder therefore has its **own self-contained renv** at `output/<run>/renv/library/`.
- To inspect what a run actually loaded, check `output/<run>/renv/library/` — not the main library.
- To open R with the run's renv: `renv::activate("<run_folder>")` or `cd` into the run folder
  (`.Rprofile` auto-activates).
- `cfg$UseThisRenvLock` propagates a lockfile across cascade runs.

## Debugging renv issues
- `log_renv.txt` in the run folder captures the full `renv::restore()` output. Check it when a
  package behaves as if the wrong version is installed.
- **"linked from cache"** means renv used a cached build at that SHA — if the branch was updated
  without pushing before the cache was populated, the cached copy is stale. Fix: push the branch,
  then `renv::install(..., rebuild = TRUE)`.

## Workflow for developing a pik-piam package and testing it in a REMIND run
1. Push your changes to a branch on GitHub (e.g. `tonnrueter/remindClimateAssessment@sealvl`) —
   **must be pushed before installing**.
2. From the REMIND repo root: `renv::install("tonnrueter/<package>@<branch>", rebuild = TRUE)` —
   `rebuild = TRUE` forces a fresh download even if renv has a cache entry at that SHA.
3. Do **not** run `renv::snapshot()` — this would create a `renv.lock` in the repo root that
   REMIND's workflow does not expect and may interfere with `submit.R`.
4. Verify the correct version is in the main library:
   `packageDescription("<package>")[c("RemoteRef", "RemoteSha")]`.
5. Start the REMIND run normally. `submit.R` snapshots the main library (including your dev version)
   into `output/<run>/renv.lock` and restores it into `output/<run>/renv/library/`.
6. Confirm the run used the right version:
   `grep RemoteSha output/<run>/renv/library/R-*/*/DESCRIPTION`.
