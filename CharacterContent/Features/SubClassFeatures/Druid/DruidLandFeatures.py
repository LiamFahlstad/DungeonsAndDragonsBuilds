import Core.Definitions as Definitions
from Core.Definitions import (
    DRUID_HIT_DIE,
    Ability,
    CharacterClass,
    Condition,
    DamageType,
)
from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureDice,
    FeatureTarget,
)
from Model.Content.Improvements import ConditionImmunity, DamageResistance
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph, Table, dc_formula

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

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Whenever you finish a Long Rest, choose one type of land. You have its spells for your Druid level and lower prepared."
            ),
            Facts((("Current choice", f"{self.land_type.value} land"),)),
            Table(
                ("Land", "Druid level 3", "5", "7", "9"),
                (
                    (
                        "Arid",
                        "Blur, Burning Hands, Fire Bolt",
                        "Fireball",
                        "Blight",
                        "Wall of Stone",
                    ),
                    (
                        "Polar",
                        "Fog Cloud, Hold Person, Ray of Frost",
                        "Sleet Storm",
                        "Ice Storm",
                        "Cone of Cold",
                    ),
                    (
                        "Temperate",
                        "Misty Step, Shocking Grasp, Sleep",
                        "Lightning Bolt",
                        "Freedom of Movement",
                        "Tree Stride",
                    ),
                    (
                        "Tropical",
                        "Acid Splash, Ray of Sickness, Web",
                        "Stinking Cloud",
                        "Polymorph",
                        "Insect Plague",
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Whenever you finish a Long Rest, choose one type of land: arid, polar, temperate, or tropical. Consult the table below that corresponds to the chosen type; you have the spells listed for your Druid level and lower prepared.\n"
            f"You have chosen the {self.land_type.value} land."
        )
        return description


LANDS_AID_DICE = FeatureDice(
    "Land's Aid",
    (
        (3, "2d6"),
        (10, "3d6"),
        (14, "4d6"),
    ),
    CharacterClass.DRUID,
    note="Necrotic damage and healing",
)


class LandsAid(Feature):
    def __init__(self):
        super().__init__(
            name="Land's Aid",
            origin="Circle of the Land Druid Level 3",
            activation=FeatureActivation(
                action_type=ActionType.ACTION, range="60 Feet (10-Foot-Radius Sphere)"
            ),
            usage_tags=["damage", "heal"],
            dice=LANDS_AID_DICE,
        )

    def calculate_dc(self, character: CharacterView) -> int:
        return character.calculate_difficulty_class_for_ability(Ability.WISDOM)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The damage and healing dice are in the panel below.
        return [
            Paragraph(
                "Flowers and thorns bloom for a moment, harming foes and mending an ally."
            ),
            Facts(
                (
                    ("Action", "Magic action"),
                    ("Cost", "One use of Wild Shape"),
                    ("Range", "A point within 60 feet"),
                    ("Area", "10-foot-radius Sphere centered on that point"),
                    ("Target", "Each creature of your choice in the Sphere"),
                    (
                        "Save",
                        f"Constitution save against your spell save DC ({dc_formula(Ability.WISDOM)})",
                    ),
                    ("Failed", "Land's Aid dice (see Dice below) Necrotic damage"),
                    ("Succeeded", "Half damage"),
                    (
                        "Heal",
                        "One creature of your choice in the area regains Land's Aid dice (see Dice below) Hit Points",
                    ),
                )
            ),
        ]

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.AREA

    def get_description(self, character: CharacterView) -> str:
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

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Free spell",
                        "Cast one level 1+ spell prepared from your Circle Spells without a spell slot. Once per Long Rest.",
                    ),
                    (
                        "Recover slots",
                        "When you finish a Short Rest, recover expended spell slots with a combined level up to half your Druid level (round up), none level 6+. Once per Long Rest.",
                    ),
                    (
                        "Example",
                        "A level 6 Druid recovers one level 3 slot, a level 2 and a level 1 slot, or three level 1 slots",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can cast one of the level 1+ spells that you have prepared from your Circle Spells feature without expending a spell slot, and you must finish a Long Rest before you do so again.\n"
            "In addition, when you finish a Short Rest, you can choose expended spell slots to recover. The spell slots can have a combined level that is equal to or less than half your Druid level (round up), and none of them can be level 6+. For example, if you're a level 6 Druid, you can recover up to three levels' worth of spell slots. You can recover a level 3 spell slot, a level 2 and a level 1 spell slot, or three level 1 spell slots. Once you recover spell slots with this feature, you can't do so again until you finish a Long Rest."
        )
        return description


class NaturesWard(Feature):
    def __init__(self, land_type: Definitions.DruidLandType):
        super().__init__(
            name="Nature's Ward",
            origin="Circle of the Land Druid Level 10",
            passive=True,
            usage_tags=["buff"],
        )
        self.land_type = land_type
        self._condition_immunity = ConditionImmunity(Condition.POISONED)
        self._resistance = DamageResistance(
            DamageType(_LAND_TYPE_RESISTANCE[self.land_type])
        )

    def apply(self, ledger_writer: LedgerWriter):
        self._condition_immunity.apply(ledger_writer)
        self._resistance.apply(ledger_writer)

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Immunity", "The Poisoned condition"),
                    (
                        "Resistance",
                        f"{_LAND_TYPE_RESISTANCE[self.land_type]} damage, from your {self.land_type.value} land choice in Circle of the Land Spells",
                    ),
                )
            ),
            Table(
                ("Land", "Resistance"),
                (
                    ("Arid", "Fire"),
                    ("Polar", "Cold"),
                    ("Temperate", "Lightning"),
                    ("Tropical", "Poison"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        resistance = _LAND_TYPE_RESISTANCE[self.land_type]
        description = (
            f"You are immune to the Poisoned condition, and you have Resistance to {resistance} damage, "
            f"the damage type associated with your {self.land_type.value} land choice in the Circle Spells feature."
        )
        return description


class NaturesSanctuary(Feature):
    def __init__(self):
        super().__init__(
            name="Nature's Sanctuary",
            origin="Circle of the Land Druid Level 14",
            activation=FeatureActivation(
                action_type=ActionType.ACTION,
                duration="1 Minute or Until Incapacitated",
                range="120 Feet (15-Foot Cube)",
            ),
            usage_tags=["buff"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.AREA

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Raise spectral trees and vines that shelter you and your allies."
            ),
            Facts(
                (
                    ("Action", "Magic action"),
                    ("Cost", "One use of Wild Shape"),
                    ("Area", "A 15-foot Cube on the ground within 120 feet"),
                    (
                        "Duration",
                        "1 minute, or until you have the Incapacitated condition or die",
                    ),
                    (
                        "Effect",
                        "You and your allies have Half Cover in the area, and your allies gain your Nature's Ward Resistance while there",
                    ),
                    (
                        "Move",
                        "Bonus Action: move the Cube up to 60 feet, to ground within 120 feet of you",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Magic action, you can expend a use of your Wild Shape and cause spectral trees and vines to appear in a 15-foot Cube on the ground within 120 feet of yourself. They last there for 1 minute or until you have the Incapacitated condition or die. You and your allies have Half Cover while in that area, and your allies gain the current Resistance of your Nature's Ward while there.\n"
            "As a Bonus Action, you can move the Cube up to 60 feet to ground within 120 feet of yourself."
        )
        return description
