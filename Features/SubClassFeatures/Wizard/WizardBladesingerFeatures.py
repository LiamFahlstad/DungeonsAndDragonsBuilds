from Definitions import Ability, Skill, WIZARD_HIT_DIE
from Features.Core.BaseFeatures import Feature
from Features.Core.SubFeatures import SkillProficiencyChoice
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class BladesongText(Feature):
    def __init__(self):
        super().__init__(name="Bladesong", origin="Bladesinger Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        int_mod = character_stat_block.get_ability_modifier(Ability.INTELLIGENCE)
        description = (
            "As a Bonus Action, you invoke an elven magic called the Bladesong, provided you aren't wearing armor or using a Shield.\n"
            "The Bladesong lasts for 1 minute and ends early if you have the Incapacitated condition, if you don armor or a Shield, or if you use two hands to make an attack with a weapon. You can dismiss the Bladesong at any time (no action required).\n"
            f"While the Bladesong is active, you gain the following benefits. You can invoke the Bladesong a number of times equal to your Intelligence modifier ({int_mod}, minimum of once), and you regain all expended uses when you finish a Long Rest. You regain one expended use when you use Arcane Recovery.\n"
            f"    * Agility: You gain a bonus to your AC equal to your Intelligence modifier ({int_mod}, minimum of +1), and your Speed increases by 10 feet. In addition, you have Advantage on Dexterity (Acrobatics) checks.\n"
            f"    * Bladework: Whenever you attack with a weapon with which you have proficiency, you can use your Intelligence modifier ({int_mod}) for the attack and damage rolls instead of using Strength or Dexterity.\n"
            f"    * Focus: When you make a Constitution saving throw to maintain Concentration, you can add your Intelligence modifier ({int_mod}) to the total."
        )
        return description


class TrainingInWarAndSong(Feature):
    VALID_SKILLS = [
        Skill.ACROBATICS,
        Skill.ATHLETICS,
        Skill.PERFORMANCE,
        Skill.PERSUASION,
    ]

    def __init__(self, skill: Skill):
        self._choice = SkillProficiencyChoice(
            [skill], self.VALID_SKILLS, count=1, error_prefix="Training in War and Song"
        )
        super().__init__(
            name="Training in War and Song", origin="Bladesinger Wizard Level 3"
        )

    def apply(self, character_stat_block: CharacterStatBlock):
        self._choice.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain proficiency with all Melee Martial weapons that don't have the Two-Handed or Heavy property. You can use a Melee weapon with which you have proficiency as a Spellcasting Focus for your Wizard spells.\n"
            f"You also gain proficiency in {self._choice.skills[0].value}."
        )
        return description


class ExtraAttack(Feature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="Bladesinger Wizard Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can attack twice, instead of once, whenever you take the Attack action on your turn. Moreover, you can cast one of your Wizard cantrips that has a casting time of an action in place of one of those attacks."
        return description


class SongOfDefense(Feature):
    def __init__(self):
        super().__init__(name="Song of Defense", origin="Bladesinger Wizard Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you take damage while your Bladesong is active, you can take a Reaction to expend one spell slot and reduce the damage taken by an amount equal to five times the spell slot's level."
        return description


class SongOfVictory(Feature):
    def __init__(self):
        super().__init__(name="Song of Victory", origin="Bladesinger Wizard Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "After you cast a spell that has a casting time of an action, you can make one attack with a weapon as a Bonus Action."
        return description
