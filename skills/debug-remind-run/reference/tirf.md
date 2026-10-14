# Inspect the climate impulse response (TIRF) in a full.lst

Use when: a REMIND SCC / internalizeDamages run looks wrong in a climate-driven way —
an "impossible" temperature spike at a pulse year, a **negative** impulse response, or a
carbon price that flips sign — and you need to see *when* the TIRF went bad without
wrestling a ~GB `full.lst` by hand.

Background: REMIND recomputes the Temperature Impulse Response Function each iteration
(iter ≤10, then every 5th; `modules/15_climate/magicc7_ar6/postsolve.gms`) and `display`s
`pm_temperatureImpulseResponseCO2(period, pulse_year)` [K/GtCO2] in the postsolve block, so
a run's `full.lst` accumulates **one table per iteration**. The healthy invariant: for every
`period >= pulse_year`, TIRF **> 0** (a CO2 pulse warms). A negative TIRF is corruption — a
baseline temperature that came back too high — and feeds a perverse "emit to cool" signal into
the SCC. One known root cause: a shared-SCEN7-dir race in `openscm_runner` letting a concurrent
run clobber this run's emissions (see any `HANDOFF-*SCEN7*` doc in the workspace).

Shell prep: needs a python with pandas. The climate-assessment conda env has it:
`/p/projects/rd3mod/python/environments/climate-assessment/bin/python`.

## Tool
`<python-with-pandas> remind-context/scripts/tirf_lst.py <full.lst> [option]`
- (default) `--summary` — one row per iteration: `idx iter lst_line nNonzero nNeg min max allzero`,
  then the **first corrupted iteration** (first with `nNeg > 0`). Start here.
- `--pulse-year Y` — TIRF vs period for pulse year `Y` across **all** iterations (the
  "when does pulse-2020 go bad" view); shows onset and whether it worsens over time.
- `--iter N` — dump iteration `N`'s table (period × pulse_year), strided for the terminal.
- `--csv OUT` — tidy long CSV (`iter,period,pulse_year,value`) of every cell, all iterations.
- `--symbol NAME` — parse a different displayed parameter.
- `--max-periods K` — rows shown in `--iter`/`--pulse-year` (default 26 via a year stride; 0 = all).

## Reading it
- **`nNeg > 0` is the alarm.** Onset iteration and severity vary per run; mild corruption
  (min ≈ −0.002) is often tolerated, severe (min ≈ −0.4) correlates with Intermediate-Infeasible
  aborts. The **final gdx reflects the last recompute only**, so a clean final table does not
  prove the run was clean throughout — scan all iterations.
- Values are read as GAMS prints them (~3 sig. decimals; E-notation for small). Precise enough
  for sign / rough magnitude / onset; for exact numbers read the gdx.

## Cross-check against the gdx (exact values)
`pm_magicc_temperatureImpulseResponse.gdx` (written by `climateAssessmentImpulseResponse.R`)
holds the exact interpolated TIRF. Inspect it with the gdx playbook
(`remind-context/prompts/inspect-verify-gdx.md`, tool `gdx_inspect.R`); the parameter is over
`(tall, tall)` and is large — never dump it, use the tool. The R script now also guards the
invariant (`tirf > 0` for `period >= year_pulse`) and aborts before writing a poisoned gdx, so a
run that tripped the guard will have **no** gdx and a clear message in `log_climate.txt`.
