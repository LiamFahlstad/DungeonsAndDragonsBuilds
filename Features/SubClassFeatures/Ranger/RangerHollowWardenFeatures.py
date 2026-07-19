
from Definitions import RANGER_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class HollowWardenSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Hollow Warden Spells", origin="Hollow Warden Ranger Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach a Ranger level specified in the Hollow Warden Spells table, you thereafter always have the listed spell prepared.\n"
            "Hollow Warden Spells\n"
            "Ranger Level	Spells\n"
            "3	Wrathful Smite\n"
            "5	Alter Self\n"
            "9	Phantom Steed\n"
            "13	Dominate Beast\n"
            "17	Steel Wind Strike"
        )
        return description


class WrathOfTheWild(Feature):
    def __init__(self):
        super().__init__(
            name="Wrath of the Wild", origin="Hollow Warden Ranger Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You draw power from the strange and ancient horrors of the land, causing you to sprout unnatural growths, such as bloody antlers or putrid fangs, or causing your shadow to lengthen or twist around you. As a Bonus Action, you can expend a use of Favored Enemy to transform into a ghastly form, gaining the following benefits for 1 minute or until you have the Incapacitated condition, die, or end the transformation (no action required).\n"
            "Ancient Armor. You gain a +1 bonus to AC, as your body is wreathed in rotten bark and beastly bristles. This bonus increases to +2 when you reach Ranger level 11.\n"
            "Prowling Retribution. Immediately after a creature you can see within 5 feet of yourself deals damage to you or one of your allies, you can make an Opportunity Attack against that creature.\n"
            "Unnerving Aura. When you transform and at the start of each of your subsequent turns, each creature of your choice in a 10-foot Emanation originating from you makes a Wisdom saving throw against your spell save DC. On a failed save, a creature has the Frightened condition until the start of your next turn."
        )
        return description


class HungeringMight(Feature):
    def __init__(self):
        super().__init__(name="Hungering Might", origin="Hollow Warden Ranger Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain a bonus to Constitution saving throws equal to your Wisdom modifier (minimum of +1).\n"
            "In addition, once per turn when you hit a creature with an attack roll while you are transformed using Wrath of the Wild, you regain a number of Hit Points equal to 1d10 plus your Wisdom modifier, provided you are Bloodied when you hit."
        )
        return description


class RotAndViolence(Feature):
    def __init__(self):
        super().__init__(
            name="Rot and Violence", origin="Hollow Warden Ranger Level 11"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your dedication to wild eldritch beings alters you further. When transformed using Wrath of the Wild, you gain the following additional benefits.\n"
            "Menacing Aura. When a creature fails its saving throw against your Unnerving Aura, it also can’t regain Hit Points or take Reactions until the start of your next turn.\n"
            "Strangling Roots. When you hit a creature with an attack roll using a weapon, you can activate the Sap or Slow mastery property in addition to a different mastery property you’re using with that weapon."
        )
        return description


class AncientMight(Feature):
    def __init__(self):
        super().__init__(name="Ancient Might", origin="Hollow Warden Ranger Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You become wholly suffused with the wild’s ancient and terrible power, granting you the following benefits.\n"
            "Ominous Strikes. When you hit a creature that has the Frightened condition with an attack roll, that attack deals extra damage equal to your Wisdom modifier.\n"
            "Persistent Wrath. If you’re reduced to 0 Hit Points but not killed outright while transformed using Wrath of the Wild, you can surge with wild power. Your Hit Points instead change to a number equal to twice your Ranger level. Once you use this feature, you can’t do so again until you finish a Long Rest. You can also expend a level 4+ spell slot (no action required) to restore your use of this feature.\n"
            "Timeless. You have Immunity to the Exhaustion condition."
        )
        return description
