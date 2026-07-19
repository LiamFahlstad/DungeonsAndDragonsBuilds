from typing import Optional

from CharacterConfigs.BaseClasses.ClassBuilder import (
    AppliedLevelFeatures,
    MulticlassBuilder,
    StarterClassBuilder,
)
from CharacterSheetCreator import CharacterSheetData
from SpeciesConfigs.SpeciesBuilder import SpeciesBuilder


class CharacterBuilder:
    def __init__(
        self,
        name: str,
        starter_class_builder: StarterClassBuilder,
        species_builder: SpeciesBuilder,
        multiclass_builders: Optional[list[MulticlassBuilder]] = None,
    ):
        self.name = name
        self.starter_class_builder = starter_class_builder
        self.species_builder = species_builder
        self.multiclass_builders = multiclass_builders or []

    def build(self) -> CharacterSheetData:
        character_sheet_data = CharacterSheetData()
        applied_level_features = AppliedLevelFeatures()

        character_sheet_data = self.starter_class_builder.create(
            character_sheet_data, applied_level_features
        )

        for multiclass_builder in self.multiclass_builders:
            character_sheet_data = multiclass_builder.create(
                character_sheet_data, applied_level_features
            )

        # Set spellcasting ability
        abilities = character_sheet_data.abilities
        if abilities is None:
            raise ValueError("AbilitiesStatBlock is None.")
        ability_with_highest_modifier = (
            abilities.get_spell_casting_ability_with_highest_modifier()
        )
        character_sheet_data.spell_casting_ability = ability_with_highest_modifier

        # Get species data
        self.species_builder.set_character_level(character_sheet_data.character_level)
        self.species_builder.set_spell_casting_ability(ability_with_highest_modifier)
        character_sheet_data.merge_with(self.species_builder.build())

        # Set character name
        character_sheet_data.character_name = self.name

        # Return final character sheet data
        return character_sheet_data
