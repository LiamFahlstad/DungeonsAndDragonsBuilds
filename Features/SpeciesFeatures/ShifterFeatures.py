from enum import Enum

from Definitions import Skill
from Features.BaseFeatures import CharacterFeature, TextFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

SPEED = 30  # Given by your species


class ShiftForm(str, Enum):
    BESAST_HIDE = "Beast Hide"
    LONG_TOOTH = "Long Tooth"
    SWIFTSTRIDE = "Swiftstride"
    WILD_HUNT = "Wild Hunt"


class Darkvision(TextFeature):
    def __init__(self, distance: int):
        self.distance = distance
        super().__init__(name="Darkvision", origin="Shifter Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return f"You have Darkvision with a range of {self.distance} feet."


class Shifting(TextFeature):
    def __init__(self, shift_form: ShiftForm):
        self.shift_form = shift_form
        super().__init__(name="Shifting", origin="Shifter Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you can shape-shift to assume a more bestial appearance. This transformation lasts for 1 minute or until you revert to your normal appearance as a Bonus Action. When you shift, you gain Temporary Hit Points equal to 2 times your Proficiency Bonus. You can shift a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest."
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
        return description


class BestialInstincts(CharacterFeature):
    def __init__(self, skill: Skill):
        self.skill = skill

    def validate(self, character_stat_block: CharacterStatBlock):
        assert not character_stat_block.skills.is_proficient(self.skill)
        assert self.skill in [
            Skill.ACROBATICS,
            Skill.ATHLETICS,
            Skill.INTIMIDATION,
            Skill.SURVIVAL,
        ]

    def modify(self, character_stat_block: CharacterStatBlock):
        self.validate(character_stat_block)
        return character_stat_block.skills.add_skill_proficiency(self.skill)
