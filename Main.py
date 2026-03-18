from Builds import (
    Aska,
    Greta,
    JanHeting,
    OptimizedBardLore,
    OptimizedBerserkerBarbarian,
    OptimizedClericLight,
    OptimizedDruidMoon,
    OptimizedMonkShadow,
    OptimizedPaladinGlory,
    OptimizedRogueAssassin,
    OptimizedWarlockArchfey,
    RodericAshelm,
    Sten,
)
from Builds.CharacterBuilder import CharacterBuilder


class BuildSelector:
    @staticmethod
    def get_build(build_name: str) -> CharacterBuilder:
        builds = {
            "Aska": Aska.AskaCharacterBuilder(),
            "Greta": Greta.GretaCharacterBuilder(),
            "JanHeting": JanHeting.JanHetingCharacterBuilder(),
            "OptimizedBardLore": OptimizedBardLore.OptimizedLoreBardCharacterBuilder(),
            "OptimizedBerserkerBarbarian": OptimizedBerserkerBarbarian.OptimizedBerserkerBarbarianCharacterBuilder(),
            "OptimizedClericLight": OptimizedClericLight.OptimizedLightClericCharacterBuilder(),
            "OptimizedDruidMoon": OptimizedDruidMoon.OptimizedMoonDruidCharacterBuilder(),
            "OptimizedMonkShadow": OptimizedMonkShadow.OptimizedShadowMonkCharacterBuilder(),
            "OptimizedPaladinGlory": OptimizedPaladinGlory.OptimizedGloryPaladinCharacterBuilder(),
            "OptimizedRogueAssassin": OptimizedRogueAssassin.OptimizedAssassinRogueCharacterBuilder(),
            "OptimizedWarlockArchfey": OptimizedWarlockArchfey.OptimizedWarlockArchfeyCharacterBuilder(),
            "RodericAshelm": RodericAshelm.RodericAshelmCharacterBuilder(),
            "Sten": Sten.StenCharacterBuilder(),
        }
        return builds[build_name]


if __name__ == "__main__":
    build_names = [
        "Aska",
        "Greta",
        "JanHeting",
        "OptimizedBardLore",
        "OptimizedBerserkerBarbarian",
        "OptimizedClericLight",
        "OptimizedDruidMoon",
        "OptimizedMonkShadow",
        "OptimizedPaladinGlory",
        "OptimizedRogueAssassin",
        "OptimizedWarlockArchfey",
        "RodericAshelm",
        "Sten",
    ]
    for build_name in build_names:
        build_class = BuildSelector.get_build(build_name)
        character_sheet_data = build_class.build()
        character_sheet_data.create_character_sheet()
