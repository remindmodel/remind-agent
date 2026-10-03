#!/usr/bin/env python3
"""
tirf_lst.py - inspect pm_temperatureImpulseResponseCO2 display tables inside a GAMS full.lst.

REMIND recomputes the climate impulse response (TIRF) each iteration (iter <=10, then every 5th;
see modules/15_climate/magicc7_ar6/postsolve.gms) and `display`s pm_temperatureImpulseResponseCO2 in
the SCC / internalizeDamages postsolve block. So a run's full.lst accumulates ONE 2-D table per
iteration: pm_temperatureImpulseResponseCO2(period, pulse_year) in K/GtCO2. This tool pulls them out
so you can see WHEN the TIRF goes bad (the pulse-2020 spike / growing negative values) without
wrestling the ~GB listing by hand.

Caveat: values are read exactly as GAMS prints them - ~3 significant decimals for larger magnitudes
(e.g. -0.015), E-notation for small ones. That is precise enough to locate corruption (sign, rough
magnitude, onset iteration); for exact numbers read pm_magicc_temperatureImpulseResponse.gdx.

GAMS display shape handled:
  ----<srcline> PARAMETER pm_temperatureImpulseResponseCO2  <desc>   <- instance header
                 ( ALL   0.000 )                                     <- all-zero form
             2010        2011   ... (<=15 cols, 12-char fields)       <- first column block header
     +       2190        2191   ...                                   <- continuation column block ('+')
  2011 2.027190E-4                                                    <- data row: period then values,
  2012 3.542109E-4 2.027190E-4                                           right-justified under columns
                                                                         (omitted cell == 0)
  ...ends at the next '----<srcline> SYMBOL' (e.g. pm_damageMarginal).
  o_iterationNumber = N.000 is displayed just after -> used to tag each instance's iteration.

Usage (run with a python that has pandas, e.g. the climate-assessment conda env):
  /p/projects/rd3mod/python/environments/climate-assessment/bin/python \
      remind-context/scripts/tirf_lst.py FULL_LST [options]
    (default)            --summary
    --summary            one row per iteration: idx iter lst_line nNonzero nNeg min max allzero
    --iter N             dump the table of iteration N (period x pulse_year), strided for the terminal
    --pulse-year Y       TIRF-vs-period for pulse-year Y across ALL iterations (the "when 2020 goes bad" view)
    --csv OUT            write tidy long CSV: iter,period,pulse_year,value (every cell, all iterations)
    --symbol NAME        parse a different displayed parameter (default pm_temperatureImpulseResponseCO2)
    --max-periods K      rows to show in --iter/--pulse-year (default 26 via a year stride; 0 = all)
"""
import argparse
import re
import sys

import pandas as pd

SYM_DEFAULT = "pm_temperatureImpulseResponseCO2"
FIELD = 12  # GAMS display field width

YEAR = re.compile(r"\b(?:19|20|21|22|23)\d{2}\b")
SYMHDR = re.compile(r"^----\d+ (?:PARAMETER|VARIABLE|EQUATION|SET)\s+(\S+)")
ITERNUM = re.compile(r"^----\d+ PARAMETER o_iterationNumber\s*=\s*([0-9.]+)")
DATAROW = re.compile(r"^(\d{4}) ")                      # period label flush at column 0
COLHDR = re.compile(r"^\s+\+?\s*\d{4}(?:\s+\d{4})*\s*$")  # leading space or '+', then only years
ALLZERO = re.compile(r"\(\s*ALL\s+[-0-9.E+]+\s*\)")


def parse(path, symbol):
    """Return a list of instances; each is dict(lst_line, iter, allzero, cells{(period,py):val})."""
    instances = []
    cur = None
    cols = []  # [(pulse_year, end_char_pos)] for the current column block
    with open(path, "r", errors="replace") as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.rstrip("\n")

            m = SYMHDR.match(line)
            if m:
                if m.group(1) == symbol:
                    cur = {"lst_line": lineno, "iter": None, "allzero": False, "cells": {}}
                    instances.append(cur)
                    cols = []
                    continue
                # a different symbol ends the current instance (but let o_iterationNumber through)
                cur = None
                cols = []

            mi = ITERNUM.match(line)
            if mi:
                it = int(float(mi.group(1)))
                for inst in reversed(instances):
                    if inst["iter"] is None:
                        inst["iter"] = it
                        break
                continue

            if cur is None:
                continue

            if ALLZERO.search(line):
                cur["allzero"] = True
                continue

            if COLHDR.match(line) and not DATAROW.match(line):
                cols = [(int(mm.group(0)), mm.end()) for mm in YEAR.finditer(line)]
                continue

            dm = DATAROW.match(line)
            if dm and cols:
                period = int(dm.group(1))
                for pulse_year, end in cols:
                    s = line[end - FIELD:end].strip()
                    if not s:
                        continue  # omitted cell == 0
                    try:
                        cur["cells"][(period, pulse_year)] = float(s)
                    except ValueError:
                        pass
    return instances


def iter_label(inst, idx):
    return inst["iter"] if inst["iter"] is not None else idx


def cmd_summary(instances):
    rows = []
    for idx, inst in enumerate(instances, 1):
        vals = list(inst["cells"].values())
        if inst["allzero"] or not vals:
            rows.append(dict(idx=idx, iter=iter_label(inst, idx), lst_line=inst["lst_line"],
                             nNonzero=0, nNeg=0, min=0.0, max=0.0, allzero=True))
        else:
            rows.append(dict(idx=idx, iter=iter_label(inst, idx), lst_line=inst["lst_line"],
                             nNonzero=len(vals), nNeg=sum(1 for v in vals if v < 0),
                             min=min(vals), max=max(vals), allzero=False))
    df = pd.DataFrame(rows)
    print(f"{len(instances)} display instance(s) of the TIRF table\n")
    with pd.option_context("display.width", 160, "display.float_format", lambda v: f"{v:.3e}"):
        print(df.to_string(index=False))
    bad = df[df.nNeg > 0]
    if len(bad):
        print(f"\nfirst corrupted iteration: {int(bad.iloc[0]['iter'])} "
              f"(idx {int(bad.iloc[0]['idx'])}, nNeg={int(bad.iloc[0]['nNeg'])}, "
              f"min={bad.iloc[0]['min']:.4g})")
    else:
        print("\nno negative TIRF values found in any iteration")


def stride_rows(df, max_periods):
    """Keep <= max_periods rows by a year stride (0 => all)."""
    if max_periods and len(df) > max_periods:
        step = -(-len(df) // max_periods)  # ceil
        return df.iloc[::step]
    return df


def cmd_pulse_year(instances, y, max_periods):
    data = {}  # period -> {iter: value}
    for idx, inst in enumerate(instances, 1):
        it = iter_label(inst, idx)
        for (p, py), v in inst["cells"].items():
            if py == y:
                data.setdefault(p, {})[it] = v
    if not data:
        print(f"pulse-year {y} not present in any displayed table (shown pulse years depend on nonzeros)")
        return
    df = pd.DataFrame(data).T.sort_index().sort_index(axis=1)
    df.index.name = "period"
    print(f"TIRF(period, pulse_year={y}) across iterations (columns) [K/GtCO2]\n")
    with pd.option_context("display.width", 200, "display.max_columns", 40,
                           "display.float_format", lambda v: f"{v: .3e}"):
        print(stride_rows(df, max_periods).to_string())


def cmd_iter(instances, n, max_periods):
    chosen = next((inst for i, inst in enumerate(instances, 1)
                   if iter_label(inst, i) == n), None)
    if chosen is None:
        print(f"no instance with iter=={n} (have: "
              f"{[iter_label(inst, i) for i, inst in enumerate(instances, 1)]})")
        return
    if chosen["allzero"] or not chosen["cells"]:
        print(f"iteration {n}: ( ALL 0.000 )")
        return
    s = pd.Series(chosen["cells"])
    s.index = pd.MultiIndex.from_tuples(s.index, names=["period", "pulse_year"])
    df = s.unstack("pulse_year").sort_index().sort_index(axis=1)
    df = stride_rows(df, max_periods)                       # stride periods (rows)
    df = stride_rows(df.T, max_periods).T                   # stride pulse years (cols), same budget
    print(f"iteration {n}: pm_temperatureImpulseResponseCO2(period[rows] x pulse_year[cols]) [K/GtCO2]"
          f"  (strided; use --csv for the full matrix)\n")
    with pd.option_context("display.width", 220, "display.max_columns", 60,
                           "display.float_format", lambda v: f"{v: .3e}"):
        print(df.to_string())


def cmd_csv(instances, out):
    rows = []
    for idx, inst in enumerate(instances, 1):
        it = iter_label(inst, idx)
        for (p, py), v in inst["cells"].items():
            rows.append((it, p, py, v))
    df = pd.DataFrame(rows, columns=["iter", "period", "pulse_year", "value"])
    df = df.sort_values(["iter", "pulse_year", "period"])
    df.to_csv(out, index=False)
    print(f"wrote {len(df)} rows to {out}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("lst", help="path to a REMIND full.lst")
    ap.add_argument("--symbol", default=SYM_DEFAULT)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--summary", action="store_true", help="per-iteration health (default)")
    g.add_argument("--iter", type=int, metavar="N", help="dump the table of iteration N")
    g.add_argument("--pulse-year", type=int, metavar="Y", help="TIRF vs period for pulse-year Y across iterations")
    g.add_argument("--csv", metavar="OUT", help="write tidy long CSV of every cell")
    ap.add_argument("--max-periods", type=int, default=26, help="rows in --iter/--pulse-year (0=all)")
    args = ap.parse_args(argv)

    instances = parse(args.lst, args.symbol)
    if not instances:
        print(f"no display of '{args.symbol}' found in {args.lst}", file=sys.stderr)
        return 1

    if args.iter is not None:
        cmd_iter(instances, args.iter, args.max_periods)
    elif args.pulse_year is not None:
        cmd_pulse_year(instances, args.pulse_year, args.max_periods)
    elif args.csv:
        cmd_csv(instances, args.csv)
    else:
        cmd_summary(instances)
    return 0


if __name__ == "__main__":
    sys.exit(main())
