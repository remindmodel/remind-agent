# pik-piam dependencies

REMIND depends on a family of R packages maintained at https://github.com/pik-piam/. They are
installed via `renv` — there are no local checkouts. Treat them as third-party libraries.
Non-pik-piam dependencies (e.g. `callr`, `ggplot2`, `testthat`) are standard CRAN packages — do not
look for them on pik-piam.

Key packages and their roles:
| Package | Role | GitHub |
|---|---|---|
| `remind2` | R reporting layer — reads GDX, produces `.mif` | https://github.com/pik-piam/remind2 |
| `magclass` | Core array class for spatio-temporal data | https://github.com/pik-piam/magclass |
| `piamInterfaces` | Variable mapping / IIASA template handling | https://github.com/pik-piam/piamInterfaces |
| `piamenv` | Python/conda environment management | https://github.com/pik-piam/piamenv |
| `piamutils` | Shared utilities across piam packages | https://github.com/pik-piam/piamutils |
| `piamPlotComparison` | Scenario comparison plots | https://github.com/pik-piam/piamPlotComparison |
| `lucode2` | Run management, config, job submission | https://github.com/pik-piam/lucode2 |
| `mip` | Model intercomparison plots | https://github.com/pik-piam/mip |
| `magpie4` | MAgPIE output reporting helpers | https://github.com/pik-piam/magpie4 |
| `magpiesets` | Regional/sectoral set definitions | https://github.com/pik-piam/magpiesets |
| `edgeTransport` | Transport sector input data | https://github.com/pik-piam/edgeTransport |
| `reporttransport` | Transport sector reporting | https://github.com/pik-piam/reporttransport |
| `gdx` / `gdxrrw` | GDX file I/O bridge between GAMS and R | https://github.com/pik-piam/gdx |
| `gdxdt` | GDX to data.table helpers | https://github.com/pik-piam/gdxdt |
| `GDPuc` | GDP unit conversion | https://github.com/pik-piam/GDPuc |
| `luplot` | Plotting utilities | https://github.com/pik-piam/luplot |
| `luscale` | Scaling/aggregation helpers | https://github.com/pik-piam/luscale |
| `lusweave` | PDF report generation | https://github.com/pik-piam/lusweave |
| `madrat` | Data preprocessing framework | https://github.com/pik-piam/madrat |
| `gms` | GAMS modularization toolkit — provides the module/realization code structure and naming conventions that MAgPIE and REMIND are built on; monitors compliance with modular coding guidelines | https://github.com/pik-piam/gms |
| `quitte` | Tidy data helpers for IAM data | https://github.com/pik-piam/quitte |
| `rmndt` | Transport data utilities | https://github.com/pik-piam/rmndt |
| `remindClimateAssessment` | Climate assessment / MAGICC integration | https://github.com/pik-piam/remindClimateAssessment |
| `modelstats` | Run statistics collection | https://github.com/pik-piam/modelstats |
| `lpjclass` | LPJmL data class | https://github.com/pik-piam/lpjclass |
| `goxygen` | GAMS code documentation | https://github.com/pik-piam/goxygen |

## When a traceback bottoms out in a pik-piam package
1. Ask the user to paste the relevant function source: `getAnywhere(<function>)` or browse
   `https://github.com/pik-piam/<package>/blob/main/R/<function>.R`.
2. Check the package's GitHub **Issues** and **Releases/Changelog** for the installed version.
3. Check whether the installed version in `renv.lock` is current — a newer version may have the fix.
4. Only escalate to assuming a REMIND-side bug if the package is behaving correctly per its own spec.
5. Do **not** suggest cloning these repos locally — reference GitHub URLs only.
