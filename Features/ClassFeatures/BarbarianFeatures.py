import Definitions
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Definitions import Ability, DiceRollCondition, Skill
from Features.BaseFeatures import CharacterFeature, TextFeature


BARBARIAN_HIT_DIE = 12


class Rage(TextFeature):
    def __init__(self):
        super().__init__(name="Rage", origin="Barbarian Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        barbarian_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.BARBARIAN
        )
        if barbarian_level <= 4:
            rage_usages = 2
        elif barbarian_level <= 8:
            rage_usages = 3
        elif barbarian_level <= 12:
            rage_usages = 4
        elif barbarian_level <= 16:
            rage_usages = 5
        else:
            rage_usages = 6
        rage_damage_bonus = get_rage_damage_bonus(barbarian_level)
        description = (
            "You can imbue yourself with a primal power called Rage, a force that grants you extraordinary might and resilience.\n"
            " * Casting Time: Bonus Action\n"
            " * Condition: Not wearing Heavy armor\n"
            f" * Number of usages: You can enter your Rage {rage_usages} times.\n"
            " * Regaining: You regain one expended use when you finish a Short Rest, and you regain all expended uses when you finish a Long Rest.\n"
            " * While active, your Rage follows the rules below.\n"
            "    - Damage Resistance: You have Resistance to Bludgeoning, Piercing, and Slashing damage.\n"
            f"    - Rage Damage: When you make an attack using Strength—with either a weapon or an Unarmed Strike—and deal damage to the target, you gain +{rage_damage_bonus} bonus to the damage.\n"
            "    - Strength Advantage: You have Advantage on Strength checks and Strength saving throws.\n"
            "    - No Concentration or Spells: You can't maintain Concentration, and you can't cast spells.\n"
            "    - Duration: The Rage lasts until the end of your next turn, and it ends early if you don Heavy armor or have the Incapacitated condition. If your Rage is still active on your next turn, you can extend the Rage for another round by doing one of the following:\n"
            "       > Make an attack roll against an enemy.\n"
            "       > Force an enemy to make a saving throw.\n"
            "       > Take a Bonus Action to extend your Rage.\n"
            "Each time the Rage is extended, it lasts until the end of your next turn. You can maintain a Rage for up to 10 minutes."
        )
        return description


class UnarmoredDefenseText(TextFeature):
    def __init__(self):
        super().__init__(name="Unarmored Defense", origin="Barbarian Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        dexterity_modifier = character_stat_block.get_ability_modifier(
            Definitions.Ability.DEXTERITY
        )
        constitution_modifier = character_stat_block.get_ability_modifier(
            Definitions.Ability.CONSTITUTION
        )
        armor_class = 10 + dexterity_modifier + constitution_modifier
        description = f"While you aren't wearing any armor, your base Armor Class equals 10 plus your Dexterity and Constitution modifiers (total {armor_class}). You can use a Shield and still gain this benefit."
        return description


class UnarmoredDefense(CharacterFeature):
    def modify(self, character_stat_block: CharacterStatBlock):
        dexterity_modifier = character_stat_block.get_ability_modifier(
            Definitions.Ability.DEXTERITY
        )
        constitution_modifier = character_stat_block.get_ability_modifier(
            Definitions.Ability.CONSTITUTION
        )
        armor_class = 10 + dexterity_modifier + constitution_modifier
        character_stat_block.combat.update_armor_class(armor_class, pick_max=True)


class WeaponMastery(TextFeature):
    def __init__(self):
        super().__init__(name="Weapon Mastery", origin="Barbarian Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your training with weapons allows you to use the mastery properties of two kinds of Simple or Martial Melee weapons of your choice, such as Greataxes and Handaxes. Whenever you finish a Long Rest, you can practice weapon drills and change one of those weapon choices.\n"
            "When you reach certain Barbarian levels, you gain the ability to use the mastery properties of more kinds of weapons, as shown in the Weapon Mastery column of the Barbarian Features table."
        )
        return description


class DangerSenseText(TextFeature):
    def __init__(self):
        super().__init__(name="Danger Sense", origin="Barbarian Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain an uncanny sense of when things aren't as they should be, giving you an edge when you dodge perils. You have Advantage on Dexterity saving throws unless you have the Incapacitated condition."
        return description


class DangerSense(CharacterFeature):
    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.saving_throws.add_advantage(Ability.DEXTERITY)
        character_stat_block.saving_throws.add_advantage(Ability.STRENGTH)


class RecklessAttack(TextFeature):
    def __init__(self):
        super().__init__(name="Reckless Attack", origin="Barbarian Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can throw aside all concern for defense to attack with increased ferocity. When you make your first attack roll on your turn, you can decide to attack recklessly. Doing so gives you Advantage on attack rolls using Strength until the start of your next turn, but attack rolls against you have Advantage during that time."
        return description


class PrimalKnowledgeSkillProficiency(CharacterFeature):
    def __init__(self, skill: Skill):
        if skill not in [
            Skill.ANIMAL_HANDLING,
            Skill.ATHLETICS,
            Skill.INTIMIDATION,
            Skill.NATURE,
            Skill.PERCEPTION,
            Skill.SURVIVAL,
        ]:
            raise ValueError(f"Invalid skill for Primal Knowledge: {skill}")
        self.skill = skill

    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.skills.add_skill_proficiency(self.skill)


class PrimalKnowledge(TextFeature):
    def __init__(self):
        super().__init__(name="Primal Knowledge", origin="Barbarian Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "In addition, while your Rage is active, you can channel primal power when you attempt certain tasks; whenever you make an ability check using one of the following skills, you can make it as a Strength check even if it normally uses a different ability: Acrobatics, Intimidation, Perception, Stealth, or Survival. When you use this ability, your Strength represents primal power coursing through you, honing your agility, bearing, and senses."
        return description


class ExtraAttack(TextFeature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="Barbarian Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can attack twice instead of once whenever you take the Attack action on your turn."
        return description


class FastMovement(TextFeature):
    def __init__(self):
        super().__init__(name="Fast Movement", origin="Barbarian Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your speed increases by 10 feet while you aren't wearing Heavy armor."
        )
        return description


class FeralInstinct(TextFeature):
    def __init__(self):
        super().__init__(name="Feral Instinct", origin="Barbarian Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your instincts are so honed that you have Advantage on Initiative rolls."
        )
        return description


class InstinctivePounce(TextFeature):
    def __init__(self):
        super().__init__(name="Instinctive Pounce", origin="Barbarian Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "As part of the Bonus Action you take to enter your Rage, you can move up to half your Speed."
        return description


class BrutalStrike(TextFeature):
    def __init__(self):
        super().__init__(name="Brutal Strike", origin="Barbarian Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "If you use Reckless Attack, you can forgo any Advantage on one Strength-based attack roll of your choice on your turn. The chosen attack roll mustn't have Disadvantage. If the chosen attack roll hits, the target takes an extra 1d10 damage of the same type dealt by the weapon or Unarmed Strike, and you can cause one Brutal Strike effect of your choice.\n"
            "You have the following effect options.\n"
            "Forceful Blow. The target is pushed 15 feet straight away from you. You can then move up to half your Speed straight toward the target without provoking Opportunity Attacks.\n"
            "Hamstring Blow. The target’s Speed is reduced by 15 feet until the start of your next turn. A target can be affected by only one Hamstring Blow at a time— the most recent one."
        )
        return description


class RelentlessRage(TextFeature):
    def __init__(self):
        super().__init__(name="Relentless Rage", origin="Barbarian Level 11")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your Rage can keep you fighting despite grievous wounds. If you drop to 0 Hit Points while your Rage is active and don't die outright, you can make a DC 10 Constitution saving throw. If you succeed, your Hit Points instead change to a number equal to twice your Barbarian level.\n"
            "Each time you use this feature after the first, the DC increases by 5. When you finish a Short or Long Rest, the DC resets to 10."
        )
        return description


class ImprovedBrutalStrike1(TextFeature):
    def __init__(self):
        super().__init__(name="Improved Brutal Strike 1", origin="Barbarian Level 13")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have honed new ways to attack furiously. The following effects are now among your Brutal Strike options.\n"
            "Staggering Blow. The target has Disadvantage on the next saving throw it makes, and it can’t make Opportunity Attacks until the start of your next turn.\n"
            "Sundering Blow. Before the start of your next turn, the next attack roll made by another creature against the target gains a +5 bonus to the roll. An attack roll can gain only one Sundering Blow bonus."
        )
        return description


class PersistentRage(TextFeature):
    def __init__(self):
        super().__init__(name="Persistent Rage", origin="Barbarian Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you roll Initiative, you can regain all expended uses of Rage. After you regain uses of Rage in this way, you can’t do so again until you finish a Long Rest.\n"
            "In addition, your Rage is so fierce that it now lasts for 10 minutes without you needing to do anything to extend it from round to round. Your Rage ends early if you have the Unconscious condition (not just the Incapacitated condition) or don Heavy armor."
        )
        return description


class ImprovedBrutalStrike2(TextFeature):
    def __init__(self):
        super().__init__(name="Improved Brutal Strike 2", origin="Barbarian Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The extra damage of your Brutal Strike increases to 2d10. In addition, you can use two different Brutal Strike effects whenever you use your Brutal Strike feature."
        return description


class IndomitableMight(TextFeature):
    def __init__(self):
        super().__init__(name="Indomitable Might", origin="Barbarian Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "If your total for a Strength check or Strength saving throw is less than your Strength score, you can use that score in place of the total."
        return description


class PrimalChampion(TextFeature):
    def __init__(self):
        super().__init__(name="Primal Champion", origin="Barbarian Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You embody primal power. Your Strength and Constitution scores increase by 4, to a maximum of 25."
        return description


### Path of the Berserker Barbarian Features ###


class Frenzy(TextFeature):
    def __init__(self):
        super().__init__(
            name="Frenzy", origin="Path Of The Berserker Barbarian Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        rage_damage_bonus = get_rage_damage_bonus(
            character_stat_block.get_class_level(Definitions.CharacterClass.BARBARIAN)
        )
        description = f"If you use Reckless Attack while your Rage is active, you deal extra damage to the first target you hit on your turn with a Strength-based attack. To determine the extra damage, roll a number of d6s equal to your Rage Damage bonus ({rage_damage_bonus}), and add them together. The damage has the same type as the weapon or Unarmed Strike used for the attack."
        return description


class MindlessRage(TextFeature):
    def __init__(self):
        super().__init__(
            name="Mindless Rage", origin="Path Of The Berserker Barbarian Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have Immunity to the Charmed and Frightened conditions while your Rage is active. If you're Charmed or Frightened when you enter your Rage, the condition ends on you."
        return description


class Retaliation(TextFeature):
    def __init__(self):
        super().__init__(
            name="Retaliation", origin="Path Of The Berserker Barbarian Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you take damage from a creature that is within 5 feet of you, you can take a Reaction to make one melee attack against that creature, using a weapon or an Unarmed Strike."
        return description


class IntimidatingPresence(TextFeature):
    def __init__(self):
        super().__init__(
            name="Intimidating Presence",
            origin="Path Of The Berserker Barbarian Level 14",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you can strike terror into others with your menacing presence and primal power. When you do so, each creature of your choice in a 30-foot Emanation originating from you must make a Wisdom saving throw (DC 8 plus your Strength modifier and Proficiency Bonus). On a failed save, a creature has the Frightened condition for 1 minute. At the end of each of the Frightened creature's turns, the creature repeats the save, ending the effect on itself on a success.\n"
            "Once you use this feature, you can't use it again until you finish a Long Rest unless you expend a use of your Rage (no action required) to restore your use of it."
        )
        return description


### Path of the Wild Heart Barbarian Features ###


class AnimalSpeaker(TextFeature):
    def __init__(self):
        super().__init__(
            name="Animal Speaker", origin="Path Of The Wild Heart Barbarian Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can cast the Beast Sense and Speak with Animals spells but only as Rituals. Wisdom is your spellcasting ability for them."
        return description


class RageOfTheWilds(TextFeature):
    def __init__(self):
        super().__init__(
            name="Rage of the Wilds", origin="Path Of The Wild Heart Barbarian Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your Rage taps into the primal power of animals. Whenever you activate your Rage, you gain one of the following options of your choice.\n"
            "Bear. While your Rage is active, you have Resistance to every damage type except Force, Necrotic, Psychic, and Radiant.\n"
            "Eagle. When you activate your Rage, you can take the Disengage and Dash actions as part of that Bonus Action. While your Rage is active, you can take a Bonus Action to take both of those actions.\n"
            "Wolf. While your Rage is active, your allies have Advantage on attack rolls against any enemy of yours within 5 feet of you."
        )
        return description


class AspectOfTheWilds(TextFeature):
    def __init__(self):
        super().__init__(
            name="Aspect of the Wilds",
            origin="Path Of The Wild Heart Barbarian Level 6",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain one of the following options of your choice. Whenever you finish a Long Rest, you can change your choice.\n"
            "Owl. You have Darkvision with a range of 60 feet. If you already have Darkvision, its range increases by 60 feet.\n"
            "Panther. You have a Climb Speed equal to your Speed.\n"
            "Salmon. You have a Swim Speed equal to your Speed."
        )
        return description


class NatureSpeaker(TextFeature):
    def __init__(self):
        super().__init__(
            name="Nature Speaker", origin="Path Of The Wild Heart Barbarian Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can cast the Commune with Nature spell but only as a Ritual. Wisdom is your spellcasting ability for it."
        return description


class PowerOfTheWilds(TextFeature):
    def __init__(self):
        super().__init__(
            name="Power of the Wilds",
            origin="Path Of The Wild Heart Barbarian Level 14",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Whenever you activate your Rage, you gain one of the following options of your choice.\n"
            "Falcon. While your Rage is active, you have a Fly Speed equal to your Speed if you aren’t wearing any armor.\n"
            "Lion. While your Rage is active, any of your enemies within 5 feet of you have Disadvantage on attack rolls against targets other than you or another Barbarian who has this option active.\n"
            "Ram. While your Rage is active, you can cause a Large or smaller creature to have the Prone condition when you hit it with a melee attack."
        )
        return description


### Path of the World Tree Barbarian Features ###


class VitalityOfTheTree(TextFeature):
    def __init__(self):
        super().__init__(
            name="Vitality of the Tree",
            origin="Path Of The World Tree Barbarian Level 3",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your Rage taps into the life force of the World Tree. You gain the following benefits.\n"
            "Vitality Surge. When you activate your Rage, you gain a number of Temporary Hit Points equal to your Barbarian level.\n"
            "Life-Giving Force. At the start of each of your turns while your Rage is active, you can choose another creature within 10 feet of yourself to gain Temporary Hit Points. To determine the number of Temporary Hit Points, roll a number of d6s equal to your Rage Damage bonus, and add them together. If any of these Temporary Hit Points remain when your Rage ends, they vanish."
        )
        return description


class BranchesOfTheTree(TextFeature):
    def __init__(self):
        super().__init__(
            name="Branches of the Tree",
            origin="Path Of The World Tree Barbarian Level 6",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Whenever a creature you can see starts its turn within 30 feet of you while your Rage is active, you can take a Reaction to summon spectral branches of the World Tree around it. The target must succeed on a Strength saving throw (DC 8 plus your Strength modifier and Proficiency Bonus) or be teleported to an unoccupied space you can see within 5 feet of yourself or in the nearest unoccupied space you can see. After the target teleports, you can reduce its Speed to 0 until the end of the current turn."
        return description


class BatteringRoots(TextFeature):
    def __init__(self):
        super().__init__(
            name="Battering Roots", origin="Path Of The World Tree Barbarian Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "During your turn, your reach is 10 feet greater with any Melee weapon that has the Heavy or Versatile property, as tendrils of the World Tree extend from you. When you hit with such a weapon on your turn, you can activate the Push or Topple mastery property in addition to a different mastery property you're using with that weapon."
        return description


class TravelAlongTheTree(TextFeature):
    def __init__(self):
        super().__init__(
            name="Travel along the Tree",
            origin="Path Of The World Tree Barbarian Level 14",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you activate your Rage and as a Bonus Action while your Rage is active, you can teleport up to 60 feet to an unoccupied space you can see. In addition, once per Rage, you can increase the range of that teleport to 150 feet. When you do so, you can also bring up to six willing creatures who are within 10 feet of you. Each creature teleports to an unoccupied space of your choice within 10 feet of your destination space."
        return description


### Path of the Zealot Barbarian Features ###


class DivineFury(TextFeature):
    def __init__(self):
        super().__init__(
            name="Divine Fury", origin="Path Of The Zealot Barbarian Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can channel divine power into your strikes. On each of your turns while your Rage is active, the first creature you hit with a weapon or an Unarmed Strike takes extra damage equal to 1d6 plus half your Barbarian level (round down). The extra damage is Necrotic or Radiant; you choose the type each time you deal the damage."
        return description


class WarriorOfTheGods(TextFeature):
    def __init__(self):
        super().__init__(
            name="Warrior of the Gods", origin="Path Of The Zealot Barbarian Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "A divine entity helps ensure you can continue the fight. You have a pool of four d12s that you can spend to heal yourself. As a Bonus Action, you can expend dice from the pool, roll them, and regain a number of Hit Points equal to the roll’s total.\n"
            "Your pool regains all expended dice when you finish a Long Rest.\n"
            "The pool's maximum number of dice increases by one when you reach Barbarian levels 6 (5 dice), 12 (6 dice), and 17 (7 dice)."
        )
        return description


class FanaticalFocus(TextFeature):
    def __init__(self):
        super().__init__(
            name="Fanatical Focus", origin="Path Of The Zealot Barbarian Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Once per active Rage, if you fail a saving throw, you can reroll it with a bonus equal to your Rage Damage bonus, and you must use the new roll."
        return description


class ZealousPresence(TextFeature):
    def __init__(self):
        super().__init__(
            name="Zealous Presence", origin="Path Of The Zealot Barbarian Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you unleash a battle cry infused with divine energy. Up to ten other creatures of your choice within 60 feet of you gain Advantage on attack rolls and saving throws until the start of your next turn.\n"
            "Once you use this feature, you can’t use it again until you finish a Long Rest unless you expend a use of your Rage (no action required) to restore your use of it."
        )
        return description


class RageOfTheGods(TextFeature):
    def __init__(self):
        super().__init__(
            name="Rage of the Gods", origin="Path Of The Zealot Barbarian Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you activate your Rage, you can assume the form of a divine warrior. This form lasts for 1 minute or until you drop to 0 Hit Points. Once you use this feature, you can't do so again until you finish a Long Rest.\n"
            "While in this form, you gain the benefits below.\n"
            "Flight. You have a Fly Speed equal to your Speed and can hover.\n"
            "Resistance. You have Resistance to Necrotic, Psychic, and Radiant damage.\n"
            "Revivification. When a creature within 30 feet of you would drop to 0 Hit Points, you can take a Reaction to expend a use of your Rage to instead change the target’s Hit Points to a number equal to your Barbarian level."
        )
        return description


def get_rage_damage_bonus(barbarian_level: int) -> int:
    if barbarian_level <= 8:
        rage_damage_bonus = 2
    elif barbarian_level <= 15:
        rage_damage_bonus = 3
    else:
        rage_damage_bonus = 4
    return rage_damage_bonus
