from Combat import Combatants


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


def get_bull() -> list[Combatants.BasicCombatantData]:
    bull = Combatants.Bull()
    return [bull]
