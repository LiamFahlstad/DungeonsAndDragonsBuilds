"""See this repo's apps without a display: PNG screenshots of the PyQt6 windows, and a build's
sheet rendered to a throwaway folder.

Usage (from the repo root):
    python .claude/skills/run-apps/screenshot.py combat                               # default campaign's first scenario
    python .claude/skills/run-apps/screenshot.py combat --scenario ashelm_church --size 1800x1100
    python .claude/skills/run-apps/screenshot.py creator                              # every tab of the Character Creator
    python .claude/skills/run-apps/screenshot.py creator --load-build Builds/Characters/Y2024_Fighter_BardValor_Clover.py --tab Equipment
    python .claude/skills/run-apps/screenshot.py sheet Obmar                          # render a registered build's sheet pages

Windows are built offscreen (QT_QPA_PLATFORM=offscreen), exactly as the app builds them, but
never run an event loop, start a timer or write a log into a campaign folder. A modal dialog
or message box that would have blocked is skipped and printed instead. Output goes to
<system temp>/dnd-screenshots/ unless --out is given; every file written is printed, so open
the PNGs (Claude: Read them) to look at the result.
"""

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
# The offscreen platform has no font database of its own on Windows: without this every glyph
# renders as an empty box.
if os.name == "nt":
    os.environ.setdefault("QT_QPA_FONTDIR", os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"))


def qt_app():
    """The QApplication, with blocking dialogs patched out. Create it before importing an app's
    UI module: Builds.CharacterCreator.Ui makes Qt objects at import time, and without a
    QApplication the process dies silently."""
    from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox

    app = QApplication.instance() or QApplication([])

    def skipped_dialog(self, *args, **kwargs):
        print(f"  (skipped modal dialog: {self.windowTitle() or type(self).__name__})")
        return 0

    def skipped_message(kind):
        def show(parent, title, text, *args, **kwargs):
            print(f"  ({kind} message box skipped) {title}: {text}")
            return QMessageBox.StandardButton.Ok

        return staticmethod(show)

    QDialog.exec = skipped_dialog
    for kind in ("critical", "warning", "information", "question"):
        setattr(QMessageBox, kind, skipped_message(kind))
    return app


def size_of(text: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d+)x(\d+)", text)
    if not match:
        raise argparse.ArgumentTypeError("size must look like 1600x1000")
    return int(match.group(1)), int(match.group(2))


def grab(app, widget, path: Path, size) -> None:
    if size:
        widget.resize(*size)
    widget.show()
    for _ in range(3):
        app.processEvents()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not widget.grab().save(str(path)):
        sys.exit(f"Could not save {path}")
    print(path)


def combat(args, out: Path) -> None:
    app = qt_app()
    import Combat.Scenarios as Scenarios
    from Combat.CombatUIQt import CombatAppQt
    from Combat.CombatUIQt.styles import QSS

    if args.scenario and args.scenario not in Scenarios.SCENARIOS:
        sys.exit(f"Unknown scenario {args.scenario!r}. Known: {', '.join(sorted(Scenarios.SCENARIOS))}")
    name = args.scenario or Scenarios.CAMPAIGNS[Scenarios.DEFAULT_CAMPAIGN].scenarios[0].name
    scenario = Scenarios.SCENARIOS[name]
    app.setStyleSheet(QSS)
    ui = CombatAppQt(
        combatants=scenario.build_allies() + scenario.build_combatants(),
        character_sheets=scenario.build_character_sheets(),
        combat_log_dir=Path(tempfile.mkdtemp(prefix="dnd-combat-logs-")),
        combatants_per_column=scenario.combatants_per_column,
        scenario_name=name,
    )
    ui._build_window()
    grab(app, ui._window, out / f"combat_{name}.png", args.size)


def creator(args, out: Path) -> None:
    app = qt_app()
    from PyQt6.QtWidgets import QTabWidget

    from Builds.CharacterCreator.Ui import CreatorApp, build_stylesheet

    app.setStyleSheet(build_stylesheet())
    window = CreatorApp()
    if args.load_build:
        window.load_build(args.load_build)
    stem = f"creator_{Path(args.load_build).stem}" if args.load_build else "creator"
    tabs = window.findChild(QTabWidget)
    if tabs is None:
        grab(app, window, out / f"{stem}.png", args.size)
        return
    names = [tabs.tabText(i) for i in range(tabs.count())]
    wanted = range(tabs.count())
    if args.tab:
        wanted = [i for i, n in enumerate(names) if args.tab.lower() in n.lower() or args.tab == str(i)]
        if not wanted:
            sys.exit(f"No tab matches {args.tab!r}. Tabs: {names}")
    for i in wanted:
        tabs.setCurrentIndex(i)
        slug = re.sub(r"\W+", "_", names[i]).strip("_").lower()
        grab(app, window, out / f"{stem}_{i}_{slug}.png", args.size)


def sheet(args, out: Path) -> None:
    import Core.Definitions as Definitions
    from Presentation.CharacterSheetWriters import HtmlCharacterSheetWriter, get_output_folder
    from RunCharacterCreator import BuildSelector, ExampleSelector

    builds = {**BuildSelector.builds(), **ExampleSelector.builds()}
    matches = sorted(n for n in builds if args.build.lower() in n.lower())
    if len(matches) != 1:
        sys.exit(f"{len(matches)} builds match {args.build!r}: {matches[:20]}. Give a more specific name.")
    data = builds[matches[0]]().build()
    folder = out / os.path.basename(get_output_folder(data))
    config = Definitions.SkillConfig.HOMEBREW if args.homebrew_skills else Definitions.SkillConfig.DEFAULT
    HtmlCharacterSheetWriter(show_feature_tags=args.feature_tags).write_character_sheet(data, skill_config=config, output_folder=str(folder))
    for page in sorted(folder.rglob("*.html")):
        print(page)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=Path(tempfile.gettempdir()) / "dnd-screenshots", help="output folder (default: <temp>/dnd-screenshots)")
    sub = parser.add_subparsers(dest="app", required=True)

    p = sub.add_parser("combat", help="the combat simulator window (RunCombatSimulator.py)")
    p.add_argument("--scenario", help="scenario name, as RunCombatSimulator.py --scenario takes it")
    p.add_argument("--size", type=size_of, default=(1600, 1000), help="window size, WxH (default 1600x1000)")

    p = sub.add_parser("creator", help="the Character Creator window (RunCharacterCreatorUI.py), one PNG per tab")
    p.add_argument("--load-build", metavar="PATH", help="preload a build file, as --load-build does")
    p.add_argument("--tab", help="only this tab (index, or part of its title)")
    p.add_argument("--size", type=size_of, default=(1200, 880), help="window size, WxH (default 1200x880, the app's own)")

    p = sub.add_parser("sheet", help="render one registered or example build's sheet pages (never into Output/)")
    p.add_argument("build", help="part of the build's registered name, e.g. Obmar")
    p.add_argument("--feature-tags", action="store_true", help="show the tag chips, as RunCharacterCreator.py --feature-tags")
    p.add_argument("--homebrew-skills", action="store_true", help="SkillConfig.HOMEBREW instead of DEFAULT")

    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    {"combat": combat, "creator": creator, "sheet": sheet}[args.app](args, args.out.resolve())


if __name__ == "__main__":
    main()
