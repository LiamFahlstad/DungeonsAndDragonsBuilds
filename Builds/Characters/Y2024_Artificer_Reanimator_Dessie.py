from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ArtificerBase import (
    ArtificerLevel1,
    ArtificerLevel2,
    ArtificerLevel3,
)
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.SubClasses2024.ArtificerReanimator import (
    ArtificerReanimatorCustomStarterClassArgs,
    ArtificerReanimatorLevel3,
)
from CharacterContent.Features.CharacterFeats import Backgrounds, OriginFeats
from CharacterContent.Items import Armor, Items, Weapons
from CharacterContent.Species import Human
from CharacterContent.Spells.SpellLists import (
    ArtificerLevel0Spells,
    ArtificerLevel1Spells,
    WizardLevel0Spells,
    WizardLevel1Spells,
)
from CharacterContent.ToolProficiencies.Proficiencies import (
    AlchemistsSupplies,
    CalligraphersSupplies,
    TinkersTools,
)
from Core.Definitions import Ability, Skill
from Model.AbilityScores import PointBuyAbilityScores


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=ArtificerReanimatorCustomStarterClassArgs(
            skills=[
                Skill.INVESTIGATION,
                Skill.NATURE,
            ],
        ),
        base_class_level=3,
        # Point buy: scores 8-15, total cost must equal 27.
        abilities=PointBuyAbilityScores(
            strength=8,
            dexterity=14,
            constitution=15,
            intelligence=14,
            wisdom=12,
            charisma=8,
        ),
        # Sage: +2 Intelligence, +1 Constitution.
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.INTELLIGENCE, 2),
                (Ability.CONSTITUTION, 1),
            ]
        ),
        # Sage skills.
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.ARCANA,
                Skill.HISTORY,
            ]
        ),
        add_default_equipment=False,
        # Sage origin feat.
        origin_feat=OriginFeats.MagicInitiateWizard(
            cantrip_1=WizardLevel0Spells.TRUE_STRIKE,
            cantrip_2=WizardLevel0Spells.MINOR_ILLUSION,
            spell=WizardLevel1Spells.SHIELD,
            spell_casting_ability=Ability.INTELLIGENCE,
        ),
        armor=[
            Armor.ScaleMailArmor(),
            Armor.ShieldArmor(),
        ],
        weapons=[
            Weapons.LightCrossbow(),
            Weapons.Dagger(),
        ],
        # One-shot party role: light-bearer and tinkerer. Only gear that can
        # matter on the adventure; climbing gear is left to Hanna, healing and
        # maps to Maggie.
        items=[
            (Items.CrossbowBolts(), 1),  # one case of 20 bolts
            (Items.TinkersTools(), 1),
            (Items.HoodedLantern(), 1),
            (Items.FlasksOfOil(), 3),
            (Items.Crowbar(), 1),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: ArtificerLevel1(
                    cantrip_1=ArtificerLevel0Spells.SHOCKING_GRASP,
                    cantrip_2=ArtificerLevel0Spells.THUNDERCLAP,
                    spell_1=ArtificerLevel1Spells.GREASE,
                    spell_2=ArtificerLevel1Spells.FAERIE_FIRE,
                ),
                2: ArtificerLevel2(
                    spell=ArtificerLevel1Spells.DISGUISE_SELF,
                ),
                3: ArtificerLevel3(
                    spell=ArtificerLevel1Spells.FEATHER_FALL,
                ),
            },
            subclass_features_by_level={
                3: ArtificerReanimatorLevel3(),
            },
        ),
        tool_proficiencies=[
            TinkersTools(),
            AlchemistsSupplies(),
            CalligraphersSupplies(),
        ],
    )


class Y2024ArtificerReanimatorDessieCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Dessie",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.PERCEPTION,
                origin_feat=OriginFeats.Alert(),
            ),
        )
        # Kingdom Saving Agency mission issue (the agency that recruited the
        # party): Dessie is the party's investigator. A magnifying glass for
        # clues and evidence, and alchemist's fire as her emergency answer
        # to a crowd closing in on her companion.
        self.add_adventuring_gear(
            "Kingdom Saving Agency",
            items=[
                (Items.MagnifyingGlass(), 1),
                (Items.AlchemistsFire(), 2),
                (Items.PotionOfHealing(), 1),
            ],
            gold=10,  # travel expenses
        )
