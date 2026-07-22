
from Definitions import Ability, RANGER_HIT_DIE, Skill
from Features.Core.BaseFeatures import Feature
from Features.Core.SubFeatures import SkillExpertiseChoice
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class SpellCasting(Feature):
    def __init__(self):
        super().__init__(name="Spell Casting", origin="Ranger Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Spellcasting:\n"
            "    * Whenever you finish a Long Rest, you can replace one spell on your list with another Ranger spell for which you have spell slots.\n"
            "    * You regain all expended slots when you finish a Long Rest.\n"
            "    * Wisdom is your spellcasting ability for your Ranger spells."
        )
        return description


class ReplacingWeaponMasteries(Feature):
    def __init__(self):
        super().__init__(name="Replacing Weapon Masteries", origin="Ranger Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Whenever you finish a Long Rest, you can change the kinds of weapons you chose."
        return description


class FavoredEnemy(Feature):
    def __init__(self):
        super().__init__(name="Favored Enemy", origin="Ranger Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        if character_stat_block.character_level < 5:
            free_hunters_mark_uses = 2
        elif character_stat_block.character_level < 9:
            free_hunters_mark_uses = 3
        elif character_stat_block.character_level < 13:
            free_hunters_mark_uses = 4
        elif character_stat_block.character_level < 17:
            free_hunters_mark_uses = 5
        else:
            free_hunters_mark_uses = 6

        description = (
            "You always have the Hunter's Mark spell prepared.\n"
            f"You can cast it {free_hunters_mark_uses} times without expending a spell slot, and you regain all expended uses of this ability when you finish a Long Rest.\n"
        )
        return StringUtils.add_boxes(
            description, free_hunters_mark_uses, regain_all_on="long rest"
        )


class DeftExplorerExpertise(Feature):
    def __init__(self, skill: Skill):
        super().__init__(name="Deft Explorer Expertise", origin="Deft Explorer Ranger Level 2")
        self.skill = skill
        self._choice = SkillExpertiseChoice(
            [skill], list(Skill), count=1, error_prefix="Deft Explorer Expertise"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return f"You gain Expertise with the {self.skill.value} skill."

    def apply(self, character_stat_block: CharacterStatBlock):
        self._choice.apply(character_stat_block)


class DeftExplorerLanguages(Feature):
    def __init__(self):
        super().__init__(name="Deft Explorer", origin="Ranger Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Languages.: You know two languages of your choice from the language tables in chapter 2."
        return description


class ExtraAttack(Feature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="Ranger Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can attack twice instead of once whenever you take the Attack action on your turn."
        return description


class Roving(Feature):
    def __init__(self):
        super().__init__(name="Roving", origin="Ranger Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your speed increases by 10 feet while you aren't wearing Heavy Armor. You also have a Climb speed and a Swim Speed equal to your Speed."
        return description


class Expertise(Feature):
    def __init__(self, skill_1: Skill, skill_2: Skill):
        super().__init__(name="Expertise", origin="Ranger Level 7")
        self.skill_1 = skill_1
        self.skill_2 = skill_2
        self._choice = SkillExpertiseChoice(
            [skill_1, skill_2], list(Skill), count=2, error_prefix="Ranger Expertise"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return f"You gain Expertise with the {self.skill_1.value} and {self.skill_2.value} skills."

    def apply(self, character_stat_block: CharacterStatBlock):
        self._choice.apply(character_stat_block)


class Tireless(Feature):
    def __init__(self):
        super().__init__(name="Tireless", origin="Ranger Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        wis_mod = character_stat_block.get_ability_modifier(Ability.WISDOM)
        uses = max(1, wis_mod)
        description = (
            "Primal forces now help fuel you on your journeys, granting you the following benefits.\n"
            f"    * Temporary Hit Points: As a Magic Action, you can give yourself a number of Temporary Hit Points equal to 1d8 plus your Wisdom modifier (minimum of 1) ({uses}).\n"
            f"   You can use this action a number of times equal to your Wisdom modifier (minimum of once) ({uses}), and you regain all expended uses when you finish a Long Rest.\n"
            "    * Decrease Exhaustion: Whenever you finish a Short Rest, your Exhaustion level, if any, decreases by 1."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class RelentlessHunter(Feature):
    def __init__(self):
        super().__init__(name="Relentless Hunter", origin="Ranger Level 13")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Taking damage can't break your Concentration on Hunter's Mark."
        return description


class NaturesVeil(Feature):
    def __init__(self):
        super().__init__(name="Nature's Veil", origin="Ranger Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        wis_mod = character_stat_block.get_ability_modifier(Ability.WISDOM)
        uses = max(1, wis_mod)
        description = (
            "You invoke spirits of nature to magically hide yourself. As a Bonus Action you can give yourself the Invisible condition until the end of your next turn.\n"
            f"You can use this feature a number of times equal to your Wisdom modifier (minimum of once) ({uses}), and you regain all expended uses when you finish a Long Rest."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class PreciseHunter(Feature):
    def __init__(self):
        super().__init__(name="Precise Hunter", origin="Ranger Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have Advantage on attack rolls against the creature currently marked by your Hunter's Mark."
        return description


class FeralSenses(Feature):
    def __init__(self):
        super().__init__(name="Feral Senses", origin="Ranger Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your connection to the forces of nature grants you Blindsight with a range of 30 feet."
        return description


class FoeSlayer(Feature):
    def __init__(self):
        super().__init__(name="Foe Slayer", origin="Ranger Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The damage die of your Hunter's Mark is a d10 rather than a d6."
        return description
