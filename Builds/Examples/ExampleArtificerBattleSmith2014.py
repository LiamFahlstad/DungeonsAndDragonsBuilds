"""Example build: Artificer Battle Smith (2014 rules). Demonstrates the subclass through level 17."""

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
from CharacterConfigs.SubClasses2014.ArtificerBattleSmith import (
    ArtificerBattleSmithCustomStarterClassArgs,
    ArtificerBattleSmithLevel3,
    ArtificerBattleSmithLevel5,
    ArtificerBattleSmithLevel9,
    ArtificerBattleSmithLevel13,
    ArtificerBattleSmithLevel15,
    ArtificerBattleSmithLevel17,
)
from Core.Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from Features.Equipment import Armor, Weapons
from SpeciesConfigs import Dwarf
from Spells import SpellLists as SpellDefinitions
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import ArtificerSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=ArtificerBattleSmithCustomStarterClassArgs(
            skills=ArtificerSkillsStatBlock(
                proficiencies={
                    Skill.ARCANA: True,
                    Skill.HISTORY: True,
                    Skill.NATURE: False,
                    Skill.INVESTIGATION: False,
                    Skill.MEDICINE: False,
                    Skill.PERCEPTION: False,
                    Skill.SLEIGHT_OF_HAND: False,
                }
            ),
        ),
        base_class_level=17,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=14,
            dexterity=12,
            constitution=15,
            intelligence=13,
            wisdom=10,
            charisma=8,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.INTELLIGENCE, 2),
                (Ability.STRENGTH, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.INVESTIGATION,
                Skill.PERCEPTION,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Alert(),
        armor=[
            Armor.StuddedLeatherArmor(),
            Armor.ShieldArmor(),
        ],
        weapons=[
            Weapons.Longsword(player_is_proficient=True, ability=Ability.INTELLIGENCE),
            Weapons.Dagger(),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: ArtificerLevel1(
                    cantrip_1=SpellDefinitions.ArtificerLevel0Spells.FIRE_BOLT,
                    cantrip_2=SpellDefinitions.ArtificerLevel0Spells.GUIDANCE,
                    spell_1=SpellDefinitions.ArtificerLevel1Spells.FAERIE_FIRE,
                    spell_2=SpellDefinitions.ArtificerLevel1Spells.CURE_WOUNDS,
                ),
                2: ArtificerLevel2(
                    spell=SpellDefinitions.ArtificerLevel1Spells.CATAPULT,
                ),
                3: ArtificerLevel3(
                    spell=SpellDefinitions.ArtificerLevel1Spells.TASHAS_CAUSTIC_BREW,
                ),
                4: ArtificerLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.STRENGTH, 2),
                        ]),
                    spell=SpellDefinitions.ArtificerLevel1Spells.SANCTUARY,
                ),
                5: ArtificerLevel5(
                    spell=SpellDefinitions.ArtificerLevel2Spells.MAGIC_WEAPON,
                ),
                6: ArtificerLevel6(),
                7: ArtificerLevel7(
                    spell=SpellDefinitions.ArtificerLevel2Spells.ENHANCE_ABILITY,
                ),
                8: ArtificerLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.INTELLIGENCE, 2),
                        ]),
                ),
                9: ArtificerLevel9(
                    spell_1=SpellDefinitions.ArtificerLevel3Spells.REVIVIFY,
                    spell_2=SpellDefinitions.ArtificerLevel3Spells.HASTE,
                ),
                10: ArtificerLevel10(
                    cantrip=SpellDefinitions.ArtificerLevel0Spells.RESISTANCE,
                ),
                11: ArtificerLevel11(
                    spell=SpellDefinitions.ArtificerLevel3Spells.PROTECTION_FROM_ENERGY,
                ),
                12: ArtificerLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.CONSTITUTION, 2),
                        ]),
                ),
                13: ArtificerLevel13(
                    spell=SpellDefinitions.ArtificerLevel4Spells.FREEDOM_OF_MOVEMENT,
                ),
                14: ArtificerLevel14(
                    cantrip=SpellDefinitions.ArtificerLevel0Spells.THUNDERCLAP,
                ),
                15: ArtificerLevel15(
                    spell=SpellDefinitions.ArtificerLevel4Spells.STONESKIN,
                ),
                16: ArtificerLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.STRENGTH, 2),
                        ]),
                ),
                17: ArtificerLevel17(
                    spell_1=SpellDefinitions.ArtificerLevel5Spells.GREATER_RESTORATION,
                    spell_2=SpellDefinitions.ArtificerLevel5Spells.CIRCLE_OF_POWER,
                ),
            },
            subclass_features_by_level={
                3: ArtificerBattleSmithLevel3(),
                5: ArtificerBattleSmithLevel5(),
                9: ArtificerBattleSmithLevel9(),
                13: ArtificerBattleSmithLevel13(),
                15: ArtificerBattleSmithLevel15(),
                17: ArtificerBattleSmithLevel17(),
            },
        ),
    )


class ExampleArtificerBattleSmith2014CharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Battle Smith Artificer",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Dwarf.DwarfSpeciesBuilder(),
        )
