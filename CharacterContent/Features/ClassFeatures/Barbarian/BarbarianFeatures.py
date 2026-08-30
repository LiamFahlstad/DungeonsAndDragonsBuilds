import Core.Definitions as Definitions
from CharacterContent.Features.Core.BaseFeatures import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
    RegainedOn,
)
from CharacterContent.Features.Core.Improvements import (
    AbilityScoreBonus,
    InitiativeRollCondition,
    MultiAbilityArmorClass,
    SavingThrowAdvantage,
    SkillProficiencyChoice,
    SpeedBonus,
)
from Core.Definitions import Ability, Skill
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class Rage(Feature):
    def __init__(self):
        super().__init__(
            name="Rage",
            origin="Barbarian Level 1",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION, duration="Until End of Your Next Turn"),
            usage_tags=["buff"],
            uses=FeatureUses(
                max_uses=6,
                regain_x_on=(1, "short rest"),
                regain_all_on="long rest",
                current_formula="Current amount: determined by your Barbarian level — 2 uses at levels 1-2, 3 at 3-5, 4 at 6-11, 5 at 12-16, 6 at 17-20.",
            ),
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can imbue yourself with a primal power called Rage, a force that grants you extraordinary might and resilience.\n"
            "    * Casting Time: Bonus Action\n"
            "    * Condition: Not wearing Heavy armor\n"
            "    * Number of usages: You can enter your Rage.\n"
            "    * Regaining: You regain one expended use when you finish a Short Rest, and you regain all expended uses when you finish a Long Rest.\n"
            "    * While active, your Rage follows the rules below.\n"
            "        - Damage Resistance: You have Resistance to Bludgeoning, Piercing, and Slashing damage.\n"
            "        - Rage Damage: When you make an attack using Strength—with either a weapon or an Unarmed Strike—and deal damage to the target, you gain a bonus to the damage, as shown in the Rage Damage column of the Barbarian Features table.\n"
            "        - Strength Advantage: You have Advantage on Strength checks and Strength saving throws.\n"
            "        - No Concentration or Spells: You can't maintain Concentration, and you can't cast spells.\n"
            "        - Duration: The Rage lasts until the end of your next turn, and it ends early if you don Heavy armor or have the Incapacitated condition. If your Rage is still active on your next turn, you can extend the Rage for another round by doing one of the following:\n"
            "            > Make an attack roll against an enemy.\n"
            "            > Force an enemy to make a saving throw.\n"
            "            > Take a Bonus Action to extend your Rage.\n"
            "Each time the Rage is extended, it lasts until the end of your next turn. You can maintain a Rage for up to 10 minutes."
        )
        return description

    def get_resource_tiles(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, list[tuple[str, str]]]]:
        rage_uses_by_level = {}
        rage_damage_by_level = {}
        for level in range(1, 21):
            if level <= 2:
                rage_uses_by_level[level] = 2
            elif level <= 5:
                rage_uses_by_level[level] = 3
            elif level <= 11:
                rage_uses_by_level[level] = 4
            elif level <= 16:
                rage_uses_by_level[level] = 5
            else:
                rage_uses_by_level[level] = 6
            rage_damage_by_level[level] = f"+{get_rage_damage_bonus(level)}"

        uses_steps = [
            (f"Lv {level_range}", str(value))
            for level_range, value in StringUtils.compress_level_progression(
                rage_uses_by_level
            )
        ]
        damage_steps = [
            (f"Lv {level_range}", value)
            for level_range, value in StringUtils.compress_level_progression(
                rage_damage_by_level
            )
        ]
        return [
            ("Rage Uses", uses_steps),
            ("Rage Damage", damage_steps),
        ]

    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.SHORT_OR_LONG_REST

    def number_of_uses(self, character_stat_block: CharacterStatBlock) -> int:
        barbarian_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.BARBARIAN
        )
        if barbarian_level >= 17:
            return 6
        elif barbarian_level >= 12:
            return 5
        elif barbarian_level >= 6:
            return 4
        elif barbarian_level >= 3:
            return 3
        else:
            return 2

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class UnarmoredDefenseText(Feature):
    def __init__(self):
        super().__init__(
            name="Unarmored Defense", origin="Barbarian Level 1", usage_tags=["buff"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "While you aren't wearing any armor, your base Armor Class equals 10 plus your Dexterity and Constitution modifiers. You can use a Shield and still gain this benefit."
        return description


class UnarmoredDefense(Feature):
    def __init__(self):
        super().__init__(
            name="Unarmored Defense",
            origin="Barbarian Level 1",
            skippable_in_concise=True,
        )
        self._ac = MultiAbilityArmorClass(10, [Ability.DEXTERITY, Ability.CONSTITUTION])

    def apply(self, character_stat_block: CharacterStatBlock):
        self._ac.apply(character_stat_block)


class WeaponMastery(Feature):
    def __init__(self):
        super().__init__(name="Weapon Mastery", origin="Barbarian Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your training with weapons allows you to use the mastery properties of two kinds of Simple or Martial Melee weapons of your choice, such as Greataxes and Handaxes. Whenever you finish a Long Rest, you can practice weapon drills and change one of those weapon choices.\n"
            "When you reach certain Barbarian levels, you gain the ability to use the mastery properties of more kinds of weapons, as shown in the Weapon Mastery column of the Barbarian Features table."
        )
        return description

    def get_concise_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "You master 2 kinds of Simple or Martial Melee weapons of your choice and can "
            "change one choice on long rest. At higher Barbarian levels, you gain the ability "
            "to use the mastery properties of additional weapon kinds."
        )


class DangerSenseText(Feature):
    def __init__(self):
        super().__init__(name="Danger Sense", origin="Barbarian Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain an uncanny sense of when things aren't as they should be, giving you an edge when you dodge perils. You have Advantage on Dexterity saving throws unless you have the Incapacitated condition."
        return description


class DangerSense(Feature):
    def __init__(self):
        super().__init__(skippable_in_concise=True, usage_tags=["buff"])
        self._advantage = SavingThrowAdvantage([Ability.DEXTERITY])

    def apply(self, character_stat_block: CharacterStatBlock):
        self._advantage.apply(character_stat_block)


class RecklessAttack(Feature):
    def __init__(self):
        super().__init__(
            name="Reckless Attack",
            origin="Barbarian Level 2",
            activation=FeatureActivation(duration="Until Start of Your Next Turn"),
            usage_tags=["buff"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can throw aside all concern for defense to attack with increased ferocity. When you make your first attack roll on your turn, you can decide to attack recklessly. Doing so gives you Advantage on attack rolls using Strength until the start of your next turn, but attack rolls against you have Advantage during that time."
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Trigger", "First attack roll of your turn"),
            ("Benefit", "Advantage on attack rolls using Strength"),
            ("Cost", "Attack rolls against you have Advantage"),
            ("Duration", "Until start of your next turn"),
        ]

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class PrimalKnowledgeSkillProficiency(Feature):
    SKILL_POOL = [
        Skill.ANIMAL_HANDLING,
        Skill.ATHLETICS,
        Skill.INTIMIDATION,
        Skill.NATURE,
        Skill.PERCEPTION,
        Skill.SURVIVAL,
    ]

    def __init__(self, skill: Skill):
        super().__init__(
            name="Primal Knowledge",
            origin="Barbarian Level 3",
            skippable_in_concise=True,
        )
        self._proficiency = SkillProficiencyChoice(
            [skill],
            self.SKILL_POOL,
            count=1,
            error_prefix="Invalid skill for Primal Knowledge",
        )

    def apply(self, character_stat_block: CharacterStatBlock):
        for skill in self.SKILL_POOL:
            character_stat_block.skills.update_skill_to_ability(skill, Ability.STRENGTH)
        self._proficiency.apply(character_stat_block)


class PrimalKnowledge(Feature):
    def __init__(self):
        super().__init__(name="Primal Knowledge", origin="Barbarian Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "In addition, while your Rage is active, you can channel primal power when you attempt certain tasks; whenever you make an ability check using one of the following skills, you can make it as a Strength check even if it normally uses a different ability: Acrobatics, Intimidation, Perception, Stealth, or Survival. When you use this ability, your Strength represents primal power coursing through you, honing your agility, bearing, and senses."
        return description


class ExtraAttack(Feature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="Barbarian Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can attack twice instead of once whenever you take the Attack action on your turn."
        return description


class FastMovement(Feature):
    def __init__(self):
        super().__init__(
            name="Fast Movement", origin="Barbarian Level 5", usage_tags=["buff"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your speed increases by 10 feet while you aren't wearing Heavy armor."
        )
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class FastMovementBonus(Feature):
    """Mechanical half of Fast Movement, kept separate from the descriptive
    FastMovement feature since extend_feature()'d features never get apply()
    called on them - this one must be add_feature()'d directly."""

    def __init__(self):
        super().__init__(skippable_in_concise=True, usage_tags=["buff"])

    def apply(self, character_stat_block: CharacterStatBlock):
        SpeedBonus(10).apply(character_stat_block)


class FeralInstinct(Feature):
    def __init__(self):
        super().__init__(
            name="Feral Instinct",
            origin="Barbarian Level 7",
            skippable_in_concise=True,
            usage_tags=["buff"],
        )

    def apply(self, character_stat_block: CharacterStatBlock):
        InitiativeRollCondition(Definitions.DiceRollCondition.ADVANTAGE).apply(
            character_stat_block
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your instincts are so honed that you have Advantage on Initiative rolls."
        )
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class InstinctivePounce(Feature):
    def __init__(self):
        super().__init__(
            name="Instinctive Pounce", origin="Barbarian Level 7", usage_tags=["buff"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "As part of the Bonus Action you take to enter your Rage, you can move up to half your Speed."
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class BrutalStrike(Feature):
    def __init__(self):
        super().__init__(
            name="Brutal Strike",
            origin="Barbarian Level 9",
            usage_tags=["damage", "control"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "If you use Reckless Attack, you can forgo any Advantage on one Strength-based attack roll of your choice on your turn. The chosen attack roll mustn't have Disadvantage. If the chosen attack roll hits, the target takes an extra 1d10 damage of the same type dealt by the weapon or Unarmed Strike, and you can cause one Brutal Strike effect of your choice.\n"
            "You have the following effect options.\n"
            "    * Forceful Blow. The target is pushed 15 feet straight away from you. You can then move up to half your Speed straight toward the target without provoking Opportunity Attacks.\n"
            "    * Hamstring Blow. The target’s Speed is reduced by 15 feet until the start of your next turn. A target can be affected by only one Hamstring Blow at a time— the most recent one."
        )
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class RelentlessRage(Feature):
    def __init__(self):
        super().__init__(
            name="Relentless Rage", origin="Barbarian Level 11", usage_tags=["heal"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your Rage can keep you fighting despite grievous wounds. If you drop to 0 Hit Points while your Rage is active and don't die outright, you can make a DC 10 Constitution saving throw. If you succeed, your Hit Points instead change to a number equal to twice your Barbarian level.\n"
            "Each time you use this feature after the first, the DC increases by 5. When you finish a Short or Long Rest, the DC resets to 10."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        barbarian_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.BARBARIAN
        )
        return [
            ("Trigger", "Drop to 0 Hit Points during Rage"),
            ("Save", "DC 10 Constitution saving throw"),
            (
                "Effect on Success",
                f"Regain Hit Points equal to 2 × your Barbarian level ({2 * barbarian_level} HP)",
            ),
            ("Scaling", "DC increases by 5 each use; resets on Short or Long Rest"),
        ]

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class ImprovedBrutalStrikeLevel13(Feature):
    def __init__(self):
        super().__init__(
            name="Improved Brutal Strike 1",
            origin="Barbarian Level 13",
            usage_tags=["control"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have honed new ways to attack furiously. The following effects are now among your Brutal Strike options.\n"
            "Staggering Blow. The target has Disadvantage on the next saving throw it makes, and it can’t make Opportunity Attacks until the start of your next turn.\n"
            "Sundering Blow. Before the start of your next turn, the next attack roll made by another creature against the target gains a +5 bonus to the roll. An attack roll can gain only one Sundering Blow bonus."
        )
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class PersistentRage(Feature):
    def __init__(self):
        super().__init__(name="Persistent Rage", origin="Barbarian Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you roll Initiative, you can regain all expended uses of Rage. After you regain uses of Rage in this way, you can’t do so again until you finish a Long Rest.\n"
            "In addition, your Rage is so fierce that it now lasts for 10 minutes without you needing to do anything to extend it from round to round. Your Rage ends early if you have the Unconscious condition (not just the Incapacitated condition) or don Heavy armor."
        )
        return description

    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.INITIATIVE_ROLL

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class ImprovedBrutalStrikeLevel17(Feature):
    def __init__(self):
        super().__init__(
            name="Improved Brutal Strike 2",
            origin="Barbarian Level 17",
            usage_tags=["damage"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The extra damage of your Brutal Strike increases to 2d10. In addition, you can use two different Brutal Strike effects whenever you use your Brutal Strike feature."
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class IndomitableMight(Feature):
    def __init__(self):
        super().__init__(
            name="Indomitable Might", origin="Barbarian Level 18", usage_tags=["buff"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "If your total for a Strength check or Strength saving throw is less than your Strength score, you can use that score in place of the total."
        return description


class PrimalChampion(Feature):
    def __init__(self):
        super().__init__(
            name="Primal Champion",
            origin="Barbarian Level 20",
            skippable_in_concise=True,
            usage_tags=["buff"],
        )
        self._bonuses = AbilityScoreBonus(
            [
                (Ability.STRENGTH, 4),
                (Ability.CONSTITUTION, 4),
            ],
            total=8,
        )

    def apply(self, character_stat_block: CharacterStatBlock):
        self._bonuses.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You embody primal power. Your Strength and Constitution scores increase by 4, to a maximum of 25."
        return description


def get_rage_damage_bonus(barbarian_level: int) -> int:
    if barbarian_level <= 8:
        return 2
    if barbarian_level <= 15:
        return 3
    return 4
