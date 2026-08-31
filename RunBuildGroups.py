import argparse

from Combat.Campaigns.CurseOfTheLich.Players import get_players_group_not_obmar
from Utils.BuildGroupSheetWriter import write_build_group_pages


def _parse_level_range(value: str) -> tuple[int, int]:
    """'4' -> (4, 4); '4-6' -> (4, 6)."""
    if "-" in value:
        start, end = value.split("-", 1)
        return int(start), int(end)
    level = int(value)
    return level, level


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate joint BuildGroup character sheets (features/spells/items/weapons.html)."
    )
    parser.add_argument(
        "--level",
        type=str,
        default=None,
        help=(
            "Restrict Features and Spells to a single level ('4') or an "
            "inclusive level range ('4-6'). Items and Weapons are always "
            "shown in full, since they aren't tied to a grant level. "
            "Default: all levels."
        ),
    )
    args = parser.parse_args()

    min_level = max_level = None
    folder_suffix = ""
    if args.level is not None:
        min_level, max_level = _parse_level_range(args.level)
        folder_suffix = (
            f"_level{min_level}"
            if min_level == max_level
            else f"_level{min_level}-{max_level}"
        )

    group_name = "Players (not Obmar)"  # Hardcoded for now; can be made dynamic later.
    characters = get_players_group_not_obmar()
    print(f"Generating build group sheets for {group_name}...")
    write_build_group_pages(
        group_name=group_name,
        output_folder=f"Output/BuildGroups/{group_name}{folder_suffix}",
        characters=characters,
        min_level=min_level,
        max_level=max_level,
    )
