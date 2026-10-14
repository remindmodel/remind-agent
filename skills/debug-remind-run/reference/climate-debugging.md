# Climate-assessment debugging (`log_climate.txt`)

Only consult `log_climate.txt` after `log.txt` has been triaged and points at the climate stage.
Typical wrapper error in `log.txt`:
`climateAssessmentInterimRun.R: Climate assessment output file not found` — that's a *symptom*; the
real traceback is in `log_climate.txt`.

Structure of `log_climate.txt`:
- **Config block at the top** echoes the resolved climate stage `cfg`: `mode`, `scenario`,
  `condaEnv`, `magiccBin`, `variablesFile`, `infillingDatabase`, **`probabilisticFile`**, emission
  file paths, `nSets`. Read this first — it shows which MAGICC binary and which parset the run
  *actually* used, regardless of what `default.cfg` says.
- **`condaRun` blocks** — for each Python sub-step (`run_harm_inf.py`, `runOpenSCM.py`) the log lists
  the exported env vars (`MAGICC_EXECUTABLE_7`, `MAGICC_WORKER_ROOT_DIR`, `MAGICC_WORKER_NUMBER`) and
  the full command line including `--probabilistic-file`. For fresh runs all relevant env vars are
  also dumped near the top. Cross-check these against the config block.
- **Pipeline order is fixed**: harmonize → infill → OpenSCM/MAGICC. Errors like `ValueError: No runs
  to append` from `openscm_runner` are aggregator symptoms — every MAGICC worker died, so there was
  nothing to concatenate. Root cause is upstream.
- **MAGICC failures** surface as `magicc run failed: b"…"` followed by a Fortran backtrace. The path
  inside that backtrace points at the MAGICC source tree the binary was built from — useful for
  telling stock vs. fork apart.

Binary ↔ parset compatibility caveat:
- A MAGICC fork that adds new CFG keys requires a matching parset variant. Pointing such a binary at
  a stock parset can leave keys unset and produce `Cannot open file ''` from `read_allcfg` (Fortran
  `open('')`). Always verify `magiccBin` and `probabilisticFile` line up — both are visible in the
  config block at the top of `log_climate.txt` and (resolved) in `cfg.txt`.
