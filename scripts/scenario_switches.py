#!/usr/bin/env python3
"""
scenario_switches.py - list the NON-DEFAULT switches in a REMIND scenario config.

A REMIND scenario config (config/scenario_config*.csv, ';'-separated) has one column per switch
and one row per scenario. An EMPTY cell means "inherit the default"; a non-empty cell OVERRIDES
the default. This tool resolves each switch's default from the SAME REMIND checkout the config
lives in - so SCC / fork-only switches (e.g. cm_scc_weight_matrix, cm_dr_scc_scen) resolve
correctly, which a stale central code index cannot do - and reports, per scenario, which switches
are actually set away from their default.

Defaults are resolved in this order (first hit wins):
  1. main.gms  `$setGlobal <name> <val> !! def = <default>`  -> the `def =` annotation
     (covers module selections like climate/damages AND cm_*/c_* macro switches)
  2. main.gms  `$setGlobal <name> <val>` with no `def =`      -> the literal <val> is the default
  3. main.gms  scalar assignment `<name> = <value>;`          -> e.g. `cm_dr_scc_scen = 0;`
  4. default.cfg  `cfg$<name> <- <value>` / `cfg$gms$<name> <- <value>`  (cfg-level settings)
Columns with no resolvable default are reported in a separate "unknown default" block rather than
silently dropped - an unknown default usually means a fork-only switch or a non-switch column.

Run-identity / input-path columns are skipped by default (title, start, description, path_gdx*).

Usage (any python3, no third-party deps):
  scenario_switches.py CONFIG.csv [options]
    --remind-root DIR   REMIND checkout holding main.gms + config/default.cfg
                        (default: two levels up from CONFIG.csv)
    --all               every scenario row (default: only rows with start == 1)
    --scenario NAME     only this scenario title (repeatable); implies selecting across all rows
    --show-redundant    also list cells that are set but EQUAL the default (redundant overrides)
    --unknown           also list columns whose default could not be resolved
"""
import argparse
import csv
import os
import re
import sys

# columns that are run identity or input paths, never "switches"
SKIP = {
    "title", "start", "description",
    "path_gdx", "path_gdx_ref", "path_gdx_bau",
    "path_gdx_refpolicycost", "path_gdx_carbonprice",
}

SETGLOBAL = re.compile(r"^\s*\$setglobal\s+(\S+)\s*(.*)$", re.IGNORECASE)
DEF_ANNO = re.compile(r"^\s*def\s*=\s*(.*?)\s*$")
# scalar / preloop assignment of a simple numeric or quoted value: `name = 0 ;`
SCALAR = re.compile(r'^\s*([A-Za-z]\w*)\s*=\s*("[^"]*"|[-+]?[0-9][0-9.eE+-]*)\s*;')
# default.cfg: cfg$name <- value   or   cfg$gms$name <- value
CFGLINE = re.compile(r"^\s*cfg\$(?:gms\$)?([A-Za-z0-9_.]+)\s*<-\s*(.*?)\s*$")


def _unquote(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        s = s[1:-1]
    return s.strip()


def parse_defaults(remind_root):
    """Return (defaults: name->(value, source), raw_sources: for reporting)."""
    defaults = {}
    main_gms = os.path.join(remind_root, "main.gms")
    default_cfg = os.path.join(remind_root, "config", "default.cfg")

    scalar_defaults = {}
    if os.path.isfile(main_gms):
        with open(main_gms, "r", errors="replace") as fh:
            for line in fh:
                m = SETGLOBAL.match(line)
                if m:
                    name = m.group(1)
                    rest = m.group(2)
                    segments = rest.split("!!")
                    value = segments[0].strip()
                    dflt = None
                    for seg in segments[1:]:
                        dm = DEF_ANNO.match(seg)
                        if dm:
                            dflt = dm.group(1).strip()
                            break
                    chosen = dflt if dflt is not None else value
                    defaults[name] = (_unquote(chosen), "main.gms:setGlobal")
                    continue
                sm = SCALAR.match(line)
                if sm:
                    scalar_defaults[sm.group(1)] = _unquote(sm.group(2))
        # scalar assignments only fill names not already set as a setGlobal
        for name, val in scalar_defaults.items():
            defaults.setdefault(name, (val, "main.gms:scalar"))

    if os.path.isfile(default_cfg):
        with open(default_cfg, "r", errors="replace") as fh:
            for line in fh:
                if line.lstrip().startswith("#"):
                    continue
                m = CFGLINE.match(line)
                if m:
                    name = m.group(1)
                    val = m.group(2).split("#")[0].strip().rstrip(",")
                    defaults.setdefault(name, (_unquote(val), "default.cfg"))
    return defaults


def read_config(path):
    with open(path, "r", errors="replace", newline="") as fh:
        rows = list(csv.reader(fh, delimiter=";"))
    # drop fully-empty and comment (#...) rows, keep the first non-comment as header
    header = None
    data = []
    for r in rows:
        if not any(c.strip() for c in r):
            continue
        if header is None:
            header = [c.strip() for c in r]
            continue
        if r and r[0].strip().startswith("#"):
            continue
        data.append(r)
    return header, data


def norm(v):
    v = _unquote(v)
    # numeric-equivalence so "0" == "0.0" == "0."
    try:
        return ("num", float(v))
    except (ValueError, TypeError):
        return ("str", v)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config", help="path to a REMIND scenario_config*.csv (';'-separated)")
    ap.add_argument("--remind-root", default=None,
                    help="REMIND checkout with main.gms (default: two levels up from CONFIG)")
    ap.add_argument("--all", action="store_true", help="all rows (default: start==1 only)")
    ap.add_argument("--scenario", action="append", default=[], help="only this title (repeatable)")
    ap.add_argument("--show-redundant", action="store_true",
                    help="also show cells set but equal to the default")
    ap.add_argument("--unknown", action="store_true",
                    help="also show columns whose default could not be resolved")
    args = ap.parse_args(argv)

    cfg_path = os.path.abspath(args.config)
    root = args.remind_root or os.path.dirname(os.path.dirname(cfg_path))
    root = os.path.abspath(root)

    defaults = parse_defaults(root)
    if not defaults:
        print(f"warning: no defaults parsed from {root} (main.gms/default.cfg missing?)",
              file=sys.stderr)

    header, data = read_config(cfg_path)
    if header is None:
        print(f"no header row in {cfg_path}", file=sys.stderr)
        return 1
    try:
        i_title = header.index("title")
    except ValueError:
        i_title = 0
    i_start = header.index("start") if "start" in header else None

    def cell(row, i):
        return row[i].strip() if i is not None and i < len(row) else ""

    # select scenarios
    selected = []
    for row in data:
        title = cell(row, i_title)
        if args.scenario:
            if title in args.scenario:
                selected.append(row)
        elif args.all:
            selected.append(row)
        elif i_start is not None and cell(row, i_start) in ("1", "1.0"):
            selected.append(row)
    if not selected:
        where = ("titles " + ", ".join(args.scenario)) if args.scenario else (
            "all rows" if args.all else "rows with start==1")
        print(f"no scenarios matched ({where})", file=sys.stderr)
        return 1

    print(f"config      : {cfg_path}")
    print(f"remind-root : {root}  ({len(defaults)} switch defaults parsed)")
    print(f"scenarios   : {len(selected)}"
          f"{'' if args.all or args.scenario else ' (start==1; use --all for every row)'}\n")

    switch_cols = [(i, h) for i, h in enumerate(header) if h and h not in SKIP]
    pad = max((len(h) for _, h in switch_cols), default=10)

    for row in selected:
        title = cell(row, i_title)
        start = cell(row, i_start) if i_start is not None else "?"
        print(f"### {title}  (start={start})")
        overrides, redundant, unknown = [], [], []
        for i, h in switch_cols:
            v = cell(row, i)
            if v == "":
                continue  # empty => inherit default
            if h not in defaults:
                unknown.append((h, v))
                continue
            d = defaults[h][0]
            if norm(v) == norm(d):
                redundant.append((h, v, d))
            else:
                overrides.append((h, v, d))
        if overrides:
            for h, v, d in overrides:
                print(f"  {h:<{pad}}  {v:<22} (default: {d if d != '' else '<empty>'})")
        else:
            print("  (no non-default switches)")
        if args.show_redundant and redundant:
            print("  -- set but equal to default (redundant):")
            for h, v, d in redundant:
                print(f"  {h:<{pad}}  {v}")
        if args.unknown and unknown:
            print("  -- unknown default (fork-only switch or non-switch column):")
            for h, v in unknown:
                print(f"  {h:<{pad}}  {v}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
