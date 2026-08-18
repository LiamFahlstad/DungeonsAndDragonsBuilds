from typing import Literal, TextIO

from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import Html

FEATURE_CARD_CSS = """/* ── Feature cards ───────────────────────────────────────────────── */
        .features {
            max-width: 100%;
        }

        .feature-card {
            margin: 0 0 0.4rem 0;
            max-width: none;
            padding: 0 0 0.4rem 0;
        }

        .feature-card + .feature-card {
            border-top: 2px solid #9a7040;
            padding-top: 0.4rem;
        }

        .feature-header {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: 0.8rem;
            padding: 5px 10px;
            border-bottom: 1px solid #d8c8a8;
            max-width: none;
            margin: 0;
        }

        .feature-name-group {
            display: flex;
            align-items: baseline;
            gap: 0.5rem;
        }

        .feature-name {
            font-size: 1rem;
            font-weight: 700;
            color: #4a3020;
            letter-spacing: 0.02em;
        }

        /* Shown on full-mode sheets for features normally skipped in concise
           mode — flags at a glance that there's nothing here to actively track. */
        .feature-passive-tag {
            display: inline-block;
            font-size: 0.68rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--muted-color);
            border: 1px solid #bbb;
            border-radius: 3px;
            padding: 1px 6px;
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

        /* Core resource numbers (e.g. Martial Arts die, Focus Points) called
           out at the top of a feature's own card - reuses .stat-tile /
           .stat-tile-resource from the base sheet CSS, just laid out to fit
           inside a card instead of the overview row. The sheet isn't
           reprinted every level-up, so every level's value is shown as an
           equally-weighted box - there's no "current level" callout, since
           that would go stale the moment the player levels up without a
           reprint. */
        .feature-resource-section {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            margin: 0 0 0.5rem 0;
        }

        .feature-resource-group-label {
            display: block;
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #6a5636;
            margin-bottom: 0.2rem;
        }

        .feature-resource-tiles {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
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
            border-bottom: 2px solid #9a7040;
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

    # Optional alternate renderings: get_table_description() and get_concise_description()
    # both fall back to get_description() when they return None.

    def __init__(
        self,
        name: str | None = None,
        origin: str | None = None,
        skippable_in_concise: bool = False,
    ):
        self.name = name if name is not None else type(self).__name__
        self.origin = origin
        self.extensions: list["Feature"] = []
        # Set True for features that only modify the stat block (e.g. a flat bonus
        # or a resource pool) where the prose description adds nothing on a
        # concise/table character sheet. Full-mode sheets always show it.
        self.skippable_in_concise = skippable_in_concise

    def extend_feature(self, feature: "Feature"):
        self.extensions.append(feature)

    def apply(self, character_stat_block: CharacterStatBlock):
        pass

    def get_description(self, character_stat_block: CharacterStatBlock) -> str | None:
        return None

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]] | None:
        """Override to provide a concise label/value table version of the description
        (e.g. [("What", "..."), ("Casting Time", "...")]), used when table descriptions
        are requested. Return None to fall back to get_description()."""
        return None

    def get_concise_description(
        self, character_stat_block: CharacterStatBlock
    ) -> str | None:
        """Override to provide a short prose summary of the description (a sentence
        or two, same formatting rules as get_description), used when concise
        descriptions are requested. Return None to fall back to get_description()."""
        return None

    def get_resource_tiles(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, list[tuple[str, str]]]] | None:
        """Override to surface this feature's core numbers as small stat
        tiles at the top of its own feature card (visually the same idea as
        the Max HP tile, sized down to fit a card) for resources checked
        constantly in play - e.g. a martial arts die size or a resource
        point total. Returns a list of (group_label, steps) tuples, where
        steps is a list of (step_label, value) pairs - typically one tile
        per level or level-range, e.g. [("Martial Arts Die",
        [("Lv 1-4", "1d6"), ("Lv 5-10", "1d8"), ...])], commonly built from
        StringUtils.compress_level_progression(). Every step is shown with
        equal weight and no "current level" is called out: the generated
        page isn't reprinted on every level-up, so a step highlighted as
        "current" at generation time would silently go stale. Return None
        (default) for features with no resource tile at all."""
        return None

    def render_html_description(
        self,
        character_stat_block: CharacterStatBlock,
        description_mode: Literal["table", "concise"] | None = None,
    ) -> str | None:
        if description_mode is not None and self.skippable_in_concise:
            return None

        if description_mode == "table":
            table_rows = self.get_table_description(character_stat_block)
            if table_rows is not None:
                return Html.highlight_damage_types(
                    Html.key_value_table_to_html(table_rows)
                )

        if description_mode == "concise":
            concise_description = self.get_concise_description(character_stat_block)
            if concise_description is not None:
                return self._description_to_html(concise_description)

        description = self.get_description(character_stat_block)
        if description is None:
            return None
        return self._description_to_html(description)

    def write_to_file(
        self,
        character_stat_block: CharacterStatBlock,
        file: TextIO,
        description_mode: Literal["table", "concise"] | None = None,
    ):
        html_description = self.render_html_description(
            character_stat_block, description_mode
        )
        if html_description is None:
            return

        # A skippable-in-concise feature that's still showing means we're on a
        # full-mode sheet — flag it as passive so the player knows there's
        # nothing here to actively track.
        passive_tag = (
            "<span class='feature-passive-tag'>Passive</span>"
            if description_mode is None and self.skippable_in_concise
            else ""
        )

        file.write("<div class='feature-card'>\n")
        file.write("<div class='feature-header'>\n")
        file.write("<span class='feature-name-group'>\n")
        file.write(f"<span class='feature-name'>{self.name}</span>\n")
        if passive_tag:
            file.write(f"{passive_tag}\n")
        file.write("</span>\n")
        file.write(f"<span class='feature-origin'>{self.origin}</span>\n")
        file.write("</div>\n")
        file.write("<div class='feature-body'>\n")

        resource_tiles = self.get_resource_tiles(character_stat_block)
        if resource_tiles:
            file.write("<div class='feature-resource-section'>\n")
            for group_label, steps in resource_tiles:
                file.write("<div class='feature-resource-group'>\n")
                file.write(
                    f"<span class='feature-resource-group-label'>{group_label}</span>\n"
                )
                file.write("<div class='feature-resource-tiles'>\n")
                for step_label, value in steps:
                    file.write(self._resource_tile_html(step_label, value))
                file.write("</div>\n")
                file.write("</div>\n")
            file.write("</div>\n")

        file.write(f"{html_description}\n")

        for extension in self.extensions:
            ext_html = extension.render_html_description(
                character_stat_block, description_mode
            )
            if ext_html is None:
                continue
            ext_passive_tag = (
                " <span class='feature-passive-tag'>Passive</span>"
                if description_mode is None and extension.skippable_in_concise
                else ""
            )
            file.write(
                f"<div class='feature-upgrade'>\n"
                f"<span class='feature-upgrade-label'>{extension.origin}: {extension.name}{ext_passive_tag}</span>\n"
                f"<div class='feature-upgrade-body'>{ext_html}</div>\n"
                f"</div>\n"
            )

        file.write("</div>\n")
        file.write("</div>\n")

    @staticmethod
    def _resource_tile_html(label: str, value) -> str:
        return (
            "<div class='stat-tile stat-tile-resource'>"
            f"<span class='stat-tile-label'>{label}</span>"
            f"<span class='stat-tile-value'>{value}</span>"
            "</div>\n"
        )

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
