import Core.Definitions as Definitions
from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class OpenHandTechnique(Feature):
    def __init__(self):
        super().__init__(name="Open Hand Technique", origin="Way of the Open Hand Monk Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can manipulate your enemy's ki when you harness your own. Whenever you hit a creature with one of the attacks granted by your Flurry of Blows, you can impose one of the following effects on that target:\n"
            "\n"
            "    * It must succeed on a Dexterity saving throw or be knocked prone.\n"
            "    * It must make a Strength saving throw. If it fails, you can push it up to 15 feet away from you.\n"
            "    * It can't take reactions until the end of your next turn."
        )
        return description


class WholenessOfBody(Feature):
    def __init__(self):
        super().__init__(name="Wholeness of Body", origin="Way of the Open Hand Monk Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        monk_level = character_stat_block.get_class_level(Definitions.CharacterClass.MONK)
        healing = monk_level * 3
        description = (
            f"You gain the ability to heal yourself. As an action, you can regain hit points equal to three times your monk level ({healing})."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="long rest")

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        monk_level = character_stat_block.get_class_level(Definitions.CharacterClass.MONK)
        healing = monk_level * 3
        return [
            ("Action", "Action"),
            ("Healing", f"3 × monk level ({healing} hp)"),
            ("Uses", "1 per long rest"),
        ]


class Tranquility(Feature):
    def __init__(self):
        super().__init__(name="Tranquility", origin="Way of the Open Hand Monk Level 11")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        wisdom_modifier = character_stat_block.get_ability_modifier(Definitions.Ability.WISDOM)
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        dc = 8 + wisdom_modifier + proficiency_bonus
        description = (
            f"You can enter a special meditation that surrounds you with an aura of peace. At the end of a long rest, you gain the effect of a Sanctuary spell that lasts until the start of your next long rest (the spell can end early as normal). The saving throw DC for the spell equals {dc}."
        )
        return description


class QuiveringPalm(Feature):
    def __init__(self):
        super().__init__(name="Quivering Palm", origin="Way of the Open Hand Monk Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        monk_level = character_stat_block.get_class_level(Definitions.CharacterClass.MONK)
        description = (
            f"You gain the ability to set up lethal vibrations in someone's body. When you hit a creature with an unarmed strike, you can spend 3 ki points to start these imperceptible vibrations, which last for a number of days equal to your monk level ({monk_level}). The vibrations are harmless unless you use your action to end them. To do so, you and the target must be on the same plane of existence. When you use this action, the creature must make a Constitution saving throw. If it fails, it is reduced to 0 hit points. If it succeeds, it takes 10d10 necrotic damage.\n"
            "\n"
            "You can have only one creature under the effect of this feature at a time. You can choose to end the vibrations harmlessly without using an action."
        )
        return description

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        monk_level = character_stat_block.get_class_level(Definitions.CharacterClass.MONK)
        return [
            ("Trigger", "Hit with unarmed strike"),
            ("Cost", "3 ki points"),
            ("Duration", f"{monk_level} days"),
            ("Save", "Constitution (to end vibrations)"),
            ("Effect on Fail", "Reduced to 0 hit points"),
            ("Effect on Success", "10d10 necrotic damage"),
            ("Limit", "Only one creature at a time"),
        ]
