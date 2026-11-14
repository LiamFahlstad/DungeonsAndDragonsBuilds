"""Example build: Ranger Demon Hunter (Havoc). A dual-wielding Wisdom-fuelled glaive fighter, built to Ranger 20 to demonstrate every subclass feature."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.RangerBase import (
    RangerLevel1,
    RangerLevel2,
    RangerLevel3,
    RangerLevel4,
    RangerLevel5,
    RangerLevel6,
    RangerLevel7,
    RangerLevel8,
    RangerLevel9,
    RangerLevel10,
    RangerLevel11,
    RangerLevel12,
    RangerLevel13,
    RangerLevel14,
    RangerLevel15,
    RangerLevel16,
    RangerLevel17,
    RangerLevel18,
    RangerLevel19,
    RangerLevel20,
)
from CharacterContent.Classes.SubClasses2024.RangerDemonHunter import (
    RangerDemonHunterCustomStarterClassArgs,
    RangerDemonHunterLevel3,
    RangerDemonHunterLevel5,
    RangerDemonHunterLevel7,
    RangerDemonHunterLevel9,
    RangerDemonHunterLevel11,
    RangerDemonHunterLevel13,
    RangerDemonHunterLevel15,
    RangerDemonHunterLevel17,
    RangerDemonHunterLevel18,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import (
    Backgrounds,
    EpicBoon,
    GeneralFeats,
    OriginFeats,
)
from CharacterContent.Features.CombatFeatures import FightingStyles
from CharacterContent.Features.SubClassFeatures.Ranger.RangerDemonHunterFeatures import (
    DemonHunterSpecialization,
)
from CharacterContent.Items import Weapons
from CharacterContent.Species import Elf
from CharacterContent.Spells.SpellLists import (
    RangerLevel1Spells,
    RangerLevel2Spells,
    RangerLevel3Spells,
    RangerLevel4Spells,
    RangerLevel5Spells,
)
from Model.AbilityScores import StandardArrayAbilityScores


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=RangerDemonHunterCustomStarterClassArgs(
            skills=[
                Skill.ATHLETICS,
                Skill.PERCEPTION,
                Skill.STEALTH,
            ],
        ),
        base_class_level=20,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilityScores(
            strength=10,
            dexterity=15,
            constitution=13,
            intelligence=8,
            wisdom=14,
            charisma=12,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.DEXTERITY, 2),
                (Ability.WISDOM, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.INTIMIDATION,
                Skill.SURVIVAL,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Alert(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: RangerLevel1(
                    weapon_mastery_1=Weapons.Scimitar(),
                    weapon_mastery_2=Weapons.Shortsword(),
                    spell_1=RangerLevel1Spells.ENSNARING_STRIKE,
                    spell_2=RangerLevel1Spells.CURE_WOUNDS,
                ),
                2: RangerLevel2(
                    skill_expertise=Skill.PERCEPTION,
                    fighting_style=FightingStyles.TwoWeaponFighting(),
                    spell=RangerLevel1Spells.FOG_CLOUD,
                ),
                3: RangerLevel3(
                    spell=RangerLevel1Spells.ENTANGLE,
                ),
                4: RangerLevel4(
                    general_feat=GeneralFeats.DualWielder(
                        character_level=4, ability=Ability.DEXTERITY
                    ),
                    spell=RangerLevel1Spells.GOODBERRY,
                ),
                5: RangerLevel5(
                    spell=RangerLevel2Spells.PASS_WITHOUT_TRACE,
                ),
                6: RangerLevel6(),
                7: RangerLevel7(
                    spell=RangerLevel2Spells.SPIKE_GROWTH,
                ),
                8: RangerLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 2),
                        ]
                    ),
                ),
                9: RangerLevel9(
                    skill_expertise_1=Skill.STEALTH,
                    skill_expertise_2=Skill.SURVIVAL,
                    spell_1=RangerLevel3Spells.CONJURE_ANIMALS,
                    spell_2=RangerLevel2Spells.LESSER_RESTORATION,
                ),
                10: RangerLevel10(),
                11: RangerLevel11(
                    spell=RangerLevel3Spells.DISPEL_MAGIC,
                ),
                12: RangerLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.DEXTERITY, 2),
                        ]
                    ),
                ),
                13: RangerLevel13(
                    spell=RangerLevel4Spells.FREEDOM_OF_MOVEMENT,
                ),
                14: RangerLevel14(),
                15: RangerLevel15(
                    spell=RangerLevel4Spells.CONJURE_WOODLAND_BEINGS,
                ),
                16: RangerLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 1),
                            (Ability.CONSTITUTION, 1),
                        ]
                    ),
                ),
                17: RangerLevel17(
                    spell_1=RangerLevel5Spells.SWIFT_QUIVER,
                    spell_2=RangerLevel5Spells.GREATER_RESTORATION,
                ),
                18: RangerLevel18(),
                19: RangerLevel19(
                    epic_boon=EpicBoon.DummyEpicBoon(),
                    spell=RangerLevel5Spells.TREE_STRIDE,
                ),
                20: RangerLevel20(),
            },
            subclass_features_by_level={
                3: RangerDemonHunterLevel3(
                    specialization=DemonHunterSpecialization.HAVOC
                ),
                5: RangerDemonHunterLevel5(
                    specialization=DemonHunterSpecialization.HAVOC
                ),
                7: RangerDemonHunterLevel7(),
                9: RangerDemonHunterLevel9(
                    specialization=DemonHunterSpecialization.HAVOC
                ),
                11: RangerDemonHunterLevel11(),
                13: RangerDemonHunterLevel13(
                    specialization=DemonHunterSpecialization.HAVOC
                ),
                15: RangerDemonHunterLevel15(),
                17: RangerDemonHunterLevel17(
                    specialization=DemonHunterSpecialization.HAVOC
                ),
                18: RangerDemonHunterLevel18(),
            },
        ),
        replace_spells={},
    )


class Y2024RangerDemonHunterVaelinFelbrandCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Vaelin Felbrand",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Elf.ElfSpeciesBuilder(
                elven_lineage=Elf.ElvenLineage.HIGH_ELF,
                skill_proficiency=Skill.INSIGHT,
            ),
        )
