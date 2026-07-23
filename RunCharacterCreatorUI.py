"""Character creation UI.

Usage:
    python RunCharacterCreatorUI.py
    python RunCharacterCreatorUI.py --load-build Builds/Characters/OptimizedBarbarianBerserker.py

Pick a class, subclass, level, species, skills, feats, spells and equipment,
then press "Generate" to write a runnable build file into
Builds/GeneratedBuilds/. "Load build…" (or --load-build) preloads any
existing build so you can tweak it.
"""

import argparse

from Builds.CharacterCreator import ui

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="D&D character creation UI")
    parser.add_argument(
        "--load-build",
        metavar="PATH",
        help="Preload an existing build file, e.g. Builds/Characters/OptimizedBarbarianBerserker.py",
    )
    args = parser.parse_args()

    ui.run(load_build_path=args.load_build)
