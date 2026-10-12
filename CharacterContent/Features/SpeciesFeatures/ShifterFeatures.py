from enum import Enum

from Core.Definitions import Skill, Sense
from Core.Rules import MAX_PROFICIENCY_BONUS, PROFICIENCY_BONUS_GAINED_AT
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from Model.Content.Improvements import SkillProficiencyChoice, GrantSense
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.View import CharacterView

SPEED = 30  # Given by your species


class ShiftForm(str, Enum):
    BESAST_HIDE = "Beast Hide"
    LONG_TOOTH = "Long Tooth"
    SWIFTSTRIDE = "Swiftstride"
    WILD_HUNT = "Wild Hunt"


class Darkvision(Feature):
    def __init__(self, distance: int):
        self.distance = distance
        super().__init__(name="Darkvision", origin="Shifter Trait")
        self._sense = GrantSense(Sense.DARKVISION, self.distance)

    def apply(self, ledger_writer: LedgerWriter):
        self._sense.apply(ledger_writer)

    def get_description(self, character: CharacterView) -> str:
        return f"You have Darkvision with a range of {self.distance} feet."


class Shifting(Feature):
    def __init__(self, shift_form: ShiftForm):
        self.shift_form = shift_form
        super().__init__(
            name="Shifting",
            origin="Shifter Trait",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, duration="1 Minute"
            ),
            usage_tags=["heal", "buff", "damage"],
            uses=FeatureUses(
                max_uses=MAX_PROFICIENCY_BONUS,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your proficiency bonus.",
                gained_at=PROFICIENCY_BONUS_GAINED_AT,
            ),
        )

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Bonus Action, you can shape-shift to assume a more bestial appearance. This transformation lasts for 1 minute or until you revert to your normal appearance as a Bonus Action. When you shift, you gain Temporary Hit Points equal to 2 times your Proficiency Bonus. You can shift a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest.\n"
            "Whenever you shift, you gain the benefit of one of the following options (choose when you select this species):"
        )

        if self.shift_form == ShiftForm.BESAST_HIDE:
            description += "\n- You gain 1d6 additional Temporary Hit Points. While shifted, you have a +1 bonus to your Armor Class."
        elif self.shift_form == ShiftForm.LONG_TOOTH:
            description += "\n- When you shift and as a Bonus Action on your other turns while shifted, you can use your elongated fangs to make an Unarmed Strike. If you hit with this Unarmed Strike and deal damage, you can deal Piercing damage equal to 1d6 plus your Strength modifier, instead of the normal damage of an Unarmed Strike."
        elif self.shift_form == ShiftForm.SWIFTSTRIDE:
            description += "\n- While you are shifted, your Speed increases by 10 feet. Additionally, you can move up to 10 feet as a Reaction when a creature ends its turn within 5 feet of you. This reactive movement doesn’t provoke Opportunity Attack action."
        elif self.shift_form == ShiftForm.WILD_HUNT:
            description += "\n- While shifted, you have Advantage on Wisdom checks. Additionally, no creature within 30 feet of you can have Advantage on an attack roll against you unless you have the Incapacitated condition."
        return description + "\n" + self._current_values(character)

    def _current_values(self, character: CharacterView) -> str:
        temp_hp = 2 * character.get_proficiency_bonus()
        line = f"Right now: {temp_hp} Temporary Hit Points when you shift"
        if self.shift_form == ShiftForm.BESAST_HIDE:
            line += " (plus 1d6)"
        if self.shift_form == ShiftForm.LONG_TOOTH:
            line += f"; fangs deal 1d6 + {character.get_strength_modifier()} Piercing damage"
        return line + "."

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class BestialInstincts(Feature):
    VALID_SKILLS = [
        Skill.ACROBATICS,
        Skill.ATHLETICS,
        Skill.INTIMIDATION,
        Skill.SURVIVAL,
    ]

    def __init__(self, skill: Skill):
        self.skill = skill
        super().__init__(name="Bestial Instincts", origin="Shifter Trait")
        self._choice = SkillProficiencyChoice(
            [skill], self.VALID_SKILLS, count=1, error_prefix="Bestial Instincts"
        )

    def apply(self, ledger_writer: LedgerWriter):
        self._choice.apply(ledger_writer)

    def get_description(self, character: CharacterView) -> str:
        return f"You gain proficiency in the {self.skill.value} skill."
