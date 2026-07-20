"""Example build: Druid Circle of the Land. A control/support caster starting in the
Tropical land (Web, Ray of Sickness) and switching to Arid at level 5+ (Fireball, Wall
of Stone) for offense and fire resistance."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.DruidBase import (
    DruidLevel1,
    DruidLevel2,
    DruidLevel3,
    DruidLevel4,
    DruidLevel5,
    DruidLevel6,
    DruidLevel7,
    DruidLevel8,
    DruidLevel9,
    DruidLevel10,
    DruidLevel11,
    DruidLevel12,
    DruidLevel13,
    DruidLevel14,
    DruidLevel15,
    DruidLevel16,
    DruidLevel17,
    DruidLevel18,
    DruidLevel19,
    DruidLevel20,
)
from CharacterConfigs.SubClasses2024.DruidLand import (
    DruidLandCustomStarterClassArgs,
    DruidLandLevel3,
    DruidLandLevel5,
    DruidLandLevel6,
    DruidLandLevel7,
    DruidLandLevel9,
    DruidLandLevel10,
    DruidLandLevel14,
)
from Combat.Monsters.CR_0.monsters import (
    Deer,
    GiantBadger,
    GiantSeahorse,
    GiantWolfSpider,
    Owl,
    Pteranodon,
    RidingHorse,
)
from Combat.Monsters.CR_1.monsters import GiantOctopus, GiantSpider
from Definitions import Ability, DruidLandType, Skill
from Features.CharacterFeats import Backgrounds, EpicBoon, GeneralFeats, OriginFeats
from Features.ClassFeatures.Druid import DruidFeatures
from Features.Equipment import Armor
from Features.Items import Items
from SpeciesConfigs import Human
from Spells.SpellLists import (
    AbjurationLevel0Spells,
    AbjurationLevel1Spells,
    DivinationLevel9Spells,
    DruidLevel0Spells,
    DruidLevel1Spells,
    DruidLevel2Spells,
    DruidLevel3Spells,
    DruidLevel4Spells,
    DruidLevel5Spells,
    EnchantmentLevel8Spells,
    EvocationLevel0Spells,
    IllusionLevel7Spells,
    TransmutationLevel9Spells,
)
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SkillsStatBlock import DruidSkillsStatBlock
from ToolProficiencies.ToolProficiencies import HerbalismKit

# Circle land type is chosen independently at each subclass level (3, 5, 7, 9, 10).
# Tropical early for Web/battlefield control, then Arid from level 5 on for Fireball,
# Wall of Stone, and fire resistance (Nature's Ward).
_EARLY_LAND = DruidLandType.TROPICAL
_LATE_LAND = DruidLandType.ARID


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=DruidLandCustomStarterClassArgs(
            skills=DruidSkillsStatBlock(
                proficiencies={
                    Skill.ARCANA: True,
                    Skill.ANIMAL_HANDLING: False,
                    Skill.INSIGHT: False,
                    Skill.MEDICINE: False,
                    Skill.NATURE: False,
                    Skill.PERCEPTION: True,
                    Skill.RELIGION: False,
                    Skill.SURVIVAL: False,
                }
            ),
        ),
        base_class_level=20,
        # Custom array (not standard array, since it repeats 8 three times):
        # base 8/15/15/8/15/8, background bonus below pushes WIS to 17 and CON to 16.
        abilities=AbilitiesStatBlock(
            strength=8,
            dexterity=15,
            constitution=15,
            intelligence=8,
            wisdom=15,
            charisma=8,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.WISDOM, 2),
                (Ability.CONSTITUTION, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.INSIGHT,
                Skill.SURVIVAL,
            ]
        ),
        add_default_equipment=False,
        # Second origin feat slot: Magic Initiate (Wizard), tuned to Wisdom so it scales
        # with the Druid's primary casting stat, per the build's "Magic Initiate: Wizard
        # (Wisdom)" pick.
        origin_feat=OriginFeats.MagicInitiateWizard(
            cantrip_1=AbjurationLevel0Spells.BLADE_WARD,
            cantrip_2=EvocationLevel0Spells.RAY_OF_FROST,
            spell=AbjurationLevel1Spells.SHIELD,
            spell_casting_ability=Ability.WISDOM,
        ),
        # Warden Primal Order (below) grants Medium armor proficiency; Chain Shirt is
        # the closest available Medium armor to Scale Mail/Half Plate in this codebase.
        armor=[
            Armor.ChainShirtArmor(),
            Armor.ShieldArmor(),
        ],
        weapons=[],
        items=[
            (Items.BullseyeLantern(), 1),
            (Items.FlasksOfOil(), 10),
            (Items.Backpack(), 1),
            (Items.Rope(), 1),
            (Items.Caltrops(), 1),
            (Items.BallBearings(), 1),
            (Items.HealersKit(), 1),
        ],
        # Only one tool proficiency slot is modeled; Herbalism Kit is picked over
        # Tinker's Tools since it isn't implemented in this codebase and fits the
        # "craft healing potions" downtime priority.
        tool_proficiencies=HerbalismKit(),
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: DruidLevel1(
                    cantrip_1=DruidLevel0Spells.GUIDANCE,
                    cantrip_2=DruidLevel0Spells.THORN_WHIP,
                    spell_1=DruidLevel1Spells.GOODBERRY,
                    spell_2=DruidLevel1Spells.HEALING_WORD,
                    spell_3=DruidLevel1Spells.ENTANGLE,
                    spell_4=DruidLevel1Spells.FOG_CLOUD,
                    primal_order=DruidFeatures.PrimalOrderType.WARDEN,
                ),
                2: DruidLevel2(
                    spell=DruidLevel1Spells.DETECT_MAGIC,
                    known_forms=[
                        Deer,
                        RidingHorse,
                        GiantWolfSpider,
                        GiantBadger,
                        GiantSeahorse,
                        GiantSpider,
                        Owl,
                        Pteranodon,
                        GiantOctopus,
                    ],
                ),
                3: DruidLevel3(
                    spell=DruidLevel2Spells.SPIKE_GROWTH,
                ),
                4: DruidLevel4(
                    general_feat=GeneralFeats.WarCaster(
                        character_level=4,
                        ability=Ability.WISDOM,
                    ),
                    cantrip=EvocationLevel0Spells.FIRE_BOLT,
                    spell=DruidLevel2Spells.MOONBEAM,
                ),
                5: DruidLevel5(
                    spell_1=DruidLevel3Spells.PLANT_GROWTH,
                    spell_2=DruidLevel3Spells.CONJURE_ANIMALS,
                ),
                6: DruidLevel6(
                    spell=DruidLevel3Spells.REVIVIFY,
                ),
                7: DruidLevel7(
                    spell=DruidLevel4Spells.WALL_OF_FIRE,
                ),
                8: DruidLevel8(
                    general_feat=GeneralFeats.MageSlayer(
                        character_level=8,
                        ability=Ability.DEXTERITY,
                    ),
                    spell=DruidLevel4Spells.GIANT_INSECT,
                ),
                9: DruidLevel9(
                    spell_1=DruidLevel3Spells.DISPEL_MAGIC,
                    spell_2=DruidLevel4Spells.CONJURE_WOODLAND_BEINGS,
                ),
                10: DruidLevel10(
                    cantrip=DruidLevel0Spells.STARRY_WISP,
                    spell=DruidLevel4Spells.POLYMORPH,
                ),
                11: DruidLevel11(
                    spell=DruidLevel3Spells.WATER_BREATHING,
                ),
                12: DruidLevel12(
                    # Resilient (CON): +1 CON (16 -> 17).
                    general_feat=GeneralFeats.Resilient(
                        character_level=12,
                        ability=Ability.CONSTITUTION,
                    ),
                ),
                13: DruidLevel13(
                    spell=IllusionLevel7Spells.MIRAGE_ARCANE,
                ),
                14: DruidLevel14(),
                15: DruidLevel15(
                    spell=EnchantmentLevel8Spells.ANTIPATHY_SYMPATHY,
                ),
                16: DruidLevel16(
                    # +2 WIS (18 -> 20).
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 2),
                        ]
                    ),
                ),
                17: DruidLevel17(
                    spell=TransmutationLevel9Spells.SHAPECHANGE,
                ),
                18: DruidLevel18(
                    spell=DivinationLevel9Spells.FORESIGHT,
                ),
                19: DruidLevel19(
                    # NOTE: "Boon of Recovery" isn't implemented in this codebase (only
                    # DummyEpicBoon exists as a placeholder), so the +1 CON at level 19
                    # from the source build isn't mechanically represented here.
                    epic_boon=EpicBoon.DummyEpicBoon(),
                    spell=DruidLevel2Spells.PASS_WITHOUT_TRACE,
                ),
                20: DruidLevel20(
                    spell=DruidLevel5Spells.SCRYING,
                ),
            },
            subclass_features_by_level={
                3: DruidLandLevel3(land_type=_EARLY_LAND),
                5: DruidLandLevel5(land_type=_LATE_LAND),
                6: DruidLandLevel6(),
                7: DruidLandLevel7(land_type=_LATE_LAND),
                9: DruidLandLevel9(land_type=_LATE_LAND),
                10: DruidLandLevel10(land_type=_LATE_LAND),
                14: DruidLandLevel14(),
            },
        ),
        replace_spells={},
    )


class ExampleDruidLandCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Land Druid",
            starter_class_builder=get_starter_class_builder(),
            # NOTE: Human is hardcoded as Medium size in this codebase, so the source
            # build's "Human (Small)" pick isn't available; using standard Medium Human.
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.ACROBATICS,
                origin_feat=OriginFeats.Alert(),
            ),
        )
