"""Example build: Artificer Alchemist (2014 rules). Demonstrates the subclass through level 17."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ArtificerBase import (
    ArtificerLevel1,
    ArtificerLevel2,
    ArtificerLevel3,
    ArtificerLevel4,
    ArtificerLevel5,
    ArtificerLevel6,
    ArtificerLevel7,
    ArtificerLevel8,
    ArtificerLevel9,
    ArtificerLevel10,
    ArtificerLevel11,
    ArtificerLevel12,
    ArtificerLevel13,
    ArtificerLevel14,
    ArtificerLevel15,
    ArtificerLevel16,
    ArtificerLevel17,
)
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.SubClasses2014.ArtificerAlchemist import (
    ArtificerAlchemistCustomStarterClassArgs,
    ArtificerAlchemistLevel3,
    ArtificerAlchemistLevel5,
    ArtificerAlchemistLevel9,
    ArtificerAlchemistLevel13,
    ArtificerAlchemistLevel15,
    ArtificerAlchemistLevel17,
)
from Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from Features.Equipment import Armor, Weapons
from SpeciesConfigs import Gnome
from Spells import SpellLists as SpellDefinitions
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import ArtificerSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=ArtificerAlchemistCustomStarterClassArgs(
            skills=ArtificerSkillsStatBlock(
                proficiencies={
                    Skill.ARCANA: True,
                    Skill.HISTORY: False,
                    Skill.NATURE: False,
                    Skill.INVESTIGATION: True,
                    Skill.MEDICINE: False,
                    Skill.PERCEPTION: False,
                    Skill.SLEIGHT_OF_HAND: False,
                }
            ),
        ),
        base_class_level=17,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=13,
            constitution=14,
            intelligence=15,
            wisdom=10,
            charisma=12,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.INTELLIGENCE, 2),
                (Ability.CONSTITUTION, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.MEDICINE,
                Skill.INVESTIGATION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Alert(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: ArtificerLevel1(
                    cantrip_1=SpellDefinitions.ArtificerLevel0Spells.FIRE_BOLT,
                    cantrip_2=SpellDefinitions.ArtificerLevel0Spells.GUIDANCE,
                    spell_1=SpellDefinitions.ArtificerLevel1Spells.CURE_WOUNDS,
                    spell_2=SpellDefinitions.ArtificerLevel1Spells.FAERIE_FIRE,
                ),
                2: ArtificerLevel2(
                    spell=SpellDefinitions.ArtificerLevel1Spells.IDENTIFY,
                ),
                3: ArtificerLevel3(
                    spell=SpellDefinitions.ArtificerLevel1Spells.TASHAS_CAUSTIC_BREW,
                ),
                4: ArtificerLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.INTELLIGENCE, 2),
                        ]
                    ),
                    spell=SpellDefinitions.ArtificerLevel1Spells.SNARE,
                ),
                5: ArtificerLevel5(
                    spell=SpellDefinitions.ArtificerLevel2Spells.LESSER_RESTORATION,
                ),
                6: ArtificerLevel6(),
                7: ArtificerLevel7(
                    spell=SpellDefinitions.ArtificerLevel2Spells.PROTECTION_FROM_POISON,
                ),
                8: ArtificerLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.INTELLIGENCE, 2),
                        ]
                    ),
                ),
                9: ArtificerLevel9(
                    spell_1=SpellDefinitions.ArtificerLevel3Spells.REVIVIFY,
                    spell_2=SpellDefinitions.ArtificerLevel3Spells.DISPEL_MAGIC,
                ),
                10: ArtificerLevel10(
                    cantrip=SpellDefinitions.ArtificerLevel0Spells.POISON_SPRAY,
                ),
                11: ArtificerLevel11(
                    spell=SpellDefinitions.ArtificerLevel3Spells.WATER_BREATHING,
                ),
                12: ArtificerLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.CONSTITUTION, 2),
                        ]
                    ),
                ),
                13: ArtificerLevel13(
                    spell=SpellDefinitions.ArtificerLevel4Spells.FREEDOM_OF_MOVEMENT,
                ),
                14: ArtificerLevel14(
                    cantrip=SpellDefinitions.ArtificerLevel0Spells.RESISTANCE,
                ),
                15: ArtificerLevel15(
                    spell=SpellDefinitions.ArtificerLevel4Spells.SUMMON_CONSTRUCT,
                ),
                16: ArtificerLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.CONSTITUTION, 2),
                        ]
                    ),
                ),
                17: ArtificerLevel17(
                    spell_1=SpellDefinitions.ArtificerLevel5Spells.GREATER_RESTORATION,
                    spell_2=SpellDefinitions.ArtificerLevel5Spells.CREATION,
                ),
            },
            subclass_features_by_level={
                3: ArtificerAlchemistLevel3(),
                5: ArtificerAlchemistLevel5(),
                9: ArtificerAlchemistLevel9(),
                13: ArtificerAlchemistLevel13(),
                15: ArtificerAlchemistLevel15(),
                17: ArtificerAlchemistLevel17(),
            },
        ),
    )


class ExampleArtificerAlchemist2014CharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Alchemist Artificer",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Gnome.RockGnomeSpeciesBuilder(),
        )
