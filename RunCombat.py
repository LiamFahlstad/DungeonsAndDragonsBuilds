import argparse

import Combat.GrimsCastle.Encounters as GrimsCastleEncounters
import Combat.TimeLoop.Encounters as TimeLoopEncounters

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DnD Combat Engine")
    parser.add_argument(
        "--ui",
        choices=["tk", "qt"],
        default="qt",
        help="UI backend to use (default: qt)",
    )
    args = parser.parse_args()

    combatants = (
        TimeLoopEncounters.get_players()
        + TimeLoopEncounters.get_square_combatants()
        + GrimsCastleEncounters.get_bull()
    )

    if args.ui == "qt":
        from Combat.CombatUIQt import CombatAppQt

        app = CombatAppQt(
            combatants=combatants,
            character_sheets=[],
            combatants_per_column=4,
        )
        app.run()
    else:
        import tkinter as tk

        from Combat.CombatUI import CombatApp

        root = tk.Tk()
        app = CombatApp(
            root,
            combatants=combatants,
            character_sheets=[],
            combatants_per_column=4,
        )
        root.mainloop()
