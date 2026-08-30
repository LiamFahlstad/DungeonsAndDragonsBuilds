from CharacterContent.Features.Core.BaseFeatures import (
    ActionType,
    Feature,
    FeatureActivation,
)
from CharacterContent.Features.Core.Improvements import (
    GrantLanguage,
    SavingThrowProficiencyChoice,
    SkillExpertiseChoice,
)
from Core.Definitions import Ability, Language, Skill
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class Expertise(Feature):
    def __init__(self, skill_1: Skill, skill_2: Skill):
        super().__init__(
            name="Expertise", origin="Rogue Level 1", skippable_in_concise=True
        )
        self._choice = SkillExpertiseChoice(
            [skill_1, skill_2], list(Skill), count=2, error_prefix="Rogue Expertise"
        )

    def apply(self, character_stat_block: CharacterStatBlock):
        self._choice.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        skill_names = " and ".join(skill.value for skill in self._choice.skills)
        description = f"You have Expertise in {skill_names}. When you make an ability check using one of these skills, you add double your Proficiency Bonus to the ability check instead of adding your Proficiency Bonus once."
        return description


class SneakAttack(Feature):
    def __init__(self):
        super().__init__(
            name="Sneak Attack", origin="Rogue Level 1", usage_tags=["damage"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You know how to strike subtly and exploit a foe's distraction. Once per turn you can deal an extra 1d6 damage to one creature you hit with an attack roll if you have Advantage on the roll and the attack uses a Finesse or a Ranged weapon. The extra damage's type is the same was the weapon's type.\n"
            "You don't need Advantage on the attack roll if at least one of your allies is within 5 feet of the target, the ally doesn't have the Incapacitated condition and you don't have Disadvantage on the attack roll.\n"
            "The extra damage increases as you gain Rogue levels, as shown in the Sneak Attack column of the Rogue Features table."
        )
        return description

    def get_resource_tiles(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, list[tuple[str, str]]]]:
        dice_by_level = {level: f"{(level + 1) // 2}d6" for level in range(1, 21)}
        steps = [
            (f"Lv {level_range}", value)
            for level_range, value in StringUtils.compress_level_progression(
                dice_by_level
            )
        ]
        return [("Sneak Attack Damage", steps)]

    def get_concise_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Once per turn, add 1d6 extra damage (same type as weapon) to an attack using a Finesse or Ranged weapon if you have Advantage on the roll. Alternatively, you don't need Advantage if an ally is within 5 feet of the target (ally not Incapacitated, and you don't have Disadvantage). Damage increases with Rogue levels."


class ThievesCant(Feature):
    def __init__(self):
        super().__init__(name="Thieves' Cant", origin="Rogue Level 1")
        # Only the fixed Thieves' Cant grant is wired; the "one other
        # language of your choice" half is a player choice not recorded
        # anywhere in this class.
        self._language = GrantLanguage(Language.THIEVES_CANT, self.name)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._language.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You picked up various languages in the communities where you plied your roguish talents. You know Thieves' Cant and one other language of your choice, which you choose from the language tables in Chapter 2."
        return description


class WeaponMastery(Feature):
    def __init__(self):
        super().__init__(name="Weapon Mastery", origin="Rogue Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your training with weapons allows you to use the mastery properties of two kinds of weapons of your choice with which you have proficiency, such as Daggers and Shortbows.\n"
            "Whenever you finish a Long Rest, you can change the kinds of weapons you chose. For example, you could switch to using the mastery properties of Scimitars and Shortswords."
        )
        return description


class CunningAction(Feature):
    def __init__(self):
        super().__init__(
            name="Cunning Action",
            origin="Rogue Level 2",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION),
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your quick thinking and agility allow you to move and act quickly. On your turn, you can take one of the following actions as a Bonus Action: Dash, Disengage, or Hide."
        return description


class SteadyAim(Feature):
    def __init__(self):
        super().__init__(
            name="Steady Aim",
            origin="Rogue Level 3",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION),
            usage_tags=["buff"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "As a Bonus Action, you give yourself Advantage on your next attack roll on your current turn. You can use this feature only if you haven't moved during this turn, and after you use it, your Speed is 0 until the end of the current turn."
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Action", "Bonus Action"),
            ("Effect", "Advantage on next attack roll this turn"),
            ("Prerequisite", "Haven't moved this turn"),
            ("After Using", "Speed becomes 0 until end of turn"),
        ]


class CunningStrike(Feature):
    def __init__(self):
        super().__init__(
            name="Cunning Strike", origin="Rogue Level 5", usage_tags=["control"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You've developed cunning ways to use your Sneak Attack. When you deal Sneak Attack damage, you can add one of the following Cunning Strike effects. Each effect has a die cost, which is the number of Sneak Attack dice you must forgo to add the effect. You remove the die before rolling, and the effect occurs immediately after the attack's damage is dealt. For example, if you add the Poison effect, remove 1d6 from the Sneak Attack's damage before rolling.\n"
            "If a Cunning Strike requires a saving throw, the DC equals 8 plus your Dexterity modifier and Proficiency Bonus.\n"
            "    * Poison (Cost: 1d6). You add a toxin to your strike, forcing the target to make a Constitution saving throw. On a failed save, the target has the Poisoned condition for 1 minute. At the end of each of its turns, the poisoned target repeats the save, ending the effect on a success.\n"
            "   To use this effect, you must have a Poisoner's Kit on your person.\n"
            "    * Trip (Cost: 1d6). If the target is Large or smaller, it must succeed on a Dexterity saving throw or have the Prone condition.\n"
            "    * Withdraw (Cost: 1d6). Immediately after the attack, you move up to half your speed without provoking Opportunity Attacks."
        )
        return description

    def calculate_dc(self, character_stat_block: CharacterStatBlock) -> int:
        return (
            8
            + character_stat_block.get_ability_modifier(Ability.DEXTERITY)
            + character_stat_block.get_proficiency_bonus()
        )

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        saving_throw = self.calculate_dc(character_stat_block)
        return [
            (
                "Poison (Cost: 1d6)",
                f"Target makes Constitution save (DC {saving_throw}) or gains Poisoned condition for 1 minute. Requires Poisoner's Kit.",
            ),
            (
                "Trip (Cost: 1d6)",
                f"Target Large or smaller makes Dexterity save (DC {saving_throw}) or gains Prone condition",
            ),
            (
                "Withdraw (Cost: 1d6)",
                "Move up to half your speed without provoking Opportunity Attacks",
            ),
        ]


class UncannyDodge(Feature):
    def __init__(self):
        super().__init__(
            name="Uncanny Dodge",
            origin="Rogue Level 5",
            activation=FeatureActivation(action_type=ActionType.REACTION),
            usage_tags=["buff"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When an attacker that you can see hits you with an attack roll, you can take a Reaction to halve the attack's damage against you (round down)."
        return description


class Evasion(Feature):
    def __init__(self):
        super().__init__(name="Evasion", origin="Rogue Level 7", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can nimbly dodge out of the way of certain dangers. When you're subjected to an effect that allows you to make a Dexterity saving throw to take only half damage, you instead take no damage if you succeed on the saving throw and only half damage if you fail. You can't use this feature if you have the Incapacitated condition."
        return description


class ReliableTalent(Feature):
    def __init__(self):
        super().__init__(name="Reliable Talent", origin="Rogue Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Whenever you make an ability check that uses one of your skill or tool proficiencies, you can treat a d20 roll of 9 or lower as a 10."
        return description


class ImprovedCunningStrike(Feature):
    def __init__(self):
        super().__init__(name="Improved Cunning Strike", origin="Rogue Level 11")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can use up to two Cunning Strike effects when you deal Sneak Attack damage, paying the die cost for each effect."
        return description


class DeviousStrikes(Feature):
    def __init__(self):
        super().__init__(
            name="Devious Strikes", origin="Rogue Level 14", usage_tags=["control"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You've practiced new ways to use your Sneak Attack deviously. The following effects are now among your Cunning Strike options.\n"
            "Daze (Cost: 2d6). The target must succeed on a Constitution saving throw, or on its next turn, it can do only one of the following: move or take an action or a Bonus Action.\n"
            "Knock Out (Cost: 6d6). The target must succeed on a Constitution saving throw, or it has the Unconscious condition for 1 minute or until it takes any damage. The Unconscious target repeats the save at the end of its turns, ending the effect on itself on a success.\n"
            "Obscure (Cost: 3d6). The target must succeed on a Dexterity saving throw, or it has the Blinded condition until the end of its next turn."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            (
                "Daze (Cost: 2d6)",
                "Target makes Constitution save or can only move, take an action, or take a Bonus Action on its next turn (not multiple)",
            ),
            (
                "Knock Out (Cost: 6d6)",
                "Target makes Constitution save or gains Unconscious condition for 1 minute or until taking damage (repeats save at end of turn)",
            ),
            (
                "Obscure (Cost: 3d6)",
                "Target makes Dexterity save or gains Blinded condition until end of its next turn",
            ),
        ]


class SlipperyMind(Feature):
    def __init__(self):
        super().__init__(
            name="Slippery Mind", origin="Rogue Level 15", skippable_in_concise=True
        )
        self._choice = SavingThrowProficiencyChoice(
            [Ability.WISDOM, Ability.CHARISMA],
            list(Ability),
            count=2,
            error_prefix="Slippery Mind",
        )

    def apply(self, character_stat_block: CharacterStatBlock):
        self._choice.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Your mind is exceptionally difficult to control. You gain proficiency in Wisdom and Charisma saving throws."


class Elusive(Feature):
    def __init__(self):
        super().__init__(name="Elusive", origin="Rogue Level 18", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You're so evasive that attackers rarely gain the upper hand against you. No attack roll can have advantage against you unless you have the Incapacitated condition."
        return description


class StrokeOfLuck(Feature):
    def __init__(self):
        super().__init__(name="Stroke of Luck", origin="Rogue Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have a marvelous knack for succeeding when you need to. If you fail a d20 Test, you can turn the roll into a 20.\n"
            "Once you use this feature, you can't use it again until you finish a Short or Long Rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Trigger", "You fail a d20 Test"),
            ("Effect", "Turn the roll into a 20"),
            ("Recharge", "Short or Long Rest"),
        ]
