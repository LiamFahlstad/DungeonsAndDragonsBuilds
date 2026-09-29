"""Armor, weapon and tool proficiencies a class grants.

The starting class grants its full Core Traits proficiencies (ClassProficiencies,
built from the class builder's arguments). A class gained later by
multiclassing grants only part of them (MulticlassProficiencies), per each
class's "As a Multiclass Character" entry in SourceTexts/ClassTexts/<class>.txt.

Both are bookkeeping features: they record grants on the stat block and have
no card of their own - the sheet lists the proficiencies in its proficiency
section.
"""

from CharacterContent.Features.Core.BaseFeatures import Feature
from CharacterContent.Features.Core.Improvements import (
    GrantArmorTraining,
    GrantToolProficiency,
    GrantWeaponProficiency,
)
from CharacterContent.Items.Weapons import WeaponProficiency
from CharacterContent.ToolProficiencies import Proficiencies as Tools
from Core.Definitions import ArmorType, CharacterClass
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class ClassProficiencies(Feature):
    def __init__(
        self,
        character_class: CharacterClass,
        armor: list[ArmorType],
        weapons: list[WeaponProficiency],
        tools: list[Tools.ToolProficiency],
        name: str = "Proficiencies",
    ):
        super().__init__(
            name=f"{character_class.value} {name}",
            origin=f"{character_class.value} Level 1",
            skippable_in_concise=True,
        )
        self.character_class = character_class
        self._grants = [
            GrantArmorTraining(armor),
            GrantWeaponProficiency(weapons),
            GrantToolProficiency(tools),
        ]

    def apply(self, character_stat_block: CharacterStatBlock):
        for grant in self._grants:
            grant.apply(character_stat_block)


# Fixed multiclass grants. The skill (Artificer, Bard, Ranger, Rogue) and
# Musical Instrument (Bard) choices from the same entries aren't modelled.
_MULTICLASS_PROFICIENCIES: dict[
    CharacterClass,
    tuple[list[ArmorType], list[WeaponProficiency], list[type[Tools.ToolProficiency]]],
] = {
    CharacterClass.ARTIFICER: (
        [ArmorType.LIGHT, ArmorType.MEDIUM, ArmorType.SHIELD],
        [],
        [Tools.TinkersTools],
    ),
    CharacterClass.BARBARIAN: ([ArmorType.SHIELD], [WeaponProficiency.MARTIAL], []),
    CharacterClass.BARD: ([ArmorType.LIGHT], [], []),
    CharacterClass.CLERIC: (
        [ArmorType.LIGHT, ArmorType.MEDIUM, ArmorType.SHIELD],
        [],
        [],
    ),
    CharacterClass.DRUID: ([ArmorType.LIGHT, ArmorType.SHIELD], [], []),
    CharacterClass.FIGHTER: (
        [ArmorType.LIGHT, ArmorType.MEDIUM, ArmorType.SHIELD],
        [WeaponProficiency.MARTIAL],
        [],
    ),
    CharacterClass.MONK: ([], [], []),
    CharacterClass.PALADIN: (
        [ArmorType.LIGHT, ArmorType.MEDIUM, ArmorType.SHIELD],
        [WeaponProficiency.MARTIAL],
        [],
    ),
    CharacterClass.RANGER: (
        [ArmorType.LIGHT, ArmorType.MEDIUM, ArmorType.SHIELD],
        [WeaponProficiency.MARTIAL],
        [],
    ),
    CharacterClass.ROGUE: ([ArmorType.LIGHT], [], [Tools.ThievesTools]),
    CharacterClass.SORCERER: ([], [], []),
    CharacterClass.WARLOCK: ([ArmorType.LIGHT], [], []),
    CharacterClass.WIZARD: ([], [], []),
}


class MulticlassProficiencies(ClassProficiencies):
    """What a class grants when it isn't the character's first class."""

    def __init__(self, character_class: CharacterClass):
        armor, weapons, tools = _MULTICLASS_PROFICIENCIES[character_class]
        super().__init__(
            character_class,
            armor,
            weapons,
            [tool() for tool in tools],
            name="Multiclass Proficiencies",
        )
