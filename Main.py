from Builds import (
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
)
from Builds.CharacterBuilder import CharacterBuilder


class BuildSelector:
    @staticmethod
    def get_build(build_name: str) -> CharacterBuilder:
        builds = {
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
        }
        return builds[build_name]


if __name__ == "__main__":
    build_names = [
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
    ]
    for build_name in build_names:
        build_class = BuildSelector.get_build(build_name)
        character_sheet_data = build_class.build()
        character_sheet_data.create_character_sheet()
