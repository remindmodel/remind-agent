# Configuration resolution

REMIND's `cfg` is built by layering, later wins:
1. **Defaults** — `gms::readDefaultConfig()` reads the GAMS switches (`cfg$gms$<switch>`) from their
   `$setglobal` / `parameter` lines in **`main.gms`**, then overlays **`config/default.cfg`**, which
   holds the R/run settings (`cfg$title`, `cfg$regionmapping`, `cfg$inputRevision`, …) and no GAMS
   switch. A switch's default is therefore the value in `main.gms`.
2. **`config/scenario_config*.csv`** — one row per scenario; columns override individual fields.
   Multiple scenario configs exist (`_damages`, `_NGFS_v6c1`, `_ScenarioMIP`, …); only those
   referenced by the start command apply.
3. **Start-time R overrides** in `start.R` / `submit.R` (cascade `path_gdx_*`, `UseThisRenvLock`, …).
4. **Resolved result** is serialized to `output/<run>/cfg.txt` — single source of truth for both
   GAMS switches and the R ecosystem at runtime.

When a parameter looks wrong:
1. Read it in `output/<run>/cfg.txt` first — that's what was actually used.
2. If it disagrees with the default (`main.gms` for GAMS switches, `default.cfg` for the rest), find
   the overriding row:
   ```sh
   grep -n "<scenario_name>" config/scenario_config_*.csv
   ```
3. For structured / derived fields, reproduce the cfg construction inside the run folder so its renv
   activates. Example (climate stage):
   ```sh
   cd output/<run>
   Rscript -e 'cfg <- remindClimateAssessment::climateAssessmentConfig(getwd(), "iteration"); str(cfg)'
   ```
