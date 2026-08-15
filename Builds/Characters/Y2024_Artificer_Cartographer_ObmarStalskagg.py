from Builds.CharacterBuilder import Bought, CharacterBuilder
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
from CharacterContent.Items import Armor, Items, Weapons
from CharacterContent.Species import Dwarf
from CharacterContent.Spells import SpellLists as SpellDefinitions
from CharacterContent.ToolProficiencies.Proficiencies import (
    CalligraphersSupplies,
    CartographersTools,
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
                3: ArtificerCartographerLevel3(),
            },
        ),
        tool_proficiencies=[
            ThievesTools(),
            TinkersTools(),
            CalligraphersSupplies(),
            CartographersTools(),
        ],
    )


class Y2024ArtificerCartographerObmarStalskaggCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Obmar Stålskägg",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Dwarf.DwarfSpeciesBuilder(),
        )

        # Example usage: gear picked up after character creation gets its own
        # labeled entry on the sheet, separate from Starting Equipment. Call
        # add_adventuring_gear() again for each later haul. Items are found
        # by default (the Compass); wrap one in Bought(item) to mark it as
        # purchased instead - Bought(item, price=X) overrides the amount
        # paid, e.g. the 3 maps haggled down to 2 GP total instead of the
        # usual 1 GP each.
        self.add_adventuring_gear(
            "Charted the Sunken Archive (Level 3)",
            weapons=[Bought(Weapons.Dagger())],  # replaced the one dropped below, full price
            items=[
                (Items.HeartseekersCompass(), 1),
                (Bought(Items.Map(), price=2), 3),
            ],
        )

        # Example usage: drop_item() removes an item from the sheet and from
        # AC/attack calculations, while the code that added it stays in this
        # file as a record of what Obmar used to carry. Obmar now has two
        # Daggers (the starting one and the bought replacement above), so
        # dropping by class would be ambiguous - get_starting_item() scopes
        # the lookup to Starting Equipment specifically, so it stays
        # unambiguous regardless of what adventuring gear added afterward.
        self.drop_item(self.get_starting_item(Weapons.Dagger))
