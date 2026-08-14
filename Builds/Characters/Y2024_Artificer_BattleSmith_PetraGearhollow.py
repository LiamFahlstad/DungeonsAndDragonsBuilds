from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ArtificerBase import (
    ArtificerLevel1,
    ArtificerLevel2,
    ArtificerLevel3,
)
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.SubClasses2024.ArtificerBattleSmith import (
    ArtificerBattleSmithCustomStarterClassArgs,
    ArtificerBattleSmithLevel3,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import Backgrounds, OriginFeats
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Species import Dwarf
from CharacterContent.Spells import SpellLists as SpellDefinitions
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import ArtificerSkillsStatBlock
from CharacterContent.ToolProficiencies.Proficiencies import (
    SmithsTools,
    ThievesTools,
    TinkersTools,
)


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
                    spell_1=SpellDefinitions.ArtificerLevel1Spells.FALSE_LIFE,
                    spell_2=SpellDefinitions.ArtificerLevel1Spells.CURE_WOUNDS,
                ),
                2: ArtificerLevel2(
                    spell=SpellDefinitions.ArtificerLevel1Spells.CATAPULT,
                ),
                3: ArtificerLevel3(
                    spell=SpellDefinitions.ArtificerLevel1Spells.TASHAS_CAUSTIC_BREW,
                ),
            },
            subclass_features_by_level={
                3: ArtificerBattleSmithLevel3(),
            },
        ),
        tool_proficiencies=[SmithsTools(), ThievesTools(), TinkersTools()],
    )


class Y2024ArtificerBattleSmithPetraGearhollowCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Petra Gearhollow",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Dwarf.DwarfSpeciesBuilder(),
        )
