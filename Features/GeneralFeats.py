from CharacterStatBlock import CharacterStatBlock
from Definitions import Ability
from Features.BaseFeatures import CharacterFeature


class GeneralFeat(CharacterFeature):
    pass


class AbilityScoreImprovement(GeneralFeat):
    """Also add either [+1, +1] OR [+2] to any abilities."""

    def __init__(self, bonuses: list[tuple[Ability, int]]):
        self.bonuses = bonuses
        # Validate
        if not (sum([bonus[1] for bonus in self.bonuses]) == 2):
            raise ValueError("Bonuses must sum to 2.")

    def modify(self, character_stat_block: CharacterStatBlock):
        for ability, bonus in self.bonuses:
            character_stat_block.abilities.add_bonus(ability, bonus)
