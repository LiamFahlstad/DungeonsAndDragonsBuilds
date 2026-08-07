from typing import TextIO

from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import Html

FEATURE_CARD_CSS = """/* ── Feature cards ───────────────────────────────────────────────── */
        .feature-card {
            border: 1px solid #b89060;
            border-radius: 4px;
            overflow: hidden;
            margin: 0 0 0.55rem 0;
            max-width: none;
            padding: 0;
        }

        .feature-header {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: 0.8rem;
            padding: 5px 10px;
            border-bottom: 2px solid #9a7040;
            max-width: none;
            margin: 0;
        }

        .feature-name {
            font-size: 1rem;
            font-weight: 700;
            color: #4a3020;
            letter-spacing: 0.02em;
        }

        .feature-origin {
            font-size: 0.75rem;
            color: #9a7040;
            font-style: italic;
            white-space: nowrap;
            flex-shrink: 0;
        }

        .feature-body {
            padding: 0.4rem 0.7rem;
            font-size: 0.88rem;
            max-width: none;
            margin: 0;
        }

        .feature-body p {
            margin: 0.3em 0;
        }

        .feature-body ul,
        .feature-body ol {
            margin: 0.3em 0 0.3em 1.2em;
        }

        /* Tables embedded inside feature descriptions (e.g. item/plan lists) */
        .feature-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.82rem;
            margin: 0.4rem 0;
        }

        .feature-table td,
        .feature-table th {
            border: 1px solid var(--border-color);
            padding: 3px 7px;
            vertical-align: top;
            text-align: left;
        }

        .feature-table th {
            color: #3a2c1c;
            font-weight: 700;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            background: #f4ede0;
            border-bottom: 2px solid #9a7040;
        }

        .feature-table tr:nth-child(even) td {
            background: #faf7f2;
        }

        /* Feature upgrade blocks (nested inside .feature-body) */
        .feature-upgrade {
            margin-top: 0.5rem;
            border-left: 3px solid #9abbe0;
            border-radius: 0 3px 3px 0;
            padding: 0.3rem 0.6rem;
            max-width: none;
        }

        .feature-upgrade-label {
            display: block;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #3a6090;
            margin-bottom: 0.15rem;
        }

        .feature-upgrade-body {
            font-size: 0.85rem;
            color: #333;
            max-width: none;
            margin: 0;
            padding: 0;
        }

        .inv-source {
            font-size: 0.75em;
            color: #999;
            font-style: italic;
            margin-top: 0.35em;
        }

        """


class Feature:
    """A single feature type. Override apply() to modify the stat block, get_description() to render a card, or both."""

    def __init__(self, name: str | None = None, origin: str | None = None):
        self.name = name if name is not None else type(self).__name__
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
        from Utils.Html import _bold_prefix

        bolded = _bold_prefix(text, ".", 5)
        if bolded is not None:
            return bolded
        bolded = _bold_prefix(text, ":", 10)
        if bolded is not None:
            return bolded
        return text

    @staticmethod
    def _description_to_html(description: str) -> str:
        processed = Html.boxes_to_html(description)
        processed = Html.tables_to_html(processed)

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
                    bullet_text = line[len(prefix) :]
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
        return Html.highlight_damage_types(result)
