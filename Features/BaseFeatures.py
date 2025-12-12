from abc import ABC, abstractmethod
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Definitions import Ability, Skill, DiceRollCondition
from Utils.CharacterSheetUtils import write_table


class Feature(ABC):
    """A feature can be anything"""

    @abstractmethod
    def write_to_file(self, character_stat_block: CharacterStatBlock, file):
        pass

    @abstractmethod
    def modify(self, character_stat_block: CharacterStatBlock):
        pass


class CharacterFeature(Feature):
    """A feature that can modify a character's stat block."""

    def write_to_file(self, character_stat_block: CharacterStatBlock, file):
        pass


class TextFeature(Feature):
    """A feature that doesn't change that stats of the character."""

    def __init__(self, name: str, origin: str):
        self.name = name
        self.origin = origin
        self.additional_features = []
        super().__init__()

    def add_feature(self, feature: "TextFeature"):
        self.additional_features.append(feature)

    @abstractmethod
    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        pass

    def modify(self, character_stat_block: CharacterStatBlock):
        pass

    def add_feature_effects(
        self, character_stat_block: CharacterStatBlock, text_feature: "TextFeature"
    ):
        description = text_feature.get_description(character_stat_block)
        indent = "    "
        indented = "\n".join(
            (indent + line) if line.strip() else "" for line in description.splitlines()
        )
        text = "\n"  # Separate the sections
        text += f"    {text_feature.name} {text_feature.origin}:\n"  # Indent first line
        text += indented + "\n"
        return text

    def write_to_file(self, character_stat_block: CharacterStatBlock, file):
        file.write(f"Name: {self.name}\n")
        file.write(f"Origin: {self.origin}\n")
        description = self.get_description(character_stat_block)
        for addition in self.additional_features:
            description += self.add_feature_effects(character_stat_block, addition)
        if description[-1] != "\n":
            description += "\n"  # Ensure newline at end
        file.write(f"Description: {description}\n")


class MagicianDruidFeature(CharacterFeature):
    """Add WIS modifier in either arcana or nature (Magician druid)"""

    def __init__(self, skill: Skill):
        self.skill = skill
        # Validate
        if self.skill not in (Skill.ARCANA, Skill.NATURE):
            raise ValueError(
                "MagicianDruidFeature can only be applied to Arcana or Nature skills."
            )

    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.skills.bonuses[self.skill] = (
            character_stat_block.get_ability_modifier(Ability.WISDOM)
        )


class SkillfulFeature(CharacterFeature):
    """Add proficiency in a skill of your choice."""

    def __init__(self, skill: Skill):
        self.skill = skill

    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.skills.proficiencies[self.skill] = True
