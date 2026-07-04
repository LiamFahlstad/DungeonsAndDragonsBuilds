import argparse

import Combat.Scenarios as Scenarios

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DnD Combat Engine")
    parser.add_argument(
        "--ui",
        choices=["tk", "qt"],
        default="qt",
        help="UI backend to use (default: qt)",
    )
    parser.add_argument(
        "--scenario",
        choices=sorted(Scenarios.SCENARIOS.keys()),
        default="time_loop_square",
        help="Combat scenario to run (default: time_loop_square)",
    )
    args = parser.parse_args()

    scenario = Scenarios.SCENARIOS[args.scenario]
    combatants = scenario.build_combatants()
    character_sheets = scenario.build_character_sheets()

    if args.ui == "qt":
        from Combat.CombatUIQt import CombatAppQt

        app = CombatAppQt(
            combatants=combatants,
            character_sheets=character_sheets,
            combatants_per_column=scenario.combatants_per_column,
        )
        app.run()
    else:
        import tkinter as tk

        from Combat.CombatUI import CombatApp

        root = tk.Tk()
        app = CombatApp(
            root,
            combatants=combatants,
            character_sheets=character_sheets,
            combatants_per_column=scenario.combatants_per_column,
        )
        root.mainloop()
