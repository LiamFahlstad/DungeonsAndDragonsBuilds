"""
Generator for Python monster classes from Combat/monsters_raw.json
Creates subdirectories under Combat/Monsters/ organized by CR tier
"""
import json
import re
from pathlib import Path
from typing import Optional


def class_name_from_monster_name(name: str) -> str:
    """Convert monster name to Python class name.
    Example: "Ancient Red Dragon" -> "AncientRedDragon"
    """
    # Remove non-alphanumeric characters, but keep spaces
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", name)
    # Split on whitespace, title case each word, join
    words = cleaned.split()
    return "".join(word.capitalize() for word in words)


def cr_to_tier(cr: str) -> int:
    """Convert CR string to integer tier.
    Fractions (1/8, 1/4, 1/2) -> 0
    Integers -> themselves
    """
    cr = cr.strip()
    if "/" in cr:
        # It's a fraction
        return 0
    try:
        return int(cr)
    except ValueError:
        return 0


def format_dict_field(d: dict, indent: int = 12) -> str:
    """Format a dictionary for Python code."""
    if not d:
        return "{}"
    indent_str = " " * indent
    items = []
    for key, value in d.items():
        if isinstance(value, str):
            items.append(f'"{key}": "{value}"')
        else:
            items.append(f'"{key}": {value}')
    return "{" + ", ".join(items) + "}"


def format_list_field(lst: list, indent: int = 12) -> str:
    """Format a list for Python code."""
    if not lst:
        return "[]"
    items = [f'"{item}"' for item in lst]
    return "[" + ", ".join(items) + "]"


def format_ability_list(abilities: list) -> str:
    """Format a list of ability dicts as a Python literal."""
    if not abilities:
        return "[]"
    lines = ["["]
    for ab in abilities:
        name = ab.get("name", "").replace('"', '\\"')
        desc = ab.get("description", "").replace('"', '\\"').replace("\n", " ")
        lines.append(f'        {{"name": "{name}", "description": "{desc}"}},')
    lines.append("    ]")
    return "\n    ".join(lines)


def generate_monster_class(monster: dict) -> str:
    """Generate Python class code for a monster."""
    class_name = class_name_from_monster_name(monster.get("name", "Unknown"))

    # Build ability_scores string
    ability_scores = monster.get("ability_scores", {})
    if not ability_scores:
        ability_scores_str = "{}"
    else:
        ability_scores_str = format_dict_field(ability_scores)

    # Build saving_throws string
    saving_throws = monster.get("saving_throws", {})
    saving_throws_str = format_dict_field(saving_throws)

    # Build skills string
    skills = monster.get("skills", {})
    skills_str = format_dict_field(skills)

    # Build damage lists
    damage_vuln = monster.get("damage_vulnerabilities", [])
    damage_vuln_str = format_list_field(damage_vuln)

    damage_resist = monster.get("damage_resistances", [])
    damage_resist_str = format_list_field(damage_resist)

    damage_immune = monster.get("damage_immunities", [])
    damage_immune_str = format_list_field(damage_immune)

    cond_immune = monster.get("condition_immunities", [])
    cond_immune_str = format_list_field(cond_immune)

    # Build ability lists
    traits = monster.get('traits', [])
    traits_str = format_ability_list(traits)

    actions = monster.get('actions', [])
    actions_str = format_ability_list(actions)

    bonus_actions = monster.get('bonus_actions', [])
    bonus_actions_str = format_ability_list(bonus_actions)

    reactions = monster.get('reactions', [])
    reactions_str = format_ability_list(reactions)

    legendary_actions = monster.get('legendary_actions', [])
    legendary_actions_str = format_ability_list(legendary_actions)

    lair_actions = monster.get('lair_actions', [])
    lair_actions_str = format_ability_list(lair_actions)

    mythic_actions = monster.get('mythic_actions', [])
    mythic_actions_str = format_ability_list(mythic_actions)

    legendary_resistances = monster.get('legendary_resistances', 0)

    # Build the class string
    class_code = f"""class {class_name}(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            name="{monster.get('name', '')}",
            hp={monster.get('hp', 0)},
            ac={monster.get('ac', 0)},
            temp_hp=0,
            conditions=[],
            ability_scores={ability_scores_str},
            saving_throws={saving_throws_str},
            spell_slots={{}},
            cr="{monster.get('cr', '')}",
            monster_type="{monster.get('type', '')}",
            ac_note="{monster.get('ac_note', '')}",
            hp_formula="{monster.get('hp_formula', '')}",
            speed="{monster.get('speed', '')}",
            skills={skills_str},
            damage_vulnerabilities={damage_vuln_str},
            damage_resistances={damage_resist_str},
            damage_immunities={damage_immune_str},
            condition_immunities={cond_immune_str},
            senses="{monster.get('senses', '')}",
            languages="{monster.get('languages', '')}",
            traits={traits_str},
            actions={actions_str},
            bonus_actions={bonus_actions_str},
            reactions={reactions_str},
            legendary_actions={legendary_actions_str},
            legendary_resistances={legendary_resistances},
            lair_actions={lair_actions_str},
            mythic_actions={mythic_actions_str},
        )
"""
    return class_code


def generate_monsters_file(monsters: list[dict], tier: int) -> tuple[str, list[str]]:
    """Generate the content of a monsters.py file for a tier."""
    # Sort monsters by name within the tier
    sorted_monsters = sorted(monsters, key=lambda m: m.get("name", ""))

    class_names = []
    class_codes = []

    for monster in sorted_monsters:
        class_name = class_name_from_monster_name(monster.get("name", "Unknown"))
        class_names.append(class_name)
        class_codes.append(generate_monster_class(monster))

    # Build the file content
    file_content = """# Auto-generated by generate_monsters.py — do not edit manually
from Combat.Definitions import ExtendedCombatantData


"""
    file_content += "\n\n".join(class_codes)
    file_content += f"\n\n__all__ = {class_names}\n"

    return file_content, class_names


def generate_init_file(class_names: list[str]) -> str:
    """Generate an __init__.py file for a CR subdirectory."""
    file_content = """# Auto-generated by generate_monsters.py — do not edit manually
from .monsters import *  # noqa: F401, F403
"""
    return file_content


if __name__ == "__main__":
    # Read raw monster data
    raw_data_path = Path(__file__).parent / "monsters_raw.json"
    if not raw_data_path.exists():
        print(f"Error: {raw_data_path} not found. Run scrape_monsters.py first.")
        exit(1)

    with open(raw_data_path, "r", encoding="utf-8") as f:
        monsters_data = json.load(f)

    print(f"Loaded {len(monsters_data)} monsters from {raw_data_path}")

    # Group monsters by CR tier
    tier_monsters = {}
    for monster in monsters_data:
        cr = monster.get("cr", "")
        tier = cr_to_tier(cr)
        if tier not in tier_monsters:
            tier_monsters[tier] = []
        tier_monsters[tier].append(monster)

    print(f"Organized into {len(tier_monsters)} CR tiers")

    # Create base Monsters directory
    monsters_dir = Path(__file__).parent / "Monsters"
    monsters_dir.mkdir(parents=True, exist_ok=True)

    # Generate files for each tier
    total_files = 0
    total_classes = 0

    for tier in sorted(tier_monsters.keys()):
        tier_dir = monsters_dir / f"CR_{tier}"
        tier_dir.mkdir(parents=True, exist_ok=True)

        monsters_in_tier = tier_monsters[tier]
        file_content, class_names = generate_monsters_file(monsters_in_tier, tier)

        # Write monsters.py
        monsters_file = tier_dir / "monsters.py"
        with open(monsters_file, "w", encoding="utf-8") as f:
            f.write(file_content)

        # Write __init__.py
        init_file = tier_dir / "__init__.py"
        with open(init_file, "w", encoding="utf-8") as f:
            f.write(generate_init_file(class_names))

        total_files += 2
        total_classes += len(class_names)
        print(
            f"  CR {tier}: {len(class_names)} classes ({len(monsters_in_tier)} monsters)"
        )

    # Create main Monsters/__init__.py with only the tiers that exist
    import_lines = []
    for tier in sorted(tier_monsters.keys()):
        import_lines.append(f"from .CR_{tier} import *  # noqa: F401, F403")

    main_init_content = """# Auto-generated by generate_monsters.py — do not edit manually
""" + "\n".join(import_lines) + "\n"
    main_init_file = monsters_dir / "__init__.py"
    with open(main_init_file, "w", encoding="utf-8") as f:
        f.write(main_init_content)

    print(f"\nGeneration complete!")
    print(f"Generated {total_files} files with {total_classes} monster classes")
    print(f"Output directory: {monsters_dir}")
