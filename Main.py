import argparse
import importlib
import inspect
import pkgutil

import Definitions
import Builds.Examples
from Builds.Characters import (
    OptimizedArtificerBattleSmith,
    OptimizedBarbarianBerserker,
    OptimizedBarbarianWorldTree,
    OptimizedBardGlamour,
    OptimizedBardLore,
    OptimizedClericKnowledge,
    OptimizedClericLight,
    OptimizedDruidMoon,
    OptimizedFighterBattleMaster,
    OptimizedFighterChampion,
    OptimizedFighterChampion2,
    OptimizedMonkShadow,
    OptimizedPaladinGlory,
    OptimizedPaladinVengeance,
    PaladinDevotionWarlockPactBlade,
    OptimizedRangerBeastMaster,
    OptimizedRangerGloomStalker,
    OptimizedRogueAssassin,
    OptimizedSorcererDraconic,
    OptimizedWarlockArchfey,
    OptimizedWarlockGishArchfey,
    OptimizedWizardBladesinger,
    OptimizedWizardDiviner,
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
            "OptimizedArtificerBattleSmith": OptimizedArtificerBattleSmith.OptimizedArtificerBattleSmithCharacterBuilder(),
            "OptimizedBarbarianBerserker": OptimizedBarbarianBerserker.OptimizedBarbarianBerserkerCharacterBuilder(),
            "OptimizedBarbarianWorldTree": OptimizedBarbarianWorldTree.OptimizedBarbarianWorldTreeCharacterBuilder(),
            "OptimizedBardGlamour": OptimizedBardGlamour.OptimizedBardGlamourCharacterBuilder(),
            "OptimizedBardLore": OptimizedBardLore.OptimizedLoreBardCharacterBuilder(),
            "OptimizedClericKnowledge": OptimizedClericKnowledge.OptimizedClericKnowledgeCharacterBuilder(),
            "OptimizedClericLight": OptimizedClericLight.OptimizedClericLightCharacterBuilder(),
            "OptimizedDruidMoon": OptimizedDruidMoon.OptimizedDruidMoonCharacterBuilder(),
            "OptimizedFighterBattleMaster": OptimizedFighterBattleMaster.OptimizedFighterBattleMasterCharacterBuilder(),
            "OptimizedFighterChampion": OptimizedFighterChampion.OptimizedFighterChampionCharacterBuilder(),
            "OptimizedFighterChampion2": OptimizedFighterChampion2.OptimizedFighterChampionCharacterBuilder(),
            "OptimizedMonkShadow": OptimizedMonkShadow.OptimizedMonkShadowCharacterBuilder(),
            "OptimizedPaladinGlory": OptimizedPaladinGlory.OptimizedPaladinGloryCharacterBuilder(),
            "OptimizedPaladinVengeance": OptimizedPaladinVengeance.OptimizedPaladinVengeanceCharacterBuilder(),
            "PaladinDevotionWarlockPactBlade": PaladinDevotionWarlockPactBlade.PaladinDevotionWarlockPactBladeCharacterBuilder(),
            "OptimizedRangerBeastMaster": OptimizedRangerBeastMaster.OptimizedRangerBeastMasterCharacterBuilder(),
            "OptimizedRangerGloomStalker": OptimizedRangerGloomStalker.OptimizedRangerGloomStalkerCharacterBuilder(),
            "OptimizedRogueAssassin": OptimizedRogueAssassin.OptimizedRogueAssassinCharacterBuilder(),
            "OptimizedSorcererDraconic": OptimizedSorcererDraconic.OptimizedSorcererDraconicCharacterBuilder(),
            "OptimizedWarlockArchfey": OptimizedWarlockArchfey.OptimizedWarlockArchfeyCharacterBuilder(),
            "OptimizedWarlockGishArchfey": OptimizedWarlockGishArchfey.OptimizedWarlockArchfeyCharacterBuilder(),
            "OptimizedWizardBladesinger": OptimizedWizardBladesinger.OptimizedWizardBladesingerCharacterBuilder(),
            "OptimizedWizardDiviner": OptimizedWizardDiviner.OptimizedWizardDivinerCharacterBuilder(),
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
        "of the default builds in Main.py.",
    )
    args = parser.parse_args()

    skill_config = Definitions.SkillConfig.DEFAULT
    builds = ExampleSelector.builds() if args.example else BuildSelector.builds()
    for build_class in builds.values():
        character_sheet_data = build_class.build()
        character_sheet_data.create_character_sheet(skill_config=skill_config)
