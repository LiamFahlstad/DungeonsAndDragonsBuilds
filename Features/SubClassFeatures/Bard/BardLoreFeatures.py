from Core.Definitions import BARD_HIT_DIE, Skill
from Features.Core.BaseFeatures import Feature
from Features.Core.SubFeatures import SkillProficiencyChoice
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class BonusProficiencies(Feature):
    def __init__(self, skill_1: Skill, skill_2: Skill, skill_3: Skill):
        super().__init__(name="Bonus Proficiencies", origin="College of Lore Bard Level 3")
        self._proficiency = SkillProficiencyChoice(
            [skill_1, skill_2, skill_3], list(Skill), count=3
        )

    def apply(self, character_stat_block: CharacterStatBlock):
        self._proficiency.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain proficiency with three skills of your choice."
        return description


class CuttingWords(Feature):
    def __init__(self):
        super().__init__(name="Cutting Words", origin="College of Lore Bard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You learn to use your wit to supernaturally distract, confuse, and otherwise sap the confidence and competence of others. When a creature that you can see within 60 feet of yourself makes a damage roll or succeeds on an ability check or attack roll, you can take a Reaction to expend one use of your Bardic Inspiration; roll your Bardic Inspiration die, and subtract the number rolled from the creature's roll, reducing the damage or potentially turning the success into a failure."
        return description


class MagicalDiscoveries(Feature):
    def __init__(self):
        super().__init__(
            name="Magical Discoveries", origin="College of Lore Bard Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You learn two spells of your choice. These spells can come from the Cleric, Druid, or Wizard spell list or any combination thereof (see a class's section for its spell list). A spell you choose must be a cantrip or a spell for which you have spell slots, as shown in the Bard Features table.\n"
            "You always have the chosen spells prepared, and whenever you gain a Bard level, you can replace one of the spells with another spell that meets these requirements."
        )
        return description


class PeerlessSkill(Feature):
    def __init__(self):
        super().__init__(name="Peerless Skill", origin="College of Lore Bard Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you make an ability check or attack roll and fail, you can expend one use of Bardic Inspiration; roll the Bardic Inspiration die, and add the number rolled to the d20, potentially turning a failure into a success. On a failure, the Bardic Inspiration isn't expended."
        return description
