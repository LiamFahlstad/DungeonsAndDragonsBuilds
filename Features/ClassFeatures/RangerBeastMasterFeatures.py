from typing import Optional

from Definitions import DamageType
from Features.ClassFeatures import PrimalCompanions
from Features.ClassFeatures.PrimalCompanions import CompanionType
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

RANGER_HIT_DIE = 10


class PrimalCompanion(Feature):
    def __init__(self, companion_type: CompanionType, damage_type: Optional[DamageType] = None):
        self.companion_type = companion_type
        self.damage_type = damage_type
        super().__init__(name="Primal Companion", origin="Beast Master Ranger Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You magically summon a primal beast, which draws strength from your bond with nature. Choose its stat block: Beast of the Land, Beast of the Sea or Beast of the Sky. You also determine the kind of animal it is, choosing a kind appropriate for the stat block. Whatever beast you choose, it bears primal markings indicating its supernatural origin.\n"
            "    * The Beast in Combat: In Combat, the beast acts during your turn. It can move and use its Reaction on its own, but the only action it takes is the Dodge action unless you take a Bonus Action to command it to take an action in its stat block or some other action. You can also sacrifice one of your attacks when you take the Attack action to command the beast to take the Beast's Strike action. If you have the Incapacitated condition, the beast acts on its own and isn't limited to the dodge action.\n"
            "    * Restoring or Replacing the Beast: If the beast has died within the last hour, you can take a Magic action to touch it and expend a spell slot. The beast returns to life after 1 minute with all its Hit Points restored.\n"
            "   Whenever you finish a Long Rest, you can summon a different primal beast, which appears in an unoccupied space within 5 feet of you. You choose its stat block and appearance. If you already have a beast from this feature, the old one vanishes when the new one appears.\n"
            "\nAll three Beast stat blocks are below so you can switch on a Long Rest without regenerating this sheet:\n"
            + PrimalCompanions.format_all_primal_companions(
                character_stat_block, self.companion_type, self.damage_type
            )
        )
        return description


class ExceptionalTraining(Feature):
    def __init__(self):
        super().__init__(
            name="Exceptional Training", origin="Beast Master Ranger Level 7"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you take a Bonus Action to command your Primal Companion beast to take an action, you can also command it to take the Dash, Disengage, Dodge, or Help action using its Bonus Action.\n"
            "In addition, whenever it hits with an attack roll and deals damage, it can deal your choice of Force damage or its normal damage type."
        )
        return description


class BestialFury(Feature):
    def __init__(self):
        super().__init__(name="Bestial Fury", origin="Beast Master Ranger Level 11")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you command your Primal Companion beast to take the Beast's Strike action, the beast can use it twice.\n"
            "In addition, the first time each turn it hits a creature under the effect of your Hunter's Mark spell, the beast deals extra Force damage equal to the bonus damage of that spell."
        )
        return description


class ShareSpells(Feature):
    def __init__(self):
        super().__init__(name="Share Spells", origin="Beast Master Ranger Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you cast a spell targeting yourself, you can also affect your Primal Companion beast with the spell if the beast is within 30 feet of you."
        return description
