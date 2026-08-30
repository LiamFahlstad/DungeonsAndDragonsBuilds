from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureUses, FeatureActivation, ActionType, RegainedOn
from CharacterContent.Features.Core.Improvements import SkillExpertiseChoice, SpeedBonus
from Core.Definitions import Skill, MAX_ABILITY_MODIFIER
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class Spellcasting(Feature):
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

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Spell Replacement", "One spell each Long Rest"),
            ("Spell Slots", "Regain all on Long Rest"),
            ("Spellcasting Ability", "Wisdom"),
        ]

    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.LONG_REST


class ReplacingWeaponMasteries(Feature):
    def __init__(self):
        super().__init__(name="Replacing Weapon Masteries", origin="Ranger Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Whenever you finish a Long Rest, you can change the kinds of weapons you chose."
        return description


class FavoredEnemy(Feature):
    def __init__(self):
        super().__init__(
            name="Favored Enemy",
            origin="Ranger Level 1",
            uses=FeatureUses(
                max_uses=6,
                regain_all_on="long rest",
                current_formula="Current amount: determined by your character level — 2 uses at levels 1-4, 3 at 5-8, 4 at 9-12, 5 at 13-16, 6 at 17+.",
            ),
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You always have the Hunter's Mark spell prepared.\n"
            "You regain all expended uses of this ability when you finish a Long Rest.\n"
        )
        return description

    def get_resource_tiles(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, list[tuple[str, str]]]]:
        uses_by_level = {}
        for level in range(1, 21):
            if level < 5:
                uses_by_level[level] = 2
            elif level < 9:
                uses_by_level[level] = 3
            elif level < 13:
                uses_by_level[level] = 4
            elif level < 17:
                uses_by_level[level] = 5
            else:
                uses_by_level[level] = 6
        steps = [
            (f"Lv {level_range}", str(value))
            for level_range, value in StringUtils.compress_level_progression(
                uses_by_level
            )
        ]
        return [("Free Hunter's Mark Uses", steps)]

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        free_hunters_mark_uses = self.number_of_uses(character_stat_block)

        return [
            ("Spell", "Hunter's Mark (always prepared)"),
            ("Free Uses", f"{free_hunters_mark_uses}"),
            ("Regain", "Long Rest"),
        ]

    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def number_of_uses(self, character_stat_block: CharacterStatBlock) -> int:
        if character_stat_block.character_level < 5:
            return 2
        elif character_stat_block.character_level < 9:
            return 3
        elif character_stat_block.character_level < 13:
            return 4
        elif character_stat_block.character_level < 17:
            return 5
        else:
            return 6


class DeftExplorerExpertise(Feature):
    def __init__(self, skill: Skill):
        super().__init__(
            name="Deft Explorer Expertise",
            origin="Deft Explorer Ranger Level 2",
            skippable_in_concise=True,
        )
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
        super().__init__(
            name="Roving",
            origin="Ranger Level 6",
            skippable_in_concise=True,
            usage_tags=["buff", "utility"],
        )

    def apply(self, character_stat_block: CharacterStatBlock):
        SpeedBonus(10).apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your speed increases by 10 feet while you aren't wearing Heavy Armor. You also have a Climb speed and a Swim Speed equal to your Speed."
        return description


class Expertise(Feature):
    def __init__(self, skill_1: Skill, skill_2: Skill):
        super().__init__(
            name="Expertise", origin="Ranger Level 7", skippable_in_concise=True
        )
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
        super().__init__(
            name="Tireless",
            origin="Ranger Level 10",
            activation=FeatureActivation(action_type=ActionType.ACTION),
            usage_tags=["heal"],
            uses=FeatureUses(max_uses=MAX_ABILITY_MODIFIER, regain_all_on="long rest", current_formula="Current amount: equal to your Wisdom modifier."),
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Primal forces now help fuel you on your journeys, granting you the following benefits.\n"
            "    * Temporary Hit Points: As a Magic Action, you can give yourself a number of Temporary Hit Points equal to 1d8 plus your Wisdom modifier (minimum of 1).\n"
            "   You can use this action a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses when you finish a Long Rest.\n"
            "    * Decrease Exhaustion: Whenever you finish a Short Rest, your Exhaustion level, if any, decreases by 1."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        wis_mod = character_stat_block.get_wisdom_modifier()
        uses = max(1, wis_mod)
        return [
            ("Temporary Hit Points", f"1d8 + Wisdom modifier (Magic Action)"),
            ("THPs Uses", f"{uses}, regain on Long Rest"),
            ("Exhaustion Reduction", "Decrease by 1 on Short Rest"),
        ]

    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def number_of_uses(self, character_stat_block: CharacterStatBlock) -> int:
        return character_stat_block.get_wisdom_modifier()


class RelentlessHunter(Feature):
    def __init__(self):
        super().__init__(name="Relentless Hunter", origin="Ranger Level 13")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Taking damage can't break your Concentration on Hunter's Mark."
        return description


class NaturesVeil(Feature):
    def __init__(self):
        super().__init__(
            name="Nature's Veil",
            origin="Ranger Level 14",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION, duration="Until End of Your Next Turn"),
            usage_tags=["buff"],
            uses=FeatureUses(max_uses=MAX_ABILITY_MODIFIER, regain_all_on="long rest", current_formula="Current amount: equal to your Wisdom modifier."),
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You invoke spirits of nature to magically hide yourself. As a Bonus Action you can give yourself the Invisible condition until the end of your next turn.\n"
            "You can use this feature a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        wis_mod = character_stat_block.get_wisdom_modifier()
        uses = max(1, wis_mod)
        return [
            ("Action", "Bonus Action"),
            ("Effect", "Invisible condition"),
            ("Duration", "Until end of your next turn"),
            ("Uses", f"{uses}, regain on Long Rest"),
        ]

    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def number_of_uses(self, character_stat_block: CharacterStatBlock) -> int:
        return character_stat_block.get_wisdom_modifier()


class PreciseHunter(Feature):
    def __init__(self):
        super().__init__(
            name="Precise Hunter", origin="Ranger Level 17", usage_tags=["buff"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have Advantage on attack rolls against the creature currently marked by your Hunter's Mark."
        return description


class FeralSenses(Feature):
    def __init__(self):
        super().__init__(name="Feral Senses", origin="Ranger Level 18", activation=FeatureActivation(range="30 Feet"))

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your connection to the forces of nature grants you Blindsight with a range of 30 feet."
        return description


class FoeSlayer(Feature):
    def __init__(self):
        super().__init__(
            name="Foe Slayer", origin="Ranger Level 20", usage_tags=["damage"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The damage die of your Hunter's Mark is a d10 rather than a d6."
        return description
