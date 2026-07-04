import argparse

import Combat.Scenarios as Scenarios
from Combat.CombatUIQt import CombatAppQt

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DnD Combat Engine")
    parser.add_argument(
        "--scenario",
        choices=sorted(Scenarios.SCENARIOS.keys()),
        default="time_loop_square",
        help="Combat scenario to run (default: time_loop_square)",
    )
    parser.add_argument(
        "--log",
        default=None,
        help="Path to a CombatLogs/*.json file to resume from, "
        "picking up the combatants' HP/conditions/round where that log left off",
    )
    args = parser.parse_args()

    scenario = Scenarios.SCENARIOS[args.scenario]
    combatants = scenario.build_combatants()
    character_sheets = scenario.build_character_sheets()

    app = CombatAppQt(
        combatants=combatants,
        character_sheets=character_sheets,
        combatants_per_column=scenario.combatants_per_column,
        resume_log_path=args.log,
    )
    app.run()
