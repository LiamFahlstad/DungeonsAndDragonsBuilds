from Core.Definitions import CreatureSize, Skill, Sense
from Model.Content.Feature import Feature
from Model.Content.Improvements import SkillProficiencyChoice, GrantSense
from Model.Effects import Effects
from Model.View import CharacterView

SPEED = 30  # Given by your species
SIZE = CreatureSize.MEDIUM  # Given by your species


class Darkvision(Feature):
    def __init__(self, distance: int):
        self.distance = distance
        super().__init__(
            name="Darkvision", origin="Elf Trait", skippable_in_concise=True
        )
        self._sense = GrantSense(Sense.DARKVISION, self.distance, self.name)

    def apply(self, effects: Effects):
        self._sense.apply(effects)

    def get_description(self, character: CharacterView) -> str:
        return f"You have Darkvision with a range of {self.distance} feet."


class FeyAncestry(Feature):
    def __init__(self):
        super().__init__(name="Fey Ancestry", origin="Elf Trait", usage_tags=["buff"])

    def get_description(self, character: CharacterView) -> str:
        text = f"You have Advantage on saving throws you make to avoid or end the Charmed condition."
        return text


class KeenSenses(Feature):
    def __init__(self, skill: Skill):
        super().__init__(
            name="Keen Senses", origin="Elf Trait", skippable_in_concise=True
        )
        self._choice = SkillProficiencyChoice(
            [skill],
            [Skill.SURVIVAL, Skill.PERCEPTION, Skill.INSIGHT],
            count=1,
            error_prefix="KeenSenses",
        )

    def apply(self, effects: Effects):
        self._choice.apply(effects)

    def get_description(self, character: CharacterView) -> str:
        return f"You have proficiency in the {self._choice.skills[0].value} skill."


class Trance(Feature):
    def __init__(self):
        super().__init__(name="Trance", origin="Elf Trait")

    def get_description(self, character: CharacterView) -> str:
        text = "You don't need to sleep, and magic can't put you to sleep. You can finish a Long Rest in 4 hours if you spend those hours in a trancelike meditation, during which you retain consciousness."
        return text
