import json
import re
from pathlib import Path

INPUT_JSON = "Spells/spells.json"
OUTPUT_PY = "generated_spells.py"


def spell_name_to_class(name: str) -> str:
    """
    Convert spell names into valid Python class names.

    Examples:
        Acid Splash -> AcidSplash
        Tasha's Caustic Brew -> TashasCausticBrew
        Melf's Acid Arrow -> MelfsAcidArrow
    """
    name = re.sub(r"[’']", "", name)
    name = re.sub(r"[^a-zA-Z0-9 ]", "", name)
    return "".join(word.capitalize() for word in name.split())


def format_multiline_string(text: str, width: int = 88) -> str:
    """
    Format long text into:
        (
            "sentence "
            "sentence "
        )
    """
    # lines = wrap(text, width)
    lines = [line.strip() + "." for line in text.strip().split(".")]
    lines = lines if len(lines) <= 1 else lines[:-1]

    if len(lines) == 1:
        return f'"{lines[0]}"'

    formatted = "(\n"
    for line in lines:
        formatted += f'                "{line}"\n'
    formatted += "            )"

    return formatted


def generate_spell_class(spell: dict) -> str:
    class_name = spell_name_to_class(spell["name"])

    description = format_multiline_string(spell["description"])

    return f"""
class {class_name}(ExplicitSpell):
    def __init__(self, spell_casting_ability: Optional[Ability] = None):
        super().__init__(
            name="{spell['name']}",
            level={spell['level']},
            school="{spell['school']}",
            classes={spell['classes']},
            casting_time="{spell['casting_time']}",
            range="{spell['range']}",
            components="{spell['components']}",
            duration="{spell['duration']}",
            description={description},
            source="{spell['source']}",
            spell_casting_ability=spell_casting_ability,
        )
""".lstrip()


def main():
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        spells = json.load(f)

    output = []

    output.append("from typing import Optional\n\n")
    output.append("from Definitions import Ability\n")
    output.append("from Spells.Definitions import ExplicitSpell\n\n")

    for spell_name in sorted(list(spells.keys())):
        spell_data = spells[spell_name]
        output.append(generate_spell_class(spell_data))
        output.append("\n")

    output.append("SpellSet = {\n")
    for spell_name in sorted(list(spells.keys())):
        class_name = spell_name_to_class(spell_name)
        output.append(f'    "{spell_name}": {class_name},\n')
    output.append("}\n")
    Path(OUTPUT_PY).write_text("".join(output), encoding="utf-8")

    print(f"Generated {len(spells)} spells → {OUTPUT_PY}")


if __name__ == "__main__":
    main()
