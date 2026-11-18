"""What an Unarmed Strike's Grapple and Shove do in a fight, as combat
effects (arena plan, steps 21 and 22): rows after the Unarmed Strike's own
attack, "Unarmed Strike: Grapple", "Unarmed Strike: Shove (push)" and
"Unarmed Strike: Shove (Prone)", one for each choice the Rules Glossary
gives besides Damage, which is the weapon's row.

Rules Glossary, Unarmed Strike: "Grapple. The target must succeed on a
Strength or Dexterity saving throw (it chooses which), or it has the
Grappled condition. The DC for the saving throw and any escape attempts
equals 8 plus your Strength modifier and Proficiency Bonus. This grapple is
possible only if the target is no more than one size larger than you and
if you have a hand free to grab it." "Shove. The target must succeed on a
Strength or Dexterity saving throw (it chooses which), or you either push
it 5 feet away or cause it to have the Prone condition. The DC for the
saving throw equals 8 plus your Strength modifier and Proficiency Bonus.
This shove is possible only if the target is no more than one size larger
than you." Martial Arts lets a Monk use Dexterity for that DC, which the
Unarmed Strike's own ability (`attack_ability_modifier`) already is for
one.

The Grappled condition names its grappler, the user, which the battle map
drags along (Combat/Arena/grapples.py). Nothing here imports Combat."""

from Core.Definitions import Ability, Condition
from Model.Content.CombatEffect import (
    CombatCondition,
    CombatEffect,
    CombatPush,
    EffectRoll,
)
from Model.Content.Weapon import AbstractWeapon
from Model.View import CharacterView

GRAPPLE = "Unarmed Strike: Grapple"
SHOVE_PUSH = "Unarmed Strike: Shove (push)"
SHOVE_PRONE = "Unarmed Strike: Shove (Prone)"

UNARMED_STRIKE_RULES = (
    "Instead of using a weapon to make a melee attack, you can use a punch,"
    " kick, headbutt, or similar forceful blow. In game terms, this is an"
    " Unarmed Strike—a melee attack that involves you using your body to"
    " damage, grapple, or shove a target within 5 feet of you.\n"
    "Grapple. The target must succeed on a Strength or Dexterity saving throw"
    " (it chooses which), or it has the Grappled condition. The DC for the"
    " saving throw and any escape attempts equals 8 plus your Strength"
    " modifier and Proficiency Bonus. This grapple is possible only if the"
    " target is no more than one size larger than you and if you have a hand"
    " free to grab it.\n"
    "Shove. The target must succeed on a Strength or Dexterity saving throw"
    " (it chooses which), or you either push it 5 feet away or cause it to"
    " have the Prone condition. The DC for the saving throw equals 8 plus"
    " your Strength modifier and Proficiency Bonus. This shove is possible"
    " only if the target is no more than one size larger than you."
)

_CHOOSES = (
    "It chooses Strength or Dexterity: switch the ability if it picks"
    " Dexterity. Only a target within 5 feet and no more than one size"
    " larger than you."
)


def unarmed_strike_effects(
    weapon: AbstractWeapon, character: CharacterView
) -> list[CombatEffect]:
    """The Grapple's and the Shove's rows for the wielder of `weapon`, an
    Unarmed Strike, with their DC worked out (8 + the Unarmed Strike's
    ability modifier + Proficiency Bonus)."""
    dc = 8 + weapon.attack_ability_modifier(character)
    dc += character.get_proficiency_bonus()

    def row(
        name: str,
        notes: tuple[str, ...],
        push: CombatPush | None = None,
        conditions: tuple[CombatCondition, ...] = (),
    ) -> CombatEffect:
        return CombatEffect(
            name=name,
            roll=EffectRoll.SAVE,
            save_ability=Ability.STRENGTH,
            dc=dc,
            conditions=conditions,
            spends_use=False,
            notes=notes,
            push=push,
        )

    escape = (
        f"Escape DC {dc}: its action for a Strength (Athletics) or Dexterity"
        " (Acrobatics) check. Needs a hand free."
    )
    return [
        row(
            GRAPPLE,
            (_CHOOSES, escape),
            conditions=(CombatCondition(Condition.GRAPPLED),),
        ),
        row(SHOVE_PUSH, (_CHOOSES,), push=CombatPush(5)),
        row(SHOVE_PRONE, (_CHOOSES,), conditions=(CombatCondition(Condition.PRONE),)),
    ]
