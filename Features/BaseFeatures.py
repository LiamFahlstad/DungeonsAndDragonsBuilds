from abc import ABC, abstractmethod
from typing import TextIO

from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class Feature(ABC):
    """A feature can be anything"""

    @abstractmethod
    def write_to_file(
        self, character_stat_block: CharacterStatBlock, file: TextIO
    ):
        pass

    @abstractmethod
    def modify(self, character_stat_block: CharacterStatBlock):
        pass


class CharacterFeature(Feature):
    """A feature that can modify a character's stat block."""

    def write_to_file(
        self, character_stat_block: CharacterStatBlock, file: TextIO
    ):
        raise NotImplementedError(
            "CharacterFeature must implement write_to_file method."
        )


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
        text = f"(Upgrade) {text_feature.name} - {text_feature.origin}:\n"  # Indent first line
        text += description + "\n"
        return text

    def write_to_file(  # writes HTML
        self, character_stat_block: CharacterStatBlock, file: TextIO
    ):
        description = self.get_description(character_stat_block)
        for addition in self.additional_features:
            description += "\n" + self.add_feature_effects(
                character_stat_block, addition
            )

        html_description = description.replace("\n", "<br>\n").replace(
            "    ", "&nbsp;&nbsp;&nbsp;&nbsp;"
        )

        if not html_description.endswith("\n"):
            html_description += "\n"

        html_description = StringUtils.bolden_text_html(html_description)
        html_description = StringUtils.boxes_to_html(html_description)
        file.write(f"<h3>{self.name}</h3>\n")
        file.write(f"<strong>Origin:</strong> {self.origin}\n<br>\n")
        file.write("<strong>Description:</strong><br>\n")
        file.write(f"{html_description}\n")
