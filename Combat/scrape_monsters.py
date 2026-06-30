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
    # Try to find patterns like "Name +/-number"
    pattern = r"(\w+(?:\s+\w+)?)\s+([+-]\d+)"
    matches = re.findall(pattern, text)
    for name, modifier in matches:
        result[name.strip()] = int(modifier)
    return result


def parse_damage_list(text: str) -> list[str]:
    """Parse damage types or condition immunities (comma-separated)."""
    if not text:
        return []
    return [s.strip() for s in text.split(",")]


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
        "lair_actions": [],
        "mythic_actions": [],
    }

    # Find all h2 headers with class "rub" (section headers)
    headers = soup.find_all("h2", class_="rub")

    for header in headers:
        section_name = header.get_text(strip=True).lower()

        # Determine which section this is (check longer/more specific patterns first)
        section_key = None
        if "legendary action" in section_name:
            section_key = "legendary_actions"
        elif "bonus action" in section_name:
            section_key = "bonus_actions"
        elif "lair action" in section_name:
            section_key = "lair_actions"
        elif "mythic action" in section_name:
            section_key = "mythic_actions"
        elif "action" in section_name:
            section_key = "actions"
        elif "trait" in section_name:
            section_key = "traits"
        elif "reaction" in section_name:
            section_key = "reactions"

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
                    result[section_key].append({
                        "name": ability_name,
                        "description": ability_desc
                    })
                elif ability_name:
                    # Some abilities might only have a name
                    result[section_key].append({
                        "name": ability_name,
                        "description": ""
                    })

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
        "challenge": "",
        "traits": [],
        "actions": [],
        "bonus_actions": [],
        "reactions": [],
        "legendary_actions": [],
        "legendary_resistances": 0,
        "lair_actions": [],
        "mythic_actions": [],
    }

    # Extract name from h1
    heading = soup.find("h1")
    if heading:
        monster["name"] = heading.get_text(strip=True)

    # Get all text
    text = soup.get_text()

    # Extract type (e.g., "Medium Elemental, Neutral")
    type_div = soup.find("div", class_="type")
    if type_div:
        type_text = type_div.get_text(strip=True)
        monster["type"] = type_text

    # Parse the main stat block using regex on the concatenated text
    # AC pattern
    ac_match = re.search(r"AC\s+(\d+)(?:\s*\(([^)]*)\))?", text)
    if ac_match:
        monster["ac"] = int(ac_match.group(1))
        if ac_match.group(2):
            monster["ac_note"] = ac_match.group(2).strip()

    # HP pattern - looking for "HP 66 (12d8 + 12)"
    hp_match = re.search(r"HP\s+(\d+)\s*\(([^)]+)\)", text)
    if hp_match:
        monster["hp"] = int(hp_match.group(1))
        monster["hp_formula"] = hp_match.group(2).strip()

    # Speed pattern
    speed_match = re.search(r"Speed\s+([^A-Z][^\n]*?)(?=(?:[A-Z][a-z]+|STR|$))", text)
    if speed_match:
        monster["speed"] = speed_match.group(1).strip()

    # Ability scores pattern - look for the structure Str10Dex16 etc
    # The pattern is "StrXX+YY+ZZDexAA..." concatenated with possible newlines
    ability_match = re.search(
        r"Str(\d+)[\s\S]*?Dex(\d+)[\s\S]*?Con(\d+)[\s\S]*?Int(\d+)[\s\S]*?Wis(\d+)[\s\S]*?Cha(\d+)",
        text,
    )
    if ability_match:
        monster["ability_scores"] = {
            "Str": int(ability_match.group(1)),
            "Dex": int(ability_match.group(2)),
            "Con": int(ability_match.group(3)),
            "Int": int(ability_match.group(4)),
            "Wis": int(ability_match.group(5)),
            "Cha": int(ability_match.group(6)),
        }

    # Parse skills - look for "Skills" followed by content until next section
    skills_match = re.search(r"Skills\s+([^\n]*?)(?=\n(?:Senses|Damage|Languages|CR|Saving|$))", text, re.IGNORECASE | re.MULTILINE)
    if skills_match:
        monster["skills"] = parse_saves_or_skills(skills_match.group(1))

    # Parse saving throws
    saves_match = re.search(
        r"Saving Throws\s+([^A-Z][^\n]*?)(?=(?:Skills|Senses|Damage|Languages|CR|$))", text, re.IGNORECASE
    )
    if saves_match:
        monster["saving_throws"] = parse_saves_or_skills(saves_match.group(1))

    # Parse damage/condition resistances and immunities
    vuln_match = re.search(
        r"Damage Vulnerabilities\s+([^A-Z][^\n]*?)(?=(?:Damage|Senses|Languages|CR|$))", text, re.IGNORECASE
    )
    if vuln_match:
        monster["damage_vulnerabilities"] = parse_damage_list(vuln_match.group(1))

    resist_match = re.search(
        r"Damage Resistances\s+([^A-Z][^\n]*?)(?=(?:Damage|Senses|Languages|CR|$))", text, re.IGNORECASE
    )
    if resist_match:
        monster["damage_resistances"] = parse_damage_list(resist_match.group(1))

    immune_match = re.search(
        r"Damage Immunities\s+([^A-Z][^\n]*?)(?=(?:Damage|Senses|Languages|CR|$))", text, re.IGNORECASE
    )
    if immune_match:
        monster["damage_immunities"] = parse_damage_list(immune_match.group(1))

    cond_immune_match = re.search(
        r"Condition Immunities\s+([^A-Z][^\n]*?)(?=(?:Senses|Languages|Damage|CR|$))", text, re.IGNORECASE
    )
    if cond_immune_match:
        monster["condition_immunities"] = parse_damage_list(
            cond_immune_match.group(1)
        )

    # Parse senses
    senses_match = re.search(r"Senses\s+([^\n]+)", text, re.IGNORECASE)
    if senses_match:
        monster["senses"] = senses_match.group(1).strip()

    # Parse languages
    lang_match = re.search(r"Languages\s+([^\n]+)", text, re.IGNORECASE)
    if lang_match:
        monster["languages"] = lang_match.group(1).strip()

    # Parse CR/Challenge
    cr_match = re.search(r"CR\s+([\d/]+)", text)
    if cr_match:
        monster["cr"] = cr_match.group(1)

    challenge_match = re.search(r"Challenge\s+([^\n(]+)", text, re.IGNORECASE)
    if challenge_match:
        monster["challenge"] = challenge_match.group(1).strip()

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
    output_path = Path(__file__).parent / "monsters_raw.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(monsters_data, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_path}")
