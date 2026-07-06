"""Character creation UI.

Usage (from the repo root):
    python Builds/CharacterCreatorUI.py
    python Builds/CharacterCreatorUI.py --load-build Builds/Characters/OptimizedBarbarianBerserker.py

Pick a class, subclass, level, species, skills, feats, spells and equipment,
then press "Generate" to write a runnable build file into
Builds/GeneratedBuilds/. "Load build…" (or --load-build) preloads any
existing build so you can tweak it.
"""

import argparse
import sys
from pathlib import Path

# Allow running as `python Builds/CharacterCreatorUI.py` from anywhere.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main():
    parser = argparse.ArgumentParser(description="D&D character creation UI")
    parser.add_argument(
        "--load-build",
        metavar="PATH",
        help="Preload an existing build file, e.g. Builds/Characters/OptimizedBarbarianBerserker.py",
    )
    arguments = parser.parse_args()

    from Builds.CharacterCreator import ui

    ui.run(load_build_path=arguments.load_build)


if __name__ == "__main__":
    main()
