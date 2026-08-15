from typing import Optional

from CharacterContent.Classes.BaseClasses.ClassBuilder import (
    AppliedLevelFeatures,
    MulticlassBuilder,
    StarterClassBuilder,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Builds.EquipmentHandler import Bought, EquipmentHandler
from CharacterContent.Items import Armor, Items, Weapons
from CharacterContent.Species.SpeciesBuilder import SpeciesBuilder


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
        self.equipment_handler = EquipmentHandler()
        self.equipment_handler.set_starting_equipment(
            base_class=starter_class_builder.base_class,
            default_equipment=starter_class_builder.default_equipment,
            add_default_equipment=starter_class_builder.add_default_equipment,
            default_pack=starter_class_builder.default_pack,
            armor=starter_class_builder.armor,
            weapons=starter_class_builder.weapons,
            items=starter_class_builder.items,
        )

    def add_adventuring_gear(
        self,
        label: str,
        armor: Optional[list[Armor.AbstractArmor | Bought]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon | Bought]] = None,
        items: Optional[list[tuple[Items.Item | Bought, int]]] = None,
    ) -> "CharacterBuilder":
        """Record gear earned after character creation (loot, purchases, ...)
        as its own labeled entry on the sheet, separate from Starting
        Equipment. Call as many times as needed, e.g. once per adventure.
        Items are found by default; wrap one in Bought(item) - or
        Bought(item, price=X) to override the amount paid - to mark it as
        purchased instead."""
        self.equipment_handler.add_adventuring_gear(
            label, armor=armor, weapons=weapons, items=items
        )
        return self

    def drop_item(
        self, item: Armor.AbstractArmor | Weapons.AbstractWeapon | Items.Item | type
    ) -> "CharacterBuilder":
        """Mark a previously-added item (starting gear or adventuring gear)
        as no longer carried: it stops applying mechanically and disappears
        from the sheet, while the code that added it stays in the build as a
        record of what the character used to have. Pass the exact object
        reference it was added with, or its class (e.g. Weapons.Dagger) to
        look it up by type - only works when exactly one instance of that
        class was added anywhere; get_starting_item() gives you an
        unambiguous reference to something from Starting Equipment
        specifically, or otherwise pass the specific instance instead."""
        self.equipment_handler.drop_item(item)
        return self

    def get_starting_item(
        self, item_type: type
    ) -> Armor.AbstractArmor | Weapons.AbstractWeapon | Items.Item:
        """Look up a single Starting Equipment item by class, e.g. to
        drop_item() it later even after adventuring gear adds more of the
        same type. Stays unambiguous no matter what's added afterward, since
        it only ever looks at Starting Equipment."""
        return self.equipment_handler.get_starting_item(item_type)

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
        character_sheet_data.is_example = type(self).__module__.startswith(
            "Builds.Examples"
        )

        # Equipment (starting gear plus everything since added/dropped via
        # self.equipment_handler) is folded in last, once the sheet's other
        # data - weapon proficiencies in particular, which add_weapon below
        # depends on - is fully assembled.
        character_sheet_data.equipment_entries = self.equipment_handler.equipment_entries
        character_sheet_data.starting_equipment_entry = (
            self.equipment_handler.starting_equipment_entry
        )
        character_sheet_data.starting_gold = self.equipment_handler.starting_gold
        for armor in self.equipment_handler.armors:
            character_sheet_data.add_armor(armor)
        for weapon in self.equipment_handler.weapons:
            character_sheet_data.add_weapon(weapon)
        for item, quantity in self.equipment_handler.items:
            character_sheet_data.add_item(item, quantity)

        # Return final character sheet data
        return character_sheet_data
