import re
from pathlib import Path

ABILITY_MAP = {
    "strength": "Ability.STRENGTH",
    "dexterity": "Ability.DEXTERITY",
    "constitution": "Ability.CONSTITUTION",
    "intelligence": "Ability.INTELLIGENCE",
    "wisdom": "Ability.WISDOM",
    "charisma": "Ability.CHARISMA",
}


def parse_prerequisites(text: str):
    level_match = re.search(r"Level\s+(\d+)\+", text)
    level = int(level_match.group(1)) if level_match else None

    abilities = []
    for name, enum in ABILITY_MAP.items():
        if re.search(rf"\b{name}\b", text, re.IGNORECASE):
            abilities.append(enum)

    return level, abilities


def indent(text: str, spaces: int = 8) -> str:
    pad = " " * spaces
    return "\n".join(pad + line if line else pad for line in text.splitlines())


def generate_feat_class(feat_name: str, feat_text: str) -> str:
    prereq_line = feat_text.splitlines()[0]
    level, abilities = parse_prerequisites(prereq_line)

    class_name = feat_name.replace(" ", "")
    ability_list = ", ".join(abilities)

    ability_param = ""
    ability_check = ""
    ability_assign = ""
    ability_modify = ""

    if abilities:
        ability_param = ", ability: Ability"
        ability_check = (
            f"        if ability not in [{ability_list}]:\n"
            f'            raise ValueError("{feat_name} ability increase must be '
            + " or ".join(a.split(".")[1].title() for a in abilities)
            + '.")\n'
        )
        ability_assign = "        self.ability = ability\n"
        ability_modify = (
            "    def modify(self, character_stat_block: CharacterStatBlock):\n"
            "        character_stat_block.abilities.add_bonus(self.ability, 1)\n\n"
        )

    description = indent(
        "text = (\n"
        + "\n".join(f'    "{line}\\n"' for line in feat_text.splitlines())
        + "\n)\n        return text"
    )

    return f"""class {class_name}(GeneralFeatTextFeature):

    def __init__(self, character_level: int{ability_param}):
        if character_level < {level}:
            raise ValueError("{feat_name} requires character level {level} or higher.")
{ability_check}{ability_assign}        super().__init__(
            name="{feat_name}",
            origin="General Feat Level {level}+",
        )

{ability_modify}    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
{description}
"""


def main():
    input_path = Path("sentinel.txt")
    output_path = Path("sentinel.py")
    feat_name = "Sentinel"

    feat_text = input_path.read_text(encoding="utf-8").strip()
    code = generate_feat_class(feat_name, feat_text)

    # ✅ WRITE TO FILE
    output_path.write_text(code, encoding="utf-8")

    print(f"Generated feat written to {output_path.resolve()}")


if __name__ == "__main__":
    main()
