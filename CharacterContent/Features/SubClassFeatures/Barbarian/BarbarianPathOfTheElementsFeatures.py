import Core.Definitions as Definitions
from Core.Definitions import (
    Ability,
)
from Model.Content.Feature import Feature, FeatureActivation, ActionType, FeatureTarget
from CharacterContent.Features.ClassFeatures.Barbarian.BarbarianFeatures import (
    get_rage_damage_bonus,
)
from CharacterContent.Spells.SpellLists import (
    DruidLevel0Spells,
    DruidLevel3Spells,
)
from Model.Spells import FeatureSpell
from Model.View import CharacterView
from Model.Content.FeatureText import (
    Block,
    Facts,
    Option,
    Paragraph,
    dc_formula,
)


def _raging_elements_current_values(character: CharacterView) -> str:
    level = character.get_class_level(Definitions.CharacterClass.BARBARIAN)
    dice = get_rage_damage_bonus(level)
    attack_bonus = (
        character.get_constitution_modifier() + character.get_proficiency_bonus()
    )
    dc = 8 + attack_bonus
    return (
        f"Right now: Icefury {dice}d8, Lava Burst {dice}d4, Lightning Bolt {dice}d6; "
        f"spell attack +{attack_bonus}, save DC {dc}."
    )


class RagingElements(Feature):
    def __init__(self):
        super().__init__(
            name="Raging Elements",
            origin="Path Of The Elements Barbarian Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, range="30 Feet"
            ),
            usage_tags=["damage"],
        )

    def calculate_dc(self, character: CharacterView) -> int:
        constitution_modifier = character.get_constitution_modifier()
        proficiency_bonus = character.get_proficiency_bonus()
        return 8 + constitution_modifier + proficiency_bonus

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "As part of the Bonus Action that activates your Rage, use one option below. While raging, a Bonus Action uses that option again or a different one."
            ),
            Facts(
                (
                    ("Save DC", dc_formula(Ability.CONSTITUTION)),
                    (
                        "Spell attack",
                        "Constitution is your spellcasting ability",
                    ),
                    ("Dice", "A number equal to your Rage Damage bonus"),
                )
            ),
            Option(
                "Icefury",
                (
                    Facts(
                        (
                            ("Target", "One creature within 30 feet"),
                            (
                                "Attack",
                                "Melee spell attack within 5 feet, otherwise ranged spell attack",
                            ),
                            ("Hit", "Cold damage: d8s equal to your Rage Damage bonus"),
                            (
                                "Rider",
                                "The next time it takes Fire damage before the end of your next turn, it takes an extra 1d10 Fire damage",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Lava Burst",
                (
                    Facts(
                        (
                            ("Target", "One creature you can see within 30 feet"),
                            ("Save", "Dexterity"),
                            (
                                "Failed",
                                "Fire damage: d4s equal to your Rage Damage bonus; the next time it takes Lightning damage before the end of your next turn, it takes an extra 1d8 Lightning damage",
                            ),
                            ("Success", "Half damage only"),
                        )
                    ),
                ),
            ),
            Option(
                "Lightning Bolt",
                (
                    Facts(
                        (
                            ("Target", "One other creature you can see within 30 feet"),
                            ("Save", "Dexterity"),
                            (
                                "Failed",
                                "Lightning damage: d6s equal to your Rage Damage bonus; the next time it takes Cold damage before the end of your next turn, it takes an extra 1d6 Cold damage",
                            ),
                            ("Success", "Half damage only"),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Whenever you activate your Rage, you can take one of the following Raging Elements options of your choice as part of that Bonus Action. While your rage is active, you can take a Bonus Action to use that option again or a different option.\n"
            "If a Raging Elements option requires a saving throw, the DC equals 8 plus your Constitution modifier and Proficiency Bonus.\n"
            "Icefury. When this effect is activated, roll a number of d8s equal to your Rage Damage bonus, and add them together. You hurl frigid ice at one creature within 30 feet of yourself. Make either a melee spell attack (if the target is within 5 feet) or a ranged spell attack, using Constitution as your spellcasting ability. On a hit, the attack deals Cold damage equal to the number rolled, and the next time the target takes Fire damage before the end of your next turn, it takes an extra 1d10 Fire damage.\n"
            "Lava Burst. When this effect is activated, roll a number of d4s equal to your Rage Damage bonus, and add them together. You then hurl molten lava at one creature you can see within 30 feet. The target makes a Dexterity saving throw. On a failed save, the target takes Fire damage equal to the number rolled, and the next time the target takes Lightning damage until the end of your next turn, it takes an extra 1d8 Lightning damage. On a successful save, the target takes half as much damage only.\n"
            "Lightning Bolt. When this effect is activated, roll a number of d6s equal to your Rage Damage bonus, and add them together. You can then hurl a bolt of lightning at one other creature you can see within 30 feet. The target makes a Dexterity saving throw. On a failed save, the target takes Lightning damage equal to the roll's total, and the next time the target takes Cold damage until the end of your next turn, it takes an extra 1d6 Cold damage. On a successful save, the target takes half as much damage only.\n"
            + _raging_elements_current_values(character)
        )
        return description


class EchoOfTheElements(Feature):
    def __init__(self):
        super().__init__(
            name="Echo of the Elements",
            origin="Path Of The Elements Barbarian Level 6",
        )

    def granted_spells(self) -> list[FeatureSpell]:
        expend_rage = "Cast by expending a use of your Rage"
        return [
            FeatureSpell(DruidLevel0Spells.ELEMENTALISM, Ability.WISDOM),
            FeatureSpell(DruidLevel3Spells.DAYLIGHT, Ability.WISDOM, expend_rage),
            FeatureSpell(DruidLevel3Spells.WATER_WALK, Ability.WISDOM, expend_rage),
            FeatureSpell(DruidLevel3Spells.WIND_WALL, Ability.WISDOM, expend_rage),
        ]

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("You tap into the tranquility of the elements."),
            Facts(
                (
                    ("Cantrip", "Elementalism"),
                    (
                        "Expend a Rage",
                        "Cast Daylight, Water Walk or Wind Wall",
                    ),
                    ("Spellcasting ability", "Wisdom"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You tap into the tranquility of the elements. You know the Elementalism cantrip. In addition, you can expend a use of your Rage to cast Daylight, Water Walk, or Wind Wall. Wisdom is your spellcasting ability for these spells."
        return description


class PrimordialBond(Feature):
    def __init__(self):
        super().__init__(
            name="Primordial Bond",
            origin="Path Of The Elements Barbarian Level 10",
            usage_tags=["buff"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts((("While raging", "Resistance to Cold, Fire and Lightning damage"),)),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "While your Rage is active, you have Resistance to Cold, Fire, and Lightning damage."
        return description


class ElementalOverload(Feature):
    def __init__(self):
        super().__init__(
            name="Elemental Overload",
            origin="Path Of The Elements Barbarian Level 14",
            activation=FeatureActivation(range="30 Feet"),
            usage_tags=["damage", "control"],
        )

    def calculate_dc(self, character: CharacterView) -> int:
        constitution_modifier = character.get_constitution_modifier()
        proficiency_bonus = character.get_proficiency_bonus()
        return 8 + constitution_modifier + proficiency_bonus

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "The storm you channel lashes out at your foes. Your Raging Elements options gain these effects, hit or miss, saved or failed."
            ),
            Option(
                "Icefury",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "The target subtracts half the number rolled (round down) from the next damage roll it makes before the start of your next turn",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Lava Burst",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "The target and each enemy within 10 feet of it start burning",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Lightning Bolt",
                (
                    Facts(
                        (
                            (
                                "Chain",
                                "The bolt leaps to another target of your choice you can see within 30 feet of the first",
                            ),
                            (
                                "Save",
                                f"Dexterity, DC {dc_formula(Ability.CONSTITUTION)}",
                            ),
                            (
                                "Damage",
                                "Lightning damage equal to the roll's total; half on a success",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "The power of the storm you channel grows mightier, lashing out at your foes. Your Raging Elements options gain the following effects.\n"
            "Icefury. Whether or not you hit the target with this option, the target subtracts half the number rolled (round down) from the next damage roll it makes before the start of your next turn.\n"
            "Lava Burst. Whether or not the target fails its saving throw against this option, the target and each enemy within 10 feet of it start burning.\n"
            "Lightning Bolt. Whether or not the target fails its saving throw against this option, a bolt of lightning leaps from the target to another target of your choice that you can see within 30 feet of the first target. The new target makes a Dexterity saving throw, taking Lightning damage equal to the roll's total on a failed save or half as much damage on a successful one."
        )
        return description
