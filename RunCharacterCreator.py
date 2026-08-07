import argparse
import importlib
import inspect
import pkgutil

import Core.Definitions as Definitions
import Builds.Examples
from Builds.Characters import (
    Y2024_Artificer_BattleSmith_PetraGearhollow,
    Y2024_Barbarian_Berserker_YmiraSkullcrusher,
    Y2024_Barbarian_WorldTree_DagnyEvergrasp,
    Y2024_Bard_Glamour_IselleMoonweave,
    Y2024_Bard_Lore_TobiasGreyquill,
    Y2024_Cleric_Knowledge_ThaddeusLoreweaver,
    Y2024_Cleric_Light_SolenneBrightward,
    Y2024_Druid_Moon_UrsalineNightpelt,
    Y2024_Monk_Elements_KragStormfist,
    Y2024_Fighter_BattleMaster_ReynardSteelvow,
    Y2024_Fighter_Champion_OsricIronheart,
    Y2024_Fighter_Champion_TaliaSwiftguard,
    Y2024_Monk_Shadow_UmbraSilentfang,
    Y2024_Paladin_Glory_BalderSunoath,
    Y2024_Paladin_Vengeance_NadiaIronvow,
    Y2024_Paladin_Devotion_ElricPactsworn,
    Y2024_Ranger_BeastMaster_OrinPackleader,
    Y2024_Ranger_GloomStalker_NyxShadowtracker,
    Y2024_Rogue_Assassin_LysandraNightblade,
    Y2024_Rogue_ShadowMonk_KagenVoidstep,
    Y2024_Sorcerer_Draconic_IgnatiaEmberscale,
    Y2024_Warlock_Archfey_WrennaThornpact,
    Y2024_Warlock_Archfey_CaelumBladefey,
    Y2024_Wizard_Bladesinger_IlyanaBladesong,
    Y2024_Wizard_Divination_PercivalFarsight,
)
from Builds.Tests import (
    SpellSlotTestWizard5,
    SpellSlotTestPaladin5,
    SpellSlotTestPaladin4Wizard3,
    SpellSlotTestWizard3Warlock3,
)
from Builds.CharacterBuilder import CharacterBuilder


class BuildSelector:
    @staticmethod
    def builds() -> dict[str, CharacterBuilder]:
        return {
            "Y2024_Artificer_BattleSmith_PetraGearhollow": Y2024_Artificer_BattleSmith_PetraGearhollow.Y2024ArtificerBattleSmithPetraGearhollowCharacterBuilder(),
            "Y2024_Barbarian_Berserker_YmiraSkullcrusher": Y2024_Barbarian_Berserker_YmiraSkullcrusher.Y2024BarbarianBerserkerYmiraSkullcrusherCharacterBuilder(),
            "Y2024_Barbarian_WorldTree_DagnyEvergrasp": Y2024_Barbarian_WorldTree_DagnyEvergrasp.Y2024BarbarianWorldTreeDagnyEvergraspCharacterBuilder(),
            "Y2024_Bard_Glamour_IselleMoonweave": Y2024_Bard_Glamour_IselleMoonweave.Y2024BardGlamourIselleMoonweaveCharacterBuilder(),
            "Y2024_Bard_Lore_TobiasGreyquill": Y2024_Bard_Lore_TobiasGreyquill.Y2024BardLoreTobiasGreyquillCharacterBuilder(),
            "Y2024_Cleric_Knowledge_ThaddeusLoreweaver": Y2024_Cleric_Knowledge_ThaddeusLoreweaver.Y2024ClericKnowledgeThaddeusLoreweaverCharacterBuilder(),
            "Y2024_Cleric_Light_SolenneBrightward": Y2024_Cleric_Light_SolenneBrightward.Y2024ClericLightSolenneBrightwardCharacterBuilder(),
            "Y2024_Druid_Moon_UrsalineNightpelt": Y2024_Druid_Moon_UrsalineNightpelt.Y2024DruidMoonUrsalineNightpeltCharacterBuilder(),
            "Y2024_Monk_Elements_KragStormfist": Y2024_Monk_Elements_KragStormfist.Y2024MonkElementsKragStormfistCharacterBuilder(),
            "Y2024_Fighter_BattleMaster_ReynardSteelvow": Y2024_Fighter_BattleMaster_ReynardSteelvow.Y2024FighterBattleMasterReynardSteelvowCharacterBuilder(),
            "Y2024_Fighter_Champion_OsricIronheart": Y2024_Fighter_Champion_OsricIronheart.Y2024FighterChampionOsricIronheartCharacterBuilder(),
            "Y2024_Fighter_Champion_TaliaSwiftguard": Y2024_Fighter_Champion_TaliaSwiftguard.Y2024FighterChampionTaliaSwiftguardCharacterBuilder(),
            "Y2024_Monk_Shadow_UmbraSilentfang": Y2024_Monk_Shadow_UmbraSilentfang.Y2024MonkShadowUmbraSilentfangCharacterBuilder(),
            "Y2024_Paladin_Glory_BalderSunoath": Y2024_Paladin_Glory_BalderSunoath.Y2024PaladinGloryBalderSunoathCharacterBuilder(),
            "Y2024_Paladin_Vengeance_NadiaIronvow": Y2024_Paladin_Vengeance_NadiaIronvow.Y2024PaladinVengeanceNadiaIronvowCharacterBuilder(),
            "Y2024_Paladin_Devotion_ElricPactsworn": Y2024_Paladin_Devotion_ElricPactsworn.Y2024PaladinDevotionElricPactswornCharacterBuilder(),
            "Y2024_Ranger_BeastMaster_OrinPackleader": Y2024_Ranger_BeastMaster_OrinPackleader.Y2024RangerBeastMasterOrinPackleaderCharacterBuilder(),
            "Y2024_Ranger_GloomStalker_NyxShadowtracker": Y2024_Ranger_GloomStalker_NyxShadowtracker.Y2024RangerGloomStalkerNyxShadowtrackerCharacterBuilder(),
            "Y2024_Rogue_Assassin_LysandraNightblade": Y2024_Rogue_Assassin_LysandraNightblade.Y2024RogueAssassinLysandraNightbladeCharacterBuilder(),
            "Y2024_Rogue_ShadowMonk_KagenVoidstep": Y2024_Rogue_ShadowMonk_KagenVoidstep.Y2024RogueShadowMonkKagenVoidstepCharacterBuilder(),
            "Y2024_Sorcerer_Draconic_IgnatiaEmberscale": Y2024_Sorcerer_Draconic_IgnatiaEmberscale.Y2024SorcererDraconicIgnatiaEmberscaleCharacterBuilder(),
            "Y2024_Warlock_Archfey_WrennaThornpact": Y2024_Warlock_Archfey_WrennaThornpact.Y2024WarlockArchfeyWrennaThornpactCharacterBuilder(),
            "Y2024_Warlock_Archfey_CaelumBladefey": Y2024_Warlock_Archfey_CaelumBladefey.Y2024WarlockArchfeyCaelumBladefeyCharacterBuilder(),
            "Y2024_Wizard_Bladesinger_IlyanaBladesong": Y2024_Wizard_Bladesinger_IlyanaBladesong.Y2024WizardBladesingerIlyanaBladesongCharacterBuilder(),
            "Y2024_Wizard_Divination_PercivalFarsight": Y2024_Wizard_Divination_PercivalFarsight.Y2024WizardDivinationPercivalFarsightCharacterBuilder(),
            "SpellSlotTestWizard5": SpellSlotTestWizard5.SpellSlotTestWizard5CharacterBuilder(),
            "SpellSlotTestPaladin5": SpellSlotTestPaladin5.SpellSlotTestPaladin5CharacterBuilder(),
            "SpellSlotTestPaladin4Wizard3": SpellSlotTestPaladin4Wizard3.SpellSlotTestPaladin4Wizard3CharacterBuilder(),
            "SpellSlotTestWizard3Warlock3": SpellSlotTestWizard3Warlock3.SpellSlotTestWizard3Warlock3CharacterBuilder(),
        }

    @staticmethod
    def get_build(build_name: str) -> CharacterBuilder:
        return BuildSelector.builds()[build_name]


class ExampleSelector:
    @staticmethod
    def builds() -> dict[str, CharacterBuilder]:
        example_builds: dict[str, CharacterBuilder] = {}
        for module_info in pkgutil.iter_modules(Builds.Examples.__path__):
            module_name = module_info.name
            if module_name.startswith("_"):
                continue
            module = importlib.import_module(f"Builds.Examples.{module_name}")
            for attr_name, attr_value in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(attr_value, CharacterBuilder)
                    and attr_value is not CharacterBuilder
                    and attr_value.__module__ == module.__name__
                ):
                    example_builds[attr_name] = attr_value()
        return example_builds


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--example",
        action="store_true",
        help="Create character sheets for all example builds in Builds/Examples instead "
        "of the default builds in RunCharacterCreator.py.",
    )
    parser.add_argument(
        "--concise",
        nargs="?",
        const="concise",
        default=None,
        choices=["concise", "table"],
        help="Render feature descriptions in a shortened form instead of the original "
        "prose text. Bare --concise renders short prose summaries (via "
        "Feature.get_concise_description); '--concise table' renders label/value "
        "tables (via Feature.get_table_description). Features without the requested "
        "version fall back to their normal description. Output files get a "
        "'_concise' or '_table' suffix accordingly.",
    )
    args = parser.parse_args()

    skill_config = Definitions.SkillConfig.DEFAULT
    builds = ExampleSelector.builds() if args.example else BuildSelector.builds()
    for build_class in builds.values():
        character_sheet_data = build_class.build()
        character_sheet_data.create_character_sheet(
            skill_config=skill_config,
            description_mode=args.concise,
        )
