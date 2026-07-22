from Core.Definitions import PSION_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class MetamorphSpells(Feature):
    def __init__(self):
        super().__init__(name="Metamorph Spells", origin="Metamorph Psion Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach a Psion level specified in the\n"
            "Metamorph Spells table, you thereafter always have\n"
            "the listed spells prepared."
        )
        return description


class MutableForm(Feature):
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


class OrganicWeapons(Feature):
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


class FleshWeaver(Feature):
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


class ImprovedMutableForm(Feature):
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


class LifeBendingWeapons(Feature):
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
