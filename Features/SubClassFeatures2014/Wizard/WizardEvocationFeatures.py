from Core.Definitions import WIZARD_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class EvocationSavant(Feature):
    def __init__(self):
        super().__init__(name="Evocation Savant", origin="Evocation Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The gold and time you must spend to copy an Evocation spell into your spellbook is halved."
        return description


class SculptSpells(Feature):
    def __init__(self):
        super().__init__(name="Sculpt Spells", origin="Evocation Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can create pockets of relative safety within the effects of your evocation spells. When you cast an evocation spell that affects other creatures that you can see, you can choose a number of them equal to 1 + the spell's level. The chosen creatures automatically succeed on their saving throws against the spell, and they take no damage if they would normally take half damage on a successful save."
        )
        return description


class PotentCantrip(Feature):
    def __init__(self):
        super().__init__(name="Potent Cantrip", origin="Evocation Wizard Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your damaging cantrips affect even creatures that avoid the brunt of the effect. When a creature succeeds on a saving throw against your cantrip, the creature takes half the cantrip's damage (if any) but suffers no additional effect from the cantrip."
        return description


class EmpoweredEvocation(Feature):
    def __init__(self):
        super().__init__(
            name="Empowered Evocation", origin="Evocation Wizard Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can add your Intelligence modifier (minimum of +1) to one damage roll of any wizard evocation spell that you cast."
        return description


class Overchannel(Feature):
    def __init__(self):
        super().__init__(name="Overchannel", origin="Evocation Wizard Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can increase the power of your simpler spells. When you cast a wizard spell of 1st through 5th level that deals damage, you can deal maximum damage with that spell.\n"
            "The first time you do so, you suffer no adverse effect. If you use this feature again before you finish a long rest, you take 2d12 necrotic damage for each level of the spell, immediately after you cast it. Each time you use this feature again before finishing a long rest, the necrotic damage per spell level increases by 1d12. This damage ignores resistance and immunity."
        )
        return description
