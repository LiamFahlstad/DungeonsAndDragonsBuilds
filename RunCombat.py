import tkinter as tk

import Combat.GrimsCastle.Encounters as GrimsCastleEncounters
import Combat.TimeLoop.Encounters as TimeLoopEncounters
from Combat.CombatUI import CombatApp

if __name__ == "__main__":
    root = tk.Tk()
    combatants_per_column = 4
    app = CombatApp(
        root,
        combatants=TimeLoopEncounters.get_players()
        + TimeLoopEncounters.get_square_combatants()
        + GrimsCastleEncounters.get_bull(),
        character_sheets=[],
        combatants_per_column=combatants_per_column,
    )
    root.mainloop()
