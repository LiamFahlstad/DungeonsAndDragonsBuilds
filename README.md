# DungeonsAndDragonsBuilds

A Python toolkit for building optimized D&D 5e characters and generating
printable HTML character sheets, plus a Qt-based combat simulator and
character-creator GUI.

## Requirements

- Python 3.10+

## Setup

```bash
git clone <this-repo>
cd DungeonsAndDragonsBuilds
pip install -r requirements.txt
```

## Generating character sheets

```bash
python RunCharacterCreator.py             # builds the characters listed in RunCharacterCreator.py
python RunCharacterCreator.py --example   # builds every example in Builds/Examples instead
```

Generated sheets are written as HTML files to `Output/`.

## Optional tools

These live in the same repo but need extra dependencies, since they aren't
required for the core build engine above.

| Tool | Run with | Extra install |
| --- | --- | --- |
| Character Creator GUI | `python Builds/CharacterCreatorUI.py` | included in `requirements.txt` (PyQt6) |
| Combat simulator | `python RunCombatSimulator.py` | included in `requirements.txt` (PyQt6) |
| Spell/subclass/monster scrapers (`Scrapers/`, `Combat/Tools/scrape_monsters.py`) | e.g. `python Scrapers/DnD2024SpellScraper.py` | `pip install beautifulsoup4 requests tqdm` |
| Monster stat analysis | `python Combat/Tools/analyze_monster_stats.py` | `pip install matplotlib numpy` |

## Project layout

- `Builds/` — character builders; `Builds/Characters` are the default builds run by `RunCharacterCreator.py`, `Builds/Examples` covers every class/subclass combo
- `CharacterConfigs/` — per-class/subclass feature definitions used by the builders
- `Spells/`, `Invocations/`, `Features/`, `ToolProficiencies/` — game data (spells, eldritch invocations, class/species features, tools)
- `Combat/` — turn-based combat simulator (Qt UI) and monster stat blocks
- `Scrapers/` — scripts that pull spell/subclass/monster data from external wikis into the JSON files under `Spells/` and `Combat/`
- `Output/` — generated character sheets (HTML)

## License

MIT — see [LICENSE](LICENSE).
