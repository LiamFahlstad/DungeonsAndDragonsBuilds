from typing import Optional

from Core.Definitions import DamageType
from CharacterContent.Features.ClassFeatures.Ranger import PrimalCompanions
from CharacterContent.Features.ClassFeatures.Ranger.PrimalCompanions import (
    CompanionType,
)
from Model.Content.Feature import Feature, FeatureActivation, FeatureTarget
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph, StatBlock


class PrimalCompanion(Feature):
    def __init__(
        self, companion_type: CompanionType, damage_type: Optional[DamageType] = None
    ):
        self.companion_type = companion_type
        self.damage_type = damage_type
        super().__init__(
            name="Primal Companion",
            origin="Beast Master Ranger Level 3",
            activation=FeatureActivation(range="5 Feet"),
            usage_tags=["summon"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Summon a primal beast: a Beast of the Land, Sea or Sky (all three stat blocks below). Pick a fitting animal; it bears primal markings."
            ),
            Facts(
                (
                    (
                        "In combat",
                        "Acts on your turn. It moves and uses its Reaction on its own, but its only action is Dodge unless you take a Bonus Action to command it to take an action from its stat block or another action. If you have the Incapacitated condition, it acts on its own and isn't limited to Dodge.",
                    ),
                    (
                        "Beast's Strike",
                        "When you take the Attack action, give up one of your attacks to command it to take the Beast's Strike action",
                    ),
                    (
                        "Revive",
                        "Magic action: touch it within 1 hour of its death and expend a spell slot. It returns to life after 1 minute with all its Hit Points.",
                    ),
                    (
                        "Replace",
                        "When you finish a Long Rest, summon a different beast (choose its stat block and look) in an unoccupied space within 5 feet; the old one vanishes",
                    ),
                )
            ),
            StatBlock(
                PrimalCompanions.format_all_primal_companions(
                    character, self.companion_type, self.damage_type
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You magically summon a primal beast, which draws strength from your bond with nature. Choose its stat block: Beast of the Land, Beast of the Sea or Beast of the Sky. You also determine the kind of animal it is, choosing a kind appropriate for the stat block. Whatever beast you choose, it bears primal markings indicating its supernatural origin.\n"
            "    * The Beast in Combat: In Combat, the beast acts during your turn. It can move and use its Reaction on its own, but the only action it takes is the Dodge action unless you take a Bonus Action to command it to take an action in its stat block or some other action. You can also sacrifice one of your attacks when you take the Attack action to command the beast to take the Beast's Strike action. If you have the Incapacitated condition, the beast acts on its own and isn't limited to the dodge action.\n"
            "    * Restoring or Replacing the Beast: If the beast has died within the last hour, you can take a Magic action to touch it and expend a spell slot. The beast returns to life after 1 minute with all its Hit Points restored.\n"
            "   Whenever you finish a Long Rest, you can summon a different primal beast, which appears in an unoccupied space within 5 feet of you. You choose its stat block and appearance. If you already have a beast from this feature, the old one vanishes when the new one appears.\n"
            "\nAll three Beast stat blocks are below so you can switch on a Long Rest without regenerating this sheet:\n"
            + PrimalCompanions.format_all_primal_companions(
                character, self.companion_type, self.damage_type
            )
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class ExceptionalTraining(Feature):
    def __init__(self):
        super().__init__(
            name="Exceptional Training",
            origin="Beast Master Ranger Level 7",
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Bonus Action",
                        "When you command your beast to take an action, also command it to Dash, Disengage, Dodge or Help with its Bonus Action",
                    ),
                    (
                        "Force damage",
                        "When it hits with an attack roll and deals damage, it can deal Force damage or its normal type (your choice)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you take a Bonus Action to command your Primal Companion beast to take an action, you can also command it to take the Dash, Disengage, Dodge, or Help action using its Bonus Action.\n"
            "In addition, whenever it hits with an attack roll and deals damage, it can deal your choice of Force damage or its normal damage type."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class BestialFury(Feature):
    def __init__(self):
        super().__init__(
            name="Bestial Fury",
            origin="Beast Master Ranger Level 11",
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Beast's Strike",
                        "When you command it, the beast can use it twice",
                    ),
                    (
                        "Hunter's Mark",
                        "The first time each turn it hits a creature marked by your Hunter's Mark, it deals extra Force damage equal to the spell's bonus damage",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you command your Primal Companion beast to take the Beast's Strike action, the beast can use it twice.\n"
            "In addition, the first time each turn it hits a creature under the effect of your Hunter's Mark spell, the beast deals extra Force damage equal to the bonus damage of that spell."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class ShareSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Share Spells",
            origin="Beast Master Ranger Level 15",
            activation=FeatureActivation(range="30 Feet"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "You cast a spell targeting yourself"),
                    (
                        "Effect",
                        "The spell can also affect your Primal Companion beast",
                    ),
                    ("Range", "The beast is within 30 feet of you"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When you cast a spell targeting yourself, you can also affect your Primal Companion beast with the spell if the beast is within 30 feet of you."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY
