from Core.Definitions import Ability, RANGER_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class HorizonWalkerSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Horizon Walker Spells", origin="Horizon Walker Ranger Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You learn an additional spell when you reach certain levels in this class, as shown in the Horizon Walker Spells table. The spell counts as a ranger spell for you, but it doesn't count against the number of ranger spells you know.\n"
            "Horizon Walker Spells\n"
            "Ranger Level\tSpells\n"
            "3rd\tProtection from Evil and Good\n"
            "5th\tMisty Step\n"
            "9th\tHaste\n"
            "13th\tBanishment\n"
            "17th\tTeleportation Circle"
        )
        return description


class DetectPortal(Feature):
    def __init__(self):
        super().__init__(
            name="Detect Portal", origin="Horizon Walker Ranger Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to magically sense the presence of a planar portal. As an action, you detect the distance and direction to the closest planar portal within 1 mile of you.\n"
            "Once you use this feature, you can't use it again until you finish a short or long rest.\n"
            "See the \"Planar Travel\" section in chapter 2 of the Dungeon Master's Guide for examples of planar portals."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="short or long rest")


class PlanarWarrior(Feature):
    def __init__(self):
        super().__init__(
            name="Planar Warrior", origin="Horizon Walker Ranger Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You learn to draw on the energy of the multiverse to augment your attacks.\n"
            "As a bonus action, choose one creature you can see within 30 feet of you. The next time you hit that creature on this turn with a weapon attack, all damage dealt by the attack becomes force damage, and the creature takes an extra 1d8 force damage from the attack. When you reach 11th level in this class, the extra damage increases to 2d8."
        )
        return description


class EtherealStep(Feature):
    def __init__(self):
        super().__init__(
            name="Ethereal Step", origin="Horizon Walker Ranger Level 7"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You learn to step through the Ethereal Plane. As a bonus action on your turn, you can cast the Etherealness spell with this feature, without expending a spell slot, but the spell ends at the end of the current turn.\n"
            "Once you use this feature, you can't use it again until you finish a short or long rest."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="short or long rest")


class DistantStrike(Feature):
    def __init__(self):
        super().__init__(
            name="Distant Strike", origin="Horizon Walker Ranger Level 11"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to pass between the planes in a blink of an eye. When you use the Attack action, you can teleport up to 10 feet before each attack to an unoccupied space you can see.\n"
            "If you attack at least two different creatures with the action, you can make one additional attack with it against a third creature."
        )
        return description


class SpectralDefense(Feature):
    def __init__(self):
        super().__init__(
            name="Spectral Defense", origin="Horizon Walker Ranger Level 15"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your ability to move between planes enables you to slip through the planar boundaries to lessen the harm done to you during battle. When you take damage from an attack, you can use your reaction to give yourself resistance to all of that attack's damage on this turn."
        )
        return description
