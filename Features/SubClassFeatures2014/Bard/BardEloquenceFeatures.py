from Definitions import BARD_HIT_DIE, Ability
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class SilverTongue(Feature):
    def __init__(self):
        super().__init__(name="Silver Tongue", origin="College of Eloquence Bard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You are a master at saying the right thing at the right time. When you make a Charisma "
            "(Persuasion) or Charisma (Deception) check, you can treat a d20 roll of 9 or lower as a 10."
        )
        return description


class UnsettlingWords(Feature):
    def __init__(self):
        super().__init__(name="Unsettling Words", origin="College of Eloquence Bard Level 3")

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
        super().__init__(name="Unfailing Inspiration", origin="College of Eloquence Bard Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your inspiring words are so persuasive that others feel driven to succeed. When a creature "
            "adds one of your Bardic Inspiration dice to its ability check, attack roll, or saving throw "
            "and the roll fails, the creature can keep the Bardic Inspiration die."
        )
        return description


class UniversalSpeech(Feature):
    def __init__(self):
        super().__init__(name="Universal Speech", origin="College of Eloquence Bard Level 6")

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
        return StringUtils.add_boxes(description, 1, regain_all_on="long rest")


class InfectiousInspiration(Feature):
    def __init__(self):
        super().__init__(name="Infectious Inspiration", origin="College of Eloquence Bard Level 14")

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
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")
