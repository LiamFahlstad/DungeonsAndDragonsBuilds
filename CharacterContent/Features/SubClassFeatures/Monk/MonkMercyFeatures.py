import Core.Definitions as Definitions
from Core.Definitions import MONK_HIT_DIE, Skill
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureUses, FeatureActivation, ActionType, RegainedOn
from CharacterContent.Features.Core.Improvements import SkillProficiency
from CharacterContent.Items.Weapons import WeaponDamageRolls
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils

LEVEL_TO_MARTIAL_ARTS_DIE = {
    1: WeaponDamageRolls.D6,
    2: WeaponDamageRolls.D6,
    3: WeaponDamageRolls.D6,
    4: WeaponDamageRolls.D6,
    5: WeaponDamageRolls.D8,
    6: WeaponDamageRolls.D8,
    7: WeaponDamageRolls.D8,
    8: WeaponDamageRolls.D8,
    9: WeaponDamageRolls.D8,
    10: WeaponDamageRolls.D8,
    11: WeaponDamageRolls.D10,
    12: WeaponDamageRolls.D10,
    13: WeaponDamageRolls.D10,
    14: WeaponDamageRolls.D10,
    15: WeaponDamageRolls.D10,
    16: WeaponDamageRolls.D10,
    17: WeaponDamageRolls.D12,
    18: WeaponDamageRolls.D12,
    19: WeaponDamageRolls.D12,
    20: WeaponDamageRolls.D12,
}

LEVEL_TO_FOCUS_POINTS = {
    1: 0,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    6: 6,
    7: 7,
    8: 8,
    9: 9,
    10: 10,
    11: 11,
    12: 12,
    13: 13,
    14: 14,
    15: 15,
    16: 16,
    17: 17,
    18: 18,
    19: 19,
    20: 20,
}


class HandOfHarm(Feature):
    def __init__(self):
        super().__init__(name="Hand of Harm", origin="Warrior of Mercy Monk Level 3", usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Once per turn when you hit a creature with an Unarmed Strike and deal damage, you can expend 1 Focus Point to deal extra Necrotic damage equal to one roll of your Martial Arts die plus your Wisdom modifier."
        return description


class HandOfHealing(Feature):
    def __init__(self):
        super().__init__(name="Hand of Healing", origin="Warrior of Mercy Monk Level 3", activation=FeatureActivation(action_type=ActionType.ACTION, range="Touch"), usage_tags=["heal"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Magic action, you can expend 1 Focus Point to touch a creature and restore a number of Hit Points equal to a roll of your Martial Arts die plus your Wisdom modifier.\n"
            "When you use your Flurry of Blows, you can replace one of the Unarmed Strikes with a use of this feature without expending a Focus Point for the healing."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        wisdom_modifier = character_stat_block.get_wisdom_modifier()
        return [
            ("Action", "Magic action"),
            ("Cost", "1 Focus Point"),
            ("Range", "Touch"),
            ("Effect", f"Restore 1 Martial Arts die + {wisdom_modifier:+d} (Wisdom) Hit Points"),
            ("Special", "Can replace one Unarmed Strike in Flurry of Blows without spending Focus Point"),
        ]


class ImplementsOfMercy(Feature):
    def __init__(self):
        super().__init__(
            name="Implements of Mercy", origin="Warrior of Mercy Monk Level 3"
        )
        self._skill_proficiencies = SkillProficiency([Skill.INSIGHT, Skill.MEDICINE])

    def apply(self, character_stat_block: CharacterStatBlock):
        self._skill_proficiencies.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain proficiency in the Insight and Medicine skills and proficiency with the Herbalism Kit."
        return description


class PhysiciansTouch(Feature):
    def __init__(self):
        super().__init__(
            name="Physician's Touch", origin="Warrior of Mercy Monk Level 6", activation=FeatureActivation(duration="Until End of Next Turn"), usage_tags=["control", "heal"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your Hand of Harm and Hand of Healing improve, as detailed below.\n"
            "Hand of Harm. When you use Hand of Harm on a creature, you can also give that creature the Poisoned condition until the end of your next turn.\n"
            "Hand of Healing. When you use Hand of Healing, you can also end one of the following conditions on the creature you heal: Blinded, Deafened, Paralyzed, Poisoned, or Stunned."
        )
        return description


class FlurryOfHealingAndHarm(Feature):
    def __init__(self):
        super().__init__(
            name="Flurry of Healing and Harm", origin="Warrior of Mercy Monk Level 11"
        , uses=FeatureUses(max_uses=Definitions.MAX_ABILITY_MODIFIER, regain_all_on="long rest", current_formula="Current amount: equal to your Wisdom modifier."))

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you use Flurry of Blows, you can replace each of the Unarmed Strikes with a use of Hand of Healing without expending Focus Points for the healing.\n"
            "In addition, when you make an Unarmed Strike with Flurry of Blows and deal damage, you can use Hand of Harm with that strike without expending a Focus Point for Hand of Harm. You can still use Hand of Harm only once per turn.\n"
            "You can use these benefits a total number of times equal to your Wisdom modifier (minimum of once). You regain all expended uses when you finish a Long Rest."
        )
        return description


    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def number_of_uses(self, character_stat_block: CharacterStatBlock) -> int:
        return max(1, character_stat_block.get_wisdom_modifier())
class HandOfUltimateMercy(Feature):
    def __init__(self):
        super().__init__(
            name="Hand of Ultimate Mercy", origin="Warrior of Mercy Monk Level 17", activation=FeatureActivation(action_type=ActionType.ACTION, range="Touch"), usage_tags=["heal"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your mastery of life energy opens the door to the ultimate mercy. As a Magic action, you can touch the corpse of a creature that died within the past 24 hours and expend 5 Focus Points. The creature then returns to life with a number of Hit Points equal to 4d10 plus your Wisdom modifier. If the creature died with any of the following conditions, the creature revives with the conditions removed: Blinded, Deafened, Paralyzed, Poisoned, and Stunned.\n"
            "Once you use this feature, you can't use it again until you finish a Long Rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        wisdom_modifier = character_stat_block.get_wisdom_modifier()
        return [
            ("Action", "Magic action"),
            ("Cost", "5 Focus Points"),
            ("Target", "Corpse of creature dead within 24 hours"),
            ("Hit Points Restored", f"4d10 + {wisdom_modifier:+d} (Wisdom)"),
            ("Conditions Removed", "Blinded, Deafened, Paralyzed, Poisoned, Stunned"),
            ("Recharge", "Once per Long Rest"),
        ]
