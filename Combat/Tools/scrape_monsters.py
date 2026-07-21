"""
Scraper for monsters from https://www.aidedd.org/monster/
Saves raw monster data to Combat/monsters_raw.json
"""

import json
import re
import time
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup


def parse_ability_scores(text: str) -> dict[str, int]:
    """Parse ability scores from D&D stat block format."""
    abilities = {}
    pattern = r"(\w+)\s+(\d+)"
    matches = re.findall(pattern, text)
    for ability, score in matches:
        if ability in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
            abilities[ability] = int(score)
    return abilities


def parse_hp(hp_text: str) -> tuple[int, str]:
    """Parse HP into (average_hp, formula).
    Example: '52 (8d10+8)' -> (52, '8d10+8')
    """
    hp_text = hp_text.strip()
    # Try to extract average and formula
    match = re.match(r"(\d+)\s*\(([^)]+)\)", hp_text)
    if match:
        avg_hp = int(match.group(1))
        formula = match.group(2)
        return avg_hp, formula
    # Just a number
    try:
        return int(hp_text), ""
    except ValueError:
        return 0, ""


def parse_ac(ac_text: str) -> tuple[int, str]:
    """Parse AC into (ac_value, ac_note).
    Example: '15 (natural armor)' -> (15, 'natural armor')
    """
    ac_text = ac_text.strip()
    # Extract the first number
    match = re.match(r"(\d+)(?:\s*\(([^)]+)\))?", ac_text)
    if match:
        ac_val = int(match.group(1))
        ac_note = match.group(2) if match.group(2) else ""
        return ac_val, ac_note
    return 0, ""


def parse_saves_or_skills(text: str) -> dict[str, int]:
    """Parse saving throws or skills.
    Example: 'STR +3, DEX -1' or 'Stealth +2, Perception +5'
    """
    result = {}
    # Try to find patterns like "Name +/-number". Up to 2 extra words handles
    # three-word skill names like "Sleight of Hand".
    pattern = r"(\w+(?:\s+\w+){0,2})\s+([+-]\d+)"
    matches = re.findall(pattern, text)
    for name, modifier in matches:
        result[name.strip()] = int(modifier)
    return result


def parse_damage_list(text: str) -> list[str]:
    """Parse damage types or condition immunities (comma-separated)."""
    if not text:
        return []
    return [s.strip() for s in text.split(",") if s.strip()]


DAMAGE_TYPES = {
    "acid", "bludgeoning", "cold", "fire", "force", "lightning", "necrotic",
    "piercing", "poison", "psychic", "radiant", "slashing", "thunder",
}
CONDITIONS = {
    "blinded", "charmed", "deafened", "exhaustion", "frightened", "grappled",
    "incapacitated", "invisible", "paralyzed", "petrified", "poisoned",
    "prone", "restrained", "stunned", "unconscious",
}


def get_labeled_field(soup, label: str) -> Optional[str]:
    """Find a <strong>label</strong> tag in the stat block and return the
    text of its siblings up to (but not including) the next <br> or <strong>.
    Returns None if the label isn't present on the page.
    """
    for strong in soup.find_all("strong"):
        if strong.get_text(strip=True) == label:
            parts = []
            for node in strong.next_siblings:
                name = getattr(node, "name", None)
                if name == "br" or name == "strong":
                    break
                parts.append(node if isinstance(node, str) else node.get_text())
            return "".join(parts).strip(" .\n")
    return None


_ABILITY_TABLE_NAMES = {"Str", "Dex", "Con", "Int", "Wis", "Cha"}


def parse_ability_table(soup) -> tuple[dict[str, int], dict[str, int]]:
    """Parse the Str/Dex/Con/Int/Wis/Cha MOD/SAVE grid.
    aidedd.org has no separate "Saving Throws" field for the 2024 stat block
    format — proficient saves only show up as a SAVE value that differs from
    the plain ability MOD in this grid. Returns (ability_scores, saving_throws),
    where saving_throws only includes abilities where SAVE != MOD.
    """
    cells = soup.find_all("div", class_=re.compile(r"^car[1-6]$"))
    texts = [c.get_text(strip=True) for c in cells]
    ability_scores: dict[str, int] = {}
    saving_throws: dict[str, int] = {}
    for i in range(0, len(texts) - 3, 4):
        name, score, mod, save = texts[i], texts[i + 1], texts[i + 2], texts[i + 3]
        if name not in _ABILITY_TABLE_NAMES:
            continue
        try:
            ability_scores[name] = int(score)
        except ValueError:
            continue
        if save != mod:
            try:
                saving_throws[name] = int(save)
            except ValueError:
                pass
    return ability_scores, saving_throws


def parse_immunities(text: str) -> tuple[list[str], list[str]]:
    """Split an "Immunities" field into (damage_immunities, condition_immunities).
    The site combines both in one field as "<damage types>; <conditions>", but
    either half may be omitted (no semicolon) when only one kind applies.
    """
    if not text:
        return [], []
    if ";" in text:
        damage_part, condition_part = text.split(";", 1)
        return parse_damage_list(damage_part), parse_damage_list(condition_part)

    items = parse_damage_list(text)
    if items and items[0].lower() in CONDITIONS:
        return [], items
    return items, []


def parse_ability_sections(soup) -> dict:
    """Parse traits, actions, reactions, legendary actions, etc. from monster stat block HTML.
    Returns a dict with keys: traits, actions, bonus_actions, reactions,
    legendary_actions, legendary_resistances, lair_actions, mythic_actions.
    Each ability is a dict with 'name' and 'description' keys.
    """
    result = {
        "traits": [],
        "actions": [],
        "bonus_actions": [],
        "reactions": [],
        "legendary_actions": [],
        "legendary_resistances": 0,
    }

    # Find all h2 headers with class "rub" (section headers)
    headers = soup.find_all("h2", class_="rub")

    for header in headers:
        section_name = header.get_text(strip=True).lower()

        # Determine which section this is (check longer/more specific patterns first).
        # aidedd.org never has separate "Lair Actions" / "Mythic Actions" headers, so
        # there's nothing to route those into here.
        section_key = None
        if "legendary action" in section_name:
            section_key = "legendary_actions"
        elif "bonus action" in section_name:
            section_key = "bonus_actions"
        elif "reaction" in section_name:
            section_key = "reactions"
        elif "action" in section_name:
            section_key = "actions"
        elif "trait" in section_name:
            section_key = "traits"

        if section_key is None:
            continue

        # Parse all <p> tags following this header until we hit the next h2
        current = header.find_next_sibling()
        while current and current.name != "h2":
            if current.name == "p":
                # Extract ability name and description from the paragraph
                # Format is typically: <strong><em>Name</em></strong>. Description text
                ability_name = ""
                ability_desc = ""

                # Try to get the bolded/italicized name
                strong = current.find("strong")
                if strong:
                    em = strong.find("em")
                    if em:
                        ability_name = em.get_text(strip=True)
                    else:
                        ability_name = strong.get_text(strip=True)

                # Get all text and remove the name part if found
                full_text = current.get_text()
                if ability_name:
                    # Remove the name and leading punctuation from the description
                    ability_desc = full_text.replace(ability_name, "", 1).lstrip(".,: ")
                else:
                    ability_desc = full_text

                ability_name = ability_name.rstrip(".,:")
                ability_desc = ability_desc.strip()

                if ability_name and ability_desc:
                    result[section_key].append(
                        {"name": ability_name, "description": ability_desc}
                    )
                elif ability_name:
                    # Some abilities might only have a name
                    result[section_key].append(
                        {"name": ability_name, "description": ""}
                    )

            current = current.find_next_sibling()

    # Parse legendary resistances count from traits
    for trait in result["traits"]:
        # Match patterns like "Legendary Resistance (3/Day)" or "(4/Day, or 5/Day in Lair)"
        match = re.search(r"Legendary Resistance.*?\((\d+)/Day", trait.get("name", ""))
        if match:
            result["legendary_resistances"] = int(match.group(1))
            break

    return result


def scrape_monster_list() -> list[dict]:
    """Scrape the main monster list page to get slugs and names."""
    url = "https://www.aidedd.org/monster/"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    monsters = []
    # Find all links to individual monsters
    # The site structure has monster links like /monster/monster-name
    links = soup.find_all("a", href=re.compile(r"/monster/[a-z0-9-]+"))
    seen_slugs = set()

    for link in links:
        href = link.get("href", "")
        match = re.search(r"/monster/([a-z0-9-]+)", href)
        if match:
            slug = match.group(1)
            if slug not in seen_slugs:
                name = link.get_text(strip=True)
                if name:
                    monsters.append({"slug": slug, "name": name})
                    seen_slugs.add(slug)

    return monsters


def scrape_monster_detail(slug: str) -> Optional[dict]:
    """Scrape a single monster's stat block."""
    url = f"https://www.aidedd.org/monster/{slug}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"  Error fetching {slug}: {e}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    monster = {
        "slug": slug,
        "name": "",
        "cr": "",
        "type": "",
        "ac": 0,
        "ac_note": "",
        "hp": 0,
        "hp_formula": "",
        "speed": "",
        "ability_scores": {},
        "saving_throws": {},
        "skills": {},
        "damage_vulnerabilities": [],
        "damage_resistances": [],
        "damage_immunities": [],
        "condition_immunities": [],
        "senses": "",
        "languages": "",
        "traits": [],
        "actions": [],
        "bonus_actions": [],
        "reactions": [],
        "legendary_actions": [],
        "legendary_resistances": 0,
    }

    # Extract name from h1
    heading = soup.find("h1")
    if heading:
        monster["name"] = heading.get_text(strip=True)

    # Extract type (e.g., "Medium Elemental, Neutral")
    type_div = soup.find("div", class_="type")
    if type_div:
        type_text = type_div.get_text(strip=True)
        monster["type"] = type_text

    # Parse the main stat block. AC/HP/Speed/Skills/Senses/Languages/CR are each
    # wrapped in their own <strong>Label</strong> tag on aidedd.org, so pull them
    # from the HTML structure directly rather than via fragile flat-text regexes
    # (a plain-text regex bounded by "next capitalized word" breaks on values like
    # "Fly 80 ft." or "Immunities ..." that themselves start with a capital letter).
    ac_text = get_labeled_field(soup, "AC")
    if ac_text:
        monster["ac"], monster["ac_note"] = parse_ac(ac_text)

    hp_text = get_labeled_field(soup, "HP")
    if hp_text:
        monster["hp"], monster["hp_formula"] = parse_hp(hp_text)

    speed_text = get_labeled_field(soup, "Speed")
    if speed_text:
        monster["speed"] = speed_text.strip()

    # Ability scores + saving throws come from the Str/Dex/Con/Int/Wis/Cha
    # MOD/SAVE grid. Some (legacy 2014-format) pages instead have a separate
    # "Saving Throws" label; prefer that when present, otherwise fall back to
    # whatever the table implies.
    ability_scores, table_saving_throws = parse_ability_table(soup)
    if ability_scores:
        monster["ability_scores"] = ability_scores

    skills_text = get_labeled_field(soup, "Skills")
    if skills_text:
        monster["skills"] = parse_saves_or_skills(skills_text)

    saves_text = get_labeled_field(soup, "Saving Throws")
    if saves_text:
        monster["saving_throws"] = parse_saves_or_skills(saves_text)
    elif table_saving_throws:
        monster["saving_throws"] = table_saving_throws

    # Parse damage/condition resistances and immunities.
    # aidedd.org labels these "Vulnerabilities" / "Resistances" / "Immunities"
    # (not "Damage Vulnerabilities" etc.), and "Immunities" combines damage
    # immunities and condition immunities in one field separated by ";".
    vuln_text = get_labeled_field(soup, "Vulnerabilities")
    if vuln_text:
        monster["damage_vulnerabilities"] = parse_damage_list(vuln_text)

    resist_text = get_labeled_field(soup, "Resistances")
    if resist_text:
        monster["damage_resistances"] = parse_damage_list(resist_text)

    immune_text = get_labeled_field(soup, "Immunities")
    if immune_text:
        damage_immunities, condition_immunities = parse_immunities(immune_text)
        monster["damage_immunities"] = damage_immunities
        monster["condition_immunities"] = condition_immunities

    # Parse senses
    senses_text = get_labeled_field(soup, "Senses")
    if senses_text:
        monster["senses"] = senses_text.strip()

    # Parse languages
    languages_text = get_labeled_field(soup, "Languages")
    if languages_text:
        monster["languages"] = languages_text.strip()

    # Parse CR (e.g. "16 (XP 15 000, or 18 000 in Lair; PB +5)" -> "16")
    cr_text = get_labeled_field(soup, "CR")
    if cr_text:
        cr_match = re.search(r"([\d/]+)", cr_text)
        if cr_match:
            monster["cr"] = cr_match.group(1)

    # Parse ability sections from HTML structure
    ability_sections = parse_ability_sections(soup)
    monster.update(ability_sections)

    return monster


if __name__ == "__main__":
    print("Scraping monster list...")
    try:
        monster_list = scrape_monster_list()
        print(f"Found {len(monster_list)} monsters")
    except Exception as e:
        print(f"Error scraping monster list: {e}")
        monster_list = []

    print("\nScraping monster details...")
    monsters_data = []
    failed_count = 0

    for idx, monster_info in enumerate(monster_list):
        if idx % 50 == 0:
            print(f"  Progress: {idx}/{len(monster_list)}")

        monster_detail = scrape_monster_detail(monster_info["slug"])
        if monster_detail:
            monsters_data.append(monster_detail)
        else:
            failed_count += 1

        # Be polite with requests
        time.sleep(0.3)

    print(f"\nScraped {len(monsters_data)} monsters successfully")
    if failed_count > 0:
        print(f"Failed to scrape {failed_count} monsters")

    # Save to JSON
    output_path = Path(__file__).parent.parent / "monsters_raw.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(monsters_data, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_path}")
