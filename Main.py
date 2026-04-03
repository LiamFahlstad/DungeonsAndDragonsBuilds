import Definitions
from Builds import (
    MutliclassTest,
    OptimizedBarbarianBerserker,
    OptimizedBarbarianWorldTree,
    OptimizedBardGlamour,
    OptimizedBardLore,
    OptimizedClericKnowledge,
    OptimizedClericLight,
    OptimizedDruidMoon,
    OptimizedFighterBattleMaster,
    OptimizedMonkShadow,
    OptimizedPaladinGlory,
    OptimizedPaladinVengeance,
    OptimizedRangerBeastMaster,
    OptimizedRangerGloomStalker,
    OptimizedRogueAssassin,
    OptimizedWarlockArchfey,
    OptimizedWizardBladesinger,
)
from Builds.CharacterBuilder import CharacterBuilder


class BuildSelector:
    @staticmethod
    def get_build(build_name: str) -> CharacterBuilder:
        builds = {
            "MulticlassTest": MutliclassTest.MutliclassTestCharacterBuilder(),
            "OptimizedBarbarianBerserker": OptimizedBarbarianBerserker.OptimizedBarbarianBerserkerCharacterBuilder(),
            "OptimizedBarbarianWorldTree": OptimizedBarbarianWorldTree.OptimizedBarbarianWorldTreeCharacterBuilder(),
            "OptimizedBardGlamour": OptimizedBardGlamour.OptimizedBardGlamourCharacterBuilder(),
            "OptimizedBardLore": OptimizedBardLore.OptimizedLoreBardCharacterBuilder(),
            "OptimizedBeastMaster": OptimizedRangerBeastMaster.OptimizedRangerBeastMasterCharacterBuilder(),
            "OptimizedClericKnowledge": OptimizedClericKnowledge.OptimizedClericKnowledgeCharacterBuilder(),
            "OptimizedClericLight": OptimizedClericLight.OptimizedClericLightCharacterBuilder(),
            "OptimizedDruidMoon": OptimizedDruidMoon.OptimizedDruidMoonCharacterBuilder(),
            "OptimizedFighterBattleMaster": OptimizedFighterBattleMaster.OptimizedFighterBattleMasterCharacterBuilder(),
            "OptimizedMonkShadow": OptimizedMonkShadow.OptimizedMonkShadowCharacterBuilder(),
            "OptimizedPaladinGlory": OptimizedPaladinGlory.OptimizedPaladinGloryCharacterBuilder(),
            "OptimizedPaladinVengeance": OptimizedPaladinVengeance.OptimizedPaladinVengeanceCharacterBuilder(),
            "OptimizedRangerGloomStalker": OptimizedRangerGloomStalker.OptimizedRangerGloomStalkerCharacterBuilder(),
            "OptimizedRogueAssassin": OptimizedRogueAssassin.OptimizedRogueAssassinCharacterBuilder(),
            "OptimizedWarlockArchfey": OptimizedWarlockArchfey.OptimizedWarlockArchfeyCharacterBuilder(),
            "OptimizedWizardBladesinger": OptimizedWizardBladesinger.OptimizedWizardBladesingerCharacterBuilder(),
        }
        return builds[build_name]


if __name__ == "__main__":
    skill_config = Definitions.SkillConfig.HOMEBREW
    build_names = [
        "MulticlassTest",
        "OptimizedBarbarianBerserker",
        "OptimizedBarbarianWorldTree",
        "OptimizedBardGlamour",
        "OptimizedBardLore",
        "OptimizedBeastMaster",
        "OptimizedClericKnowledge",
        "OptimizedClericLight",
        "OptimizedDruidMoon",
        "OptimizedFighterBattleMaster",
        "OptimizedMonkShadow",
        "OptimizedPaladinGlory",
        "OptimizedPaladinVengeance",
        "OptimizedRangerGloomStalker",
        "OptimizedRogueAssassin",
        "OptimizedWarlockArchfey",
        "OptimizedWizardBladesinger",
    ]
    for build_name in build_names:
        build_class = BuildSelector.get_build(build_name)
        character_sheet_data = build_class.build()
        character_sheet_data.create_character_sheet(skill_config=skill_config)
