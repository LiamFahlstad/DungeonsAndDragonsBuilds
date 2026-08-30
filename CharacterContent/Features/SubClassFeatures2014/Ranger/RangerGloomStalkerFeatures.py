from typing import Optional

from Core.Definitions import Ability, RANGER_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureActivation, ActionType
from CharacterContent.Features.Core.Improvements import InitiativeBonus, SavingThrowProficiencyChoice
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class GloomStalkerMagic(Feature):
    def __init__(self):
        super().__init__(name="Gloom Stalker Magic", origin="Gloom Stalker Ranger Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You learn an additional spell when you reach certain levels in this class, as shown in the Gloom Stalker Spells table. The spell counts as a ranger spell for you, but it doesn't count against the number of ranger spells you know.\n"
            "\n"
            "Gloom Stalker Spells\n"
            "Ranger Level\tSpells\n"
            "3rd\tDisguise Self\n"
            "5th\tRope Trick\n"
            "9th\tFear\n"
            "13th\tGreater Invisibility\n"
            "17th\tSeeming"
        )
        return description


class DreadAmbusher(Feature):
    def __init__(self):
        super().__init__(name="Dread Ambusher", origin="Gloom Stalker Ranger Level 3", usage_tags=["buff", "damage", "utility"])

    def apply(self, character_stat_block: CharacterStatBlock):
        wisdom_modifier = character_stat_block.get_ability_modifier(Ability.WISDOM)
        InitiativeBonus(wisdom_modifier).apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You master the art of the ambush. You can give yourself a bonus to your initiative rolls equal to your Wisdom modifier.\n"
            "\n"
            "At the start of your first turn of each combat, your walking speed increases by 10 feet, which lasts until the end of that turn. If you take the Attack action on that turn, you can make one additional weapon attack as part of that action. If that attack hits, the target takes an extra 1d8 damage of the weapon's damage type."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        wisdom_modifier = character_stat_block.get_ability_modifier(Ability.WISDOM)
        return [
            ("Initiative Bonus", f"Wisdom modifier ({wisdom_modifier:+})"),
            ("First Turn Effect", "Walking speed +10 ft (until end of turn)"),
            ("Bonus Attack", "One additional attack on Attack action"),
            ("Attack Damage", "+1d8 damage of weapon's type on hit"),
        ]


class UmbralSight(Feature):
    def __init__(self):
        super().__init__(name="Umbral Sight", origin="Gloom Stalker Ranger Level 3", usage_tags=["utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain darkvision out to a range of 60 feet. If you already have darkvision from your race, its range increases by 30 feet.\n"
            "\n"
            "You are also adept at evading creatures that rely on darkvision. While in darkness, you are invisible to any creature that relies on darkvision to see you in that darkness."
        )
        return description


class IronMind(Feature):
    def __init__(self, alternate_saving_throw: Optional[Ability] = None):
        super().__init__(name="Iron Mind", origin="Gloom Stalker Ranger Level 7", skippable_in_concise=True, usage_tags=["buff"])
        self._alternate_saving_throw = alternate_saving_throw
        ability = alternate_saving_throw if alternate_saving_throw is not None else Ability.WISDOM
        self._proficiency_choice = SavingThrowProficiencyChoice(
            [ability],
            [Ability.WISDOM, Ability.INTELLIGENCE, Ability.CHARISMA],
            count=1,
            error_prefix="Iron Mind",
        )

    def apply(self, character_stat_block: CharacterStatBlock):
        self._proficiency_choice.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have honed your ability to resist the mind-altering powers of your prey. You gain proficiency in Wisdom saving throws. If you already have this proficiency, you instead gain proficiency in Intelligence or Charisma saving throws (your choice)."
        )
        if self._alternate_saving_throw is not None:
            description += f"\nYou already had Wisdom saving throw proficiency, so you chose {self._alternate_saving_throw.value} instead."
        return description


class StalkersFlurry(Feature):
    def __init__(self):
        super().__init__(name="Stalker's Flurry", origin="Gloom Stalker Ranger Level 11", usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You learn to attack with such unexpected speed that you can turn a miss into another strike. Once on each of your turns when you miss with a weapon attack, you can make another weapon attack as part of the same action."
        return description


class ShadowyDodge(Feature):
    def __init__(self):
        super().__init__(name="Shadowy Dodge", origin="Gloom Stalker Ranger Level 15", activation=FeatureActivation(action_type=ActionType.REACTION), usage_tags=["control"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can dodge in unforeseen ways, with wisps of supernatural shadow around you. Whenever a creature makes an attack roll against you and doesn't have advantage on the roll, you can use your reaction to impose disadvantage on it. You must use this feature before you know the outcome of the attack roll."
        return description
