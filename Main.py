from Builds import (
    Greta,
    JanHeting,
    OptimizedBardLore,
    OptimizedBerserkerBarbarian,
    OptimizedClericLight,
    OptimizedDruidMoon,
    OptimizedMonkShadow,
    OptimizedPaladinGlory,
    OptimizedRogueAssassin,
    Sten,
)
from Builds.CharacterBuilder import CharacterBuilder


class BuildSelector:
    @staticmethod
    def get_build(build_name: str) -> CharacterBuilder:
        builds = {
            "Greta": Greta.GretaCharacterBuilder(),
            "JanHeting": JanHeting.JanHetingCharacterBuilder(),
            "OptimizedBardLore": OptimizedBardLore.OptimizedLoreBardCharacterBuilder(),
            "OptimizedBerserkerBarbarian": OptimizedBerserkerBarbarian.OptimizedBerserkerBarbarianCharacterBuilder(),
            "OptimizedClericLight": OptimizedClericLight.OptimizedLightClericCharacterBuilder(),
            "OptimizedDruidMoon": OptimizedDruidMoon.OptimizedMoonDruidCharacterBuilder(),
            "OptimizedMonkShadow": OptimizedMonkShadow.OptimizedShadowMonkCharacterBuilder(),
            "OptimizedPaladinGlory": OptimizedPaladinGlory.OptimizedGloryPaladinCharacterBuilder(),
            "OptimizedRogueAssassin": OptimizedRogueAssassin.OptimizedAssassinRogueCharacterBuilder(),
            "Sten": Sten.StenCharacterBuilder(),
        }
        return builds[build_name]


if __name__ == "__main__":
    build_name = "Greta"
    build_class = BuildSelector.get_build(build_name)
    character_sheet_data = build_class.build()
    character_sheet_data.create_character_sheet()
