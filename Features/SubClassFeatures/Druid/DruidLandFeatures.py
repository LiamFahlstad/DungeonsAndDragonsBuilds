
import Definitions
from Definitions import DRUID_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


_LAND_TYPE_RESISTANCE: dict[Definitions.DruidLandType, str] = {
    Definitions.DruidLandType.ARID: "Fire",
    Definitions.DruidLandType.POLAR: "Cold",
    Definitions.DruidLandType.TEMPERATE: "Lightning",
    Definitions.DruidLandType.TROPICAL: "Poison",
}


class CircleOfTheLandSpells(Feature):
    def __init__(self, land_type: Definitions.DruidLandType):
        super().__init__(
            name="Circle of the Land Spells", origin="Circle of the Land Druid Level 3"
        )
        self.land_type = land_type

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Whenever you finish a Long Rest, choose one type of land: arid, polar, temperate, or tropical. Consult the table below that corresponds to the chosen type; you have the spells listed for your Druid level and lower prepared.\n"
            f"You have chosen the {self.land_type.value} land."
        )
        return description


class LandsAid(Feature):
    def __init__(self):
        super().__init__(name="Land's Aid", origin="Circle of the Land Druid Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Magic action, you can expend a use of your Wild Shape and choose a point within 60 feet of yourself. Vitality-giving flowers and life-draining thorns appear for a moment in a 10-foot-radius Sphere centered on that point. Each creature of your choice in the Sphere must make a Constitution saving throw against your spell save DC, taking 2d6 Necrotic damage on a failed save or half as much damage on a successful one. One creature of your choice in that area regains 2d6 Hit Points.\n"
            "The damage and healing increase by 1d6 when you reach Druid levels 10 (3d6) and 14 (4d6)."
        )
        return description


class NaturalRecovery(Feature):
    def __init__(self):
        super().__init__(
            name="Natural Recovery", origin="Circle of the Land Druid Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can cast one of the level 1+ spells that you have prepared from your Circle Spells feature without expending a spell slot, and you must finish a Long Rest before you do so again.\n"
            "In addition, when you finish a Short Rest, you can choose expended spell slots to recover. The spell slots can have a combined level that is equal to or less than half your Druid level (round up), and none of them can be level 6+. For example, if you're a level 6 Druid, you can recover up to three levels' worth of spell slots. You can recover a level 3 spell slot, a level 2 and a level 1 spell slot, or three level 1 spell slots. Once you recover spell slots with this feature, you can't do so again until you finish a Long Rest."
        )
        return description


class NaturesWard(Feature):
    def __init__(self, land_type: Definitions.DruidLandType):
        super().__init__(
            name="Nature's Ward", origin="Circle of the Land Druid Level 10"
        )
        self.land_type = land_type

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        resistance = _LAND_TYPE_RESISTANCE[self.land_type]
        description = (
            f"You are immune to the Poisoned condition, and you have Resistance to {resistance} damage, "
            f"the damage type associated with your {self.land_type.value} land choice in the Circle Spells feature."
        )
        return description


class NaturesSanctuary(Feature):
    def __init__(self):
        super().__init__(
            name="Nature's Sanctuary", origin="Circle of the Land Druid Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Magic action, you can expend a use of your Wild Shape and cause spectral trees and vines to appear in a 15-foot Cube on the ground within 120 feet of yourself. They last there for 1 minute or until you have the Incapacitated condition or die. You and your allies have Half Cover while in that area, and your allies gain the current Resistance of your Nature's Ward while there.\n"
            "As a Bonus Action, you can move the Cube up to 60 feet to ground within 120 feet of yourself."
        )
        return description
