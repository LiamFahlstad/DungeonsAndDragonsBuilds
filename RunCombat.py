import tkinter as tk

from Combat import Combatants
from Combat.CombatUI import CombatApp

if __name__ == "__main__":
    root = tk.Tk()

    bo = Combatants.BugbearWarrior()
    bo.set_name("bo")

    jax = Combatants.BugbearWarrior()
    jax.set_name("Jax")

    birk = Combatants.Pirate()
    birk.set_name("Birk")

    tiger = Combatants.Tiger()
    tiger.set_name("Tiger")

    app = CombatApp(
        root,
        combatants=[bo, jax, birk, tiger],
        character_sheets=[],
    )
    root.mainloop()
