from abc import abstractmethod
from typing import TextIO

from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class Feature:
    """A single feature type. Override apply() to modify the stat block, get_description() to render a card, or both."""

    def __init__(self, name: str | None = None, origin: str | None = None):
        self.name = name
        self.origin = origin
        self.extensions: list["Feature"] = []

    def extend_feature(self, feature: "Feature"):
        self.extensions.append(feature)

    def apply(self, character_stat_block: CharacterStatBlock):
        pass

    def get_description(self, character_stat_block: CharacterStatBlock) -> str | None:
        return None

    def write_to_file(self, character_stat_block: CharacterStatBlock, file: TextIO):
        description = self.get_description(character_stat_block)
        if description is None:
            return
        html_description = self._description_to_html(description)

        file.write("<div class='feature-card'>\n")
        file.write("<div class='feature-header'>\n")
        file.write(f"<span class='feature-name'>{self.name}</span>\n")
        file.write(f"<span class='feature-origin'>{self.origin}</span>\n")
        file.write("</div>\n")
        file.write("<div class='feature-body'>\n")
        file.write(f"{html_description}\n")

        for extension in self.extensions:
            ext_description = extension.get_description(character_stat_block)
            if ext_description is None:
                continue
            ext_html = self._description_to_html(ext_description)
            file.write(
                f"<div class='feature-upgrade'>\n"
                f"<span class='feature-upgrade-label'>{extension.origin}: {extension.name}</span>\n"
                f"<div class='feature-upgrade-body'>{ext_html}</div>\n"
                f"</div>\n"
            )

        file.write("</div>\n")
        file.write("</div>\n")

    @staticmethod
    def _bolden_line(text: str) -> str:
        from Utils.StringUtils import _bold_prefix

        bolded = _bold_prefix(text, ".", 5)
        if bolded is not None:
            return bolded
        bolded = _bold_prefix(text, ":", 10)
        if bolded is not None:
            return bolded
        return text

    @staticmethod
    def _description_to_html(description: str) -> str:
        processed = StringUtils.boxes_to_html(description)

        BULLET_PREFIXES = [
            ("            > ", 3),
            ("        - ", 2),
            ("    * ", 1),
        ]

        lines = processed.split("\n")
        html_parts: list[str] = []
        open_levels: list[int] = []

        def close_levels_down_to(target_level: int):
            while open_levels and open_levels[-1] > target_level:
                html_parts.append("</ul>")
                open_levels.pop()

        def close_all_levels():
            while open_levels:
                html_parts.append("</ul>")
                open_levels.pop()

        for line in lines:
            bullet_level = 0
            bullet_text = None
            for prefix, level in BULLET_PREFIXES:
                if line.startswith(prefix):
                    bullet_level = level
                    bullet_text = line[len(prefix):]
                    break

            if bullet_level > 0:
                assert bullet_text is not None
                close_levels_down_to(bullet_level)
                if not open_levels or open_levels[-1] < bullet_level:
                    html_parts.append("<ul>")
                    open_levels.append(bullet_level)
                bolded_text = Feature._bolden_line(bullet_text)
                html_parts.append(f"<li>{bolded_text}</li>")
            else:
                close_all_levels()
                stripped = line.strip()
                if stripped:
                    if stripped.startswith("<"):
                        html_parts.append(stripped)
                    else:
                        bolded = Feature._bolden_line(stripped)
                        html_parts.append(f"<p>{bolded}</p>")

        close_all_levels()

        result = "\n".join(html_parts)
        if result and not result.endswith("\n"):
            result += "\n"
        return result


class CharacterFeature(Feature):
    """Backward compat: a Feature that modifies the stat block and renders no card."""
    pass


class TextFeature(Feature):
    """Backward compat: a Feature that renders a card on the character sheet."""

    def __init__(self, name: str, origin: str):
        super().__init__(name=name, origin=origin)

    @abstractmethod
    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        pass
