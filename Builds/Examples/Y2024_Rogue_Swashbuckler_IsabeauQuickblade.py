"""Example build: Rogue Swashbuckler. A Charisma-leaning rapier duelist taken to
level 17 so every Swashbuckler feature (Fancy Footwork, Rakish Audacity,
Panache, Dashing Strikes, Master Duelist) shows up on the sheet."""

import Core.Definitions as Definitions
from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.RogueBase import (
    RogueLevel1,
    RogueLevel2,
    RogueLevel3,
    RogueLevel4,
    RogueLevel5,
    RogueLevel6,
    RogueLevel7,
    RogueLevel8,
    RogueLevel9,
    RogueLevel10,
    RogueLevel11,
    RogueLevel12,
    RogueLevel13,
    RogueLevel14,
    RogueLevel15,
    RogueLevel16,
    RogueLevel17,
)
from CharacterContent.Classes.SubClasses2024.RogueSwashbuckler import (
    RogueSwashbucklerCustomStarterClassArgs,
    RogueSwashbucklerLevel3,
    RogueSwashbucklerLevel9,
    RogueSwashbucklerLevel13,
    RogueSwashbucklerLevel17,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import (
    Backgrounds,
    GeneralFeats,
    OriginFeats,
)
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Items import Items
from CharacterContent.ToolProficiencies.Proficiencies import (
    ThievesTools as ThievesToolsProficiency,
)
from CharacterContent.Species import Elf
from Model.AbilityScores import StandardArrayAbilityScores


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=RogueSwashbucklerCustomStarterClassArgs(
            skills=[
                Skill.ACROBATICS,
                Skill.INSIGHT,
                Skill.PERSUASION,
                Skill.STEALTH,
            ],
        ),
        base_class_level=17,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilityScores(
            strength=8,
            dexterity=15,
            constitution=13,
            intelligence=10,
            wisdom=12,
            charisma=14,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.DEXTERITY, 2),
                (Ability.CHARISMA, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.ATHLETICS,
                Skill.PERFORMANCE,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Alert(),
        armor=[
            Armor.StuddedLeatherArmor(),
        ],
        weapons=[
            Weapons.Rapier(),
            Weapons.Dagger(),
        ],
        items=[
            (Items.ThievesTools(), 1),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: RogueLevel1(
                    skill_expertise_1=Definitions.Skill.PERSUASION,
                    skill_expertise_2=Definitions.Skill.ACROBATICS,
                    weapon_mastery_1=Weapons.Rapier(),
                    weapon_mastery_2=Weapons.Dagger(),
                ),
                2: RogueLevel2(),
                3: RogueLevel3(),
                4: RogueLevel4(
                    general_feat=GeneralFeats.DualWielder(
                        character_level=4, ability=Ability.DEXTERITY
                    ),
                ),
                5: RogueLevel5(),
                6: RogueLevel6(
                    skill_expertise_1=Definitions.Skill.STEALTH,
                    skill_expertise_2=Definitions.Skill.PERCEPTION,
                ),
                7: RogueLevel7(),
                8: RogueLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.DEXTERITY, 2),
                        ]
                    ),
                ),
                9: RogueLevel9(),
                10: RogueLevel10(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CHARISMA, 1),
                            (Ability.CONSTITUTION, 1),
                        ]
                    ),
                ),
                11: RogueLevel11(),
                12: RogueLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CHARISMA, 2),
                        ]
                    ),
                ),
                13: RogueLevel13(),
                14: RogueLevel14(),
                15: RogueLevel15(),
                16: RogueLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CHARISMA, 1),
                            (Ability.CONSTITUTION, 1),
                        ]
                    ),
                ),
                17: RogueLevel17(),
            },
            subclass_features_by_level={
                3: RogueSwashbucklerLevel3(),
                9: RogueSwashbucklerLevel9(),
                13: RogueSwashbucklerLevel13(),
                17: RogueSwashbucklerLevel17(),
            },
        ),
        tool_proficiencies=[
            ThievesToolsProficiency(),
        ],
    )


class Y2024RogueSwashbucklerIsabeauQuickbladeCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Isabeau Quickblade",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Elf.ElfSpeciesBuilder(
                elven_lineage=Elf.ElvenLineage.WOOD_ELF,
                skill_proficiency=Definitions.Skill.PERCEPTION,
            ),
        )
