from Combat import Combatants
from Combat.Monsters.CR_1.monsters import BugbearWarrior, Pirate, Tiger
from Combat.Monsters.CR_2.monsters import Priest, Rhinoceros, SabertoothedTiger
from Combat.Monsters.CR_6.monsters import Vrock


def get_drunk_oxe_combatants() -> list[Combatants.BasicCombatantData]:
    bo = BugbearWarrior()
    bo.set_name("Bo")

    jax = BugbearWarrior()
    jax.set_name("Jax")

    crock = Pirate()
    crock.set_name("Crock")

    tiger = Tiger()
    tiger.set_name("Tiger")

    return [bo, jax, crock, tiger]


def get_square_combatants() -> list[Combatants.BasicCombatantData]:
    mirelle = Vrock()
    mirelle.set_name("Mirelle")

    priest = Priest()
    priest.set_name("Guard Priest")

    rhinoceros = Rhinoceros()
    rhinoceros.set_name("Guard Rhinoceros")

    tiger = SabertoothedTiger()
    tiger.set_name("Guard Saber-Toothed Tiger")

    return [mirelle, priest, rhinoceros, tiger]
