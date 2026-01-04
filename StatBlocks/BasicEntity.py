import pathlib
from abc import abstractmethod
from enum import Enum
from typing import Optional, Sequence

import Definitions
from StatBlocks.StatBlock import StatBlock
from Utils import CharacterSheetUtils


class EntityType(str, Enum):
    HUMANOID = "Humanoid"
    ABERRATION = "Aberration"
    BEAST = "Beast"
    CELESTIAL = "Celestial"
    CONSTRUCT = "Construct"
    DRAGON = "Dragon"
    ELEMENTAL = "Elemental"
    FEY = "Fey"
    FIEND = "Fiend"
    GIANT = "Giant"
    MONSTROSITY = "Monstrosity"
    OOZE = "Ooze"
    PLANT = "Plant"
    UNDEAD = "Undead"


class TextFeature:
    """A feature that doesn't change that stats of the character."""

    def __init__(self, name: str):
        self.name = name
        self.additional_features = []
        super().__init__()

    def add_feature(self, feature: "TextFeature"):
        self.additional_features.append(feature)

    @abstractmethod
    def get_description(self) -> str:
        pass

    def add_feature_effects(self, text_feature: "TextFeature"):
        description = text_feature.get_description()
        indent = "    "
        indented = "\n".join(
            (indent + line) if line.strip() else "" for line in description.splitlines()
        )
        text = "\n"  # Separate the sections
        text += f"    {text_feature.name}:\n"  # Indent first line
        text += indented + "\n"
        return text

    def write_to_file(self, file):
        file.write(f"Name: {self.name}\n")
        description = self.get_description()
        for addition in self.additional_features:
            description += self.add_feature_effects(addition)
        if description[-1] != "\n":
            description += "\n"  # Ensure newline at end
        file.write(f"Description: {description}\n")


class Action(TextFeature):
    pass


class Trait(TextFeature):
    pass


class BasicEntity(StatBlock):
    def __init__(
        self,
        name,
        hit_points: int,
        armor_class: int,
        speed: int,
        size: Definitions.CreatureSize,
        ability_scores: dict[Definitions.Ability, int],
        saving_throw_proficiencies: Optional[Sequence[Definitions.Ability]] = None,
        proficiency_bonus: int = 0,
        fly_speed: int = 0,
        has_initiative: bool = True,
        challenge_rating: Optional[float] = None,
        traits: Optional[list[Trait]] = None,
        actions: Optional[list[Action]] = None,
    ):
        self.name = name
        self.hit_points = hit_points
        self.armor_class = armor_class
        self.speed = speed
        self.size = size
        self.ability_scores = ability_scores
        self.saving_throw_proficiencies = saving_throw_proficiencies or []
        self.proficiency_bonus = proficiency_bonus
        self.fly_speed = fly_speed
        self.has_initiative = has_initiative
        self.challenge_rating = challenge_rating
        self.traits = traits or []
        self.actions = actions or []

    def get_ability_score(self, ability: Definitions.Ability) -> int:
        return self.ability_scores.get(ability, 0)

    def get_ability_modifier(self, ability: Definitions.Ability) -> int:
        score = self.get_ability_score(ability)
        return (score - 10) // 2

    def get_saving_throw_modifier(self, ability: Definitions.Ability) -> int:
        if ability in self.saving_throw_proficiencies:
            saving_throw_bonus = self.proficiency_bonus
        else:
            saving_throw_bonus = 0
        return self.get_ability_modifier(ability) + saving_throw_bonus

    def add_trait(self, trait: Trait):
        self.traits.append(trait)

    def add_action(self, action: Action):
        self.actions.append(action)

    def slugify(self, name: str) -> str:
        # Lowercase and strip whitespace
        name = name.lower().strip()

        # Remove any non-alphanumeric characters except spaces and hyphens
        allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789_- "
        cleaned = "".join(ch for ch in name if ch in allowed_chars)

        # Replace spaces with hyphens
        return cleaned.replace(" ", "_").replace("-", "_")

    def _write_general_info(self, file):
        CharacterSheetUtils.write_separator(file, self.name)
        CharacterSheetUtils.write_table(
            headers=["Field", "Value"],
            rows=[
                ["Name", self.name],
                ["Proficiency Bonus", self.proficiency_bonus],
                [
                    "Challenge Rating",
                    (
                        self.challenge_rating
                        if self.challenge_rating is not None
                        else "N/A"
                    ),
                ],
            ],
            file=file,
        )
        file.write("\n")

    def _write_combat_stats(self, file):
        CharacterSheetUtils.write_separator(file, "Combat Stats")
        CharacterSheetUtils.write_table(
            headers=["Field", "Value"],
            rows=[
                ["Max Hit Points", self.hit_points],
                ["Armor Class", self.armor_class],
                ["Size", self.size.value],
                ["Speed (ft)", self.speed],
                ["Fly Speed (ft)", self.fly_speed if self.fly_speed > 0 else "N/A"],
                [
                    "Initiative Bonus",
                    (
                        f"d20{self.get_ability_modifier(Definitions.Ability.DEXTERITY):+}"
                        if self.has_initiative
                        else "N/A"
                    ),
                ],
            ],
            file=file,
        )
        file.write("\n")

    def _write_abilities(self, file):
        CharacterSheetUtils.write_separator(file, "Abilities")
        headers = []
        row = []
        for ability in [
            Definitions.Ability.STRENGTH,
            Definitions.Ability.DEXTERITY,
            Definitions.Ability.CONSTITUTION,
            Definitions.Ability.INTELLIGENCE,
            Definitions.Ability.WISDOM,
            Definitions.Ability.CHARISMA,
        ]:
            header_text = f"{ability.short_name} (Mod/Save)"
            headers.append(header_text)
            row_text = f"{self.get_ability_score(ability)} ({self.get_ability_modifier(ability):+}/{self.get_saving_throw_modifier(ability):+})"
            row.append(row_text)
        CharacterSheetUtils.write_table(
            headers=headers,
            rows=[row],
            file=file,
        )
        file.write("\n")

    def _write_traits(self, file):
        if not self.traits:
            return
        CharacterSheetUtils.write_separator(file, "Traits")
        for trait in self.traits:
            trait.write_to_file(file)

        file.write("\n")

    def _write_actions(self, file):
        if not self.actions:
            return
        CharacterSheetUtils.write_separator(file, "Actions")
        for action in self.actions:
            action.write_to_file(file)

        file.write("\n")

    def write_to_file(self, output_path: pathlib.Path | str, mode: str = "w"):
        with open(output_path, mode, encoding="utf-8") as file:
            if mode == "a":
                file.write("\n")  # Separate from previous content
            self._write_general_info(file)
            self._write_combat_stats(file)
            self._write_abilities(file)
            self._write_traits(file)
            self._write_actions(file)

    def create_character_sheet(self):
        output_path = f"Output/{self.slugify(self.name)}.txt"

        pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        self.write_to_file(output_path)
