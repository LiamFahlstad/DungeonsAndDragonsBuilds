import Definitions
from Features.BaseFeatures import CharacterFeature, TextFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

BARBARIAN_HIT_DIE = 8

LEVEL_TO_MARTIAL_ARTS_DIE = {
    1: "1d6",
    2: "1d6",
    3: "1d6",
    4: "1d6",
    5: "1d8",
    6: "1d8",
    7: "1d8",
    8: "1d8",
    9: "1d8",
    10: "1d8",
    11: "1d10",
    12: "1d10",
    13: "1d10",
    14: "1d10",
    15: "1d10",
    16: "1d10",
    17: "1d12",
    18: "1d12",
    19: "1d12",
    20: "1d12",
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


class MartialArts(TextFeature):
    def __init__(self):
        super().__init__(name="Martial Arts", origin="Monk Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        monk_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.MONK
        )
        martial_arts_die = LEVEL_TO_MARTIAL_ARTS_DIE.get(monk_level, "1d6")
        description = (
            "Your practice of martial arts gives you mastery of combat styles that use your Unarmed Strike and Monk weapons, which are the following:\n"
            " * Simple Melee weapons\n"
            " * Martial Melee weapons that have the Light property\n"
            "You gain the following benefits while you are unarmed or wielding only Monk weapons and you aren't wearing armor or wielding a Shield.\n"
            " * Bonus Unarmed Strike. You can make an Unarmed Strike as a Bonus Action.\n"
            f" * Martial Arts Die. You can roll {martial_arts_die} in place of the normal damage of your Unarmed Strike or Monk weapons. This die changes as you gain Monk levels, as shown in the Martial Arts column of the Monk Features table.\n"
            " * Dexterous Attacks. You can use your Dexterity modifier instead of your Strength modifier for the attack and damage rolls of your Unarmed Strikes and Monk weapons. In addition, when you use the Grapple or Shove option of your Unarmed Strike, you can use your Dexterity modifier instead of your Strength modifier to determine the save DC."
        )
        return description


class UnarmoredDefenseText(TextFeature):
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


class UnarmoredDefense(CharacterFeature):
    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.update_armor_class_base(10)
        character_stat_block.combat.add_armor_class_ability(
            Definitions.Ability.DEXTERITY
        )
        character_stat_block.combat.add_armor_class_ability(Definitions.Ability.WISDOM)


class MonksFocus(TextFeature):
    def __init__(self):
        super().__init__(name="Monk's Focus", origin="Monk Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        wisdom_modifier = character_stat_block.get_ability_modifier(
            Definitions.Ability.WISDOM
        )
        dc = 8 + wisdom_modifier + character_stat_block.get_proficiency_bonus()
        description = (
            "Rules for Focus Points:\n"
            " * Regaining: You regain all expended Focus Points when you finish a Short or Long Rest.\n"
            f" * DC: {dc}\n"
            "Known features:\n"
        )
        return description


class FlurryOfBlows(TextFeature):
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


class PatientDefense(TextFeature):
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


class StepOfTheWind(TextFeature):
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


class UnarmoredMovement(TextFeature):
    def __init__(self):
        super().__init__(name="Unarmored Movement", origin="Monk Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your speed increases by 10 feet while you aren't wearing armor or wielding a Shield. This bonus increases when you reach certain Monk levels, as shown on the Monk Features table."
        return description


class UncannyMetabolism(TextFeature):
    def __init__(self):
        super().__init__(name="Uncanny Metabolism", origin="Monk Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you roll Initiative, you can regain all expended Focus Points. When you do so, roll your Martial Arts die, and regain a number of Hit Points equal to your Monk level plus the number rolled.\n"
            "Once you use this feature, you can't use it again until you finish a Long Rest."
        )
        return description


class DeflectAttacks(TextFeature):
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


class SlowFall(TextFeature):
    def __init__(self):
        super().__init__(name="Slow Fall", origin="Monk Level 4")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can take a Reaction when you fall to reduce any damage you take from the fall by an amount equal to five times your Monk level."
        return description


class ExtraAttack(TextFeature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="Monk Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can attack twice instead of once whenever you take the Attack action on your turn."
        return description


class StunningStrike(TextFeature):
    def __init__(self):
        super().__init__(name="Stunning Strike", origin="Monk Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Once per turn when you hit a creature with a Monk weapon or an Unarmed Strike, you can expend 1 Focus Point to attempt a stunning strike. The target must make a Constitution saving throw. On a failed save, the target has the Stunned condition until the start of your next turn. On a successful save, the target's Speed is halved until the start of your next turn, and the next attack roll made against the target before then has Advantage."
        return description


class EmpoweredStrikes(TextFeature):
    def __init__(self):
        super().__init__(name="Empowered Strikes", origin="Monk Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Whenever you deal damage with your Unarmed Strike, it can deal your choice of Force damage or its normal damage type."
        return description


class Evasion(TextFeature):
    def __init__(self):
        super().__init__(name="Evasion", origin="Monk Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you're subjected to an effect that allows you to make a Dexterity saving throw to take only half damage, you instead take no damage if you succeed on the saving throw and only half damage if you fail.\n"
            "You don't benefit from this feature if you have the Incapacitated condition."
        )
        return description


class AcrobaticMovement(TextFeature):
    def __init__(self):
        super().__init__(name="Acrobatic Movement", origin="Monk Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "While you aren't wearing armor or wielding a Shield, you gain the ability to move along vertical surfaces and across liquids on your turn without falling during the movement."
        return description


class HeightenedFocus(TextFeature):
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


class SelfRestoration(TextFeature):
    def __init__(self):
        super().__init__(name="Self-Restoration", origin="Monk Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Through sheer force of will, you can remove one of the following conditions from yourself at the end of each of your turns: Charmed, Frightened, or Poisoned.\n"
            "In addition, forgoing food and drink doesn't give you levels of Exhaustion."
        )
        return description


class DeflectEnergy(TextFeature):
    def __init__(self):
        super().__init__(name="Deflect Energy", origin="Monk Level 13")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can now use your Deflect Attacks feature against attacks that deal any damage type, not just Bludgeoning, Piercing, or Slashing."
        return description


class DisciplinedSurvivorSavingThrows(TextFeature):
    def __init__(self):
        super().__init__(name="Disciplined Survivor", origin="Monk Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your physical and mental discipline grant you proficiency in all saving throws.\n"
        return description


class DisciplinedSurvivorMartialFocus(TextFeature):
    def __init__(self):
        super().__init__(name="Disciplined Survivor", origin="Monk Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Whenever you make a saving throw and fail, you can expend 1 Focus Point to reroll it, and you must use the new roll."
        return description


class PerfectFocus(TextFeature):
    def __init__(self):
        super().__init__(name="Perfect Focus", origin="Monk Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you roll Initiative and don't use Uncanny Metabolism, you regain expended Focus Points until you have 4 if you have 3 or fewer."
        return description


class SuperiorDefense(TextFeature):
    def __init__(self):
        super().__init__(name="Superior Defense", origin="Monk Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "At the start of your turn, you can expend 3 Focus Points to bolster yourself against harm for 1 minute or until you have the Incapacitated condition. During that time, you have Resistance to all damage except Force damage."
        return description


class BodyAndMind(TextFeature):
    def __init__(self):
        super().__init__(name="Body and Mind", origin="Monk Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have developed your body and mind to new heights. Your Dexterity and Wisdom scores increase by 4, to a maximum of 25."
        return description


### Warrior of Mercy Monk Features ###


class HandofHarm(TextFeature):
    def __init__(self):
        super().__init__(name="Hand of Harm", origin="Warrior of Mercy Monk Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Once per turn when you hit a creature with an Unarmed Strike and deal damage, you can expend 1 Focus Point to deal extra Necrotic damage equal to one roll of your Martial Arts die plus your Wisdom modifier."
        return description


class HandOfHealing(TextFeature):
    def __init__(self):
        super().__init__(name="Hand of Healing", origin="Warrior of Mercy Monk Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Magic action, you can expend 1 Focus Point to touch a creature and restore a number of Hit Points equal to a roll of your Martial Arts die plus your Wisdom modifier.\n"
            "When you use your Flurry of Blows, you can replace one of the Unarmed Strikes with a use of this feature without expending a Focus Point for the healing."
        )
        return description


class ImplementsOfMercy(TextFeature):
    def __init__(self):
        super().__init__(
            name="Implements of Mercy", origin="Warrior of Mercy Monk Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain proficiency in the Insight and Medicine skills and proficiency with the Herbalism Kit."
        return description


class PhysiciansTouch(TextFeature):
    def __init__(self):
        super().__init__(
            name="Physician's Touch", origin="Warrior of Mercy Monk Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your Hand of Harm and Hand of Healing improve, as detailed below.\n"
            "Hand of Harm. When you use Hand of Harm on a creature, you can also give that creature the Poisoned condition until the end of your next turn.\n"
            "Hand of Healing. When you use Hand of Healing, you can also end one of the following conditions on the creature you heal: Blinded, Deafened, Paralyzed, Poisoned, or Stunned."
        )
        return description


class FlurryOfHealingAndHarm(TextFeature):
    def __init__(self):
        super().__init__(
            name="Flurry of Healing and Harm", origin="Warrior of Mercy Monk Level 11"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you use Flurry of Blows, you can replace each of the Unarmed Strikes with a use of Hand of Healing without expending Focus Points for the healing.\n"
            "In addition, when you make an Unarmed Strike with Flurry of Blows and deal damage, you can use Hand of Harm with that strike without expending a Focus Point for Hand of Harm. You can still use Hand of Harm only once per turn.\n"
            "You can use these benefits a total number of times equal to your Wisdom modifier (minimum of once). You regain all expended uses when you finish a Long Rest."
        )
        return description


class HandOfUltimateMercy(TextFeature):
    def __init__(self):
        super().__init__(
            name="Hand of Ultimate Mercy", origin="Warrior of Mercy Monk Level 17"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your mastery of life energy opens the door to the ultimate mercy. As a Magic action, you can touch the corpse of a creature that died within the past 24 hours and expend 5 Focus Points. The creature then returns to life with a number of Hit Points equal to 4d10 plus your Wisdom modifier. If the creature died with any of the following conditions, the creature revives with the conditions removed: Blinded, Deafened, Paralyzed, Poisoned, and Stunned.\n"
            "Once you use this feature, you can't use it again until you finish a Long Rest."
        )
        return description


### Warrior of Shadow Monk Features ###


class ShadowArts(TextFeature):
    def __init__(self):
        super().__init__(name="Shadow Arts", origin="Warrior of Shadow Monk Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have learned to draw on the power of the Shadowfell, gaining the following benefits.\n"
            "Darkness. You can expend 1 Focus Point to cast the Darkness spell without spell components. You can see within the spell's area when you cast it with this feature. While the spell persists, you can move its area of Darkness to a space within 60 feet of yourself at the start of each of your turns.\n"
            "Darkvision. You gain Darkvision with a range of 60 feet. If you already have Darkvision, its range increases by 60 feet.\n"
            "Shadowy Figments. You know the Minor Illusion spell. Wisdom is your spellcasting ability for it."
        )
        return description


class ShadowStep(TextFeature):
    def __init__(self):
        super().__init__(name="Shadow Step", origin="Warrior of Shadow Monk Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "While entirely within Dim Light or Darkness, you can use a Bonus Action to teleport up to 60 feet to an unoccupied space you can see that is also in Dim Light or Darkness. You then have Advantage on the next melee attack you make before the end of the current turn."
        return description


class ImprovedShadowStep(TextFeature):
    def __init__(self):
        super().__init__(
            name="Improved Shadow Step", origin="Warrior of Shadow Monk Level 11"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can draw on your Shadowfell connection to empower your teleportation. When you use your Shadow Step, you can expend 1 Focus Point to remove the requirement that you must start and end in Dim Light or Darkness for that use of the feature. As part of this Bonus Action, you can make an Unarmed Strike immediately after you teleport."
        return description


class CloakOfShadows(TextFeature):
    def __init__(self):
        super().__init__(
            name="Cloak of Shadows", origin="Warrior of Shadow Monk Level 17"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Magic action while entirely within Dim Light or Darkness, you can expend 3 Focus Points to shroud yourself with shadows for 1 minute, until you have the Incapacitated condition, or until you end your turn in Bright Light. While shrouded by these shadows, you gain the following benefits.\n"
            "Invisibility. You have the Invisible condition.\n"
            "Partially Incorporeal. You can move through occupied spaces as if they were Difficult Terrain. If you end your turn in such a space, you are shunted to the last unoccupied space you were in.\n"
            "Shadow Flurry. You can use your Flurry of Blows without expending any Focus Points."
        )
        return description


### Warrior of the Elements Monk Features ###


class ElementalAttunement(TextFeature):
    def __init__(self):
        super().__init__(
            name="Elemental Attunement", origin="Warrior of the Elements Monk Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At the start of your turn, you can expend 1 Focus Point to imbue yourself with elemental energy. The energy lasts for 10 minutes or until you have the Incapacitated condition. You gain the following benefits while this feature is active.\n"
            "Reach. When you make an Unarmed Strike, your reach is 10 feet greater than normal, as elemental energy extends from you.\n"
            "Elemental Strikes. Whenever you hit with your Unarmed Strike, you can cause it to deal your choice of Acid, Cold, Fire, Lightning, or Thunder damage rather than its normal damage type. When you deal one of these types with it, you can also force the target to make a Strength saving throw. On a failed save, you can move the target up to 10 feet toward or away from you, as elemental energy swirls around it."
        )
        return description


class ManipulateElements(TextFeature):
    def __init__(self):
        super().__init__(
            name="Manipulate Elements", origin="Warrior of the Elements Monk Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You know the Elementalism spell. Wisdom is your spellcasting ability for it."
        return description


class ElementalBurst(TextFeature):
    def __init__(self):
        super().__init__(
            name="Elemental Burst", origin="Warrior of the Elements Monk Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Magic action, you can expend 2 Focus Points to cause elemental energy to burst in a 20-foot-radius Sphere centered on a point within 120 feet of yourself. Choose a damage type: Acid, Cold, Fire, Lightning, or Thunder.\n"
            "Each creature in the Sphere must make a Dexterity saving throw. On a failed save, a creature takes damage of the chosen type equal to three rolls of your Martial Arts die. On a successful save, a creature takes half as much damage."
        )
        return description


class StrideOfTheElements(TextFeature):
    def __init__(self):
        super().__init__(
            name="Stride of the Elements",
            origin="Warrior of the Elements Monk Level 11",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "While your Elemental Attunement is active, you also have a Fly Speed and a Swim Speed equal to your Speed."
        return description


class ElementalEpitome(TextFeature):
    def __init__(self):
        super().__init__(
            name="Elemental Epitome", origin="Warrior of the Elements Monk Level 17"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "While your Elemental Attunement is active, you also gain the following benefits.\n"
            "Damage Resistance. You gain Resistance to one of the following damage types of your choice: Acid, Cold, Fire, Lightning, or Thunder. At the start of each of your turns, you can change this choice.\n"
            "Destructive Stride. When you use your Step of the Wind, your Speed increases by 20 feet until the end of the turn. For that duration, any creature of your choice takes damage equal to one roll of your Martial Arts die when you enter a space within 5 feet of it. The damage type is your choice of Acid, Cold, Fire, Lightning, or Thunder. A creature can take this damage only once per turn.\n"
            "Empowered Strikes. Once on each of your turns, you can deal extra damage to a target equal to one roll of your Martial Arts die when you hit it with an Unarmed Strike. The extra damage is the same type dealt by that strike."
        )
        return description


### Warrior of the open Hand Monk Features ###


class OpenHandTechnique(TextFeature):
    def __init__(self):
        super().__init__(
            name="Open Hand Technique", origin="Warrior of the open Hand Monk Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Whenever you hit a creature with an attack granted by your Flurry of Blows, you can impose one of the following effects on that target.\n"
            "Addle. The target can't make Opportunity Attacks until the start of its next turn.\n"
            "Push. The target must succeed on a Strength saving throw or be pushed up to 15 feet away from you.\n"
            "Topple. The target must succeed on a Dexterity saving throw or have the Prone condition."
        )
        return description


class WholenessOfBody(TextFeature):
    def __init__(self):
        super().__init__(
            name="Wholeness of Body", origin="Warrior of the open Hand Monk Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to heal yourself. As a Bonus Action, you can roll your Martial Arts die. You regain a number of Hit Points equal to the number rolled plus your Wisdom modifier (minimum of 1 Hit Point regained).\n"
            "You can use this feature a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return description


class FleetStep(TextFeature):
    def __init__(self):
        super().__init__(
            name="Fleet Step", origin="Warrior of the open Hand Monk Level 11"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you take a Bonus Action other than Step of the Wind, you can also use Step of the Wind immediately after that Bonus Action."
        return description


class QuiveringPalm(TextFeature):
    def __init__(self):
        super().__init__(
            name="Quivering Palm", origin="Warrior of the open Hand Monk Level 17"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to set up lethal vibrations in someone's body. When you hit a creature with an Unarmed Strike, you can expend 4 Focus Points to start these imperceptible vibrations, which last for a number of days equal to your Monk level. The vibrations are harmless unless you take an action to end them. Alternatively, when you take the Attack action on your turn, you can forgo one of the attacks to end the vibrations. To end them, you and the target must be on the same plane of existence. When you end them, the target must make a Constitution saving throw, taking 10d12 Force damage on a failed save or half as much damage on a successful one.\n"
            "You can have only one creature under the effect of this feature at a time. You can end the vibrations harmlessly (no action required)."
        )
        return description
