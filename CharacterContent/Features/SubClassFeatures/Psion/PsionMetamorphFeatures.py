from Core.Definitions import PSION_HIT_DIE, Ability
from Model.Content.Feature import Feature, FeatureActivation, ActionType, FeatureTarget
from Model.View import CharacterView


class MetamorphSpells(Feature):
    def __init__(self):
        super().__init__(name="Metamorph Spells", origin="Metamorph Psion Level 3")

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you reach a Psion level specified in the "
            "Metamorph Spells table, you thereafter always have "
            "the listed spells prepared."
        )
        return description


class MutableForm(Feature):
    def __init__(self):
        super().__init__(
            name="Mutable Form",
            origin="Metamorph Psion Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, duration="1 Minute"
            ),
            usage_tags=["buff"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Bonus Action, you can expend one Psionic "
            "Energy Die to psionically stretch your limbs for 1 "
            "minute. Roll the expended Psionic Energy Die and "
            "gain a number of Temporary Hit Points equal to the "
            "number rolled plus your Intelligence modifier "
            "(minimum of 1 Temporary Hit Point). In addition, "
            "you gain the following benefits while this feature is "
            "active.\n"
            "Reach. Your reach increases by 5 feet.\n"
            "Speed. Your Speed increases by 5 feet.\n"
            "Touch. When you cast a spell that has a range of "
            "Touch and a casting time of an action, you can make "
            "the spell's range 10 feet."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class OrganicWeapons(Feature):
    def __init__(self):
        super().__init__(
            name="Organic Weapons",
            origin="Metamorph Psion Level 3",
            activation=FeatureActivation(action_type=ActionType.ACTION),
            usage_tags=["damage", "buff", "control"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can shape your limbs into weapons. As a Magic "
            "action, you can reform your free hand into one of the "
            "following organic weapons: Bone Blade, Flesh Maul, "
            "or Viscera Launcher. When you take the Attack "
            "action, you can use this feature before you make the "
            "attack roll. Your limb retains the form of the organic "
            "weapon until you take a Magic action to change it "
            "into another organic weapon, you have the "
            "Unconscious condition, or you return the limb to its "
            "previous form (no action required).\n"
            "Whenever you attack with the weapon, you can "
            "use your Intelligence modifier for the attack and "
            "damage rolls instead of using Strength or Dexterity.\n"
            "Bone Blade. A blade made of bone springs from "
            "your forearm or extends from your hand. The blade "
            "counts as a Simple Melee weapon with the Finesse "
            "property, and it deals 1d8 Piercing damage on a hit. "
            "You have Advantage on the attack roll you make "
            "with the blade if at least one of your allies is within 5 "
            "feet of the target and the ally doesn't have the "
            "Incapacitated condition.\n"
            "Flesh Maul. Your fist and forearm coalesce into a "
            "hardened mass of flesh and bone. The maul counts "
            "as a Simple Melee weapon and deals 1d10 "
            "Bludgeoning damage on a hit. A creature hit by the "
            "maul has Disadvantage on the next Strength or "
            "Constitution saving throw it makes before the start "
            "of its next turn.\n"
            "Viscera Launcher. Your hand and forearm "
            "transform into a crossbow made of muscle and "
            "sinew that fires bolts of bile. The launcher counts as "
            "a Simple Ranged weapon with a normal range of 30 "
            "feet and a long range of 90 feet, and it deals 1d6 Acid "
            "damage on a hit. Once on each of your turns when "
            "you hit a creature with an attack roll using the "
            "launcher, you can deal an extra 1d6 Acid damage to "
            "the target."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class FleshWeaver(Feature):
    def __init__(self):
        super().__init__(
            name="Flesh Weaver",
            origin="Metamorph Psion Level 6",
            usage_tags=["buff", "heal"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you use Mutable Form, you can expend an "
            "additional Psionic Energy Die to gain the following "
            "benefits while the feature is active.\n"
            "Organic Defense. You gain a +2 bonus to AC.\n"
            "Empowered Healing. When you cast a spell with a "
            "spell slot that restores Hit Points to one or more "
            "creatures, you can expend one Psionic Energy Die, "
            "roll it, and add the number rolled to the number of "
            "Hit Points regained."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class ImprovedMutableForm(Feature):
    def __init__(self):
        super().__init__(
            name="Improved Mutable Form",
            origin="Metamorph Psion Level 10",
            usage_tags=["buff", "utility"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you use Mutable Form, the duration increases "
            "to 10 minutes and you gain one of the following "
            "benefits of your choice, the effects of which last until "
            "Mutable Form ends.\n"
            "Stony Epidermis. You have Advantage on "
            "Constitution saving throws to maintain "
            "Concentration. In addition, choose one of the "
            "following damage types: Acid, Bludgeoning, Cold, "
            "Fire, Lightning, Piercing, Poison, Slashing, or "
            "Thunder. You gain Resistance to the chosen damage "
            "type.\n"
            "Superior Stride. While you aren't wearing armor, "
            "you can take the Dash action as a Bonus Action, and "
            "you have a Climb Speed and Swim Speed equal to "
            "your Speed.\n"
            "Unnatural Flexibility. You gain a +1 bonus to AC, "
            "and your body—along with any equipment you're "
            "wearing or carrying—becomes pliable. You can "
            "move through any space as narrow as 1 inch, and "
            "you can spend 5 feet of movement to escape from "
            "nonmagical restraints or end the Grappled "
            "condition."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class LifeBendingWeapons(Feature):
    def __init__(self):
        super().__init__(
            name="Life-bending Weapons",
            origin="Metamorph Psion Level 14",
            activation=FeatureActivation(range="30-Foot Emanation"),
            usage_tags=["damage", "heal"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your weapon becomes wreathed in negative energy, "
            "and you radiate life-mending psionic energy. When "
            "you hit a target with an attack roll using your "
            "Organic Weapon, roll one Psionic Energy Die. The "
            "target takes extra Necrotic damage equal to the "
            "number rolled. This roll doesn't expend the die. "
            "Alternatively, when you hit a creature with your "
            "Organic Weapon, you can instead expend one "
            "Psionic Energy Die and roll it. The target takes extra "
            "Necrotic damage equal to the roll, and each creature "
            "of your choice in a 30-foot Emanation originating "
            "from you regains Hit Points equal the number rolled "
            "plus your Intelligence modifier. Once you use this "
            "feature, you can't do so again until the start of your "
            "next turn."
        )
        return description
