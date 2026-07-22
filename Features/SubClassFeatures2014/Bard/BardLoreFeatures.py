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
        description = "You learn how to use your wit to distract, confuse, and otherwise sap the confidence and competence of others. When a creature that you can see within 60 feet of you makes an attack roll, an ability check, or a damage roll, you can use your reaction to expend one of your uses of Bardic Inspiration, rolling a Bardic Inspiration die and subtracting the number rolled from the creature's roll. You can choose to use this feature after the creature makes its roll, but before the DM determines whether the attack roll or ability check succeeds or fails, or before the creature deals its damage. The creature is immune if it can't hear you or if it's immune to being charmed."
        return description


class AdditionalMagicalSecrets(Feature):
    def __init__(self):
        super().__init__(
            name="Additional Magical Secrets", origin="College of Lore Bard Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You learn two spells of your choice from any class. A spell you choose must be of a level you can cast, as shown on the Bard table, or a cantrip. The chosen spells count as bard spells for you but don't count against the number of bard spells you know."
        return description


class PeerlessSkill(Feature):
    def __init__(self):
        super().__init__(name="Peerless Skill", origin="College of Lore Bard Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you make an ability check, you can expend one use of Bardic Inspiration. Roll a Bardic Inspiration die and add the number rolled to your ability check. You can choose to do so after you roll the die for the ability check, but before the DM tells you whether you succeed or fail."
        return description
