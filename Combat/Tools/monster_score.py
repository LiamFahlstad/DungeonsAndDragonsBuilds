"""Quick CLI: print a monster's CR-relative power score.

Same statistical model as generate_monster_cr_distributions.py -- each CR
tier's mean and standard deviation (HP, AC, the six ability scores, attack
roll bonus, damage per hit, multiattack-aware damage per round,
per-ability saving throw modifiers, save DC, action economy, and
defensive tags) are fit from
the *official* monsters.py stat blocks only, then the monster you name
(official or homebrew) is scored by how many standard deviations its stats
sit from that tier's mean (0.5 = exactly average for its CR).

Those per-attribute z-scores are combined into a single number several
different ways (see AGGREGATIONS below) -- "score" is the original combined
significance score, the rest are alternate views of the same underlying
z-scores, printed alongside it.

Usage (from the repo root):
    python Combat/Tools/monster_score.py "Air Elemental" "Barbed Devil"
    python Combat/Tools/monster_score.py --verbose "Priest of the Black Tongues"
"""

import argparse
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from Combat.Tools.generate_monster_cr_distributions import extract_all  # noqa: E402

# (key, label, invert, scored) -- invert=True means "lower is better" (e.g.
# fewer vulnerabilities), so its z is flipped before scoring/display so
# positive always means "better," consistently across every attribute.
# scored=False means the attribute is still shown (in the -v breakdown) but
# excluded from every aggregate score: DMG/DPR are read straight off
# freeform ability text via a fragile regex fallback and swing wildly with
# multiattack phrasing, so they're informative to look at but too noisy to
# let drive "how good is this monster."
ATTRS = [
    ("hp", "HP", False, True),
    ("ac", "AC", False, True),
    ("str", "STR", False, True),
    ("dex", "DEX", False, True),
    ("con", "CON", False, True),
    ("int", "INT", False, True),
    ("wis", "WIS", False, True),
    ("cha", "CHA", False, True),
    ("atk", "ATK", False, True),
    ("dmg", "DMG", False, False),
    ("dpr", "DPR", False, False),
    ("strsave", "STR-SV", False, True),
    ("dexsave", "DEX-SV", False, True),
    ("consave", "CON-SV", False, True),
    ("intsave", "INT-SV", False, True),
    ("wissave", "WIS-SV", False, True),
    ("chasave", "CHA-SV", False, True),
    ("dc", "DC", False, True),
    ("condimm", "C-IMM", False, True),
    ("dmgimm", "D-IMM", False, True),
    ("dmgres", "D-RES", False, True),
    ("dmgvuln", "D-VULN", True, True),
    ("actions", "ACT", False, True),
    ("bonusact", "B-ACT", False, True),
    ("speed", "SPD", False, True),
]
SCORED_ATTR_COUNT = sum(1 for _key, _label, _invert, scored in ATTRS if scored)


def build_stats(official_monsters):
    """stats[attr][cr] = (mean, std, median, min, max, n), fit from official monsters only."""
    by_cr = {}
    for m in official_monsters:
        by_cr.setdefault(m["cr"], []).append(m)

    stats = {key: {} for key, _label, _invert, _scored in ATTRS}
    for cr, group in by_cr.items():
        for key, _label, _invert, _scored in ATTRS:
            values = [m[key] for m in group if m[key] is not None]
            if len(values) >= 2:
                # Sample standard deviation (n-1), matching groupStats() in
                # the HTML report's JS -- keep these two tools' numbers in sync.
                stats[key][cr] = (
                    statistics.mean(values),
                    statistics.stdev(values),
                    statistics.median(values),
                    min(values),
                    max(values),
                    len(values),
                )
    return stats


def normal_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


# (key, label) -- ways to collapse a monster's per-attribute z-scores (one
# per ATTRS entry, positive always meaning "better") into a single 0-1
# power score. "score" is the original metric (unchanged); the rest are
# alternate views over the same z-scores, computed in aggregate_scores().
AGGREGATIONS = [
    ("score", "combined significance score, original/default metric"),
    ("mean", "percentile of the plain average z-score"),
    ("median", "percentile of the median z-score (robust to outlier attrs)"),
    ("min", "percentile of the single weakest attribute (bottleneck)"),
    ("max", "percentile of the single strongest attribute (ceiling)"),
    ("geomean", "geometric mean of each attribute's own percentile"),
    ("vote_share", "fraction of attributes that beat their CR-tier average"),
]


def aggregate_scores(zs):
    """zs is the list of usable per-attribute z-scores for one monster
    (positive = better). Returns {method_key: 0-1 score} for every entry in
    AGGREGATIONS. All fall back to 0.5 ("average") when zs is empty."""
    if not zs:
        return {key: 0.5 for key, _desc in AGGREGATIONS}

    k = len(zs)
    avg_z = sum(zs) / k
    # "score": treat the mean of k z-scores as itself ~N(0, 1/k) under the
    # null hypothesis of an average monster, so this sharpens toward 0/1 as
    # more attributes agree. Kept exactly as before.
    combined = normal_cdf(avg_z * math.sqrt(k))
    # "mean": the average z-score's own percentile, with no sqrt(k)
    # amplification -- reads like "how far above/below average overall."
    mean_score = normal_cdf(avg_z)
    # "median": same idea but robust to one or two extreme attributes.
    median_score = normal_cdf(statistics.median(zs))
    # "min": the monster's weakest dimension, i.e. a bottleneck view --
    # low even if every other attribute is exceptional.
    min_score = normal_cdf(min(zs))
    # "max": the mirror of "min" -- the monster's single standout
    # attribute, i.e. a ceiling/specialization view. High even if every
    # other attribute is mediocre.
    max_score = normal_cdf(max(zs))
    # "geomean": convert each attribute to its own percentile first, then
    # take the geometric mean -- like "mean" but penalizes having any one
    # very weak attribute much more than a linear average would.
    eps = 1e-9
    percentiles = [min(max(normal_cdf(z), eps), 1 - eps) for z in zs]
    geomean_score = math.exp(sum(math.log(p) for p in percentiles) / k)
    # "vote_share": ignores magnitude entirely -- just what fraction of
    # attributes are individually above their CR-tier average. A monster
    # with many small edges scores as well here as one with a few huge
    # ones, unlike every z-magnitude-based metric above.
    vote_share = sum(1 for z in zs if z > 0) / k

    return {
        "score": combined,
        "mean": mean_score,
        "median": median_score,
        "min": min_score,
        "max": max_score,
        "geomean": geomean_score,
        "vote_share": vote_share,
    }


def score_monster(m, stats):
    """Returns (scores, k, breakdown) where scores is {method_key: 0-1
    score} (see AGGREGATIONS) and breakdown is a list of
    (label, value, mean, std, median, lo, hi, z) with mean/std/median/lo/hi/z
    = None when that attribute had no usable CR-tier distribution. z is
    already sign-flipped for "lower is better" attributes, so positive
    always means "better." Every ATTRS entry appears in breakdown (for the
    -v display), but only scored=True attributes feed the z-scores behind
    `scores` and `k` -- see the ATTRS comment for why DMG/DPR are excluded."""
    zs = []
    breakdown = []
    for key, label, invert, scored in ATTRS:
        v = m[key]
        tier = stats[key].get(m["cr"])
        if v is None or tier is None:
            breakdown.append((label, v, None, None, None, None, None, None))
            continue
        mean, std, median, lo, hi, _n = tier
        raw_z = (v - mean) / std if std > 1e-9 else 0.0
        z = -raw_z if invert else raw_z
        if scored:
            zs.append(z)
        breakdown.append((label, v, mean, std, median, lo, hi, z))

    k = len(zs)
    scores = aggregate_scores(zs)
    return scores, k, breakdown


def find_matches(name, official, homebrew):
    needle = name.lower()
    pool = [(m, False) for m in official] + [(m, True) for m in homebrew]
    exact = [pair for pair in pool if pair[0]["name"].lower() == needle]
    if exact:
        return exact
    return [pair for pair in pool if needle in pair[0]["name"].lower()]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("names", nargs="+", help='Monster name(s), e.g. "Air Elemental"')
    parser.add_argument("-v", "--verbose", action="store_true", help="show the per-attribute z-score breakdown")
    args = parser.parse_args()

    data, errors = extract_all()
    for e in errors:
        print(f"warning: {e}", file=sys.stderr)
    stats = build_stats(data["monsters"])

    ok = True
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
        scores, k, breakdown = score_monster(m, stats)
        tag = "  [homebrew]" if is_homebrew else ""
        print(f"{m['name']:<32} CR {m['cr']:<5} ({k}/{SCORED_ATTR_COUNT} scored attrs){tag}")
        cols = [f"{key} {scores[key]:.2f}" for key, _desc in AGGREGATIONS]
        per_row = 4
        for i in range(0, len(cols), per_row):
            print("    " + "   ".join(f"{c:<14}" for c in cols[i:i + per_row]).rstrip())
        if args.verbose:
            for label, v, mean, std, median, lo, hi, z in breakdown:
                v_str = f"{v:.1f}" if isinstance(v, float) else str(v)
                if z is None:
                    print(f"    {label:<7} {v_str:>6}   n/a (insufficient CR-tier data)")
                else:
                    print(
                        f"    {label:<7} {v_str:>6}   mean {mean:6.1f}  median {median:6.1f}  "
                        f"sd {std:5.1f}   min {lo:6.1f}  max {hi:6.1f}   z {z:+.2f}"
                    )

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
