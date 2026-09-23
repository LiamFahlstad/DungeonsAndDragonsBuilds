from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ArtificerBase import (
    ArtificerLevel1,
    ArtificerLevel2,
    ArtificerLevel3,
)
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.SubClasses2024.ArtificerCartographer import (
    ArtificerCartographerCustomStarterClassArgs,
    ArtificerCartographerLevel3,
)
from CharacterContent.Features.CharacterFeats import Backgrounds, OriginFeats
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Species import Dwarf
from CharacterContent.Spells import SpellLists as SpellDefinitions
from CharacterContent.ToolProficiencies.Proficiencies import (
    CalligraphersSupplies,
    CartographersTools,
    MasonsTools,
    NavigatorsTools,
    ThievesTools,
    TinkersTools,
)
from Core.Definitions import Ability, Skill
from StatBlocks.AbilitiesStatBlock import PointBuyAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import ArtificerSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=ArtificerCartographerCustomStarterClassArgs(
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
        abilities=PointBuyAbilitiesStatBlock(
            strength=14,
            dexterity=12,
            constitution=13,
            intelligence=14,
            wisdom=12,
            charisma=8,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.INTELLIGENCE, 2),
                (Ability.CONSTITUTION, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.INVESTIGATION,
                Skill.PERCEPTION,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Skilled(
            skills=[
                Skill.ATHLETICS,
                Skill.PERSUASION,
                Skill.SURVIVAL,
            ]
        ),
        armor=[
            Armor.StuddedLeatherArmor(),
            Armor.ShieldArmor(),
        ],
        # Dagger and Spear are both Simple weapons, so Artificers
        # (weapon_proficiencies=[SIMPLE] in ArtificerBase) are proficient
        # with both and add_weapon auto-detects it without needing a
        # player_is_proficient override. The Spear is swapped for a Light
        # Hammer at Stonehill - see __init__.
        weapons=[
            Weapons.Dagger(),
            Weapons.Spear(),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: ArtificerLevel1(
                    cantrip_1=SpellDefinitions.ArtificerLevel0Spells.MAGE_HAND,
                    cantrip_2=SpellDefinitions.ArtificerLevel0Spells.TRUE_STRIKE,
                    spell_1=SpellDefinitions.ArtificerLevel1Spells.FEATHER_FALL,
                    spell_2=SpellDefinitions.ArtificerLevel1Spells.GREASE,
                ),
                2: ArtificerLevel2(
                    spell=SpellDefinitions.ArtificerLevel1Spells.CURE_WOUNDS,
                ),
                3: ArtificerLevel3(
                    spell=SpellDefinitions.ArtificerLevel1Spells.LONGSTRIDER,
                ),
            },
            subclass_features_by_level={
                3: ArtificerCartographerLevel3(),
            },
        ),
        tool_proficiencies=[
            ThievesTools(),
            TinkersTools(),
            CalligraphersSupplies(),
            CartographersTools(),
            MasonsTools(),
            NavigatorsTools(),
        ],
    )


class Y2024ArtificerCartographerObmarStalskaggCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Obmar Stålskägg",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Dwarf.DwarfSpeciesBuilder(),
        )
        # Stonehill Armory upgrade (gifted, not purchased): traded the
        # Studded Leather for a Breastplate (still medium, still
        # proficient) and swapped the Spear for a Light Hammer as a
        # harder-hitting thrown/melee backup. The Dagger is untouched.
        self.drop_item(Armor.StuddedLeatherArmor)
        self.drop_item(Weapons.Spear)
        self.add_adventuring_gear(
            "Stonehill Armory Upgrade",
            armor=[Armor.BreastplateArmor()],
            weapons=[Weapons.LightHammer()],
        )
        # Adventure to Ashelm: Sulvesburg's Folly, a one-of-a-kind
        # Dual/Two-Handed Hammer & Segway weapon recovered from Clan
        # Sulvesburg's mining works.
        self.add_adventuring_gear(
            "Adventure to Ashelm",
            weapons=[Weapons.SulvesburgsFolly()],
        )
