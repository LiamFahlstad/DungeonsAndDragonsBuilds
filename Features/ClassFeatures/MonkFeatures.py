import Definitions
from Features.Core.BaseFeatures import Feature
from Features.Core.SubFeatures import MultiAbilityArmorClass
from Features.Equipment.Weapons import WeaponsDamageRolls
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils

MONK_HIT_DIE = 8

LEVEL_TO_MARTIAL_ARTS_DIE = {
    1: WeaponsDamageRolls.D6,
    2: WeaponsDamageRolls.D6,
    3: WeaponsDamageRolls.D6,
    4: WeaponsDamageRolls.D6,
    5: WeaponsDamageRolls.D8,
    6: WeaponsDamageRolls.D8,
    7: WeaponsDamageRolls.D8,
    8: WeaponsDamageRolls.D8,
    9: WeaponsDamageRolls.D8,
    10: WeaponsDamageRolls.D8,
    11: WeaponsDamageRolls.D10,
    12: WeaponsDamageRolls.D10,
    13: WeaponsDamageRolls.D10,
    14: WeaponsDamageRolls.D10,
    15: WeaponsDamageRolls.D10,
    16: WeaponsDamageRolls.D10,
    17: WeaponsDamageRolls.D12,
    18: WeaponsDamageRolls.D12,
    19: WeaponsDamageRolls.D12,
    20: WeaponsDamageRolls.D12,
}

LEVEL_TO_FOCUS_POINTS = {
    1: 0,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    6: 6,
    7: 7,
    8: 8,
    9: 9,
    10: 10,
    11: 11,
    12: 12,
    13: 13,
    14: 14,
    15: 15,
    16: 16,
    17: 17,
    18: 18,
    19: 19,
    20: 20,
}


class MartialArts(Feature):
    def __init__(self):
        super().__init__(name="Martial Arts", origin="Monk Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        monk_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.MONK
        )
        martial_arts_die = LEVEL_TO_MARTIAL_ARTS_DIE.get(
            monk_level, WeaponsDamageRolls.D6
        )
        description = (
            "Your practice of martial arts gives you mastery of combat styles that use your Unarmed Strike and Monk weapons, which are the following:\n"
            "    * Simple Melee weapons\n"
            "    * Martial Melee weapons that have the Light property\n"
            "You gain the following benefits while you are unarmed or wielding only Monk weapons and you aren't wearing armor or wielding a Shield.\n"
            "    * Bonus Unarmed Strike. You can make an Unarmed Strike as a Bonus Action.\n"
            f"    * Martial Arts Die. You can roll {martial_arts_die.value} in place of the normal damage of your Unarmed Strike or Monk weapons. This die changes as you gain Monk levels, as shown in the Martial Arts column of the Monk Features table.\n"
            "    * Dexterous Attacks. You can use your Dexterity modifier instead of your Strength modifier for the attack and damage rolls of your Unarmed Strikes and Monk weapons. In addition, when you use the Grapple or Shove option of your Unarmed Strike, you can use your Dexterity modifier instead of your Strength modifier to determine the save DC."
        )
        return description


class UnarmoredDefenseText(Feature):
    def __init__(self):
        super().__init__(name="Unarmored Defense", origin="Monk Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        dexterity_modifier = character_stat_block.get_ability_modifier(
            Definitions.Ability.DEXTERITY
        )
        wisdom_modifier = character_stat_block.get_ability_modifier(
            Definitions.Ability.WISDOM
        )
        armor_class = 10 + dexterity_modifier + wisdom_modifier
        description = f"While you aren't wearing armor or wielding a Shield, your base Armor Class equals 10 plus your Dexterity and Wisdom modifiers. (total {armor_class})."
        return description


class UnarmoredDefense(Feature):
    def __init__(self):
        self._ac = MultiAbilityArmorClass(10, [Definitions.Ability.DEXTERITY, Definitions.Ability.WISDOM])

    def apply(self, character_stat_block: CharacterStatBlock):
        self._ac.apply(character_stat_block)


class MonksFocus(Feature):
    def __init__(self):
        super().__init__(name="Monk's Focus", origin="Monk Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        wisdom_modifier = character_stat_block.get_ability_modifier(
            Definitions.Ability.WISDOM
        )
        dc = 8 + wisdom_modifier + character_stat_block.get_proficiency_bonus()
        monk_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.MONK
        )
        focus_points = LEVEL_TO_FOCUS_POINTS.get(monk_level, 0)
        description = (
            "Rules for Focus Points:\n"
            "    * Regaining: You regain all expended Focus Points when you finish a Short or Long Rest.\n"
            f"    * DC: {dc}\n"
            "Known features:\n"
        )
        return StringUtils.add_boxes(
            description, focus_points, regain_all_on="short or long rest"
        )


class FlurryOfBlows(Feature):
    def __init__(self):
        super().__init__(name="Flurry of Blows", origin="Monk Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        monk_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.MONK
        )
        if monk_level < 10:
            return "You can expend 1 Focus Point to make two Unarmed Strikes as a Bonus Action."
        if monk_level <= 20:
            return "You can expend 1 Focus Point to make three Unarmed Strikes as a Bonus Action."


class PatientDefense(Feature):
    def __init__(self):
        super().__init__(name="Patient Defense", origin="Monk Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        monk_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.MONK
        )
        if monk_level < 10:
            return "You can take the Disengage action as a Bonus Action. Alternatively, you can expend 1 Focus Point to take both the Disengage and the Dodge actions as a Bonus Action."
        if monk_level <= 20:
            return "You can take the Disengage action as a Bonus Action. Alternatively, you can expend 1 Focus Point to take both the Disengage and the Dodge actions as a Bonus Action. When you expend a Focus Point to use Patient Defense, you gain a number of Temporary Hit Points equal to two rolls of your Martial Arts die."


class StepOfTheWind(Feature):
    def __init__(self):
        super().__init__(name="Step of the Wind", origin="Monk Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        monk_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.MONK
        )
        if monk_level < 10:
            return "You can take the Dash action as a Bonus Action. Alternatively, you can expend 1 Focus Point to take both the Disengage and Dash actions as a Bonus Action, and your jump distance is doubled for the turn."
        if monk_level <= 20:
            return "You can take the Dash action as a Bonus Action. Alternatively, you can expend 1 Focus Point to take both the Disengage and Dash actions as a Bonus Action, and your jump distance is doubled for the turn. When you expend a Focus Point to use Step of the Wind, you can choose a willing creature within 5 feet of yourself that is Large or smaller. You move the creature with you until the end of your turn. The creature's movement doesn't provoke Opportunity Attacks."


class UnarmoredMovement(Feature):
    def __init__(self):
        super().__init__(name="Unarmored Movement", origin="Monk Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your speed increases by 10 feet while you aren't wearing armor or wielding a Shield. This bonus increases when you reach certain Monk levels, as shown on the Monk Features table."
        return description


class UncannyMetabolism(Feature):
    def __init__(self):
        super().__init__(name="Uncanny Metabolism", origin="Monk Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you roll Initiative, you can regain all expended Focus Points. When you do so, roll your Martial Arts die, and regain a number of Hit Points equal to your Monk level plus the number rolled.\n"
            "Once you use this feature, you can't use it again until you finish a Long Rest."
        )
        return description


class DeflectAttacks(Feature):
    def __init__(self):
        super().__init__(name="Deflect Attacks", origin="Monk Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        monk_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.MONK
        )
        if monk_level < 13:
            description = (
                "When an attack roll hits you and its damage includes Bludgeoning, Piercing, or Slashing damage, you can take a Reaction to reduce the attack's total damage against you. The reduction equals 1d10 plus your Dexterity modifier and Monk level.\n"
                "If you reduce the damage to 0, you can expend 1 Focus Point to redirect some of the attack's force. If you do so, choose a creature you can see within 5 feet of yourself if the attack was a melee attack or a creature you can see within 60 feet of yourself that isn't behind Total Cover if the attack was a ranged attack. That creature must succeed on a Dexterity saving throw or take damage equal to two rolls of your Martial Arts die plus your Dexterity modifier. The damage is the same type dealt by the attack."
            )
            return description
        else:
            description = (
                "When an attack roll hits you and its damage includes Bludgeoning, Piercing, or Slashing damage, you can take a Reaction to reduce the attack's total damage against you. The reduction equals 1d10 plus your Dexterity modifier and Monk level.\n"
                "If you reduce the damage to 0, you can expend 1 Focus Point to redirect some of the attack's force. If you do so, choose a creature you can see within 5 feet of yourself if the attack was a melee attack or a creature you can see within 60 feet of yourself that isn't behind Total Cover if the attack was a ranged attack. That creature must succeed on a Dexterity saving throw or take damage equal to two rolls of your Martial Arts die plus your Dexterity modifier. The damage is the same type dealt by the attack.\n"
                "You can now use your Deflect Attacks feature against attacks that deal any damage type, not just Bludgeoning, Piercing, or Slashing."
            )
            return description


class SlowFall(Feature):
    def __init__(self):
        super().__init__(name="Slow Fall", origin="Monk Level 4")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can take a Reaction when you fall to reduce any damage you take from the fall by an amount equal to five times your Monk level."
        return description


class ExtraAttack(Feature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="Monk Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can attack twice instead of once whenever you take the Attack action on your turn."
        return description


class StunningStrike(Feature):
    def __init__(self):
        super().__init__(name="Stunning Strike", origin="Monk Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Once per turn when you hit a creature with a Monk weapon or an Unarmed Strike, you can expend 1 Focus Point to attempt a stunning strike. The target must make a Constitution saving throw. On a failed save, the target has the Stunned condition until the start of your next turn. On a successful save, the target's Speed is halved until the start of your next turn, and the next attack roll made against the target before then has Advantage."
        return description


class EmpoweredStrikes(Feature):
    def __init__(self):
        super().__init__(name="Empowered Strikes", origin="Monk Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Whenever you deal damage with your Unarmed Strike, it can deal your choice of Force damage or its normal damage type."
        return description


class Evasion(Feature):
    def __init__(self):
        super().__init__(name="Evasion", origin="Monk Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you're subjected to an effect that allows you to make a Dexterity saving throw to take only half damage, you instead take no damage if you succeed on the saving throw and only half damage if you fail.\n"
            "You don't benefit from this feature if you have the Incapacitated condition."
        )
        return description


class AcrobaticMovement(Feature):
    def __init__(self):
        super().__init__(name="Acrobatic Movement", origin="Monk Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "While you aren't wearing armor or wielding a Shield, you gain the ability to move along vertical surfaces and across liquids on your turn without falling during the movement."
        return description


class HeightenedFocus(Feature):
    def __init__(self):
        super().__init__(name="Heightened Focus", origin="Monk Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your Flurry of Blows, Patient Defense, and Step of the Wind gain the following benefits.\n"
            "Flurry of Blows. You can expend 1 Focus Point to use Flurry of Blows and make three Unarmed Strikes with it instead of two.\n"
            "Patient Defense. When you expend a Focus Point to use Patient Defense, you gain a number of Temporary Hit Points equal to two rolls of your Martial Arts die.\n"
            "Step of the Wind. When you expend a Focus Point to use Step of the Wind, you can choose a willing creature within 5 feet of yourself that is Large or smaller. You move the creature with you until the end of your turn. The creature's movement doesn't provoke Opportunity Attacks."
        )
        return description


class SelfRestoration(Feature):
    def __init__(self):
        super().__init__(name="Self-Restoration", origin="Monk Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Through sheer force of will, you can remove one of the following conditions from yourself at the end of each of your turns: Charmed, Frightened, or Poisoned.\n"
            "In addition, forgoing food and drink doesn't give you levels of Exhaustion."
        )
        return description


class DeflectEnergy(Feature):
    def __init__(self):
        super().__init__(name="Deflect Energy", origin="Monk Level 13")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can now use your Deflect Attacks feature against attacks that deal any damage type, not just Bludgeoning, Piercing, or Slashing."
        return description


class DisciplinedSurvivorSavingThrows(Feature):
    def __init__(self):
        super().__init__(name="Disciplined Survivor", origin="Monk Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your physical and mental discipline grant you proficiency in all saving throws.\n"
        return description


class DisciplinedSurvivorMartialFocus(Feature):
    def __init__(self):
        super().__init__(name="Disciplined Survivor", origin="Monk Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Whenever you make a saving throw and fail, you can expend 1 Focus Point to reroll it, and you must use the new roll."
        return description


class PerfectFocus(Feature):
    def __init__(self):
        super().__init__(name="Perfect Focus", origin="Monk Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you roll Initiative and don't use Uncanny Metabolism, you regain expended Focus Points until you have 4 if you have 3 or fewer."
        return description


class SuperiorDefense(Feature):
    def __init__(self):
        super().__init__(name="Superior Defense", origin="Monk Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "At the start of your turn, you can expend 3 Focus Points to bolster yourself against harm for 1 minute or until you have the Incapacitated condition. During that time, you have Resistance to all damage except Force damage."
        return description


class BodyAndMind(Feature):
    def __init__(self):
        super().__init__(name="Body and Mind", origin="Monk Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have developed your body and mind to new heights. Your Dexterity and Wisdom scores increase by 4, to a maximum of 25."
        return description
