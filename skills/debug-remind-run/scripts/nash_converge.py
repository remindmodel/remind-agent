#!/usr/bin/env python3
"""
nash_converge.py - diagnose a non-converged REMIND Nash run from nash_info_convergence.csv.

Why a script (no native equivalent): `nashstat` shows only the LAST iteration; `dumpgdx` shows only
the final state. This reads the per-ITERATION trajectory from the CSV (oscillation vs stall,
sign-flips, price stability).

Use when a run hit the iteration ceiling (cm_iteration_max, 100 in Nash mode) with Conv=not_converged
(Case F in the REMIND debugging guide). The question is always: WHICH market won't clear, is it
oscillating or just slow, and is the economic *answer* (prices / SCC) stable despite it.

Every Nash iteration REMIND appends per-market, per-year rows to output/<run>/nash_info_convergence.csv
(written by modules/80_optimization/nash/output.gms). Columns:
  Scenario, Region(=glob), Year, Iteration, Market, p80_surplus, p80_pvp_itr,
  p80_surplusMax_iter, p80_surplusMaxRel
  - p80_surplus          : signed residual market imbalance for that (year, market) this iteration
  - p80_pvp_itr          : present-value price used for that market/year this iteration
  - p80_surplusMax_iter  : max |surplus| up to that year  (this is what the convergence GATE compares
                           to p80_surplusMaxTolerance at 2100, and to 10x it at 2150)
  - p80_surplusMaxRel    : the same, as a PERCENT of market turnover (a scale-free diagnostic)
Markets: the tradeable goods - pecoal peoil pegas peur pebiolc (primary energy), good, perm (CO2).

This CSV is self-contained (no gdx / piam module needed) - just a python with pandas, e.g.
  /p/projects/rd3mod/python/environments/climate-assessment/bin/python

What this tool does NOT have (read it from fulldata.gdx with dumpgdx - see
the debug-remind-run skill's reference/nonconvergence.md): the tolerance values (p80_surplusMaxTolerance), which criteria
are unmet (p80_messageShow), the failing (year,market) list (p80_messageFailedMarket), per-region
solve status (nashstat), and whether a blocking market sits at a variable bound (binding => the
imbalance is trade tension, not a solver limit).

Usage:
  <python-with-pandas> .claude/skills/debug-remind-run/scripts/nash_converge.py NASH_CSV [options]
    (default)         --summary
    --summary         worst market surplus per iteration (which market/year drives non-convergence),
                      the convergence trajectory (stall vs oscillation), and the final-iteration
                      per-market worst |surplus| at 2100 / 2150 (the gated years).
    --market NAME     p80_surplus trajectory for one market at key years across iterations; flags
                      sign changes (overshoot oscillation).
    --sign-flips      scan every market/year for surplus SIGN CHANGES over the last --last iterations
                      - the fingerprint of a price-adjustment overshoot that won't damp.
    --price [M ...]   p80_pvp_itr over iterations for the named markets (default: perm good) - is the
                      price (hence the answer) stable while quantities wobble?
    --years Y [Y ...] years to report for --market/--price (default: 2050 2100 2150)
    --last K          window of final iterations for stall/sign-flip tests (default: 15)
    --stride S        print every S-th iteration in trajectories (default: 10; always shows last --last)
"""
import argparse
import sys

try:
    import pandas as pd
except ImportError:
    sys.exit("needs pandas - run with e.g. /p/projects/rd3mod/python/environments/climate-assessment/bin/python")


def load(path):
    df = pd.read_csv(path, skipinitialspace=True)
    df.columns = [c.strip() for c in df.columns]
    df = df.loc[:, [c for c in df.columns if not c.startswith("Unnamed")]]
    for c in df.select_dtypes(include="object"):
        df[c] = df[c].str.strip()
    for c in ("Year", "Iteration", "p80_surplus", "p80_pvp_itr",
              "p80_surplusMax_iter", "p80_surplusMaxRel"):
        if c in df:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.dropna(subset=["Iteration", "Year"])


def _iters_to_show(iters, stride, last):
    iters = sorted(iters)
    tail = set(iters[-last:])
    return [i for i in iters if i % stride == 0 or i in (iters[0],) or i in tail]


def summary(df, stride, last):
    iters = sorted(df.Iteration.unique())
    print(f"{len(iters)} iterations in file  (markets: {', '.join(sorted(df.Market.unique()))})\n")

    # per-iteration worst RELATIVE surplus and which (market, year) drives it
    idx = df.groupby("Iteration")["p80_surplusMaxRel"].idxmax()
    worst = df.loc[idx].set_index("Iteration")
    print("=== worst market residual per iteration (p80_surplusMaxRel = % of turnover) ===")
    print(f"{'iter':>5} {'worstRel%':>10}  {'market':<9} {'year':>5}")
    for it in _iters_to_show(iters, stride, last):
        r = worst.loc[it]
        print(f"{it:5d} {r.p80_surplusMaxRel:10.3f}  {r.Market:<9} {int(r.Year):5d}")
    tailvals = worst.loc[[i for i in iters if i in set(iters[-last:])], "p80_surplusMaxRel"]
    print(f"\nlast {last} iters: worstRel% in [{tailvals.min():.3f}, {tailvals.max():.3f}] "
          f"-> {'STALLED/OSCILLATING (not shrinking)' if tailvals.max() > 0.5 else 'small'}")

    # final-iteration per-market worst ABSOLUTE surplus at the gated years (2100, 2150)
    last_it = iters[-1]
    print(f"\n=== final iteration ({last_it}): per-market |surplus| at gated years "
          f"(compare to p80_surplusMaxTolerance from the gdx) ===")
    print(f"{'market':<9} {'max|surp|@2100':>15} {'max|surp|@2150':>15}")
    fin = df[df.Iteration == last_it]
    for m in sorted(fin.Market.unique()):
        s100 = fin[(fin.Market == m) & (fin.Year <= 2100)].p80_surplus.abs().max()
        s150 = fin[(fin.Market == m) & (fin.Year <= 2150)].p80_surplus.abs().max()
        print(f"{m:<9} {s100:15.5f} {s150:15.5f}")
    print("\nNext: dumpgdx <run>/fulldata.gdx p80_messageShow / p80_messageFailedMarket -> which "
          "criterion & (year,market) is unmet; then --sign-flips and --price.")


def market(df, name, years, stride, last):
    d = df[df.Market == name]
    if d.empty:
        sys.exit(f"market '{name}' not in file (have: {', '.join(sorted(df.Market.unique()))})")
    iters = sorted(d.Iteration.unique())
    show = _iters_to_show(iters, stride, last)
    print(f"=== {name}: p80_surplus (signed) across iterations ===")
    for y in years:
        s = d[d.Year == y].set_index("Iteration")["p80_surplus"].sort_index()
        if s.empty:
            continue
        cells = "  ".join(f"{it}:{s.get(it, float('nan')):+.4f}" for it in show if it in s.index)
        tail = s.loc[[i for i in iters if i in set(iters[-last:]) and i in s.index]]
        signs = tail[tail.abs() > 1e-6]
        flips = int((signs.apply(lambda v: 1 if v > 0 else -1).diff().abs() > 0).sum()) if len(signs) else 0
        flag = f"  <-- {flips} SIGN FLIP(S) in last {last} iters (overshoot)" if flips else ""
        print(f"  @{y}: {cells}{flag}")


def sign_flips(df, last, min_mag):
    iters = sorted(df.Iteration.unique())
    tail = set(iters[-last:])
    print(f"=== markets/years whose surplus SIGN-FLIPS in the last {last} iterations (overshoot) ===")
    print(f"    (only |surplus| >= {min_mag}; raise/lower with --min-mag; tiny wobble near "
          f"convergence is normal and filtered out)")
    rows = []
    for (m, y), g in df[df.Iteration.isin(tail)].groupby(["Market", "Year"]):
        s = g.sort_values("Iteration")["p80_surplus"]
        s = s[s.abs() > 1e-6]
        if len(s) < 2 or s.abs().max() < min_mag:
            continue
        sg = s.apply(lambda v: 1 if v > 0 else -1)
        flips = int((sg.diff().abs() > 0).sum())
        if flips:
            rows.append((s.abs().max(), flips, m, int(y)))
    if not rows:
        print(f"  none above {min_mag} - non-convergence here is a slow stall, not an overshoot")
        return
    print(f"  {'market':<9} {'year':>5} {'flips':>6} {'max|surplus|':>13}")
    for mag, flips, m, y in sorted(rows, reverse=True)[:25]:
        print(f"  {m:<9} {y:5d} {flips:6d} {mag:13.4f}")


def price(df, markets, years, stride, last):
    iters = sorted(df.Iteration.unique())
    show = _iters_to_show(iters, stride, last)
    print("=== p80_pvp_itr (present-value price) across iterations - stable price => stable answer ===")
    for m in markets:
        d = df[df.Market == m]
        if d.empty:
            print(f"  {m}: (not in file)")
            continue
        for y in years:
            s = d[d.Year == y].set_index("Iteration")["p80_pvp_itr"].sort_index()
            if s.empty:
                continue
            cells = "  ".join(f"{it}:{s.get(it):.4f}" for it in show if it in s.index)
            rng = s.max() - s.min()
            print(f"  {m} @{y}: {cells}   (range over all iters: {rng:.2e})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", help="path to output/<run>/nash_info_convergence.csv")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--market", metavar="NAME")
    ap.add_argument("--sign-flips", action="store_true", dest="sign_flips")
    ap.add_argument("--price", nargs="*", metavar="M", default=None)
    ap.add_argument("--years", nargs="+", type=int, default=[2050, 2100, 2150])
    ap.add_argument("--last", type=int, default=15)
    ap.add_argument("--stride", type=int, default=10)
    ap.add_argument("--min-mag", type=float, default=0.005, dest="min_mag",
                    help="min |surplus| for --sign-flips (default 0.005; filters near-convergence noise)")
    a = ap.parse_args()
    df = load(a.csv)

    if a.market:
        market(df, a.market, a.years, a.stride, a.last)
    elif a.sign_flips:
        sign_flips(df, a.last, a.min_mag)
    elif a.price is not None:
        price(df, a.price or ["perm", "good"], a.years, a.stride, a.last)
    else:
        summary(df, a.stride, a.last)


if __name__ == "__main__":
    main()
