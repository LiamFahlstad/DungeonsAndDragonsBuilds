from Core.Definitions import CreatureSize, Skill
from Features.Core.BaseFeatures import Feature
from Features.Core.SubFeatures import SkillProficiencyChoice
from StatBlocks.CharacterStatBlock import CharacterStatBlock

SPEED = 30  # Given by your species
SIZE = CreatureSize.MEDIUM  # Given by your species


class Darkvision(Feature):
    def __init__(self, distance: int):
        self.distance = distance
        super().__init__(name="Darkvision", origin="Khoravar Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return f"You have Darkvision with a range of {self.distance} feet."


class FeyAncestry(Feature):
    def __init__(self):
        super().__init__(name="Fey Ancestry", origin="Khoravar Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Advantage on saving throws you make to avoid or end the Charmed condition."


class FeyGift(Feature):
    def __init__(self):
        super().__init__(name="Fey Gift", origin="Khoravar Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "You know the Friends cantrip. Whenever you finish a Long Rest, you can replace that cantrip with a different cantrip "
            "from the Cleric, Druid, or Wizard spell list. Intelligence, Wisdom, or Charisma is your spellcasting ability for the "
            "spell you cast with this trait (chosen when you select this species)."
        )


class SkillVersatility(Feature):
    def __init__(self, skill: Skill):
        self.skill = skill
        super().__init__(name="Skill Versatility", origin="Khoravar Trait")
        self._choice = SkillProficiencyChoice(
            [skill], list(Skill), count=1, error_prefix="SkillVersatility"
        )

    def apply(self, character_stat_block: CharacterStatBlock):
        self._choice.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return f"You gain proficiency in the {self.skill.value} skill."


class LethargyResilience(Feature):
    def __init__(self):
        super().__init__(name="Lethargy Resilience", origin="Khoravar Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "When you fail a saving throw to avoid or end the Unconscious condition, you can succeed instead. Once you use this trait, you can’t do so again until you finish 1d4 Long Rests."
