from typing import Type

from Combat.Definitions import ExtendedCombatantData


def format_wild_shape_form(monster_cls: Type[ExtendedCombatantData]) -> str:
    monster = monster_cls()
    speed = monster.speed.strip().rstrip(",")
    return (
        f"{monster.combatant_type} (CR {monster.cr}, {monster.monster_type}) - "
        f"AC {monster.ac}, HP {monster.hp}, Speed {speed}"
    )
