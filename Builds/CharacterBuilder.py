from typing import Optional

from CharacterContent.Classes.BaseClasses.ClassBuilder import (
    AppliedLevelFeatures,
    MulticlassBuilder,
    StarterClassBuilder,
)
from Model.Character import Character
from Model.CharacterSources import CharacterSources
from Builds.StartingEquipment import set_starting_equipment
from Model.Inventory import Bought, Inventory
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
        self.inventory = Inventory()
        set_starting_equipment(
            self.inventory,
            base_class=starter_class_builder.base_class,
            default_equipment=starter_class_builder.non_generic_arguments.default_equipment,
            add_default_equipment=starter_class_builder.add_default_equipment,
            default_pack=starter_class_builder.non_generic_arguments.default_pack,
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
        gold: float = 0,
    ) -> "CharacterBuilder":
        """Record gear earned after character creation (loot, purchases, ...)
        as its own labeled entry on the sheet, separate from Starting
        Equipment. Call as many times as needed, e.g. once per adventure.
        Items are found by default; wrap one in Bought(item) - or
        Bought(item, price=X) to override the amount paid - to mark it as
        purchased instead. Pass gold=X for a net GP change from this entry
        that isn't tied to a specific item (loot found, a cost paid) -
        positive gains, negative spends."""
        self.inventory.add_adventuring_gear(
            label, armor=armor, weapons=weapons, items=items, gold=gold
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
        self.inventory.drop_item(item)
        return self

    def consume_item(self, item_type: type, quantity: int = 1) -> "CharacterBuilder":
        """Reduce a stackable item's quantity (use 1 of 5 potions, fire 3 of
        20 arrows) instead of dropping the whole stack. See
        Inventory.consume_item()."""
        self.inventory.consume_item(item_type, quantity)
        return self

    def get_starting_item(
        self, item_type: type
    ) -> Armor.AbstractArmor | Weapons.AbstractWeapon | Items.Item:
        """Look up a single Starting Equipment item by class, e.g. to
        drop_item() it later even after adventuring gear adds more of the
        same type. Stays unambiguous no matter what's added afterward, since
        it only ever looks at Starting Equipment."""
        return self.inventory.get_starting_item(item_type)

    def build(self) -> Character:
        # Every builder (starting class, multiclasses, species) grants
        # into these one set of sources; the Character is made from them
        # at the end.
        character_sheet_data = CharacterSources()
        applied_level_features = AppliedLevelFeatures()

        character_sheet_data = self.starter_class_builder.create(
            character_sheet_data, applied_level_features
        )

        for multiclass_builder in self.multiclass_builders:
            character_sheet_data = multiclass_builder.create(
                character_sheet_data, applied_level_features
            )

        abilities = character_sheet_data.base_abilities
        if abilities is None:
            raise ValueError("AbilityScores is None.")
        ability_with_highest_modifier = (
            abilities.get_spell_casting_ability_with_highest_modifier()
        )
        # A spellcasting class states its own ability (Paladin: Charisma, ...);
        # only a character with no class spellcasting falls back to their best
        # mental score (e.g. for species/feat spells).
        if character_sheet_data.spell_casting_ability is None:
            character_sheet_data.spell_casting_ability = ability_with_highest_modifier

        self.species_builder.build(character_sheet_data, ability_with_highest_modifier)

        character_sheet_data.character_name = self.name
        character_sheet_data.is_example = type(self).__module__.startswith(
            "Builds.Examples"
        )

        # Equipment: starting gear plus everything since added/dropped via
        # self.inventory. A copy, so gear added to or dropped from either one
        # later never changes the other. (Weapon proficiency is worked out on
        # read, so the order this happens in doesn't matter.)
        character_sheet_data.inventory = self.inventory.copy()

        return Character(character_sheet_data)
