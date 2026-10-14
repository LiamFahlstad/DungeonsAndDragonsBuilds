from Core.Definitions import CLERIC_HIT_DIE
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    FeatureTarget,
    RegainedOn,
)
from Utils import StringUtils
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts


class GraveDomainSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Grave Domain Spells", origin="Grave Domain Cleric Level 3"
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Grave Domain Spells table, you thereafter always have the listed spells prepared.\n"
            "Grave Domain Spells\n"
            "Cleric Level	Spells\n"
            "3	Detect Evil and Good, False Life, Gentle Repose, Ray of Enfeeblement, Spare the Dying\n"
            "5	Revivify, Vampiric Touch\n"
            "7	Blight, Death Ward\n"
            "9	Dispel Evil and Good, Raise Dead"
        )
        return description


class CircleOfMortality(Feature):
    def __init__(self):
        super().__init__(
            name="Circle of Mortality",
            origin="Grave Domain Cleric Level 3",
            usage_tags=["damage", "heal"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Pull of Death",
                        "Once per turn, when you damage a creature that's missing any Hit Points with a spell or an attack roll, it takes +1d4 Necrotic damage (1d6 from Cleric level 11)",
                    ),
                    ("Return to Life", "Cast Spare the Dying as a Bonus Action"),
                    (
                        "Healing the fallen",
                        "When you heal a creature at 0 Hit Points with a spell or Channel Divinity, use the maximum on each healing die instead of rolling",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can manipulate the balance between life and death, granting you the following benefits.\n"
            "Pull of Death. Once per turn, when you deal damage to a creature that's missing any Hit Points by casting a spell or by hitting with an attack roll, that creature takes an extra 1d4 Necrotic damage. This extra damage increases to 1d6 when you reach Cleric level 11.\n"
            "Return to Life. You can cast Spare the Dying as a Bonus Action.\n"
            "Additionally, when you would normally roll one or more dice to restore Hit Points to a creature at 0 Hit Points with a spell or Channel Divinity, don't roll those dice for the healing; instead, use the highest number possible for each die. For example, instead of restoring 2d4 Hit Points to a creature at 0 Hit Points with a spell, you restore 8."
        )
        return description


class PathToTheGrave(Feature):
    def __init__(self):
        super().__init__(
            name="Path to the Grave",
            origin="Grave Domain Cleric Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="Until Start of Your Next Turn",
                range="30 Feet",
            ),
            usage_tags=["control", "damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Action", "Bonus Action, presenting your Holy Symbol"),
                    ("Cost", "One use of Channel Divinity"),
                    ("Range", "30 feet"),
                    ("Target", "One creature you can see"),
                    (
                        "Curse",
                        "Until the start of your next turn, Disadvantage on attack rolls and saving throws",
                    ),
                    (
                        "End it",
                        "When you or an ally you can see hits it with an attack roll, end the curse (no action required): the attack deals extra Necrotic or Radiant damage equal to your Cleric level",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Bonus Action, you present your Holy Symbol and expend a use of Channel Divinity to curse one creature you can see within 30 feet of yourself until the start of your next turn. While cursed, the creature has Disadvantage on attack rolls and saving throws.\n"
            "When you or an ally you can see hits the cursed target with an attack roll, you can end the curse early (no action required) to make the attack deal extra Necrotic or Radiant damage (your choice) equal to your Cleric level."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class SentinelAtDeathsDoor(Feature):
    def __init__(self):
        super().__init__(
            name="Sentinel at Death's Door",
            origin="Grave Domain Cleric Level 6",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="60 Feet"
            ),
            usage_tags=["buff"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Wisdom modifier.",
            ),
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you or a Bloodied creature you can see within 60 feet of yourself is hit with an attack roll, you can take a Reaction to halve that attack's damage (round down). If the triggering attack roll was a Critical Hit, any effects triggered by a Critical Hit are canceled.\n"
            "You can use this feature a number of times equal to your Wisdom modifier (minimum of once). You regain all expended uses when you finish a Long Rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_wisdom_modifier())

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class DivineReaper(Feature):
    def __init__(self):
        super().__init__(
            name="Divine Reaper",
            origin="Grave Domain Cleric Level 17",
            activation=FeatureActivation(range="60 Feet"),
            usage_tags=["heal"],
            uses=FeatureUses(
                max_uses=1,
                regain_all_on="short or long rest",
                current_formula="Used by Keeper of Souls.",
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Keeper of Souls' once-per-rest box is in the panel below.
        return [
            Facts(
                (
                    (
                        "Enhanced Necromancy",
                        "When you cast a level 1-5 Necromancy spell that targets one creature, or a Grave Domain spell, expend a Channel Divinity use to target a second creature in range (providing costly or consumed Material components for each)",
                    ),
                    (
                        "Keeper of Souls",
                        "When an enemy dies within 60 feet of you, you or a creature you can see within 60 feet regains 2 x Cleric level Hit Points. Not while you're Incapacitated. Once per Short or Long Rest; expend a level 6+ spell slot (no action required) to use it again.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your deep connection to this domain renders you a hallowed harbinger of death, granting you the following benefits.\n"
            "Enhanced Necromancy. When you cast a spell of level 5 or lower from the Necromancy school that targets one creature, or when you cast a spell from the Grave Domain Spells table, you can expend a use of Channel Divinity to target a second creature within the spell's range. If the spell requires costly or consumed Material components, you must provide Material components for each target.\n"
            "Keeper of Souls. When an enemy dies within 60 feet of you, you or one creature you can see within 60 feet of yourself regains Hit Points equal to twice your Cleric level. You can't use this feature if you have the Incapacitated condition. Once you use this feature, you can't use it again until you finish a Short or Long Rest, unless you expend a level 6+ spell slot (no action required) to restore your use of it."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST
