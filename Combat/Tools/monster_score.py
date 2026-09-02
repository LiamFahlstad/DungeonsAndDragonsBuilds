"""Quick CLI: print a monster's CR-relative power score.

Same statistical model as generate_monster_cr_distributions.py -- each CR
tier's mean and standard deviation (HP, AC, the six ability scores, attack
roll bonus, damage per hit, action economy, and defensive tags) are fit from
the *official* monsters.py stat blocks only, then the monster you name
(official or homebrew) is scored by how many standard deviations its stats
sit from that tier's mean, averaged and mapped to a 0-1 percentile
(0.5 = exactly average for its CR).

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

# (key, label, invert) -- invert=True means "lower is better" (e.g. fewer
# vulnerabilities), so its z is flipped before scoring/display so positive
# always means "better," consistently across every attribute.
ATTRS = [
    ("hp", "HP", False),
    ("ac", "AC", False),
    ("str", "STR", False),
    ("dex", "DEX", False),
    ("con", "CON", False),
    ("int", "INT", False),
    ("wis", "WIS", False),
    ("cha", "CHA", False),
    ("atk", "ATK", False),
    ("dmg", "DMG", False),
    ("condimm", "C-IMM", False),
    ("dmgimm", "D-IMM", False),
    ("dmgres", "D-RES", False),
    ("dmgvuln", "D-VULN", True),
    ("actions", "ACT", False),
    ("bonusact", "B-ACT", False),
    ("speed", "SPD", False),
]


def build_stats(official_monsters):
    """stats[attr][cr] = (mean, std, median, min, max, n), fit from official monsters only."""
    by_cr = {}
    for m in official_monsters:
        by_cr.setdefault(m["cr"], []).append(m)

    stats = {key: {} for key, _label, _invert in ATTRS}
    for cr, group in by_cr.items():
        for key, _label, _invert in ATTRS:
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


def score_monster(m, stats):
    """Returns (score, k, breakdown) where breakdown is a list of
    (label, value, mean, std, median, lo, hi, z) with mean/std/median/lo/hi/z
    = None when that attribute had no usable CR-tier distribution. z is
    already sign-flipped for "lower is better" attributes, so positive
    always means "better."""
    zs = []
    breakdown = []
    for key, label, invert in ATTRS:
        v = m[key]
        tier = stats[key].get(m["cr"])
        if v is None or tier is None:
            breakdown.append((label, v, None, None, None, None, None, None))
            continue
        mean, std, median, lo, hi, _n = tier
        raw_z = (v - mean) / std if std > 1e-9 else 0.0
        z = -raw_z if invert else raw_z
        zs.append(z)
        breakdown.append((label, v, mean, std, median, lo, hi, z))

    k = len(zs)
    avg_z = sum(zs) / k if k else 0.0
    standardized = avg_z * math.sqrt(k)
    score = normal_cdf(standardized) if k else 0.5
    return score, k, breakdown


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
        score, k, breakdown = score_monster(m, stats)
        tag = "  [homebrew]" if is_homebrew else ""
        print(f"{m['name']:<32} CR {m['cr']:<5} score {score:.2f}  ({k}/{len(ATTRS)} attrs){tag}")
        if args.verbose:
            for label, v, mean, std, median, lo, hi, z in breakdown:
                if z is None:
                    print(f"    {label:<7} {v!s:>6}   n/a (insufficient CR-tier data)")
                else:
                    print(
                        f"    {label:<7} {v!s:>6}   mean {mean:6.1f}  median {median:6.1f}  "
                        f"sd {std:5.1f}   min {lo:6.1f}  max {hi:6.1f}   z {z:+.2f}"
                    )

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
