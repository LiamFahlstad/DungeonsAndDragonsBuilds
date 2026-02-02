import tkinter as tk

from Combat import Combatants
from Combat.CombatUI import CombatApp


def get_players() -> list[Combatants.BasicCombatantData]:
    p1 = Combatants.Player1()
    p1.set_name("Player 1")

    p2 = Combatants.Player1()
    p2.set_name("Player 2")

    p3 = Combatants.Player1()
    p3.set_name("Player 3")

    p4 = Combatants.Player1()
    p4.set_name("Player 4")
    return [p1, p2, p3, p4]


def get_drunk_oxe_combatants() -> list[Combatants.BasicCombatantData]:
    bo = Combatants.BugbearWarrior()
    bo.set_name("bo")

    jax = Combatants.BugbearWarrior()
    jax.set_name("Jax")

    birk = Combatants.Pirate()
    birk.set_name("Birk")

    tiger = Combatants.Tiger()
    tiger.set_name("Tiger")

    return [bo, jax, birk, tiger]


def get_square_combatants() -> list[Combatants.BasicCombatantData]:
    mirelle = Combatants.Vrock()
    mirelle.set_name("Mirelle")

    g1 = Combatants.Priest()
    g1.set_name("Guard Priest 1")

    g2 = Combatants.Rhinoceros()
    g2.set_name("Guard Rhinoceros 2")

    g3 = Combatants.SaberToothedTiger()
    g3.set_name("Guard Saber-Toothed Tiger 3")

    return [mirelle, g1, g2, g3]


if __name__ == "__main__":
    root = tk.Tk()
    combatants_per_column = 4
    app = CombatApp(
        root,
        combatants=get_players() + get_square_combatants(),
        character_sheets=[],
        combatants_per_column=combatants_per_column,
    )
    root.mainloop()
