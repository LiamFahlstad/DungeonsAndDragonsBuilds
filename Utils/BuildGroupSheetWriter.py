import pathlib
from typing import Literal, Optional, TYPE_CHECKING

from Utils import Html
from Utils.CharacterSheetWriters import HtmlCharacterSheetWriter

if TYPE_CHECKING:
    from Builds.CharacterSheetAccumulator import CharacterSheetData


def _level_label(min_level: Optional[int], max_level: Optional[int]) -> str:
    if min_level is None and max_level is None:
        return ""
    if min_level == max_level:
        return f" (Level {min_level})"
    return f" (Levels {min_level}-{max_level})"


def write_build_group_pages(
    group_name: str,
    output_folder: str,
    characters: list["CharacterSheetData"],
    description_mode: Literal["table", "concise"] | None = None,
    include_probability_tables: bool = False,
    min_level: Optional[int] = None,
    max_level: Optional[int] = None,
):
    """Four joint HTML pages (features/spells/items/weapons.html) combining
    every character in the group's cards of that type into one file. Each
    character's block is preceded by a small '.build-group-owner' label so
    entries stay attributable once merged, and each individual card keeps
    break-inside: avoid on its own card class (.feature-card, .spell-entry,
    .weapon-entry, .gear-entry) so a page break never cuts through the
    middle of one - the whole card is pushed to the next page instead.

    min_level/max_level restrict Features and Spells to those granted within
    that (inclusive) character-level range; None on either bound means
    unbounded on that side, and leaving both None (the default) reproduces
    the original all-levels behavior. Items and Weapons aren't tied to a
    grant level in this codebase's data model, so they're unaffected by
    these bounds and always show everything."""
    output_folder_obj = pathlib.Path(output_folder)
    output_folder_obj.mkdir(parents=True, exist_ok=True)

    writer = HtmlCharacterSheetWriter()
    prepared = [
        (character_sheet_data, character_sheet_data.setup_character_stat_block())
        for character_sheet_data in characters
    ]

    _write_features_page(
        writer,
        output_folder_obj / "features.html",
        group_name,
        prepared,
        description_mode,
        min_level,
        max_level,
    )
    _write_spells_page(
        writer, output_folder_obj / "spells.html", group_name, prepared, min_level, max_level
    )
    _write_weapons_page(
        writer,
        output_folder_obj / "weapons.html",
        group_name,
        prepared,
        include_probability_tables,
    )
    _write_items_page(writer, output_folder_obj / "items.html", group_name, prepared)


def _write_features_page(
    writer: HtmlCharacterSheetWriter,
    path: pathlib.Path,
    group_name: str,
    prepared: list,
    description_mode: Optional[Literal["table", "concise"]],
    min_level: Optional[int] = None,
    max_level: Optional[int] = None,
):
    with open(path, "w", encoding="utf-8") as file:
        file.write(writer._get_css_style())
        file.write(f"<h1>{group_name} - Features{_level_label(min_level, max_level)}</h1>\n")
        file.write("<div class='features'>\n")
        for character_sheet_data, stat_block in prepared:
            text_features = [
                f
                for f in character_sheet_data.features
                if f.render_html_description(stat_block, description_mode) is not None
                and (min_level is None or writer._feature_level(f) >= min_level)
                and (max_level is None or writer._feature_level(f) <= max_level)
            ]
            if not text_features:
                continue
            file.write(f"<div class='build-group-owner'>{stat_block.name}</div>\n")
            sorted_features = sorted(text_features, key=writer._sort_features_key)
            for feature in sorted_features:
                # max_level caps nested extension cards to the requested
                # range's upper bound, same mechanism the per-level shard
                # pages use (see HtmlCharacterSheetWriter._write_features_page).
                feature.write_to_file(stat_block, file, description_mode, max_level=max_level)
        file.write("</div>\n")


def _write_spells_page(
    writer: HtmlCharacterSheetWriter,
    path: pathlib.Path,
    group_name: str,
    prepared: list,
    min_level: Optional[int] = None,
    max_level: Optional[int] = None,
):
    with open(path, "w", encoding="utf-8") as file:
        file.write(writer._get_css_style())
        file.write(f"<h1>{group_name} - Spells{_level_label(min_level, max_level)}</h1>\n")
        for character_sheet_data, stat_block in prepared:
            level_filtered_spells = [
                spell
                for spell in character_sheet_data.spells
                if (min_level is None or writer._spell_level(spell) >= min_level)
                and (max_level is None or writer._spell_level(spell) <= max_level)
            ]
            if not level_filtered_spells:
                continue
            file.write(f"<div class='build-group-owner'>{stat_block.name}</div>\n")
            writer._write_spell_cards(stat_block, file, level_filtered_spells)


def _write_weapons_page(
    writer: HtmlCharacterSheetWriter,
    path: pathlib.Path,
    group_name: str,
    prepared: list,
    include_probability_tables: bool,
):
    with open(path, "w", encoding="utf-8") as file:
        file.write(writer._get_css_style())
        file.write(f"<h1>{group_name} - Weapons</h1>\n")
        for character_sheet_data, stat_block in prepared:
            if not character_sheet_data.weapons:
                continue
            file.write(f"<div class='build-group-owner'>{stat_block.name}</div>\n")
            writer._write_weapons(
                stat_block,
                file,
                character_sheet_data.weapons,
                character_sheet_data.weapon_masteries,
                include_probability_tables,
            )


def _write_items_page(
    writer: HtmlCharacterSheetWriter, path: pathlib.Path, group_name: str, prepared: list
):
    with open(path, "w", encoding="utf-8") as file:
        file.write(writer._get_css_style())
        file.write(f"<h1>{group_name} - Items</h1>\n")
        for character_sheet_data, stat_block in prepared:
            non_empty_entries = [
                entry
                for entry in character_sheet_data.equipment_entries
                if entry.armors or entry.weapons or entry.items or entry.gold
            ]
            if not non_empty_entries:
                continue
            combined_rows = []
            for entry in non_empty_entries:
                is_starting_equipment = entry is character_sheet_data.starting_equipment_entry
                sections = writer._build_item_sections(entry, is_starting_equipment)
                for title, rows in sections:
                    if title == "Weapons":
                        continue  # weapon attack cards live on weapons.html instead
                    combined_rows.extend(rows)
            if not combined_rows:
                continue
            file.write(f"<div class='build-group-owner'>{stat_block.name}</div>\n")
            Html.write_item_cards(file, None, combined_rows)
