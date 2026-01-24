from Builds import (
    OptimizedBardLore,
    OptimizedBerserkerBarbarian,
    OptimizedClericLight,
    OptimizedRogueAssassin,
)


class BuildSelector:
    @staticmethod
    def get_build(build_name: str):
        builds = {
            "OptimizedBerserkerBarbarian": OptimizedBerserkerBarbarian,
            "OptimizedRogueAssassin": OptimizedRogueAssassin,
            "OptimizedBardLore": OptimizedBardLore,
            "OptimizedClericLight": OptimizedClericLight,
        }
        return builds.get(build_name, None)


if __name__ == "__main__":
    build_name = "OptimizedClericLight"
    build_class = BuildSelector.get_build(build_name)
    character_sheet_data = build_class.get_data()
    character_sheet_data.create_character_sheet()
