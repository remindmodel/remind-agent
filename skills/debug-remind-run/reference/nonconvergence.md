# Diagnose a non-converged REMIND Nash run (Case F)

Use when a run **finished but did not converge** — it hit the iteration ceiling
(`cm_iteration_max`, overwritten to 100 in Nash mode) with `Conv = not_converged`, modelstat 1/2.
This is Case F in `tutorials/10_DebuggingREMIND.md` / the remind-model skill. The goal is not "make it
converge" (that is a tuning/scenario decision for the run's owner) — it is to say **which market or
region won't settle, whether it is oscillating or just slow, whether the cause is economic (a binding
bound / trade tension) or numeric (a region's solver), and whether the run's answer is usable anyway.**

Shell: on the cluster the gdx steps need the piam module (`source /p/system/modulefiles/defaults/piam/module_load_piam`)
for `dumpgdx` / `nashstat`. Elsewhere use `gdxdump` and `p80_repy` instead (debug-remind-run
SKILL.md, "Without the piam tools"). The CSV tool needs a python with pandas
(`/p/projects/rd3mod/python/environments/climate-assessment/bin/python`).

## Tools
- `nash_converge.py <run>/nash_info_convergence.csv [opt]` — the per-iteration convergence story from
  the structured CSV (no gdx needed):
  - (default) `--summary` — worst market residual per iteration (`p80_surplusMaxRel`, % of turnover:
    which market/year drives it), the trajectory (shrinking vs **stalled/oscillating**), and the
    final-iteration per-market worst `|p80_surplus|` at the **gated years 2100 / 2150**.
  - `--sign-flips [--min-mag M]` — markets/years whose surplus **changes sign** in the last iterations:
    the fingerprint of a price-adjustment overshoot that won't damp (vs a monotone stall). Filters
    near-convergence noise below `M` (default 0.005).
  - `--market NAME` — one market's signed `p80_surplus` over iterations at key years, flags sign flips.
  - `--price [M ...]` — `p80_pvp_itr` over iterations (default `perm good`): **flat price ⇒ the answer
    is stable** even if quantities wobble.
- `dumpgdx <run>/fulldata.gdx <symbol> "<regex>"` — exact values the CSV doesn't carry (always filter).

## Workflow
1. **Confirm the case.** `nashstat` (in the run folder) → modelstat 1/2, some regions `terminated by
   solver / feasible solution` (= modelstat 7). `o_iterationNumber` = `cm_iteration_max` ⇒ hit the
   ceiling.
2. **Which criterion is unmet?** `dumpgdx fulldata.gdx p80_messageShow ".*"`. The set
   `convMessage80` = `surplus` (a market won't clear), `infes` (a region modelstat ∉ {2,7}),
   `nonopt` (a status-7 region whose objval dropped > `cm_nashObjVal_tolerance`=1e-4 below its last
   optimal), plus for policy/SCC runs `taxconv`, `damage`, `DevPriceAnticip`. This tells you which
   branch of `modules/80_optimization/nash/postsolve.gms` to follow.
3. **Which market / year?** `dumpgdx fulldata.gdx p80_messageFailedMarket ".*"` → the exact
   `(year, market)` cells above tolerance. Cross-check with `nash_converge.py --summary` (note: the
   `--summary` relative view flags thin markets like `peur`/`peoil`; the GATE is absolute, so trust
   `p80_messageFailedMarket` + the final-iter absolute table for the real blocker). `good` often has
   the biggest raw swing but a looser tolerance (`p80_surplusMaxTolerance("good")` ≈ 0.02 vs ≈ 0.0095
   for PE at `cm_nash_autoconverge=2`) so it may wobble without failing.
4. **Oscillation or stall?** `nash_converge.py --sign-flips` and `--market <blocker>`. Sign flips =
   overshoot (the price update is too aggressive for that market); monotone-but-above-tol = slow.
5. **Economic (trade tension) or numeric (solver)?** — the key fork:
   - **Trade tension**: the blocking market's variable sits at a **bound**, so supply is inelastic and
     Nash can only reshuffle a fixed quantity → surplus overshoots. Confirm: `dumpgdx fulldata.gdx
     vm_<var> "<regex>"` shows level at its `.up`/`.lo` with a **nonzero marginal** across regions, and
     the governing switch is active (e.g. `pebiolc` ↔ `cm_maxProdBiolc` 100 EJ/yr bound in
     `modules/30_biomass/magpie/bounds.gms`; total production pinned at the cap). Report the bound, not
     a "fix".
   - **Solver**: `nashstat` shows modelstat-7 regions; `dumpgdx fulldata.gdx p80_convNashObjVal_iter
     ".*"` → per-region objval deviation per iteration. **Tiny** deviations (≈1e-4) ⇒ regions are
     solving fine and the status-7 is a *downstream* symptom of the moving trade point (still trade
     tension). **Large, persistent** negative deviations ⇒ a genuinely struggling region (then look at
     CONOPT: `conopt3.opt`, `resusd` vs `reslim`).
6. **Is the answer usable anyway?** `nash_converge.py --price` (flat `perm`/`good` price ⇒ stable).
   For SCC / `internalizeDamages` runs also check the damage loop converged independently of the
   markets: `dumpgdx fulldata.gdx p80_sccConvergenceMaxDeviation_iter ".*"` and `p80_gmt_conv_iter`
   (tolerance `cm_sccConvergence`, e.g. 0.05 %). If the SCC/GMT deviation is below tolerance and the
   price is flat, the non-convergence is confined to quantity reshuffling and the SCC is robust; if the
   `damage`/`taxconv` criteria are unmet and GMT deviation is high, the climate/damage loop itself has
   not settled and the result is *not* reliable.

## dumpgdx cheat-sheet (all on `<run>/fulldata.gdx`; without piam: `gdxdump fulldata.gdx Symb=<symbol> Format=csv`)
- `p80_messageShow ".*"` — which criteria unmet (step 2)
- `p80_messageFailedMarket ".*"` — failing (year, market) cells (step 3)
- `p80_surplusMaxTolerance ".*"` — per-market tolerance (set by `cm_nash_autoconverge`: 2 = fine/prod)
- `p80_convNashObjVal_iter ".*"` — per-region, per-iteration objval deviation (step 5 solver test)
- `p80_sccConvergenceMaxDeviation_iter ".*"` / `p80_gmt_conv_iter ".*"` — SCC / GMT loop (step 6)
- `o_iterationNumber ".*"` — iterations run

## Reading it
- `surplus` + a single failing PE market that **sign-flips** while `perm`/`good` prices and the SCC are
  flat ⇒ a **binding-bound trade oscillation** (e.g. biomass at `cm_maxProdBiolc`); the run's price/SCC
  answer is usable, convergence is cosmetic. Report the bound to the run owner.
- `surplus` across **many** markets (`good`, fossils, biomass) **and** `damage`/`taxconv` unmet with
  high `p80_gmt_conv_iter` ⇒ the policy/climate feedback is too strong to settle at this forcing
  (e.g. a high-ECS parset or high-damage spec); the answer is **not** settled. Still a scenario/tuning
  matter, not necessarily a code bug — say so and hand the specifics (markets, criteria, magnitudes) to
  the owner.
