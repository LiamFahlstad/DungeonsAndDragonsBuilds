from Core.Definitions import BARD_HIT_DIE, Ability
from CharacterContent.Features.Core.BaseFeatures import FeatureUses, Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class SilverTongue(Feature):
    def __init__(self):
        super().__init__(name="Silver Tongue", origin="College of Eloquence Bard Level 3", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You are a master at saying the right thing at the right time. When you make a Charisma "
            "(Persuasion) or Charisma (Deception) check, you can treat a d20 roll of 9 or lower as a 10."
        )
        return description


class UnsettlingWords(Feature):
    def __init__(self):
        super().__init__(name="Unsettling Words", origin="College of Eloquence Bard Level 3", action_type="bonus_action", duration="Until Start of Your Next Turn", range="60 Feet", usage_tags=["control"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can spin words laced with magic that unsettle a creature and cause it to doubt itself. "
            "As a bonus action, you can expend one use of your Bardic Inspiration and choose one creature "
            "you can see within 60 feet of you. Roll the Bardic Inspiration die. The creature must subtract "
            "the number rolled from the next saving throw it makes before the start of your next turn."
        )
        return description


class UnfailingInspiration(Feature):
    def __init__(self):
        super().__init__(name="Unfailing Inspiration", origin="College of Eloquence Bard Level 6", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your inspiring words are so persuasive that others feel driven to succeed. When a creature "
            "adds one of your Bardic Inspiration dice to its ability check, attack roll, or saving throw "
            "and the roll fails, the creature can keep the Bardic Inspiration die."
        )
        return description


class UniversalSpeech(Feature):
    def __init__(self):
        super().__init__(name="Universal Speech", origin="College of Eloquence Bard Level 6", action_type="action", duration="1 Hour", range="60 Feet", usage_tags=["utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        cha_mod = character_stat_block.get_ability_modifier(Ability.CHARISMA)
        creatures = max(1, cha_mod)
        description = (
            f"You have gained the ability to make your speech intelligible to any creature. As an action, "
            f"choose one or more creatures within 60 feet of you, up to a number equal to your Charisma "
            f"modifier ({creatures} creature{'s' if creatures != 1 else ''}). The chosen creatures can magically "
            f"understand you, regardless of the language you speak, for 1 hour.\n"
            f"\n"
            f"Once you use this feature, you can't use it again until you finish a long rest, unless you "
            f"expend a spell slot to use it again."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        cha_mod = character_stat_block.get_ability_modifier(Ability.CHARISMA)
        creatures = max(1, cha_mod)
        return [
            ("Action", "Action"),
            ("Range", "60 feet"),
            ("Targets", f"Up to {creatures} creature{'s' if creatures != 1 else ''}"),
            ("Effect", "Chosen creatures understand you regardless of language"),
            ("Duration", "1 hour"),
            ("Cost", "Reusable with long rest, or spell slot to repeat"),
        ]


class InfectiousInspiration(Feature):
    def __init__(self):
        super().__init__(name="Infectious Inspiration", origin="College of Eloquence Bard Level 14", action_type="reaction", range="60 Feet", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        cha_mod = character_stat_block.get_ability_modifier(Ability.CHARISMA)
        uses = max(1, cha_mod)
        description = (
            "When you successfully inspire someone, the power of your eloquence can now spread to someone else. "
            "When a creature within 60 feet of you adds one of your Bardic Inspiration dice to its ability check, "
            "attack roll, or saving throw and the roll succeeds, you can use your reaction to encourage a different "
            "creature (other than yourself) that can hear you within 60 feet of you, giving it a Bardic Inspiration "
            "die without expending any of your Bardic Inspiration uses."
        )
        return description
