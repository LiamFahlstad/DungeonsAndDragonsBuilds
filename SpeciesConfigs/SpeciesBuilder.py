from abc import abstractmethod

import Definitions
from CharacterSheetCreator import CharacterSheetData
from Features import OriginFeats


class SpeciesBuilder:
    def __init__(
        self,
        name: str,
    ):
        self.name = name

    @abstractmethod
    def build(self) -> CharacterSheetData:
        pass

    def add_origin_feat(
        self, data: CharacterSheetData, origin_feat: OriginFeats.OriginFeat
    ):
        data.add_origin_feat(origin_feat)

    def set_spell_casting_ability(self, ability: Definitions.Ability):
        self.spell_casting_ability = ability

    def set_character_level(self, level: int):
        self.character_level = level
