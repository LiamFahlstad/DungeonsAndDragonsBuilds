from Features.BaseFeatures import TextFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

BARBARIAN_HIT_DIE = 6


class PsionicPower(TextFeature):
    def __init__(self):
        super().__init__(name="Psionic Power", origin="Psion Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You harbor a wellspring of psionic energy within\n"
            "yourself. This energy is represented by your Psionic\n"
            "Energy Dice. Your Psion level determines the die\n"
            "size and number of Psionic Energy Dice you have, as\n"
            "shown in the Energy Dice column of the Psiopn table\n"
            "Your Psionic Energy Dice are used to enhance or\n"
            "fuel certain Psion features. You start with two such\n"
            "features: Telekinetic Propel and Telepathic\n"
            "Connection, each of which is detailed below. Some of\n"
            "your powers expend the Psionic Energy Dice, as\n"
            "specified in a power's description, and you can't use\n"
            "a power if it requires you to use a die when all your\n"
            "Psionic Energy Dice are expended.\n"
            "You regain one expended Psionic Energy Die when\n"
            "you finish a Short Rest, and you regain all of them\n"
            "when you finish a Long Rest.\n"
            "Some features that use Psionic Energy Dice\n"
            "require your target to make a saving throw. The save\n"
            "DC equals the spell save DC from this class's\n"
            "Spellcasting feature.\n"
            "Telekinetic Propel. As a Bonus Action, choose one\n"
            "Large or smaller creature other than you that you\n"
            "can see within 30 feet of yourself. When you do so,\n"
            "the target must succeed on a Strength saving throw\n"
            "or be moved 5 feet straight toward you or straight\n"
            "away from you. Alternatively, you can roll one\n"
            "Psionic Energy Die when you take this Bonus Action,\n"
            "and the distance moved is equal to 5 times the\n"
            "number rolled. The die is expended only if the target\n"
            "fails the saving throw.\n"
            "Telepathic Connection. You have telepathy with a\n"
            "range of 30 feet. As a Bonus Action, you can roll one\n"
            "Psionic Energy Die. For the next hour, the range of\n"
            "your telepathy increases by a number of feet equal\n"
            "to 10 times the number rolled. The first time you use\n"
            "this Bonus Action after each Long Rest, you don't\n"
            "expend the Psionic Energy Die. All other times you\n"
            "use this feature, you expend the die."
        )
        return description


class SubtleTelekinesis(TextFeature):
    def __init__(self):
        super().__init__(name="Subtle Telekinesis", origin="Psion Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You know the Mage Hand cantrip. You can cast it\n"
            "without Somatic components, and you can make the\n"
            "spectral hand Invisible when you cast it."
        )
        return description


class PsionicDiscipline(TextFeature):
    def __init__(self):
        super().__init__(name="Psionic Discipline", origin="Psion Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You learn further psionic techniques that are fueled\n"
            "by your Psionic Energy Dice. You gain two\n"
            "disciplines of your choice, such as Expanded\n"
            "Awareness and Id Insinuation. Disciplines are\n"
            "described in the “Psionic Discipline Options” section\n"
            "later in this class's description.\n"
            "You can use only one Discipline each turn and only\n"
            "once per turn unless otherwise noted in one of those\n"
            "options.\n"
            "Whenever you gain a Psion level, you can replace\n"
            "one of your Psionic Discipline options with one you\n"
            "don't know. You gain one additional option at Psion\n"
            "levels 5, 10, 13, and 17."
        )
        return description


class PsionicRestoration(TextFeature):
    def __init__(self):
        super().__init__(name="Psionic Restoration", origin="Psion Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can perform a meditation that focuses the mind\n"
            "for 1 minute. At the end of it, you regain expended\n"
            "Psionic Energy Dice. Once you use this feature, you\n"
            "can't do so again until you finish a Long Rest."
        )
        return description


class PsionicSurge(TextFeature):
    def __init__(self):
        super().__init__(name="Psionic Surge", origin="Psion Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can push your psionic powers using your life\n"
            "force. After you roll one or more Psionic Energy\n"
            "Dice, you can expend one of your Hit Point Dice and\n"
            "treat any roll of 1, 2, or 3 on those Psionic Energy\n"
            "Dice as a 4."
        )
        return description


class PsionicReserves(TextFeature):
    def __init__(self):
        super().__init__(name="Psionic Reserves", origin="Psion Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you roll Initiative, you regain expended uses\n"
            "of Psionic Energy Dice until you have four if you\n"
            "have fewer than that."
        )
        return description


class EpicBoon(TextFeature):
    def __init__(self):
        super().__init__(name="Epic Boon", origin="Psion Level 19")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain an Epic Boon feat or another feat of your\n"
            "choice for which you qualify. Boon of Energy\n"
            "Resistance is recommended."
        )
        return description


class EnkindledLifeForce(TextFeature):
    def __init__(self):
        super().__init__(name="Enkindled Life Force", origin="Psion Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You burn your life force to achieve greater psionics.\n"
            "Once per turn, when you roll one or more Psionic\n"
            "Energy Dice for a Psion feature or Psionic Discipline,\n"
            "you can expend one or two of your Hit Point Dice.\n"
            "For each Hit Point Die expended, roll an additional\n"
            "Psionic Energy Die and add the numbers rolled to\n"
            "the total. This roll does not expend the Psionic\n"
            "Energy Die."
        )
        return description


### Metamorph subclass feature ###


class MetamorphSpells(TextFeature):
    def __init__(self):
        super().__init__(name="Metamorph Spells", origin="Metamorph Psion Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach a Psion level specified in the\n"
            "Metamorph Spells table, you thereafter always have\n"
            "the listed spells prepared."
        )
        return description


class MutableForm(TextFeature):
    def __init__(self):
        super().__init__(name="Mutable Form", origin="Metamorph Psion Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you can expend one Psionic\n"
            "Energy Die to psionically stretch your limbs for 1\n"
            "minute. Roll the expended Psionic Energy Die and\n"
            "gain a number of Temporary Hit Points equal to the\n"
            "number rolled plus your Intelligence modifier\n"
            "(minimum of 1 Temporary Hit Point). In addition,\n"
            "you gain the following benefits while this feature is\n"
            "active.\n"
            "Reach. Your reach increases by 5 feet.\n"
            "Speed. Your Speed increases by 5 feet.\n"
            "Touch. When you cast a spell that has a range of\n"
            "Touch and a casting time of an action, you can make\n"
            "the spell's range 10 feet."
        )
        return description


class OrganicWeapons(TextFeature):
    def __init__(self):
        super().__init__(name="Organic Weapons", origin="Metamorph Psion Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can shape your limbs into weapons. As a Magic\n"
            "action, you can reform your free hand into one of the\n"
            "following organic weapons: Bone Blade, Flesh Maul,\n"
            "or Viscera Launcher. When you take the Attack\n"
            "action, you can use this feature before you make the\n"
            "attack roll. Your limb retains the form of the organic\n"
            "weapon until you take a Magic action to change it\n"
            "into another organic weapon, you have the\n"
            "Unconscious condition, or you return the limb to its\n"
            "previous form (no action required).\n"
            "Whenever you attack with the weapon, you can\n"
            "use your Intelligence modifier for the attack and\n"
            "damage rolls instead of using Strength or Dexterity.\n"
            "Bone Blade. A blade made of bone springs from\n"
            "your forearm or extends from your hand. The blade\n"
            "counts as a Simple Melee weapon with the Finesse\n"
            "property, and it deals 1d8 Piercing damage on a hit.\n"
            "You have Advantage on the attack roll you make\n"
            "with the blade if at least one of your allies is within 5\n"
            "feet of the target and the ally doesn't have the\n"
            "Incapacitated condition.\n"
            "Flesh Maul. Your fist and forearm coalesce into a\n"
            "hardened mass of flesh and bone. The maul counts\n"
            "as a Simple Melee weapon and deals 1d10\n"
            "Bludgeoning damage on a hit. A creature hit by the\n"
            "maul has Disadvantage on the next Strength or\n"
            "Constitution saving throw it makes before the start\n"
            "of its next turn.\n"
            "Viscera Launcher. Your hand and forearm\n"
            "transform into a crossbow made of muscle and\n"
            "sinew that fires bolts of bile. The launcher counts as\n"
            "a Simple Ranged weapon with a normal range of 30\n"
            "feet and a long range of 90 feet, and it deals 1d6 Acid\n"
            "damage on a hit. Once on each of your turns when\n"
            "you hit a creature with an attack roll using the\n"
            "launcher, you can deal an extra 1d6 Acid damage to\n"
            "the target."
        )
        return description


class FleshWeaver(TextFeature):
    def __init__(self):
        super().__init__(name="Flesh Weaver", origin="Metamorph Psion Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you use Mutable Form, you can expend an\n"
            "additional Psionic Energy Die to gain the following\n"
            "benefits while the feature is active.\n"
            "Organic Defense. You gain a +2 bonus to AC.\n"
            "Empowered Healing. When you cast a spell with a\n"
            "spell slot that restores Hit Points to one or more\n"
            "creatures, you can expend one Psionic Energy Die,\n"
            "roll it, and add the number rolled to the number of\n"
            "Hit Points regained."
        )
        return description


class ImprovedMutableForm(TextFeature):
    def __init__(self):
        super().__init__(
            name="Improved Mutable Form", origin="Metamorph Psion Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you use Mutable Form, the duration increases\n"
            "to 10 minutes and you gain one of the following\n"
            "benefits of your choice, the effects of which last until\n"
            "Mutable Form ends.\n"
            "Stony Epidermis. You have Advantage on\n"
            "Constitution saving throws to maintain\n"
            "Concentration. In addition, choose one of the\n"
            "following damage types: Acid, Bludgeoning, Cold,\n"
            "Fire, Lightning, Piercing, Poison, Slashing, or\n"
            "Thunder. You gain Resistance to the chosen damage\n"
            "type.\n"
            "Superior Stride. While you aren't wearing armor,\n"
            "you can take the Dash action as a Bonus Action, and\n"
            "you have a Climb Speed and Swim Speed equal to\n"
            "your Speed.\n"
            "Unnatural Flexibility. You gain a +1 bonus to AC,\n"
            "and your body—along with any equipment you're\n"
            "wearing or carrying—becomes pliable. You can\n"
            "move through any space as narrow as 1 inch, and\n"
            "you can spend 5 feet of movement to escape from\n"
            "nonmagical restraints or end the Grappled\n"
            "condition."
        )
        return description


class LifeBendingWeapons(TextFeature):
    def __init__(self):
        super().__init__(name="Life-bending Weapons", origin="Metamorph Psion Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your weapon becomes wreathed in negative energy,\n"
            "and you radiate life-mending psionic energy. When\n"
            "you hit a target with an attack roll using your\n"
            "Organic Weapon, roll one Psionic Energy Die. The\n"
            "target takes extra Necrotic damage equal to the\n"
            "number rolled. This roll doesn't expend the die.\n"
            "Alternatively, when you hit a creature with your\n"
            "Organic Weapon, you can instead expend one\n"
            "Psionic Energy Die and roll it. The target takes extra\n"
            "Necrotic damage equal to the roll, and each creature\n"
            "of your choice in a 30-foot Emanation originating\n"
            "from you regains Hit Points equal the number rolled\n"
            "plus your Intelligence modifier. Once you use this\n"
            "feature, you can't do so again until the start of your\n"
            "next turn."
        )
        return description


### Psykinetic subclass feature ###


class StrongerTelekinesis(TextFeature):
    def __init__(self):
        super().__init__(name="Stronger Telekinesis", origin="Psykinetic Psion Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you cast Mage Hand, its range increases by 30\n"
            "feet when you cast it, and the hand can carry up to\n"
            "20 pounds."
        )
        return description


class TelekineticTechniques(TextFeature):
    def __init__(self):
        super().__init__(
            name="Telekinetic Techniques", origin="Psykinetic Psion Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you use Telekinetic Propel, you can roll 1d4\n"
            "and use the number rolled instead of expending a\n"
            "Psionic Energy Die.\n"
            "In addition, when a target fails the saving throw\n"
            "against your Telekinetic Propel, you can impose one\n"
            "of the following effects on that target\n"
            "Boost. The target's Speed increases by 10 feet\n"
            "until the start of your next turn.\n"
            "Disorient. The target can't make Opportunity\n"
            "Attacks until the start of its next turn.\n"
            "Telekinetic Bolt. The target takes Force damage\n"
            "equal to the number rolled on the Psionic Energy\n"
            "Die."
        )
        return description


class DestructiveTrance(TextFeature):
    def __init__(self):
        super().__init__(name="Destructive Trance", origin="Psykinetic Psion Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At the start of your turn, you can expend one Psionic\n"
            "Energy Die to enter a destructive state. For the next\n"
            "10 minutes, you gain a Fly Speed of 20 feet and can\n"
            "hover, and when you cast a Psion spell that expends\n"
            "a spell slot, you can roll your Psionic Energy Die and\n"
            "add the number rolled to one damage roll of that\n"
            "spell. This roll doesn't expend the Psionic Energy\n"
            "Die."
        )
        return description


class ReboundingField(TextFeature):
    def __init__(self):
        super().__init__(name="Rebounding Field", origin="Psykinetic Psion Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you cast Shield in response to being hit by an\n"
            "attack roll and cause the triggering attack to miss,\n"
            "you can expend one Psionic Energy Die to launch the\n"
            "force back at the attacker. The attacker makes a\n"
            "Dexterity saving throw. Roll one Psionic Energy Die.\n"
            "On a failed save, the attacker takes Force damage\n"
            "equal to the amount rolled plus your Intelligence\n"
            "modifier. On a successful save, the attacker takes\n"
            "half as much damage only. Whether the target fails\n"
            "or succeeds on the saving throw, you gain\n"
            "Temporary Hit Points equal to the amount of\n"
            "damage dealt."
        )
        return description


class EnhancedTelekineticCrush(TextFeature):
    def __init__(self):
        super().__init__(
            name="Enhanced Telekinetic Crush", origin="Psykinetic Psion Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you cast Telekinetic Crush, you can expend one\n"
            "Psionic Energy Die to modify the spell so that\n"
            "whether a creature fails or succeeds on the saving\n"
            "throw against the spell, its Speed is halved until the\n"
            "start of your next turn. In addition, you can roll the\n"
            "expended Psionic Energy Die and add the number\n"
            "rolled to one damage roll of the spell."
        )
        return description


class HeightenedTelekinesis(TextFeature):
    def __init__(self):
        super().__init__(
            name="Heightened Telekinesis", origin="Psykinetic Psion Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can cast Telekinesis without expending a spell\n"
            "slot by instead expending four Psionic Energy Dice.\n"
            "When you cast Telekinesis without expending a spell\n"
            "slot using this feature, you can modify the spell so\n"
            "that it doesn't require Concentration. If you do so,\n"
            "the spell's duration becomes 1 minute for that\n"
            "casting, and you"
        )
        return description


### Telepath subclass feature ###


class MindInfiltrator(TextFeature):
    def __init__(self):
        super().__init__(name="Mind Infiltrator", origin="Telepath Psion Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you cast Detect Thoughts, you can expend one\n"
            "Psionic Energy Die to modify the spell so that the\n"
            "spell doesn't require spell components or\n"
            "Concentration. In addition, when you use the Read\n"
            "Thoughts effect of the spell, the target doesn't know\n"
            "you're probing its mind if it fails the Wisdom saving\n"
            "throw."
        )
        return description


class TelepathicDistraction(TextFeature):
    def __init__(self):
        super().__init__(name="Telepathic Distraction", origin="Telepath Psion Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When a creature you can see within range of your\n"
            "telepathy hits with an attack roll, you can take a\n"
            "Reaction to roll one Psionic Energy Die and subtract\n"
            "the number rolled from attack roll, potentially\n"
            "causing the attack to miss. The die is expended only\n"
            "if the target misses the attack."
        )
        return description


class BulwarkMind(TextFeature):
    def __init__(self):
        super().__init__(name="Bulwark Mind", origin="Telepath Psion Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At the start of your turn, you can expend one Psionic\n"
            "Energy Die to strengthen your mind and enter a\n"
            "fortified state. For the next 10 minutes, you have\n"
            "Resistance to Psychic damage; and whenever you\n"
            "make an Intelligence, Wisdom, or Charisma saving\n"
            "throw, you add a roll of your Psionic Energy Die to\n"
            "the save. Rolling the Psionic Energy Die doesn't\n"
            "expend it. You can't use this benefit if you have the\n"
            "Incapacitated condition."
        )
        return description


class PotentThoughts(TextFeature):
    def __init__(self):
        super().__init__(name="Potent Thoughts", origin="Telepath Psion Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have telepathy with a range of 60 feet. In\n"
            "addition, you add your Intelligence modifier to the\n"
            "damage you deal with any Psion cantrip."
        )
        return description


class TelepathicBolstering(TextFeature):
    def __init__(self):
        super().__init__(name="Telepathic Bolstering", origin="Telepath Psion Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you or a creature you can see within range of\n"
            "your telepathy fails an ability check or misses with\n"
            "an attack roll, you can take a Reaction to expend one\n"
            "Psionic Energy Die. Roll the die and add the number\n"
            "rolled to the d20, potentially turning a failed check\n"
            "into a success or a miss into a hit. The Psionic\n"
            "Energy Die is expended only if the check succeeds or\n"
            "the attack hits."
        )
        return description


class ScrambleMinds(TextFeature):
    def __init__(self):
        super().__init__(name="Scramble Minds", origin="Telepath Psion Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can cast Confusion without expending a spell\n"
            "slot by instead expending four Psionic Energy Dice.\n"
            "When you cast Confusion without a spell slot using\n"
            "this feature, you can modify the spell so that the\n"
            "radius of the spell's Sphere becomes 30 feet and you\n"
            "can choose one creature you can see in the spell's\n"
            "area to automatically succeed on their saving throw\n"
            "against the spell.\n"
            "In addition, when a creature under the effect of\n"
            "the spell starts its turn, you choose their behavior\n"
            "from the table for the turn instead of the creature\n"
            "rolling to determine its behavior."
        )
        return description
