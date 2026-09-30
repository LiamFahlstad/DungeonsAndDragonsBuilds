"""Armor, weapon, tool and saving throw proficiencies a class grants, plus its
skill proficiency choice.

The starting class grants its full Core Traits proficiencies (ClassProficiencies,
built from the class builder's arguments) and its two saving throws. A class
gained later by multiclassing grants only part of its proficiencies
(MulticlassProficiencies) and no saving throws, per each class's "As a
Multiclass Character" entry in SourceTexts/ClassTexts/<class>.txt.

CLASS_SKILL_CHOICES and the saving-throw table below are the class-invariant
facts every build draws on: which skills a class may choose from, how many,
and which two abilities it saves with. ClassSkillChoice is the feature that
records a build's actual pick from that pool, validated the way the
background skill choice is (CharacterContent.Features.CharacterFeats.Backgrounds).

All of these are bookkeeping features: they record grants on the stat block
and have no card of their own - the sheet lists proficiencies and saving
throws in its own sections.
"""

from Core.Definitions import Ability, ArmorType, CharacterClass, Skill
from CharacterContent.Features.Core.BaseFeatures import Feature
from CharacterContent.Features.Core.Improvements import (
    GrantArmorTraining,
    GrantToolProficiency,
    GrantWeaponProficiency,
    SavingThrowProficiency,
    SkillProficiencyChoice,
)
from CharacterContent.Items.Weapons import WeaponProficiency
from CharacterContent.ToolProficiencies import Proficiencies as Tools
from Model.Character import Character
from Model.Effects import Effects

# Every class's two saving throw proficiencies, granted by ClassProficiencies
# only for the starting class (multiclassing grants none - PHB "Multiclassing").
_CLASS_SAVING_THROWS: dict[CharacterClass, tuple[Ability, Ability]] = {
    CharacterClass.ARTIFICER: (Ability.CONSTITUTION, Ability.INTELLIGENCE),
    CharacterClass.BARBARIAN: (Ability.STRENGTH, Ability.CONSTITUTION),
    CharacterClass.BARD: (Ability.DEXTERITY, Ability.CHARISMA),
    CharacterClass.CLERIC: (Ability.WISDOM, Ability.CHARISMA),
    CharacterClass.DRUID: (Ability.WISDOM, Ability.INTELLIGENCE),
    CharacterClass.FIGHTER: (Ability.STRENGTH, Ability.CONSTITUTION),
    CharacterClass.MONK: (Ability.STRENGTH, Ability.DEXTERITY),
    CharacterClass.PALADIN: (Ability.WISDOM, Ability.CHARISMA),
    CharacterClass.RANGER: (Ability.STRENGTH, Ability.DEXTERITY),
    CharacterClass.ROGUE: (Ability.DEXTERITY, Ability.INTELLIGENCE),
    CharacterClass.SORCERER: (Ability.CONSTITUTION, Ability.CHARISMA),
    CharacterClass.WARLOCK: (Ability.WISDOM, Ability.CHARISMA),
    CharacterClass.WIZARD: (Ability.WISDOM, Ability.INTELLIGENCE),
}

# Every class's skill proficiency choice: the pool it may pick from, and how
# many picks it gets. Read by ClassBuilder.StarterClassBuilder to build this
# build's ClassSkillChoice, and by the Character Creator's Registry to drive
# the skill picker UI/codegen.
CLASS_SKILL_CHOICES: dict[CharacterClass, tuple[list[Skill], int]] = {
    CharacterClass.ARTIFICER: (
        [
            Skill.ARCANA,
            Skill.HISTORY,
            Skill.INVESTIGATION,
            Skill.MEDICINE,
            Skill.NATURE,
            Skill.PERCEPTION,
            Skill.SLEIGHT_OF_HAND,
        ],
        2,
    ),
    CharacterClass.BARBARIAN: (
        [
            Skill.ANIMAL_HANDLING,
            Skill.ATHLETICS,
            Skill.INTIMIDATION,
            Skill.NATURE,
            Skill.PERCEPTION,
            Skill.SURVIVAL,
        ],
        2,
    ),
    CharacterClass.BARD: (list(Skill), 3),
    CharacterClass.CLERIC: (
        [
            Skill.HISTORY,
            Skill.INSIGHT,
            Skill.MEDICINE,
            Skill.PERSUASION,
            Skill.RELIGION,
        ],
        2,
    ),
    CharacterClass.DRUID: (
        [
            Skill.ARCANA,
            Skill.ANIMAL_HANDLING,
            Skill.INSIGHT,
            Skill.MEDICINE,
            Skill.NATURE,
            Skill.PERCEPTION,
            Skill.RELIGION,
            Skill.SURVIVAL,
        ],
        2,
    ),
    CharacterClass.FIGHTER: (
        [
            Skill.ACROBATICS,
            Skill.ANIMAL_HANDLING,
            Skill.ATHLETICS,
            Skill.HISTORY,
            Skill.INSIGHT,
            Skill.INTIMIDATION,
            Skill.PERSUASION,
            Skill.PERCEPTION,
            Skill.SURVIVAL,
        ],
        2,
    ),
    CharacterClass.MONK: (
        [
            Skill.ACROBATICS,
            Skill.ATHLETICS,
            Skill.HISTORY,
            Skill.INSIGHT,
            Skill.RELIGION,
            Skill.STEALTH,
        ],
        2,
    ),
    CharacterClass.PALADIN: (
        [
            Skill.ATHLETICS,
            Skill.INSIGHT,
            Skill.INTIMIDATION,
            Skill.MEDICINE,
            Skill.PERSUASION,
            Skill.RELIGION,
        ],
        2,
    ),
    CharacterClass.RANGER: (
        [
            Skill.ANIMAL_HANDLING,
            Skill.ATHLETICS,
            Skill.INSIGHT,
            Skill.INVESTIGATION,
            Skill.NATURE,
            Skill.PERCEPTION,
            Skill.STEALTH,
            Skill.SURVIVAL,
        ],
        3,
    ),
    CharacterClass.ROGUE: (
        [
            Skill.ACROBATICS,
            Skill.ATHLETICS,
            Skill.DECEPTION,
            Skill.INSIGHT,
            Skill.INTIMIDATION,
            Skill.INVESTIGATION,
            Skill.PERCEPTION,
            Skill.PERSUASION,
            Skill.SLEIGHT_OF_HAND,
            Skill.STEALTH,
        ],
        4,
    ),
    CharacterClass.SORCERER: (
        [
            Skill.ARCANA,
            Skill.DECEPTION,
            Skill.INSIGHT,
            Skill.INTIMIDATION,
            Skill.PERSUASION,
            Skill.RELIGION,
        ],
        2,
    ),
    CharacterClass.WARLOCK: (
        [
            Skill.ARCANA,
            Skill.DECEPTION,
            Skill.HISTORY,
            Skill.INTIMIDATION,
            Skill.INVESTIGATION,
            Skill.NATURE,
            Skill.RELIGION,
        ],
        2,
    ),
    CharacterClass.WIZARD: (
        [
            Skill.ARCANA,
            Skill.HISTORY,
            Skill.INSIGHT,
            Skill.INVESTIGATION,
            Skill.MEDICINE,
            Skill.NATURE,
            Skill.RELIGION,
        ],
        2,
    ),
}


class ClassProficiencies(Feature):
    def __init__(
        self,
        character_class: CharacterClass,
        armor: list[ArmorType],
        weapons: list[WeaponProficiency],
        tools: list[Tools.ToolProficiency],
        name: str = "Proficiencies",
        grant_saving_throws: bool = True,
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
        if grant_saving_throws:
            saving_throws = _CLASS_SAVING_THROWS.get(character_class)
            if saving_throws is not None:
                self._grants.append(SavingThrowProficiency(list(saving_throws)))

    def apply(self, effects: Effects):
        for grant in self._grants:
            grant.apply(effects)


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
            grant_saving_throws=False,
        )


class ClassSkillChoice(Feature):
    """The starting class's skill proficiency choice (e.g. the Paladin picks
    2 of Athletics, Insight, Intimidation, Medicine, Persuasion, Religion -
    CLASS_SKILL_CHOICES above). Validated the way the background skill choice
    is (Backgrounds.FreeBackgroundSkillProficiency): `chosen` must be exactly
    `count` skills, all drawn from `pool`.

    Bookkeeping only, like ClassProficiencies: no card of its own, and
    skippable_in_concise so a concise/table sheet never shows it either."""

    def __init__(self, pool: list[Skill], count: int, chosen: list[Skill]):
        self._choice = SkillProficiencyChoice(
            chosen, pool, count, error_prefix="Class skill choice"
        )
        super().__init__(
            name="Class Skill Proficiencies",
            skippable_in_concise=True,
        )

    def apply(self, effects: Effects):
        self._choice.apply(effects)
