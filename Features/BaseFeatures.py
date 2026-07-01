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
    def apply(self, character_stat_block: CharacterStatBlock):
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

    def apply(self, character_stat_block: CharacterStatBlock):
        pass

    @staticmethod
    def _bolden_line(text: str) -> str:
        """Apply bold markup to a single plain-text string (no leading whitespace)."""
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
        # Apply box substitution on the raw description before HTML structuring.
        # bolden_text_html is applied per-line below so bullet prefixes are preserved.
        processed = StringUtils.boxes_to_html(description)

        # Bullet prefixes in order from most-indented to least, so nesting is detected
        # correctly.  Each entry: (prefix_string, nesting_level).
        BULLET_PREFIXES = [
            ("            > ", 3),
            ("        - ", 2),
            ("    * ", 1),
        ]

        lines = processed.split("\n")
        html_parts: list[str] = []
        # Stack tracks open <ul> nesting depths (list of ints).
        open_levels: list[int] = []

        def close_levels_down_to(target_level: int):
            """Close any open <ul> levels deeper than target_level."""
            while open_levels and open_levels[-1] > target_level:
                html_parts.append("</ul>")
                open_levels.pop()

        def close_all_levels():
            while open_levels:
                html_parts.append("</ul>")
                open_levels.pop()

        for line in lines:
            # Detect bullet level by checking prefixes (most-indented first).
            bullet_level = 0
            bullet_text = None
            for prefix, level in BULLET_PREFIXES:
                if line.startswith(prefix):
                    bullet_level = level
                    bullet_text = line[len(prefix) :]
                    break

            if bullet_level > 0:
                # Close any levels strictly deeper than this one (going back up).
                close_levels_down_to(bullet_level)
                # Open a new <ul> if we are not already at this level.
                if not open_levels or open_levels[-1] < bullet_level:
                    html_parts.append("<ul>")
                    open_levels.append(bullet_level)
                # Apply bold markup to the bullet text content only.
                bolded_text = TextFeature._bolden_line(bullet_text)
                html_parts.append(f"<li>{bolded_text}</li>")
            else:
                # Non-bullet line: close all open list levels first.
                close_all_levels()
                stripped = line.strip()
                if stripped:
                    # Preserve structural HTML emitted by boxes_to_html verbatim.
                    if stripped.startswith("<"):
                        html_parts.append(stripped)
                    else:
                        bolded = TextFeature._bolden_line(stripped)
                        html_parts.append(f"<p>{bolded}</p>")

        close_all_levels()

        result = "\n".join(html_parts)
        if result and not result.endswith("\n"):
            result += "\n"
        return result

    def write_to_file(self, character_stat_block: CharacterStatBlock, file: TextIO):
        description = self.get_description(character_stat_block)
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
            ext_html = self._description_to_html(ext_description)
            file.write(
                f"<div class='feature-upgrade'>\n"
                f"<span class='feature-upgrade-label'>{extension.origin}: {extension.name}</span>\n"
                f"<div class='feature-upgrade-body'>{ext_html}</div>\n"
                f"</div>\n"
            )

        file.write("</div>\n")
        file.write("</div>\n")
