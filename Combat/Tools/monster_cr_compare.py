"""Quick CLI: compare monsters' power level across *different* CR tiers.

monster_score.py's score is always relative to a monster's own CR tier --
a 0.90 at CR 2 and a 0.90 at CR 15 both mean "strong for its own CR," but
say nothing about how those two monsters would actually fare against each
other. This script instead computes each monster's *implied CR*: the
continuous CR value (interpolated between official CR tiers' fitted stat
distributions) at which its raw stats would be exactly average (composite
z-score = 0). It reuses monster_score.py's ATTRS list and scored/invert
choices directly (same fitted means/stds, same excluded DMG/DPR noise), so
the two tools can't drift apart -- this just asks a different question of
the same underlying model.

Comparing implied CR (instead of assigned CR or per-tier score) puts
monsters from different CR tiers on one common scale, and the "delta"
column (implied - assigned) flags monsters that are over- or under-tuned
relative to their label -- e.g. delta +3.5 means "built more like a CR
(assigned + 3.5) monster than what its label says."

Usage (from the repo root):
    python Combat/Tools/monster_cr_compare.py "Air Elemental" "Barbed Devil"
    python Combat/Tools/monster_cr_compare.py -v "Priest of the Black Tongues"
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from Combat.Tools.generate_monster_cr_distributions import cr_key, extract_all  # noqa: E402
from Combat.Tools.monster_score import (  # noqa: E402
    ATTRS,
    SCORED_ATTR_COUNT,
    build_stats,
    find_matches,
    score_monster,
)


def build_continuous_stats(official_monsters):
    """attr_tiers[key] = sorted [(cr_num, mean, std), ...] -- the same
    per-CR-tier fitted means/stds monster_score.build_stats() computes,
    just also keyed by numeric CR (via cr_key) so they can be interpolated
    between tiers instead of only looked up at one exact tier."""
    stats = build_stats(official_monsters)
    attr_tiers = {}
    for key, _label, _invert, _scored in ATTRS:
        tiers = [
            (cr_key(cr), mean, std)
            for cr, (mean, std, _median, _lo, _hi, _n) in stats[key].items()
        ]
        tiers.sort(key=lambda t: t[0])
        attr_tiers[key] = tiers
    return attr_tiers


def _interp(tiers, cr_num):
    """Piecewise-linear interpolation of (mean, std) at cr_num from a
    sorted [(cr_num, mean, std), ...] list. Flat-extrapolates (clamps to
    the nearest known tier) outside the data's CR range -- implied_cr()
    only ever searches within that range, so this only matters for the
    exact boundary points."""
    if not tiers:
        return None, None
    if cr_num <= tiers[0][0]:
        return tiers[0][1], tiers[0][2]
    if cr_num >= tiers[-1][0]:
        return tiers[-1][1], tiers[-1][2]
    for (c0, m0, s0), (c1, m1, s1) in zip(tiers, tiers[1:]):
        if c0 <= cr_num <= c1:
            t = (cr_num - c0) / (c1 - c0) if c1 > c0 else 0.0
            return m0 + t * (m1 - m0), s0 + t * (s1 - s0)
    return tiers[-1][1], tiers[-1][2]


def composite_z(m, cr_num, attr_tiers):
    """Plain average z-score (same recipe as monster_score's "mean"
    aggregation) of m's stats against the CR-cr_num distribution
    interpolated from attr_tiers, using only ATTRS entries with
    scored=True. Returns (avg_z, k); avg_z is None if no attribute had
    usable data at that CR."""
    zs = []
    for key, _label, invert, scored in ATTRS:
        if not scored:
            continue
        v = m[key]
        if v is None:
            continue
        mean, std = _interp(attr_tiers[key], cr_num)
        if mean is None or std is None or std <= 1e-9:
            continue
        z = (v - mean) / std
        zs.append(-z if invert else z)
    return (sum(zs) / len(zs), len(zs)) if zs else (None, 0)


def implied_cr(m, attr_tiers, cr_order_nums):
    """The continuous CR at which m's composite z-score crosses zero (i.e.
    where it would be exactly average), found by bracketing a sign change
    across the official CR tiers and linearly interpolating within that
    bracket. Returns (cr_value, clamped): clamped is "low"/"high" when the
    monster is stronger/weaker than every official tier (cr_value is then
    just that tier's boundary, not a genuine root), or None for a real
    interpolated root. cr_value is None only when no attribute had usable
    data at all."""
    lo, hi = cr_order_nums[0], cr_order_nums[-1]
    f_lo, _ = composite_z(m, lo, attr_tiers)
    f_hi, _ = composite_z(m, hi, attr_tiers)
    if f_lo is None or f_hi is None:
        return None, None
    if f_lo <= 0:
        return lo, "low"
    if f_hi >= 0:
        return hi, "high"

    prev_cr, prev_f = lo, f_lo
    for cr_num in cr_order_nums[1:]:
        f, _ = composite_z(m, cr_num, attr_tiers)
        if f is None:
            continue
        if f <= 0:
            t = 0.0 if prev_f == f else prev_f / (prev_f - f)
            return prev_cr + t * (cr_num - prev_cr), None
        prev_cr, prev_f = cr_num, f
    return hi, "high"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("names", nargs="+", help='Monster name(s), e.g. "Air Elemental"')
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="show the composite z-score at every official CR tier",
    )
    args = parser.parse_args()

    data, errors = extract_all()
    for e in errors:
        print(f"warning: {e}", file=sys.stderr)
    stats = build_stats(data["monsters"])
    attr_tiers = build_continuous_stats(data["monsters"])
    cr_order_nums = sorted({cr_key(cr) for cr in data["cr_order"]})

    ok = True
    results = []
    for name in args.names:
        matches = find_matches(name, data["monsters"], data["homebrew"])
        if not matches:
            print(f'"{name}": no monster found')
            ok = False
            continue
        if len(matches) > 1:
            listed = ", ".join(m["name"] for m, _ in matches[:8])
            more = "..." if len(matches) > 8 else ""
            print(f'"{name}": {len(matches)} matches, be more specific -> {listed}{more}')
            ok = False
            continue

        m, is_homebrew = matches[0]
        assigned_cr_num = cr_key(m["cr"])
        cr_val, clamped = implied_cr(m, attr_tiers, cr_order_nums)
        scores, k, _breakdown = score_monster(m, stats)
        results.append((m, is_homebrew, assigned_cr_num, cr_val, clamped, scores, k))

    if results:
        # Sort strongest-implied-CR first so monsters from different tiers
        # line up on the one scale this tool exists to provide.
        results.sort(key=lambda r: r[3] if r[3] is not None else -1, reverse=True)

        print(f"{'Name':<32} {'CR':<7} {'Implied CR':<12} {'Delta':<8} {'Score':<7} Attrs")
        for m, is_homebrew, assigned, cr_val, clamped, scores, k in results:
            tag = "  [homebrew]" if is_homebrew else ""
            if cr_val is None:
                implied_str, delta_str = "n/a", "n/a"
            else:
                prefix = "<=" if clamped == "low" else (">=" if clamped == "high" else "")
                implied_str = f"{prefix}{cr_val:.2f}"
                delta_str = f"{cr_val - assigned:+.2f}"
            print(
                f"{m['name']:<32} {m['cr']:<7} {implied_str:<12} {delta_str:<8} "
                f"{scores['score']:<7.2f} {k}/{SCORED_ATTR_COUNT}{tag}"
            )
            if args.verbose:
                for cr_num in cr_order_nums:
                    f, n = composite_z(m, cr_num, attr_tiers)
                    f_str = f"{f:+.2f}" if f is not None else "n/a"
                    print(f"    CR {cr_num:<6} avg z {f_str:<7} ({n} attrs)")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
