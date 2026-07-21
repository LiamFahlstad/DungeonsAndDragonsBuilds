"""Aggregate stat analysis across every monster in Combat/Monsters/CR_*/
(both auto-generated monsters.py and hand-written monsters_homebrew.py).

Produces an HTML report with:
  - mean HP vs CR (with std band)
  - mean AC vs CR (with std band)
  - HP vs AC scatter, colored by CR, to show their relation directly
  - mean total ability score vs CR (with std band)
  - mean damage resistance / immunity counts vs CR
  - mean Attack Roll to-hit bonus vs CR (monsters with no attack roll are excluded)

Run from the repo root:
    python -m Combat.Tools.analyze_monster_stats
Writes Combat/Tools/monster_stats_report.html
"""

import base64
import importlib
import inspect
import io
import re
import statistics
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from Combat.Definitions import ExtendedCombatantData

MONSTERS_DIR = Path(__file__).resolve().parent.parent / "Monsters"
OUTPUT_HTML = Path(__file__).resolve().parent / "monster_stats_report.html"

# ---------------------------------------------------------------------------
# Palette (validated default categorical/sequential palette — see the dataviz
# skill's references/palette.md). Reused unchanged, so no re-validation needed.
# ---------------------------------------------------------------------------
INK = "#0b0b0b"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"
SURFACE = "#fcfcfb"
SLOT_BLUE = "#2a78d6"  # categorical slot 1 / sequential base hue
SLOT_ORANGE = "#eb6834"  # categorical slot 2
SEQUENTIAL_BLUE = [
    "#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7",
    "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b",
]

_FRACTION_CR = {"1/8": 0.125, "1/4": 0.25, "1/2": 0.5}
_ATTACK_ROLL_RE = re.compile(r"Attack Roll:\s*([+-]\d+)")
_ATTACK_FIELDS = (
    "actions", "bonus_actions", "reactions",
    "legendary_actions", "mythic_actions", "lair_actions",
)


def cr_sort_key(cr: str) -> float:
    cr = cr.strip()
    if cr in _FRACTION_CR:
        return _FRACTION_CR[cr]
    try:
        return float(cr)
    except ValueError:
        return float("inf")


def load_all_monsters() -> list[ExtendedCombatantData]:
    """Import every CR_*/monsters.py and CR_*/monsters_homebrew.py module and
    instantiate every ExtendedCombatantData subclass defined directly in it."""
    instances = []
    for py_file in sorted(MONSTERS_DIR.glob("CR_*/monsters*.py")):
        module_name = f"Combat.Monsters.{py_file.parent.name}.{py_file.stem}"
        module = importlib.import_module(module_name)
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if not (
                obj.__module__ == module.__name__
                and issubclass(obj, ExtendedCombatantData)
                and obj is not ExtendedCombatantData
            ):
                continue
            try:
                instances.append(obj())
            except Exception as exc:  # noqa: BLE001 - keep going on a bad homebrew entry
                print(f"  ! skipping {module_name}.{obj.__name__}: {exc}")
    return instances


def ability_sum(m: ExtendedCombatantData) -> int:
    return sum(m.ability_scores.values())


def damage_type_count(entries) -> int:
    """Counts individual damage types across all entries, e.g. one entry
    covering [BLUDGEONING, PIERCING, SLASHING] counts as 3, not 1."""
    return sum(len(e.damage_types) for e in entries)


def attack_bonus(m: ExtendedCombatantData) -> float | None:
    """Average +to-hit across every 'Attack Roll: +N' found in the monster's
    action-like ability lists. None if the monster has no attack roll at all
    (e.g. a pure save-or-suffer caster)."""
    bonuses = []
    for field in _ATTACK_FIELDS:
        for ability in getattr(m, field) or []:
            match = _ATTACK_ROLL_RE.search(ability.description)
            if match:
                bonuses.append(int(match.group(1)))
    if not bonuses:
        return None
    return sum(bonuses) / len(bonuses)


@dataclass
class CrStats:
    cr: str
    n: int
    hp_mean: float
    hp_std: float
    ac_mean: float
    ac_std: float
    ability_mean: float
    ability_std: float
    resist_mean: float
    resist_std: float
    immune_mean: float
    immune_std: float
    attack_n: int
    attack_mean: float | None
    attack_std: float | None


def _mean_std(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    return statistics.fmean(values), statistics.pstdev(values)


def group_by_cr(monsters: list[ExtendedCombatantData]) -> list[CrStats]:
    groups: dict[str, list[ExtendedCombatantData]] = {}
    for m in monsters:
        groups.setdefault(m.cr, []).append(m)

    stats = []
    for cr, ms in sorted(groups.items(), key=lambda kv: cr_sort_key(kv[0])):
        hp_mean, hp_std = _mean_std([m.hp for m in ms])
        ac_mean, ac_std = _mean_std([m.ac for m in ms])
        ability_mean, ability_std = _mean_std([ability_sum(m) for m in ms])
        resist_mean, resist_std = _mean_std(
            [damage_type_count(m.damage_resistances) for m in ms]
        )
        immune_mean, immune_std = _mean_std(
            [damage_type_count(m.damage_immunities) for m in ms]
        )
        attacks = [b for b in (attack_bonus(m) for m in ms) if b is not None]
        attack_mean, attack_std = (None, None) if not attacks else _mean_std(attacks)

        stats.append(
            CrStats(
                cr=cr,
                n=len(ms),
                hp_mean=hp_mean, hp_std=hp_std,
                ac_mean=ac_mean, ac_std=ac_std,
                ability_mean=ability_mean, ability_std=ability_std,
                resist_mean=resist_mean, resist_std=resist_std,
                immune_mean=immune_mean, immune_std=immune_std,
                attack_n=len(attacks), attack_mean=attack_mean, attack_std=attack_std,
            )
        )
    return stats


# ---------------------------------------------------------------------------
# Charting
# ---------------------------------------------------------------------------

def _new_axes(figsize=(7.5, 4.2)):
    fig, ax = plt.subplots(figsize=figsize, dpi=150)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("bottom", "left"):
        ax.spines[side].set_color(BASELINE)
    ax.tick_params(colors=INK_MUTED, labelsize=9)
    ax.yaxis.grid(True, color=GRIDLINE, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.xaxis.label.set_color(INK_MUTED)
    ax.yaxis.label.set_color(INK_MUTED)
    return fig, ax


def fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def line_with_band(x_labels, means, stds, title, y_label, color=SLOT_BLUE) -> str:
    fig, ax = _new_axes()
    x = np.arange(len(x_labels))
    means_arr, stds_arr = np.array(means), np.array(stds)
    lower = np.clip(means_arr - stds_arr, 0, None)
    ax.fill_between(x, lower, means_arr + stds_arr, color=color, alpha=0.15, linewidth=0)
    ax.plot(x, means_arr, color=color, linewidth=2, solid_capstyle="round",
            marker="o", markersize=5, markerfacecolor=color, markeredgewidth=0)
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45, ha="right")
    ax.set_ylabel(y_label)
    ax.set_title(title, color=INK, fontsize=12, loc="left", pad=12)
    return fig_to_base64(fig)


def _asymmetric_yerr(means, stds):
    """Clip the lower error bar at 0 — these are non-negative counts, so a
    symmetric std bar dipping below zero would be misleading."""
    means_arr, stds_arr = np.array(means), np.array(stds)
    lower = means_arr - np.clip(means_arr - stds_arr, 0, None)
    upper = stds_arr
    return np.vstack([lower, upper])


def two_series_with_errorbars(
    x_labels, means1, stds1, label1, means2, stds2, label2, title, y_label,
) -> str:
    fig, ax = _new_axes()
    x = np.arange(len(x_labels))
    ax.errorbar(
        x - 0.08, means1, yerr=_asymmetric_yerr(means1, stds1), color=SLOT_BLUE, linewidth=2,
        marker="o", markersize=5, capsize=3, label=label1, linestyle="-",
    )
    ax.errorbar(
        x + 0.08, means2, yerr=_asymmetric_yerr(means2, stds2), color=SLOT_ORANGE, linewidth=2,
        marker="s", markersize=5, capsize=3, label=label2, linestyle="--",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45, ha="right")
    ax.set_ylabel(y_label)
    ax.set_title(title, color=INK, fontsize=12, loc="left", pad=12)
    legend = ax.legend(frameon=False, fontsize=9, loc="upper left")
    for text in legend.get_texts():
        text.set_color(INK_MUTED)
    return fig_to_base64(fig)


def hp_vs_ac_scatter(monsters: list[ExtendedCombatantData], cr_order: list[str]) -> str:
    rank = {cr: i for i, cr in enumerate(cr_order)}
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("seq_blue", SEQUENTIAL_BLUE)
    fig, ax = _new_axes(figsize=(7.5, 5.5))
    ac_vals = [m.ac for m in monsters]
    hp_vals = [m.hp for m in monsters]
    color_vals = [rank[m.cr] / max(len(cr_order) - 1, 1) for m in monsters]
    scatter = ax.scatter(
        ac_vals, hp_vals, c=color_vals, cmap=cmap, s=36,
        edgecolors="white", linewidths=0.4, alpha=0.9,
    )
    ax.set_xlabel("Armor Class")
    ax.set_ylabel("Hit Points")
    ax.set_title("HP vs AC, colored by CR tier", color=INK, fontsize=12, loc="left", pad=12)

    tick_positions = np.linspace(0, 1, min(8, len(cr_order)))
    tick_crs = [cr_order[int(round(p * (len(cr_order) - 1)))] for p in tick_positions]
    cbar = fig.colorbar(scatter, ax=ax, ticks=tick_positions)
    cbar.ax.set_yticklabels(tick_crs)
    cbar.ax.tick_params(colors=INK_MUTED, labelsize=8)
    cbar.set_label("CR", color=INK_MUTED)
    cbar.outline.set_visible(False)
    return fig_to_base64(fig)


# ---------------------------------------------------------------------------
# HTML assembly
# ---------------------------------------------------------------------------

def build_table(stats: list[CrStats]) -> str:
    rows = []
    for s in stats:
        attack_cell = (
            f"{s.attack_mean:.1f} ± {s.attack_std:.1f} (n={s.attack_n})"
            if s.attack_mean is not None else "—"
        )
        rows.append(
            "<tr>"
            f"<td>{s.cr}</td><td>{s.n}</td>"
            f"<td>{s.hp_mean:.1f} ± {s.hp_std:.1f}</td>"
            f"<td>{s.ac_mean:.1f} ± {s.ac_std:.1f}</td>"
            f"<td>{s.ability_mean:.1f} ± {s.ability_std:.1f}</td>"
            f"<td>{s.resist_mean:.2f} ± {s.resist_std:.2f}</td>"
            f"<td>{s.immune_mean:.2f} ± {s.immune_std:.2f}</td>"
            f"<td>{attack_cell}</td>"
            "</tr>"
        )
    return (
        "<table>"
        "<thead><tr>"
        "<th>CR</th><th>Count</th><th>HP (mean ± std)</th><th>AC (mean ± std)</th>"
        "<th>Ability score sum (mean ± std)</th><th>Resistances (mean ± std)</th>"
        "<th>Immunities (mean ± std)</th><th>Attack bonus (mean ± std)</th>"
        "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
    )


PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Monster Stats Report</title>
<style>
  :root {{
    color-scheme: light dark;
    --page: #f9f9f7; --card: #ffffff; --ink: #0b0b0b; --ink-secondary: #52514e;
    --border: rgba(11,11,11,0.10);
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --page: #0d0d0d; --card: #17171a; --ink: #ffffff; --ink-secondary: #c3c2b7;
             --border: rgba(255,255,255,0.10); }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 2rem 1.5rem 4rem; background: var(--page); color: var(--ink);
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  }}
  h1 {{ font-size: 1.5rem; margin-bottom: 0.25rem; }}
  .subtitle {{ color: var(--ink-secondary); margin-top: 0; margin-bottom: 2rem; font-size: 0.95rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 1.25rem; }}
  .card {{
    background: var(--card); border: 1px solid var(--border); border-radius: 12px;
    padding: 1rem; overflow-x: auto;
  }}
  .card img {{ max-width: 100%; height: auto; display: block; background: {surface}; border-radius: 8px; }}
  .card p {{ color: var(--ink-secondary); font-size: 0.85rem; margin: 0.5rem 0 0; }}
  .table-wrap {{ margin-top: 2.5rem; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 0.85rem; min-width: 900px; }}
  th, td {{ text-align: left; padding: 0.45rem 0.7rem; border-bottom: 1px solid var(--border); white-space: nowrap; }}
  th {{ color: var(--ink-secondary); font-weight: 600; }}
  caption {{ text-align: left; color: var(--ink-secondary); margin-bottom: 0.5rem; font-size: 0.85rem; }}
</style>
</head>
<body>
<h1>Monster Stats Report</h1>
<p class="subtitle">{n_monsters} monsters across {n_cr} CR tiers, from Combat/Monsters/CR_*/monsters.py and monsters_homebrew.py. Std is population std within each CR tier. Attack bonus is averaged across every parsed "Attack Roll: +N" on a monster's actions/bonus actions/reactions/legendary actions; monsters with no attack roll (pure save-effect casters) are excluded from that chart only.</p>
<div class="grid">
  <div class="card"><img src="data:image/png;base64,{img_hp}"><p>Mean HP by CR tier, shaded band is ±1 population std.</p></div>
  <div class="card"><img src="data:image/png;base64,{img_ac}"><p>Mean AC by CR tier, shaded band is ±1 population std.</p></div>
  <div class="card"><img src="data:image/png;base64,{img_scatter}"><p>Every monster's HP vs AC, colored by CR tier (light = low CR, dark = high CR).</p></div>
  <div class="card"><img src="data:image/png;base64,{img_ability}"><p>Mean total ability score (sum of all six scores) by CR tier.</p></div>
  <div class="card"><img src="data:image/png;base64,{img_damage}"><p>Mean count of individually-typed damage resistances vs immunities by CR tier (error bars are ±1 std).</p></div>
  <div class="card"><img src="data:image/png;base64,{img_attack}"><p>Mean Attack Roll to-hit bonus by CR tier, monsters with no attack roll excluded.</p></div>
</div>
<div class="table-wrap card">
  <caption>Full per-CR data</caption>
  {table}
</div>
</body>
</html>
"""


def main() -> None:
    print("Loading monsters...")
    monsters = load_all_monsters()
    print(f"Loaded {len(monsters)} monsters")

    stats = group_by_cr(monsters)
    cr_order = [s.cr for s in stats]
    print(f"Grouped into {len(cr_order)} CR tiers")

    img_hp = line_with_band(cr_order, [s.hp_mean for s in stats], [s.hp_std for s in stats],
                             "Mean HP by CR", "Hit Points")
    img_ac = line_with_band(cr_order, [s.ac_mean for s in stats], [s.ac_std for s in stats],
                             "Mean AC by CR", "Armor Class")
    img_scatter = hp_vs_ac_scatter(monsters, cr_order)
    img_ability = line_with_band(
        cr_order, [s.ability_mean for s in stats], [s.ability_std for s in stats],
        "Mean total ability score by CR", "Sum of all six ability scores",
    )
    img_damage = two_series_with_errorbars(
        cr_order,
        [s.resist_mean for s in stats], [s.resist_std for s in stats], "Damage Resistances",
        [s.immune_mean for s in stats], [s.immune_std for s in stats], "Damage Immunities",
        "Damage resistances & immunities by CR", "Count of damage types",
    )
    attack_stats = [s for s in stats if s.attack_mean is not None]
    img_attack = line_with_band(
        [s.cr for s in attack_stats],
        [s.attack_mean for s in attack_stats], [s.attack_std for s in attack_stats],
        "Mean Attack Roll to-hit bonus by CR", "To-hit bonus",
    )

    html = PAGE_TEMPLATE.format(
        surface=SURFACE,
        n_monsters=len(monsters),
        n_cr=len(cr_order),
        img_hp=img_hp,
        img_ac=img_ac,
        img_scatter=img_scatter,
        img_ability=img_ability,
        img_damage=img_damage,
        img_attack=img_attack,
        table=build_table(stats),
    )
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"Wrote {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
