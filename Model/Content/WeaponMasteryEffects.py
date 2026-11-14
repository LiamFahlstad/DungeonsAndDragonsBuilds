"""What a weapon's mastery property does in a fight, as combat effects
(Notes/combat-effects-plan.md, step 6.9): a row of its own after the weapon's
attack ("Longsword: Sap"), with a HIT or MISS trigger that comes `after` the
weapon's row, as a monster's rider comes after its attack (6.4). The combat
picker adds them under the weapon's row when its wielder has its mastery
(AbstractWeapon.has_mastery), worked out for the wielder as they are now.

    Topple  a Constitution save or Prone (DC 8 + the attack's ability
            modifier + Proficiency Bonus), "you can": asked
    Vex     Advantage on the wielder's next attack roll against it, a badge
            on the creature hit that only the wielder's roll uses up
    Sap     Disadvantage on its next attack roll, a badge it uses up
    Slow    Speed -10 feet, a badge (one, however many hits)
    Graze   on a miss, damage equal to the ability modifier, "you can"
    Push    Large or smaller: pushed 10 feet, moved at the table
    Cleave  an attack roll against another creature near it, once per turn
    Nick    changes the Light property's extra attack: a note on the weapon,
            no row (nothing happens on a hit or a miss)

The rules text is the 2024 Player's Handbook's (Weapons, Mastery Properties):
the Rules Glossary has no entry for them. Nothing here imports Combat."""

from Core.Definitions import Ability, Condition, CreatureSize, DamageType
from Core.Weapons import WeaponMastery
from Model.Content.Weapon import AbstractWeapon
from Model.Content.CombatEffect import (
    CombatCondition,
    CombatDamage,
    CombatEffect,
    EffectRoll,
    TurnEdge,
    TurnOf,
    with_bonus,
)
from Model.Content.CombatModifiers import (
    AttacksAgainst,
    D20Mode,
    D20Test,
    RollMode,
    Speed,
)
from Model.Content.CombatTriggers import CombatTrigger, TriggerAim, TriggerEvent
from Model.View import CharacterView

MASTERY_RULES: dict[WeaponMastery, str] = {
    WeaponMastery.CLEAVE: (
        "If you hit a creature with a melee attack roll using this weapon, you"
        " can make a melee attack roll with the weapon against a second creature"
        " within 5 feet of the first that is also within your reach. On a hit,"
        " the second creature takes the weapon's damage, but don't add your"
        " ability modifier to that damage unless that modifier is negative. You"
        " can make this extra attack only once per turn."
    ),
    WeaponMastery.GRAZE: (
        "If your attack roll with this weapon misses a creature, you can deal"
        " damage to that creature equal to the ability modifier you used to make"
        " the attack roll. This damage is the same type dealt by the weapon, and"
        " the damage can be increased only by increasing the ability modifier."
    ),
    WeaponMastery.NICK: (
        "When you make the extra attack of the Light property, you can make it"
        " as part of the Attack action instead of as a Bonus Action. You can make"
        " this extra attack only once per turn."
    ),
    WeaponMastery.PUSH: (
        "If you hit a creature with this weapon, you can push the creature up to"
        " 10 feet straight away from yourself if it is Large or smaller."
    ),
    WeaponMastery.SAP: (
        "If you hit a creature with this weapon, that creature has Disadvantage"
        " on its next attack roll before the start of your next turn."
    ),
    WeaponMastery.SLOW: (
        "If you hit a creature with this weapon and deal damage to it, you can"
        " reduce its Speed by 10 feet until the start of your next turn. If the"
        " creature is hit more than once by weapons that have this property, the"
        " Speed reduction doesn't exceed 10 feet."
    ),
    WeaponMastery.TOPPLE: (
        "If you hit a creature with this weapon, you can force the creature to"
        " make a Constitution saving throw (DC 8 plus the ability modifier used"
        " to make the attack roll and your Proficiency Bonus). On a failed save,"
        " the creature has the Prone condition."
    ),
    WeaponMastery.VEX: (
        "If you hit a creature with this weapon and deal damage to the creature,"
        " you have Advantage on your next attack roll against that creature"
        " before the end of your next turn."
    ),
}

# Its badge lasts until the start of its wielder's next turn (Sap, Slow), or
# the end of it (Vex).
_START_OF_WIELDERS_TURN = (TurnEdge.START, TurnOf.SOURCE)
_END_OF_WIELDERS_TURN = (TurnEdge.END, TurnOf.SOURCE)


def mastery_row_name(weapon: AbstractWeapon) -> str:
    """The name of a weapon's mastery row: "Longsword: Sap"."""
    assert weapon.mastery is not None
    return f"{weapon.name}: {weapon.mastery.value}"


def mastery_note(weapon: AbstractWeapon) -> str:
    """What the weapon's row says about a mastery that has no row of its own
    (Nick, which changes when the Light property's extra attack is made),
    or "" for one that has a row."""
    if weapon.mastery is WeaponMastery.NICK:
        return (
            "Nick: its Light property's extra attack can be made as part of the"
            " Attack action instead of as a Bonus Action, once per turn."
        )
    return ""


def mastery_effects(
    weapon: AbstractWeapon, character: CharacterView
) -> list[CombatEffect]:
    """The rows the weapon's mastery property gives its wielder, `character`,
    who has that mastery (the caller checks): one, or none for Nick, or for
    Graze when the ability modifier it deals isn't above 0."""
    mastery = weapon.mastery
    if mastery is None:
        return []
    name = mastery_row_name(weapon)
    after = weapon.name
    modifier = weapon.attack_ability_modifier(character)
    if mastery is WeaponMastery.TOPPLE:
        return [
            CombatEffect(
                name=name,
                roll=EffectRoll.SAVE,
                save_ability=Ability.CONSTITUTION,
                dc=8 + modifier + character.get_proficiency_bonus(),
                conditions=(CombatCondition(Condition.PRONE),),
                spends_use=False,
                trigger=CombatTrigger(TriggerEvent.HIT, after=after),
            )
        ]
    if mastery is WeaponMastery.VEX:
        return [
            CombatEffect(
                name=name,
                conditions=(
                    CombatCondition(
                        mastery.value,
                        until=_END_OF_WIELDERS_TURN,
                        modifiers=(
                            AttacksAgainst(
                                RollMode.ADVANTAGE, by_caster=True, once=True
                            ),
                        ),
                    ),
                ),
                spends_use=False,
                trigger=CombatTrigger(
                    TriggerEvent.HIT, optional=False, after=after, needs_damage=True
                ),
            )
        ]
    if mastery is WeaponMastery.SAP:
        return [
            CombatEffect(
                name=name,
                conditions=(
                    CombatCondition(
                        mastery.value,
                        until=_START_OF_WIELDERS_TURN,
                        modifiers=(
                            D20Mode(
                                (D20Test.ATTACK_ROLL,),
                                RollMode.DISADVANTAGE,
                                once=True,
                            ),
                        ),
                    ),
                ),
                spends_use=False,
                trigger=CombatTrigger(TriggerEvent.HIT, optional=False, after=after),
            )
        ]
    if mastery is WeaponMastery.SLOW:
        return [
            CombatEffect(
                name=name,
                # One badge of the name on a creature: a second Slow only
                # renews it, so the reduction never passes 10 feet.
                conditions=(
                    CombatCondition(
                        mastery.value,
                        until=_START_OF_WIELDERS_TURN,
                        modifiers=(Speed(bonus=-10),),
                    ),
                ),
                spends_use=False,
                trigger=CombatTrigger(TriggerEvent.HIT, after=after, needs_damage=True),
            )
        ]
    damage_type = DamageType(weapon.damage_type.value)
    if mastery is WeaponMastery.GRAZE:
        if modifier <= 0:
            return []
        return [
            CombatEffect(
                name=name,
                damage=(CombatDamage(str(modifier), damage_type),),
                spends_use=False,
                trigger=CombatTrigger(TriggerEvent.MISS, after=after),
            )
        ]
    if mastery is WeaponMastery.PUSH:
        return [
            CombatEffect(
                name=name,
                spends_use=False,
                notes=(
                    "It's pushed up to 10 feet straight away from its attacker:"
                    " move it at the table.",
                ),
                trigger=CombatTrigger(
                    TriggerEvent.HIT,
                    after=after,
                    largest_target=CreatureSize.LARGE,
                ),
            )
        ]
    if mastery is WeaponMastery.CLEAVE:
        # The weapon's damage without the ability modifier, unless it's
        # negative; its other bonuses (a +1 weapon's) stay.
        bonus = weapon.calculate_damage_bonus_int(character) - max(modifier, 0)
        die = weapon.get_damage_roll(character).value
        return [
            CombatEffect(
                name=name,
                roll=EffectRoll.ATTACK,
                attack_bonus=weapon.calculate_total_attack_roll_bonus_int(character),
                damage=(CombatDamage(with_bonus(die, bonus), damage_type),),
                spends_use=False,
                notes=(
                    "Against a second creature within 5 feet of the first and"
                    " within its attacker's reach.",
                ),
                trigger=CombatTrigger(
                    TriggerEvent.HIT,
                    after=after,
                    once_per_turn=True,
                    aim=TriggerAim.ANOTHER,
                ),
            )
        ]
    return []  # Nick: a note on the weapon's row (mastery_note)
