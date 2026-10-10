from Core.Definitions import CreatureSize, Skill
from Model.Content.Feature import Feature
from Model.Content.Improvements import SkillProficiencyChoice
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.View import CharacterView

SPEED = 30  # Given by your species
SIZE = CreatureSize.MEDIUM  # Given by your species


class Resourceful(Feature):
    def __init__(self):
        super().__init__(name="Resourceful", origin="Human Trait")

    def get_description(self, character: CharacterView) -> str:
        return "You gain Heroic Inspiration whenever you finish a Long Rest.\n"


class Skillful(Feature):
    def __init__(self, skill: Skill):
        self.skill = skill
        super().__init__(
            name="Skillful", origin="Human Trait", skippable_in_concise=True
        )
        self._choice = SkillProficiencyChoice(
            [skill], list(Skill), count=1, error_prefix="Skillful"
        )

    def apply(self, ledger_writer: LedgerWriter):
        self._choice.apply(ledger_writer)

    def get_description(self, character: CharacterView) -> str:
        return f"You gain proficiency in the {self.skill.value} skill."


class Versatile(Feature):
    def __init__(self):
        super().__init__(name="Versatile", origin="Human Trait")

    def get_description(self, character: CharacterView) -> str:
        return "You gain an Origin feat of your choice (see 'Feats'). Skilled is recommended.\n"
