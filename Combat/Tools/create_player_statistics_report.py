"""Read a persistent player log and write a standalone HTML report of lifetime
player statistics. Mirrors the in-app "Players" tabs of the Statistics dialog,
but as a shareable static file instead of a Qt dialog.

Run from the repo root:
    python -m Combat.Tools.create_player_statistics_report

Or pick another campaign, or a custom log and output:
    python -m Combat.Tools.create_player_statistics_report --campaign time_loop_pr
    python -m Combat.Tools.create_player_statistics_report --log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json --output my_report.html

Reads the campaign's PlayerLogs/main_party.json, the encounter logs its
entries point to, and the sessions older long rests archived
(main_party_long_rest_*.json; see Combat/PlayerLog.py), and writes
player_statistics_report.html into the campaign's folder (or custom --log /
--output) with lifetime player statistics.
"""

import argparse
from pathlib import Path

import Combat.PlayerLog as PlayerLog
import Combat.Scenarios as Scenarios
from Combat.Campaign import Campaign
from Combat.CombatUIQt.stats import (
    SPELL_SLOT_LEVELS,
    compute_player_log_stats,
    damage_dealt_key,
    damage_taken_key,
    long_rest_archives,
    player_log_history,
    spell_slots_used_key,
)
from Core.Definitions import DamageType


def player_roster(campaign: Campaign) -> list[str]:
    """Load the canonical player roster (character names) from the campaign's
    Players group. Skip and warn if a character builder raises."""
    names = []
    for cs in campaign.players():
        try:
            names.append(cs.character_name)
        except Exception as exc:
            print(f"  ! skipping a player in the roster: {exc}")
    return names


def escape(text: str) -> str:
    """Escape HTML special characters."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an HTML report of lifetime player statistics from a player log."
    )
    parser.add_argument(
        "--campaign",
        choices=sorted(Scenarios.CAMPAIGNS.keys()),
        default=Scenarios.DEFAULT_CAMPAIGN,
        help=f"Campaign whose party the log tracks (default: {Scenarios.DEFAULT_CAMPAIGN})",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=None,
        help="Path to the player log JSON file "
        "(default: the campaign's PlayerLogs/main_party.json)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Path to write the HTML report "
        "(default: player_statistics_report.html in the campaign's folder)",
    )
    args = parser.parse_args()
    campaign = Scenarios.CAMPAIGNS[args.campaign]
    if args.log is None:
        args.log = campaign.default_player_log
    if args.output is None:
        args.output = campaign.folder / "player_statistics_report.html"

    if not args.log.exists():
        raise SystemExit(
            f"No player log for campaign '{campaign.name}' at {args.log}. Run a "
            "session with --player-log first, or pass --log."
        )

    # The whole history: the sessions older long rests archived, then the
    # log's own entries with their encounter logs' events.
    log_data = player_log_history(args.log)

    # Compute stats
    stats_by_name = compute_player_log_stats(log_data)
    names = player_roster(campaign)

    # Session summary: long rests are entries of their own now, archives before.
    entries = log_data.get("sessions", [])
    sessions = [s for s in entries if s.get("type") != PlayerLog.LONG_REST]
    long_rest_count = len(long_rest_archives(args.log)) + len(entries) - len(sessions)
    session_count = len(sessions)

    started_ats = [s.get("started_at") for s in sessions if s.get("started_at")]
    first_session = min(started_ats) if started_ats else None
    last_session = max(started_ats) if started_ats else None

    # Scenario breakdown
    scenario_counts = {}
    for s in sessions:
        scenario = s.get("scenario") or "Freeform adventure"
        scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1
    scenario_items = sorted(
        scenario_counts.items(),
        key=lambda x: (-x[1], x[0]),
    )

    campaign_title = campaign.display_title
    party_name = args.log.stem.replace("_", " ").title()

    # Build summary chip content
    session_chip = f"Sessions: {session_count}"
    long_rest_chip = f"Long rests: {long_rest_count}"
    first_chip = (
        f"First session: {first_session[:10]}" if first_session else "First session: —"
    )
    last_chip = (
        f"Latest session: {last_session[:10]}" if last_session else "Latest session: —"
    )
    scenario_chip = "Scenarios: " + ", ".join(
        f"{escape(name)} ({count})" for name, count in scenario_items
    )

    # Damage columns (flat keys + per-type breakdowns)
    damage_columns = (
        [("Damage Dealt", "damage_dealt")]
        + [
            (f"Dealt: {dtype.value}", damage_dealt_key(dtype.value))
            for dtype in DamageType
        ]
        + [("Damage Taken", "damage_taken")]
        + [
            (f"Taken: {dtype.value}", damage_taken_key(dtype.value))
            for dtype in DamageType
        ]
    )

    # Healing columns
    healing_columns = [
        ("Healing Done", "healing_done"),
        ("Healing Received", "healing_received"),
        ("Temp HP Granted", "temp_hp_granted"),
        ("Temp HP Received", "temp_hp_received"),
    ]

    # Outcome columns
    outcome_columns = [
        ("Knockouts", "knockouts"),
        ("Times Downed", "times_downed"),
        ("Deaths", "deaths"),
    ]

    # Condition columns (dynamic per actually-used conditions)
    condition_names = set()
    for name in names:
        stats = stats_by_name.get(name) or {}
        condition_names.update(stats.get("conditions_given_by_name", {}).keys())
        condition_names.update(stats.get("conditions_received_by_name", {}).keys())
    sorted_condition_names = sorted(condition_names)
    condition_columns = (
        [
            ("Given (Total)", "conditions_given"),
            ("Received (Total)", "conditions_received"),
        ]
        + [
            (f"Given: {name}", ("conditions_given_by_name", name))
            for name in sorted_condition_names
        ]
        + [
            (f"Received: {name}", ("conditions_received_by_name", name))
            for name in sorted_condition_names
        ]
    )

    # Spell columns (dynamic per actually-cast spells)
    spell_names = set()
    for name in names:
        stats = stats_by_name.get(name) or {}
        spell_names.update(stats.get("spells_cast_by_name", {}).keys())
    sorted_spell_names = sorted(spell_names)
    spell_columns = (
        [("Spell Slots Used", "spell_slots_used")]
        + [
            (f"Level {level}", spell_slots_used_key(level))
            for level in SPELL_SLOT_LEVELS
        ]
        + [("Spells Cast", "spells_cast")]
        + [
            (f"Cast: {name}", ("spells_cast_by_name", name))
            for name in sorted_spell_names
        ]
    )

    def _column_value(stats, key):
        """key is either a flat stats key, or a (dict_key, name) nested lookup."""
        if isinstance(key, tuple):
            dict_key, name = key
            return stats.get(dict_key, {}).get(name, 0)
        return stats.get(key, 0)

    def _build_table_html(columns):
        """Build an HTML table for the given (header, key) columns."""
        rows = ["<tr><th>Player</th>"]
        for header, _ in columns:
            rows[0] += f"<th>{escape(header)}</th>"
        rows[0] += "</tr>"

        for name in names:
            stats = stats_by_name.get(name) or {}
            row = f"<tr><td>{escape(name)}</td>"
            for _, key in columns:
                value = _column_value(stats, key)
                row += f"<td>{value}</td>"
            row += "</tr>"
            rows.append(row)

        return (
            "<table>"
            + "<thead>"
            + rows[0]
            + "</thead><tbody>"
            + "".join(rows[1:])
            + "</tbody></table>"
        )

    party_cards = []
    for name in names:
        stats = stats_by_name.get(name) or {}
        card = f"""<div class="player-card">
<h3>{escape(name)}</h3>
<div class="stat-row"><span>Damage Dealt</span><span class="value">{stats.get('damage_dealt', 0)}</span></div>
<div class="stat-row"><span>Damage Taken</span><span class="value">{stats.get('damage_taken', 0)}</span></div>
<div class="stat-row"><span>Healing Done</span><span class="value">{stats.get('healing_done', 0)}</span></div>
<div class="stat-row"><span>Healing Received</span><span class="value">{stats.get('healing_received', 0)}</span></div>
<div class="stat-row"><span>Knockouts</span><span class="value">{stats.get('knockouts', 0)}</span></div>
<div class="stat-row"><span>Times Downed</span><span class="value">{stats.get('times_downed', 0)}</span></div>
<div class="stat-row"><span>Deaths</span><span class="value">{stats.get('deaths', 0)}</span></div>
<div class="stat-row"><span>Spells Cast</span><span class="value">{stats.get('spells_cast', 0)}</span></div>
<div class="stat-row"><span>Conditions Given</span><span class="value">{stats.get('conditions_given', 0)}</span></div>
<div class="stat-row"><span>Conditions Received</span><span class="value">{stats.get('conditions_received', 0)}</span></div>
</div>"""
        party_cards.append(card)

    party_grid = '<div class="player-grid">' + "".join(party_cards) + "</div>"

    def _build_bar_section(stat_key, css_class):
        """Build a bar-chart comparison section for a single stat."""
        values = [
            (name, stats_by_name.get(name, {}).get(stat_key, 0)) for name in names
        ]
        # Sort descending by value
        values.sort(key=lambda x: x[1], reverse=True)

        if all(v == 0 for _, v in values):
            return '<p class="empty-note">No data yet.</p>'

        max_val = max((v for _, v in values), default=1)
        rows = []
        for name, value in values:
            pct = (value / max_val * 100) if max_val > 0 else 0
            rows.append(
                f'<div class="bar-row"><span>{escape(name)}</span><div class="bar-track"><div class="bar-fill {css_class}" style="width:{pct}%"></div></div><span>{value}</span></div>'
            )
        return '<div class="bar-section">' + "".join(rows) + "</div>"

    damage_dealt_section = _build_bar_section("damage_dealt", "dealt")
    damage_taken_section = _build_bar_section("damage_taken", "taken")
    healing_done_section = _build_bar_section("healing_done", "heal")
    spells_cast_section = _build_bar_section("spells_cast", "spells")

    detailed_tables = [
        ("Damage", _build_table_html(damage_columns)),
        ("Healing", _build_table_html(healing_columns)),
        ("Conditions", _build_table_html(condition_columns)),
        ("Spells", _build_table_html(spell_columns)),
        ("Outcomes", _build_table_html(outcome_columns)),
    ]

    details_html = ""
    for label, table_html in detailed_tables:
        details_html += f"""<details>
<summary>{escape(label)}</summary>
<div class="table-wrap">
{table_html}
</div>
</details>
"""

    CSS = """
:root {
  --bg: #1a1a2e; --panel: #16213e; --panel-border: #0f3460;
  --gold: #c9a84c; --text: #eaeaea; --muted: #a0a0b0;
  --danger: #e74c3c; --heal: #2ecc71;
}
* { box-sizing: border-box; }
body { margin: 0; padding: 2rem 1.75rem 4rem; background: var(--bg); color: var(--text); font-family: "Segoe UI", system-ui, sans-serif; }
h1 { color: var(--gold); font-size: 1.6rem; margin: 0 0 0.25rem; letter-spacing: 0.02em; }
.subtitle { color: var(--muted); margin: 0 0 2rem; font-size: 0.92rem; }
.summary-bar { display: flex; flex-wrap: wrap; gap: 0.75rem; margin-bottom: 2rem; }
.summary-chip { background: var(--panel); border: 1px solid var(--panel-border); border-radius: 8px; padding: 0.5rem 1rem; font-size: 0.85rem; color: var(--muted); }
.summary-chip b { color: var(--text); }
h2 { color: var(--gold); font-size: 1.15rem; margin: 2.5rem 0 1rem; border-bottom: 1px solid var(--panel-border); padding-bottom: 0.4rem; }
.player-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1rem; }
.player-card { background: var(--panel); border: 1px solid var(--panel-border); border-radius: 10px; padding: 1.1rem 1.25rem; }
.player-card h3 { margin: 0 0 0.75rem; color: var(--text); font-size: 1.05rem; }
.stat-row { display: flex; justify-content: space-between; font-size: 0.85rem; padding: 0.2rem 0; color: var(--muted); }
.stat-row span.value { color: var(--text); font-weight: 600; }
.bar-section { display: flex; flex-direction: column; gap: 0.9rem; }
.bar-row { display: grid; grid-template-columns: 140px 1fr 60px; align-items: center; gap: 0.75rem; font-size: 0.85rem; }
.bar-track { background: #0e0e18; border-radius: 6px; overflow: hidden; height: 14px; border: 1px solid var(--panel-border); }
.bar-fill { height: 100%; border-radius: 6px 0 0 6px; }
.bar-fill.dealt { background: linear-gradient(90deg, var(--gold), #e0c169); }
.bar-fill.taken { background: linear-gradient(90deg, var(--danger), #ff8b78); }
.bar-fill.heal { background: linear-gradient(90deg, var(--heal), #7ee8a8); }
.bar-fill.spells { background: linear-gradient(90deg, #7a2fa0, #b06fd6); }
details { background: var(--panel); border: 1px solid var(--panel-border); border-radius: 10px; margin-bottom: 0.75rem; overflow: hidden; }
summary { cursor: pointer; padding: 0.75rem 1.1rem; color: var(--gold); font-weight: 600; font-size: 0.95rem; }
summary:hover { background: rgba(201,168,76,0.08); }
.table-wrap { overflow-x: auto; padding: 0 1.1rem 1rem; }
table { border-collapse: collapse; width: 100%; font-size: 0.85rem; min-width: 500px; }
th, td { text-align: left; padding: 0.4rem 0.7rem; border-bottom: 1px solid var(--panel-border); white-space: nowrap; }
th { color: var(--muted); font-weight: 600; }
td { color: var(--text); }
.empty-note { color: var(--muted); font-style: italic; padding: 1rem 0; }
"""

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Player Statistics - {escape(campaign_title)}</title>
<style>
{CSS}
</style>
</head>
<body>
<h1>Player Statistics — {escape(campaign_title)} ({escape(party_name)})</h1>
<p class="subtitle">{escape(str(args.log))} and its long-rest archives</p>
<div class="summary-bar">
<div class="summary-chip">{session_chip}</div>
<div class="summary-chip">{long_rest_chip}</div>
<div class="summary-chip">{first_chip}</div>
<div class="summary-chip">{last_chip}</div>
<div class="summary-chip">{scenario_chip}</div>
</div>

<h2>Party Overview</h2>
{party_grid}

<h2>Damage Dealt</h2>
{damage_dealt_section}

<h2>Damage Taken</h2>
{damage_taken_section}

<h2>Healing Done</h2>
{healing_done_section}

<h2>Spells Cast</h2>
{spells_cast_section}

<h2>Detailed Breakdown</h2>
{details_html}

</body>
</html>
"""

    args.output.write_text(html, encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
