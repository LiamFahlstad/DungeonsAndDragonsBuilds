from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.PaladinBase import (
    PaladinLevel1,
    PaladinLevel2,
    PaladinLevel3,
    PaladinLevel4,
    PaladinLevel5,
    PaladinLevel6,
    PaladinLevel7,
    PaladinLevel8,
    PaladinLevel9,
    PaladinLevel10,
    PaladinLevel11,
    PaladinLevel12,
    PaladinLevel13,
    PaladinLevel14,
    PaladinLevel15,
    PaladinLevel16,
    PaladinLevel17,
    PaladinLevel18,
    PaladinLevel19,
)
from CharacterConfigs.BaseClasses.WarlockBase import WarlockLevel1
from CharacterConfigs.SubClasses2024.PaladinDevotion import (
    DevotionPaladinLevel3,
    DevotionPaladinLevel5,
    DevotionPaladinLevel7,
    DevotionPaladinLevel9,
    DevotionPaladinLevel13,
    DevotionPaladinLevel17,
    DevotionPaladinMulticlassBuilder,
    PaladinDevotionCustomStarterClassArgs,
)
from CharacterConfigs.SubClasses2024.WarlockArchfey import (
    ArchfeyWarlockMulticlassBuilder,
)
from Core.Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, EpicBoon, GeneralFeats, OriginFeats
from Features.Combat import FightingStyles
from Features.Equipment import Weapons
from Invocations.Definitions import InvocationsLevel0
from SpeciesConfigs import Human
from Spells.SpellLists import (
    PaladinLevel1Spells,
    PaladinLevel2Spells,
    PaladinLevel3Spells,
    PaladinLevel4Spells,
    PaladinLevel5Spells,
    WarlockLevel0Spells,
    WarlockLevel1Spells,
    WizardLevel0Spells,
    WizardLevel1Spells,
)
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=PaladinDevotionCustomStarterClassArgs(
            skills=PaladinSkillsStatBlock(
                proficiencies={
                    Skill.ATHLETICS: True,
                    Skill.INSIGHT: True,
                    Skill.INTIMIDATION: False,
                    Skill.MEDICINE: False,
                    Skill.PERSUASION: False,
                    Skill.RELIGION: False,
                }
            ),
        ),
        base_class_level=1,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=14,
            dexterity=8,
            constitution=13,
            intelligence=10,
            wisdom=12,
            charisma=15,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CONSTITUTION, 1),
                (Ability.CHARISMA, 2),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.INTIMIDATION,
                Skill.PERSUASION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.MagicInitiateWizard(
            cantrip_1=WizardLevel0Spells.BLADE_WARD,
            cantrip_2=WizardLevel0Spells.PRESTIDIGITATION,
            spell=WizardLevel1Spells.SHIELD,
            spell_casting_ability=Ability.CHARISMA,
        ),
        armor=[],
        weapons=[
            Weapons.Greatsword(
                ability=Ability.STRENGTH,
            ),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: PaladinLevel1(
                    weapon_mastery_1=Weapons.Longsword(),
                    weapon_mastery_2=Weapons.Greatsword(),
                    # Shield of Faith is deliberately not picked here - Oath
                    # of Devotion grants it automatically at level 3.
                    spell_1=PaladinLevel1Spells.COMPELLED_DUEL,
                    spell_2=PaladinLevel1Spells.DIVINE_FAVOR,
                ),
            },
            subclass_features_by_level={},
        ),
    )


def get_warlock_multiclass_builder():
    return ArchfeyWarlockMulticlassBuilder(
        warlock_level=1,
        warlock_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: WarlockLevel1(
                    cantrip_1=WarlockLevel0Spells.ELDRITCH_BLAST,
                    cantrip_2=WarlockLevel0Spells.MINOR_ILLUSION,
                    spell_1=WarlockLevel1Spells.HEX,
                    spell_2=WarlockLevel1Spells.ARMOR_OF_AGATHYS,
                    eldritch_invocation=InvocationsLevel0.PACT_OF_THE_BLADE,
                ),
            },
            subclass_features_by_level={},
        ),
        replace_spells={},
    )


def get_paladin_multiclass_builder():
    return DevotionPaladinMulticlassBuilder(
        paladin_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                # Level 1 is granted by the starter class builder; the
                # engine applies a given class level's features only once,
                # from whichever builder is processed first.
                2: PaladinLevel2(
                    fighting_style=FightingStyles.GreatWeaponFighting(),
                    spell=PaladinLevel1Spells.COMMAND,
                ),
                3: PaladinLevel3(
                    spell=PaladinLevel1Spells.DETECT_MAGIC,
                ),
                4: PaladinLevel4(
                    general_feat=GeneralFeats.GreatWeaponMaster(
                        character_level=5,
                        ability=Ability.STRENGTH,
                    ),
                    spell=PaladinLevel1Spells.BLESS,
                ),
                5: PaladinLevel5(
                    spell=PaladinLevel1Spells.CURE_WOUNDS,
                ),
                6: PaladinLevel6(),
                7: PaladinLevel7(
                    spell=PaladinLevel2Spells.LESSER_RESTORATION,
                ),
                8: PaladinLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.STRENGTH, 2),
                        ]
                    ),
                ),
                9: PaladinLevel9(
                    spell_1=PaladinLevel3Spells.BLINDING_SMITE,
                    spell_2=PaladinLevel3Spells.CRUSADERS_MANTLE,
                ),
                10: PaladinLevel10(),
                11: PaladinLevel11(
                    spell=PaladinLevel3Spells.DAYLIGHT,
                ),
                12: PaladinLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CONSTITUTION, 2),
                        ]
                    ),
                ),
                13: PaladinLevel13(
                    spell=PaladinLevel4Spells.AURA_OF_LIFE,
                ),
                14: PaladinLevel14(),
                15: PaladinLevel15(
                    spell=PaladinLevel4Spells.BANISHMENT,
                ),
                16: PaladinLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CHARISMA, 2),
                        ]
                    ),
                ),
                17: PaladinLevel17(
                    spell_1=PaladinLevel4Spells.FIND_GREATER_STEED,
                    spell_2=PaladinLevel5Spells.CIRCLE_OF_POWER,
                ),
                18: PaladinLevel18(),
                19: PaladinLevel19(
                    epic_boon=EpicBoon.DummyEpicBoon(),
                    spell=PaladinLevel5Spells.HOLY_WEAPON,
                ),
            },
            subclass_features_by_level={
                3: DevotionPaladinLevel3(),
                5: DevotionPaladinLevel5(),
                7: DevotionPaladinLevel7(),
                9: DevotionPaladinLevel9(),
                13: DevotionPaladinLevel13(),
                17: DevotionPaladinLevel17(),
            },
        ),
        paladin_level=19,
        replace_spells={},
    )


class PaladinDevotionWarlockPactBladeCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Paladin Devotion Warlock Pact Blade",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.PERSUASION,
                origin_feat=OriginFeats.Skilled(
                    skills=[
                        Skill.INSIGHT,
                        Skill.MEDICINE,
                        Skill.RELIGION,
                    ]
                ),
            ),
            multiclass_builders=[
                get_warlock_multiclass_builder(),
                get_paladin_multiclass_builder(),
            ],
        )
