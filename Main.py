import Definitions
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
    OptimizedRangerBeastMaster,
    OptimizedRangerGloomStalker,
    OptimizedRogueAssassin,
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
            "OptimizedRangerBeastMaster": OptimizedRangerBeastMaster.OptimizedRangerBeastMasterCharacterBuilder(),
            "OptimizedRangerGloomStalker": OptimizedRangerGloomStalker.OptimizedRangerGloomStalkerCharacterBuilder(),
            "OptimizedRogueAssassin": OptimizedRogueAssassin.OptimizedRogueAssassinCharacterBuilder(),
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


if __name__ == "__main__":
    skill_config = Definitions.SkillConfig.DEFAULT
    for build_class in BuildSelector.builds().values():
        character_sheet_data = build_class.build()
        character_sheet_data.create_character_sheet(skill_config=skill_config)
