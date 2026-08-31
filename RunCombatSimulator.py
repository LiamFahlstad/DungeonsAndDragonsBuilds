import argparse
import sys

import Combat.CombatantGroups as CombatantGroups
import Combat.Scenarios as Scenarios
from Combat.CombatUIQt import CombatAppQt

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DnD Combat Engine")
    parser.add_argument(
        "--scenario",
        choices=sorted(Scenarios.SCENARIOS.keys()),
        default=None,
        help="Combat scenario to run. Omit to run without an encounter "
        "(e.g. an out-of-combat adventure session when combined with --player-log).",
    )
    parser.add_argument(
        "--log",
        default=None,
        help="Path to a Combat/CombatLogs/*.json file to resume from, "
        "picking up the combatants' HP/conditions/round where that log left off",
    )
    parser.add_argument(
        "--player-log",
        default=None,
        help="Path to a persistent player log JSON file (e.g. Combat/PlayerLogs/main_party.json). "
        "The 'Players' combatant group is loaded, preloading HP/conditions/etc. from the most "
        "recent session, and every action taken against a player is appended to this file "
        "across runs. A new session entry ('encounter' if --scenario is given, else 'adventure') "
        "is started each run.",
    )
    parser.add_argument(
        "--rest",
        choices=["long", "short"],
        default=None,
        help="Apply a rest to the tracked party instead of launching a session (requires "
        "--player-log). 'long' fully restores HP and spell slots and writes a new, "
        "timestamped player log file, without opening any window. 'short' opens a small "
        "healing window (not the main combat window) where each player can be healed a "
        "manually-entered amount, updating the existing player log in place.",
    )
    args = parser.parse_args()

    if args.rest and not args.player_log:
        parser.error("--rest requires --player-log")

    if args.rest:
        from Combat.CombatUIQt.rest import apply_long_rest, run_short_rest

        if args.rest == "long":
            new_path = apply_long_rest(args.player_log)
            print(f"Long rest applied. New player log: {new_path}")
        else:
            run_short_rest(args.player_log)
        sys.exit(0)

    if args.scenario is None and not args.player_log:
        args.scenario = "time_loop_square"

    scenario = Scenarios.SCENARIOS[args.scenario] if args.scenario else None
    combatants = scenario.build_combatants() if scenario else []
    character_sheets = scenario.build_character_sheets() if scenario else []

    if args.player_log:
        players_group = CombatantGroups.get_players_group()
        player_names = {cs.character_name for cs in players_group}
        character_sheets = [
            cs for cs in character_sheets if cs.character_name not in player_names
        ]
        character_sheets = players_group + character_sheets

    app = CombatAppQt(
        combatants=combatants,
        character_sheets=character_sheets,
        combatants_per_column=scenario.combatants_per_column if scenario else 4,
        resume_log_path=args.log,
        player_log_path=args.player_log,
        scenario_name=args.scenario,
    )
    app.run()
