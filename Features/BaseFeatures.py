from abc import ABC, abstractmethod
from typing import TextIO

from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class Feature(ABC):
    """A feature can be anything"""

    @abstractmethod
    def write_to_file(self, character_stat_block: CharacterStatBlock, file: TextIO):
        pass

    @abstractmethod
    def modify(self, character_stat_block: CharacterStatBlock):
        pass


class CharacterFeature(Feature):
    """A feature that can modify a character's stat block."""

    def write_to_file(self, character_stat_block: CharacterStatBlock, file: TextIO):
        raise NotImplementedError(
            "CharacterFeature must implement write_to_file method."
        )


class TextFeature(Feature):
    """A feature that doesn't change that stats of the character."""

    def __init__(self, name: str, origin: str):
        self.name = name
        self.origin = origin
        self.extensions: list["TextFeature"] = []
        super().__init__()

    def extend_feature(self, feature: "TextFeature"):
        """Attach an upgrade/expansion to this feature that will be rendered below it."""
        self.extensions.append(feature)

    @abstractmethod
    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        pass

    def modify(self, character_stat_block: CharacterStatBlock):
        pass

    @staticmethod
    def _description_to_html(description: str) -> str:
        html = description.replace("\n", "<br>\n").replace(
            "    ", "&nbsp;&nbsp;&nbsp;&nbsp;"
        )
        if not html.endswith("\n"):
            html += "\n"
        html = StringUtils.bolden_text_html(html)
        html = StringUtils.boxes_to_html(html)
        return html

    def write_to_file(self, character_stat_block: CharacterStatBlock, file: TextIO):
        description = self.get_description(character_stat_block)
        html_description = self._description_to_html(description)

        file.write(f"<h3>{self.name}</h3>\n")
        file.write(f"<strong>Origin:</strong> {self.origin}\n<br>\n")
        file.write("<strong>Description:</strong><br>\n")
        file.write(f"{html_description}\n")

        for extension in self.extensions:
            ext_description = extension.get_description(character_stat_block)
            ext_html = self._description_to_html(ext_description)
            file.write(
                f"<div class='feature-upgrade'>\n"
                f"<span class='feature-upgrade-label'>{extension.origin}: {extension.name}</span>\n"
                f"<div class='feature-upgrade-body'>{ext_html}</div>\n"
                f"</div>\n"
            )
