from Builds import (Aska, OptimizedBarbarianBerserker,
                    OptimizedBarbarianWorldTree, OptimizedBardGlamour,
                    OptimizedBardLore, OptimizedClericKnowledge,
                    OptimizedClericLight, OptimizedDruidMoon,
                    OptimizedMonkShadow, OptimizedPaladinGlory,
                    OptimizedRangerBeastMaster, OptimizedRogueAssassin,
                    OptimizedWarlockArchfey, RodericAshelm, Sten)
from Builds.CharacterBuilder import CharacterBuilder


class BuildSelector:
    @staticmethod
    def get_build(build_name: str) -> CharacterBuilder:
        builds = {
            "Aska": Aska.AskaCharacterBuilder(),
            "OptimizedBardGlamour": OptimizedBardGlamour.OptimizedBardGlamourCharacterBuilder(),
            "OptimizedBardLore": OptimizedBardLore.OptimizedLoreBardCharacterBuilder(),
            "OptimizedBeastMaster": OptimizedRangerBeastMaster.OptimizedRangerBeastMasterCharacterBuilder(),
            "OptimizedBerserkerBarbarian": OptimizedBarbarianBerserker.OptimizedBerserkerBarbarianCharacterBuilder(),
            "OptimizedClericKnowledge": OptimizedClericKnowledge.OptimizedKnowledgeClericCharacterBuilder(),
            "OptimizedClericLight": OptimizedClericLight.OptimizedLightClericCharacterBuilder(),
            "OptimizedDruidMoon": OptimizedDruidMoon.OptimizedMoonDruidCharacterBuilder(),
            "OptimizedMonkShadow": OptimizedMonkShadow.OptimizedShadowMonkCharacterBuilder(),
            "OptimizedPaladinGlory": OptimizedPaladinGlory.OptimizedGloryPaladinCharacterBuilder(),
            "OptimizedRogueAssassin": OptimizedRogueAssassin.OptimizedAssassinRogueCharacterBuilder(),
            "OptimizedWarlockArchfey": OptimizedWarlockArchfey.OptimizedWarlockArchfeyCharacterBuilder(),
            "OptimizedWarlockArchfey": OptimizedWarlockArchfey.OptimizedWarlockArchfeyCharacterBuilder(),
            "OptimizedWorldTreeBarbarian": OptimizedBarbarianWorldTree.OptimizedWorldTreeBarbarianCharacterBuilder(),
            "RodericAshelm": RodericAshelm.RodericAshelmCharacterBuilder(),
            "Sten": Sten.StenCharacterBuilder(),
        }
        return builds[build_name]


if __name__ == "__main__":
    build_names = [
        "Aska",
        "OptimizedBardGlamour",
        "OptimizedBardLore",
        "OptimizedBeastMaster",
        "OptimizedBerserkerBarbarian",
        "OptimizedClericKnowledge",
        "OptimizedClericLight",
        "OptimizedDruidMoon",
        "OptimizedMonkShadow",
        "OptimizedPaladinGlory",
        "OptimizedRogueAssassin",
        "OptimizedWarlockArchfey",
        "OptimizedWarlockArchfey",
        "OptimizedWorldTreeBarbarian",
        "RodericAshelm",
        "Sten",
    ]
    for build_name in build_names:
        build_class = BuildSelector.get_build(build_name)
        character_sheet_data = build_class.build()
        character_sheet_data.create_character_sheet()
