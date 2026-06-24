from Definitions import CreatureSize, Skill
from Features.BaseFeatures import CharacterFeature, TextFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

SPEED = 30  # Given by your species
SIZE = CreatureSize.MEDIUM  # Given by your species


class Darkvision(TextFeature):
    def __init__(self, distance: int):
        self.distance = distance
        super().__init__(name="Darkvision", origin="Khoravar Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return f"You have Darkvision with a range of {self.distance} feet."


class FeyAncestry(TextFeature):
    def __init__(self):
        super().__init__(name="Fey Ancestry", origin="Khoravar Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Advantage on saving throws you make to avoid or end the Charmed condition."


class FeyGift(TextFeature):
    def __init__(self):
        super().__init__(name="Fey Gift", origin="Khoravar Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "You know the Friends cantrip. Whenever you finish a Long Rest, you can replace that cantrip with a different cantrip "
            "from the Cleric, Druid, or Wizard spell list. Intelligence, Wisdom, or Charisma is your spellcasting ability for the "
            "spell you cast with this trait (chosen when you select this species)."
        )


class SkillVersatility(CharacterFeature):
    def __init__(self, skill: Skill):
        self.skill = skill

    def validate(self, character_stat_block: CharacterStatBlock):
        assert not character_stat_block.skills.is_proficient(self.skill)

    def modify(self, character_stat_block: CharacterStatBlock):
        self.validate(character_stat_block)
        return character_stat_block.skills.add_skill_proficiency(self.skill)


class LethargyResilience(TextFeature):
    def __init__(self):
        super().__init__(name="Lethargy Resilience", origin="Khoravar Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "When you fail a saving throw to avoid or end the Unconscious condition, you can succeed instead. Once you use this trait, you can’t do so again until you finish 1d4 Long Rests."
