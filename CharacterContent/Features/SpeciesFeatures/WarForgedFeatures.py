from Core.Definitions import CreatureSize, DamageType, Skill
from Model.Content.Feature import Feature
from Model.Content.Improvements import (
    ArmorClassBonus,
    DamageResistance,
    SkillProficiencyChoice,
)
from Model.Effects import Effects
from Model.View import CharacterView

SPEED = 30  # Given by your species
SIZE = CreatureSize.MEDIUM  # Given by your species


class ConstructResilience(Feature):
    def __init__(self):
        super().__init__(
            name="Construct Resilience",
            origin="Warforged Trait",
            skippable_in_concise=True,
            usage_tags=["buff"],
        )
        self._resistance = DamageResistance(DamageType.POISON, self.name)

    def apply(self, effects: Effects):
        self._resistance.apply(effects)

    def get_description(self, character: CharacterView) -> str:
        return "You have Resistance to Poison damage. You also have Advantage on saving throws to avoid or end the Poisoned condition."


class SentrysRest(Feature):
    def __init__(self):
        super().__init__(name="Sentry's Rest", origin="Warforged Trait")

    def get_description(self, character: CharacterView) -> str:
        return "You don’t need to sleep, and magic can’t put you to sleep. You can finish a Long Rest in 6 hours if you spend those hours in an inactive, motionless state. During this time, you appear inert but remain conscious."


class Tireless(Feature):
    def __init__(self):
        super().__init__(name="Tireless", origin="Warforged Trait", usage_tags=["buff"])

    def get_description(self, character: CharacterView) -> str:
        return "You don’t gain Exhaustion levels from dehydration, malnutrition, or suffocation."


class IntegratedProtection(Feature):
    def __init__(self):
        super().__init__(
            name="Integrated Protection",
            origin="Warforged Trait",
            skippable_in_concise=True,
            usage_tags=["buff"],
        )
        self._bonus = ArmorClassBonus(1)

    def apply(self, effects: Effects):
        self._bonus.apply(effects)

    def get_description(self, character: CharacterView) -> str:
        return "Your Armor Class increases by 1."


class SpecializedDesign(Feature):
    def __init__(self, skill: Skill):
        self.skill = skill
        super().__init__(
            name="Specialized Design",
            origin="Warforged Trait",
            skippable_in_concise=True,
        )
        self._choice = SkillProficiencyChoice(
            [skill], list(Skill), count=1, error_prefix="SpecializedDesign"
        )

    def apply(self, effects: Effects):
        self._choice.apply(effects)

    def get_description(self, character: CharacterView) -> str:
        return f"You gain proficiency in the {self.skill.value} skill."
