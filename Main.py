import Definitions
from Builds import (
    OptimizedBarbarianBerserker,
    OptimizedBarbarianWorldTree,
    OptimizedBardGlamour,
    OptimizedBardLore,
    OptimizedClericKnowledge,
    OptimizedClericLight,
    OptimizedDruidMoon,
    OptimizedFighterBattleMaster,
    OptimizedFighterChampion,
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
from Builds.CharacterBuilder import CharacterBuilder


class BuildSelector:
    @staticmethod
    def get_build(build_name: str) -> CharacterBuilder:
        builds = {
            # "MulticlassTest": MutliclassTest.MutliclassTestCharacterBuilder(),
            "OptimizedBarbarianBerserker": OptimizedBarbarianBerserker.OptimizedBarbarianBerserkerCharacterBuilder(),
            "OptimizedBarbarianWorldTree": OptimizedBarbarianWorldTree.OptimizedBarbarianWorldTreeCharacterBuilder(),
            "OptimizedBardGlamour": OptimizedBardGlamour.OptimizedBardGlamourCharacterBuilder(),
            "OptimizedBardLore": OptimizedBardLore.OptimizedLoreBardCharacterBuilder(),
            "OptimizedClericKnowledge": OptimizedClericKnowledge.OptimizedClericKnowledgeCharacterBuilder(),
            "OptimizedClericLight": OptimizedClericLight.OptimizedClericLightCharacterBuilder(),
            "OptimizedDruidMoon": OptimizedDruidMoon.OptimizedDruidMoonCharacterBuilder(),
            "OptimizedFighterBattleMaster": OptimizedFighterBattleMaster.OptimizedFighterBattleMasterCharacterBuilder(),
            "OptimizedFighterChampion": OptimizedFighterChampion.OptimizedFighterChampionCharacterBuilder(),
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
        }
        return builds[build_name]


if __name__ == "__main__":
    skill_config = Definitions.SkillConfig.DEFAULT
    build_names = [
        # "MulticlassTest",
        "OptimizedBarbarianBerserker",
        "OptimizedBarbarianWorldTree",
        "OptimizedBardGlamour",
        "OptimizedBardLore",
        "OptimizedClericKnowledge",
        "OptimizedClericLight",
        "OptimizedDruidMoon",
        "OptimizedFighterBattleMaster",
        "OptimizedFighterChampion",
        "OptimizedMonkShadow",
        "OptimizedPaladinGlory",
        "OptimizedPaladinVengeance",
        "OptimizedRangerBeastMaster",
        "OptimizedRangerGloomStalker",
        "OptimizedRogueAssassin",
        "OptimizedWarlockArchfey",
        "OptimizedWarlockGishArchfey",
        "OptimizedWizardBladesinger",
        "OptimizedWizardDiviner",
    ]
    for build_name in build_names:
        build_class = BuildSelector.get_build(build_name)
        character_sheet_data = build_class.build()
        character_sheet_data.create_character_sheet(skill_config=skill_config)
