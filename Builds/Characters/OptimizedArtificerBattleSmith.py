import Definitions
from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.ArtificerBase import ArtificerLevel1, ArtificerLevel2, ArtificerLevel3
from CharacterConfigs.SubClasses.ArtificerBattleSmith import (
    ArtificerBattleSmithLevel3,
    ArtificerBattleSmithCustomStarterClassArgs,
)
from Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from Features.Equipment import Armor, Weapons
from SpeciesConfigs import Dwarf
from Spells import Definitions as SpellDefinitions
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import ArtificerSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=ArtificerBattleSmithCustomStarterClassArgs(
            skills=ArtificerSkillsStatBlock(
                proficiencies={
                    Skill.ARCANA: True,
                    Skill.HISTORY: True,
                    Skill.INSIGHT: False,
                    Skill.INVESTIGATION: False,
                    Skill.MEDICINE: False,
                    Skill.PERCEPTION: False,
                    Skill.SLEIGHT_OF_HAND: False,
                }
            ),
        ),
        base_class_level=3,
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
            Armor.ChainMailArmor(),
        ],
        weapons=[
            Weapons.Longsword(player_is_proficient=True, ability=Ability.INTELLIGENCE),
            Weapons.Dagger(player_is_proficient=True),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: ArtificerLevel1(
                    cantrip_1=SpellDefinitions.ArtificerLevel0Spells.FIRE_BOLT,
                    cantrip_2=SpellDefinitions.ArtificerLevel0Spells.MENDING,
                    spell_1=SpellDefinitions.ArtificerLevel1Spells.SHIELD,
                    spell_2=SpellDefinitions.ArtificerLevel1Spells.MAGIC_MISSILE,
                    spell_3=SpellDefinitions.ArtificerLevel1Spells.CURE_WOUNDS,
                    spell_4=SpellDefinitions.ArtificerLevel1Spells.IDENTIFY,
                ),
                2: ArtificerLevel2(
                    spell=SpellDefinitions.ArtificerLevel1Spells.THUNDERWAVE,
                ),
                3: ArtificerLevel3(
                    spell=SpellDefinitions.ArtificerLevel2Spells.MAGIC_WEAPON,
                ),
            },
            subclass_features_by_level={
                3: ArtificerBattleSmithLevel3(),
            },
        ),
    )


class OptimizedArtificerBattleSmithCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Optimized Battle Smith Artificer",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Dwarf.DwarfSpeciesBuilder(),
        )
