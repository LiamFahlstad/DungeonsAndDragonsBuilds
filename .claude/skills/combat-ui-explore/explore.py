"""Drive the real combat UI (CombatAppQt) the way a GM would and record what goes wrong.

A `Session` opens an encounter as RunCombatSimulator.py does, but on a temp copy of its log
(never a campaign's CombatLogs/ or PlayerLogs/), and records, each with the step it happened in
and the Python stack that caused it:
  - every Qt console message (style sheet, font, geometry warnings ...), once per text,
  - every Python warning and every exception raised in a Qt callback,
  - every modal dialog and message box the UI opened (they never block: see Session.answer),
  - every status-line message the UI showed (`_show_status`), and
  - every invariant `check()` or a round-trip check found broken.

As a library, from a probe script in the scratchpad directory (run from the repo root):

    import sys; sys.path.insert(0, ".claude/skills/combat-ui-explore")
    from explore import Session
    with Session("ashelm_church") as s:         # native=True: the real Windows platform
        s.start()                               # distinct initiatives; the fight begins
        obmar, ghoul = s.char("Obmar"), s.char("Accursed Group of 3")
        s.step("Obmar casts Burning Hands")
        print(s.picks(obmar)[:20])              # the Use / Cast rows Obmar has
        s.use_cast("Burning Hands", source=obmar, targets=[ghoul])
        s.undo_roundtrip(s.ui._advance_turn)    # do it, undo it: is the state back?
        s.replay_matches()                      # does the log rebuild the same state?
    print(s.report())

As a command:

    python .claude/skills/combat-ui-explore/explore.py sweep [--scenario NAME | --all] [--native]
    python .claude/skills/combat-ui-explore/explore.py scenarios

`sweep` opens every combo popup, card menu (and submenu), dialog, every row of every
combatant's Use / Cast picker, conditions, the Player Screen, the battle map and a few turns,
then prints the report. With --native a few windows flash on screen; it finds Windows-only
messages (geometry, DPI) that the offscreen platform never prints.
"""

from __future__ import annotations

import argparse
import collections
import os
import sys
import tempfile
import traceback
import warnings
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

_STACK_LINES = 12


def _set_platform(native: bool) -> None:
    if native:
        os.environ["QT_QPA_PLATFORM"] = "windows" if os.name == "nt" else "xcb"
        return
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    # The offscreen platform has no fonts of its own on Windows: every glyph is a box.
    if os.name == "nt":
        os.environ.setdefault(
            "QT_QPA_FONTDIR",
            os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"),
        )


@dataclass
class Finding:
    kind: str  # qt / warning / exception / invariant / undo / replay / status / dialog
    text: str
    step: str
    stack: str = ""
    count: int = 1


@dataclass
class Recorder:
    findings: dict[tuple[str, str], Finding] = field(default_factory=dict)
    step: str = "setup"

    def add(self, kind: str, text: str, stack: str | None = None) -> None:
        """Record `text` once per (kind, text), with the Python stack that got here unless
        `stack` is given ("" for none: a state diff's stack is always the check's own)."""
        key = (kind, text)
        if key in self.findings:
            self.findings[key].count += 1
            return
        if stack is None:
            stack = "".join(traceback.format_stack()[-_STACK_LINES - 2 : -2])
        self.findings[key] = Finding(kind, text, self.step, stack)

    def of(self, *kinds: str) -> list[Finding]:
        return [f for f in self.findings.values() if not kinds or f.kind in kinds]


# What the UI does that only shows in the window, not a problem by itself: listed in the report
# but not counted as findings.
_INFO_KINDS = ("status", "dialog")


class Session:
    """One encounter in a real CombatAppQt, its window built, logging to a temp folder."""

    def __init__(
        self,
        scenario: str | None = None,
        native: bool = False,
        answer: str = "yes",
        walk_dialogs: bool = False,
        player_log: bool = True,
    ):
        """`answer`: what every QMessageBox.question gets ("yes" or "no"). `walk_dialogs`:
        while a dialog is open, open its combo popups and pick every row of its trees (sweep).
        `player_log`: track the party in a temp player log, as `--player-log` does. Without
        one, a reopened fight starts the players from their sheets (HP, conditions), so
        replay_matches() only means something with it."""
        _set_platform(native)
        self.native = native
        self.answer = answer
        self.walk_dialogs = walk_dialogs
        self.player_log = player_log
        self.rec = Recorder()
        # Called with the dialog while it is open (Session.use_cast sets it); None = just close.
        self.on_dialog = None
        self.dialogs: list[str] = []
        self._scenario_name = scenario
        self._app = None
        self.ui = None
        self.log_path: Path | None = None

    # -- setup ------------------------------------------------------------------------------

    def __enter__(self) -> "Session":
        from PyQt6.QtCore import qInstallMessageHandler
        from PyQt6.QtWidgets import QApplication

        qInstallMessageHandler(lambda mode, ctx, msg: self._on_qt_message(msg))
        warnings.simplefilter("always")
        warnings.showwarning = self._on_warning
        self._old_excepthook = sys.excepthook
        sys.excepthook = self._on_exception
        self._app = QApplication.instance() or QApplication([])
        self._patch_modals()
        self._open(self._scenario_name)
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc is not None:
            self.rec.add(
                "exception",
                f"{exc_type.__name__}: {exc} (raised in the probe itself)",
                "".join(traceback.format_tb(tb)[-_STACK_LINES:]),
            )
        sys.excepthook = self._old_excepthook
        self.pump()
        return True  # the report shows it; the probe's caller still gets s.report()

    def _open(self, name: str | None) -> None:
        import Combat.Scenarios as Scenarios
        from Combat.CombatUIQt import CombatAppQt
        from Combat.CombatUIQt.styles import QSS
        from Combat.EncounterConfig import resolve_players
        from Combat.EncounterLogs import prepare_log, scenario_log_path

        if name is None:
            name = Scenarios.CAMPAIGNS[Scenarios.DEFAULT_CAMPAIGN].scenarios[0].name
        if name not in Scenarios.SCENARIOS:
            raise SystemExit(
                f"Unknown scenario {name!r}. Known: {', '.join(sorted(Scenarios.SCENARIOS))}"
            )
        self.scenario_name = name
        scenario = Scenarios.SCENARIOS[name]
        campaign = Scenarios.SCENARIO_CAMPAIGNS[name]
        self._app.setStyleSheet(QSS)
        party = campaign.players()
        sheets = {cs.character_name: cs for cs in party}
        temp = Path(tempfile.mkdtemp(prefix="dnd-combat-explore-"))
        logs = temp / "CombatLogs"
        self.log_path = scenario_log_path(logs, name)
        self.player_log_path = temp / "PlayerLogs" / "party.json" if self.player_log else None
        if self.player_log_path is not None:
            self.player_log_path.parent.mkdir(parents=True)
        prepare_log(
            self.log_path,
            scenario,
            resolve_players(scenario.players, list(sheets)),
            sheets=sheets,
        )
        self._make_ui = lambda: CombatAppQt(
            combatants=[],
            character_sheets=party,
            combat_log_dir=logs,
            combatants_per_column=scenario.combatants_per_column,
            log_path=self.log_path,
            player_log_path=str(self.player_log_path) if self.player_log_path else None,
            scenario_name=name,
            scenarios=[scenario],
            party_names=list(sheets),
            party_allies=campaign.party_allies,
        )
        self.ui = self._build_ui()
        self.window = self.ui._window
        self.window.resize(1600, 1000)
        self.window.show()
        self.pump()

    def _build_ui(self):
        ui = self._make_ui()
        ui._build_window()
        show_status = ui._show_status

        def recorded_status(text, *args, **kwargs):
            if text:
                self.rec.add("status", str(text))
            return show_status(text, *args, **kwargs)

        ui._show_status = recorded_status
        ui._open_encounter_log(self.log_path, restart=False)
        return ui

    def _patch_modals(self) -> None:
        from PyQt6.QtCore import QPoint
        from PyQt6.QtWidgets import QDialog, QMenu, QMessageBox

        session = self

        def exec_dialog(dlg, *args, **kwargs):
            title = dlg.windowTitle() or type(dlg).__name__
            session.dialogs.append(title)
            session.rec.add("dialog", title)
            dlg.show()
            session.pump()
            dlg.grab()  # paints it: style and font warnings come from painting
            if session.walk_dialogs:
                session.walk(dlg)
            handler, session.on_dialog = session.on_dialog, None
            result = 0
            if handler is not None:
                result = handler(dlg) or 0
            if dlg.isVisible():
                dlg.close()
            session.pump()
            return result

        def exec_menu(menu, *args, **kwargs):
            session.walk_menu(menu)
            return None

        def message(kind):
            def show(parent, title, text, *args, **kwargs):
                session.rec.add("dialog", f"{kind} box: {title}: {text}")
                if kind == "question":
                    return (
                        QMessageBox.StandardButton.Yes
                        if session.answer == "yes"
                        else QMessageBox.StandardButton.No
                    )
                return QMessageBox.StandardButton.Ok

            return staticmethod(show)

        QDialog.exec = exec_dialog
        QMenu.exec = exec_menu
        for kind in ("critical", "warning", "information", "question"):
            setattr(QMessageBox, kind, message(kind))
        self._menu_point = QPoint(40, 40)

    def _on_qt_message(self, message: str) -> None:
        # The offscreen platform can't raise windows, grab the keyboard or resize frames:
        # it says so for every window, and none of it happens on a real display.
        if not self.native and message.startswith("This plugin does not support"):
            return
        self.rec.add("qt", message)

    def _on_warning(self, message, category, filename, lineno, *args):
        self.rec.add(
            "warning", f"{category.__name__}: {message} ({Path(filename).name}:{lineno})"
        )

    def _on_exception(self, exc_type, exc, tb):
        self.rec.add(
            "exception",
            f"{exc_type.__name__}: {exc}",
            "".join(traceback.format_tb(tb)[-_STACK_LINES:]),
        )

    # -- driving ------------------------------------------------------------------------------

    def step(self, name: str) -> None:
        """Label what comes next: every finding records the step it happened in."""
        self.rec.step = name

    def pump(self) -> None:
        from PyQt6.QtCore import QCoreApplication, QEvent

        for _ in range(2):
            self._app.processEvents()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete.value)
        self._app.processEvents()

    def run(self, label: str, action, *args, **kwargs):
        """action(*args, **kwargs) as step `label`, its exception recorded instead of raised
        (a click handler's exception would end the real app without CombatAppQt.run's hook)."""
        self.step(label)
        try:
            result = action(*args, **kwargs)
        except Exception as error:  # noqa: BLE001 - recording it is the point
            self._on_exception(type(error), error, error.__traceback__)
            return None
        self.pump()
        return result

    def char(self, name: str) -> dict:
        """The combatant whose name contains `name` (any case); exits listing them if none."""
        wanted = name.lower()
        for char in self.ui.characters:
            if wanted in char["name"].lower():
                return char
        raise SystemExit(
            f"No combatant matches {name!r}: {[c['name'] for c in self.ui.characters]}"
        )

    def start(self, first: dict | None = None) -> None:
        """Start the fight with distinct initiatives (equal ones open the tie dialog), `first`
        first, then the window's order."""
        ui = self.ui
        units = list(ui._initiative_row_units())
        units.sort(key=lambda unit: not any(c is first for c in unit))
        for value, unit in enumerate(units):
            ui._initiative_inputs[id(unit[0])].setText(str(30 - value))
        self.run("start the fight", ui._start_combat)
        if ui.phase != "COMBAT":
            self.rec.add("invariant", f"the fight didn't start: {ui._status_label.text()}")

    def select(self, source: dict | None, targets: list[dict] = ()) -> None:
        """Make `source` the selected combatant and `targets` the targets, as clicks would."""
        ui = self.ui
        ui._clear_selection()
        if source is not None:
            ui._select_character(source)
        for i, target in enumerate(targets):
            ui._select_target_character(target, ctrl=i > 0)
        self.pump()

    def picks(self, source: dict) -> list[str]:
        """The names of the rows `source` can pick in Use / Cast (greyed rows included)."""
        from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItemIterator

        names: list[str] = []

        def read(dlg):
            from PyQt6.QtCore import Qt

            for tree in dlg.findChildren(QTreeWidget):
                it = QTreeWidgetItemIterator(tree)
                while it.value():
                    option = it.value().data(0, Qt.ItemDataRole.UserRole)
                    if option is not None:
                        names.append(option.name)
                    it += 1

        targets = [c for c in self.ui.characters if c is not source][:1]
        self.select(source, targets)
        self.on_dialog = read
        self.run(f"list picks: {source['name']}", self.ui._show_custom_condition_dialog)
        return names

    def use_cast(
        self,
        pick: str,
        source: dict,
        targets: list[dict] = (),
        fill=None,
        apply: bool = True,
    ):
        """Open Use / Cast for `source` on `targets` with row `pick` picked (its EffectOption
        name, see picks()), let `fill(dialog)` change the form, then press Apply (or Cancel).
        Returns the dialog (closed) so a probe can read what it showed."""
        from PyQt6.QtWidgets import QPushButton

        opened = []

        def handle(dlg):
            opened.append(dlg)
            if fill is not None:
                fill(dlg)
                self.pump()
            label = "Apply" if apply else "Cancel"
            button = next(
                (b for b in dlg.findChildren(QPushButton) if b.text() == label), None
            )
            if button is None:
                self.rec.add("invariant", f"Use / Cast has no {label} button")
                return 0
            button.click()
            self.pump()
            return 0

        self.select(source, list(targets))
        self.on_dialog = handle
        self.run(f"use/cast {pick}", self.ui._show_custom_condition_dialog, pick)
        if not opened:
            self.rec.add("invariant", f"Use / Cast didn't open for {pick!r}")
            return None
        return opened[0]

    def walk_menu(self, menu, depth: int = 0) -> None:
        """Pop `menu` and its submenus up, then close them (paints every entry)."""
        if menu is None or depth > 3:
            return
        menu.popup(self._menu_point)
        self.pump()
        for action in menu.actions():
            if action.menu() is not None:
                self.walk_menu(action.menu(), depth + 1)
        menu.close()
        self.pump()

    def walk(self, widget) -> None:
        """Open every visible combo popup under `widget`, and pick every row of its trees."""
        from PyQt6.QtWidgets import QComboBox, QTreeWidget, QTreeWidgetItemIterator

        for combo in widget.findChildren(QComboBox):
            if combo.isVisible():
                combo.showPopup()
                self.pump()
                combo.hidePopup()
                self.pump()
        for tree in widget.findChildren(QTreeWidget):
            it = QTreeWidgetItemIterator(tree)
            while it.value():
                tree.setCurrentItem(it.value())
                self.pump()
                it += 1

    # -- checks -------------------------------------------------------------------------------

    def state(self, ui=None) -> dict:
        """What a fight can change, as plain data: each combatant's public keys by name, who
        is in the initiative order, the round and whose turn it is."""
        from Combat.CombatUIQt.undo import _combat_data

        ui = ui or self.ui
        return {
            "combatants": {c["name"]: _combat_data(c) for c in ui.characters},
            "order": [c["name"] for c in ui.initiative_order],
            "round": ui.round_number,
            "turn": ui.current_turn_idx,
            "phase": ui.phase,
        }

    def check(self, label: str = "") -> list[str]:
        """Record (and return) every broken invariant of the current state."""
        ui = self.ui
        problems: list[str] = []
        names = [c["name"] for c in ui.characters]
        if len(set(names)) != len(names):
            problems.append(f"two combatants share a name: {names}")
        for c in ui.characters:
            who = c["name"]
            hp, max_hp, temp = c.get("hp"), c.get("max_hp"), c.get("temp_hp", 0)
            if not isinstance(hp, int) or not isinstance(max_hp, int):
                problems.append(f"{who}: hp {hp!r} / max_hp {max_hp!r} isn't a number")
            elif not 0 <= hp <= max_hp:
                problems.append(f"{who}: hp {hp} outside 0..{max_hp}")
            if not isinstance(temp, int) or temp < 0:
                problems.append(f"{who}: temp_hp {temp!r}")
            conditions = c.get("conditions", [])
            if len(set(conditions)) != len(conditions):
                problems.append(f"{who}: a condition twice: {conditions}")
            for key in ("death_saves_fail", "death_saves_success"):
                if not 0 <= c.get(key, 0) <= 3:
                    problems.append(f"{who}: {key} = {c.get(key)}")
            for key in ("spell_slots", "pact_slots"):
                for level, left in (c.get(key) or {}).items():
                    if not isinstance(left, int) or left < 0:
                        problems.append(f"{who}: {key}[{level}] = {left!r}")
            for feature, used in (c.get("feature_uses_used") or {}).items():
                if not isinstance(used, int) or used < 0:
                    problems.append(f"{who}: feature_uses_used[{feature}] = {used!r}")
        if ui.phase == "COMBAT":
            order = ui.initiative_order
            if not 0 <= ui.current_turn_idx < max(len(order), 1):
                problems.append(f"turn index {ui.current_turn_idx} of {len(order)}")
            for c in order:
                if not any(c is d for d in ui.characters):
                    problems.append(f"{c['name']} is in the turn order but not the fight")
            if ui.round_number < 1:
                problems.append(f"round {ui.round_number}")
        for problem in problems:
            self.rec.add("invariant", f"{label + ': ' if label else ''}{problem}")
        return problems

    def undo_roundtrip(self, action, *args, label: str | None = None, **kwargs) -> bool:
        """Do action(*args, **kwargs), then Undo: the state and the log must be what they were.
        False (and a finding) when they aren't, or when the action left no undo step."""
        ui = self.ui
        name = label or getattr(action, "__name__", "action")
        before, log_before = self.state(), _events(ui._read_log())
        steps = len(ui.history)
        self.run(f"undo roundtrip: {name}", action, *args, **kwargs)
        if len(ui.history) < steps:
            # It was an undo itself (Previous right after a Next pops that Next): undoing
            # again would take back one step more than it did.
            return True
        if len(ui.history) == steps:
            if self.state() != before:
                self.rec.add("undo", f"{name} changed the fight but left no undo step")
                return False
            return True  # it did nothing, so nothing to undo
        self.run(f"undo of {name}", ui._undo_last)
        ok = True
        for diff in _diff(before, self.state()):
            self.rec.add("undo", f"after undoing {name}: {diff}", "")
            ok = False
        for diff in _diff(log_before, _events(ui._read_log())):
            self.rec.add("undo", f"after undoing {name}, the log: {diff}", "")
            ok = False
        return ok

    def replay_matches(self, ignore: tuple[str, ...] = ("position",)) -> bool:
        """Open the encounter log in a fresh CombatAppQt, as the next session would: it must
        rebuild the same state. `ignore`: keys a replay legitimately doesn't restore."""
        self.step("replay the log")
        try:
            fresh = self._build_ui()
        except Exception as error:  # noqa: BLE001
            self._on_exception(type(error), error, error.__traceback__)
            return False
        now, again = self.state(), self.state(fresh)
        fresh._window.close()
        self.pump()
        ok = True
        for diff in _diff(now, again, ignore):
            self.rec.add("replay", f"replayed log differs: {diff}", "")
            ok = False
        return ok

    # -- report -------------------------------------------------------------------------------

    def report(self, stacks: bool = True) -> str:
        problems = [f for f in self.rec.of() if f.kind not in _INFO_KINDS]
        lines = [
            f"Scenario {self.scenario_name}, platform "
            f"{'native' if self.native else 'offscreen'}: {len(problems)} problem(s)"
        ]
        for f in problems:
            lines.append(f"  [{f.kind}] x{f.count} (step: {f.step}) {f.text}")
        info = self.rec.of(*_INFO_KINDS)
        if info:
            lines.append(f"Shown to the GM ({len(info)}):")
            lines += [f"  [{f.kind}] x{f.count} (step: {f.step}) {f.text}" for f in info]
        if stacks:
            for f in problems:
                if f.stack:
                    lines += ["", f"===== [{f.kind}] {f.text}", f.stack.rstrip()]
        return "\n".join(lines)


_EMPTY = (None, {}, [], 0, "", False)


def _diff(before: dict, after: dict, ignore: tuple[str, ...] = (), path: str = ""):
    """Readable differences between two state() dumps, skipping keys in `ignore`. A key that
    is missing on one side and empty (or 0/None/False) on the other is no difference."""
    if isinstance(before, dict) and isinstance(after, dict):
        for key in sorted(set(before) | set(after), key=str):
            if key in ignore:
                continue
            if (key not in after and before[key] in _EMPTY) or (
                key not in before and after[key] in _EMPTY
            ):
                continue
            where = f"{path}.{key}" if path else str(key)
            if key not in after:
                yield f"{where} is gone (was {before[key]!r})"[:300]
            elif key not in before:
                yield f"{where} is new: {after[key]!r}"[:300]
            else:
                yield from _diff(before[key], after[key], ignore, where)
    elif isinstance(before, list) and isinstance(after, list) and len(before) == len(after):
        for i, (old, new) in enumerate(zip(before, after)):
            yield from _diff(old, new, ignore, f"{path}[{i}]")
    elif before != after:
        yield f"{path}: {before!r} -> {after!r}"[:300]


def _events(log: dict) -> dict:
    """The events of an encounter log, by round: what Undo must take back. The rest (the
    combatants, the players' fight state, the order, the turn) is a snapshot every write
    refreshes."""
    return {key: value for key, value in log.items() if key.startswith("round_")}


# -- sweep ----------------------------------------------------------------------------------

_DIALOGS = [
    "_show_settings_dialog",
    "_show_add_combatant_dialog",
    "_show_load_encounter_dialog",
    "_show_player_link_dialog",
    "_show_more_info",
    "_show_statistics",
    "_show_rules",
    "_show_current_log",
]


def sweep(scenario: str | None, native: bool) -> Session:
    """Open everything the window offers once (see the module docstring)."""
    with Session(scenario, native=native, walk_dialogs=True) as s:
        ui = s.ui
        s.step("window")
        s.walk(s.window)
        s.start()
        s.check("after start")
        s.step("window in combat")
        s.walk(s.window)
        for char in list(ui.characters):
            s.run(
                f"card menu: {char['name']}",
                lambda c=char: s.walk_menu(ui._card_menu(c)),
            )
            s.run(
                f"wild shape menu: {char['name']}",
                lambda c=char: s.walk_menu(ui._wild_shape_menu(c)),
            )
            others = [c for c in ui.characters if c is not char][:1]
            s.select(char, others)
            s.run(f"use/cast picker: {char['name']}", ui._show_custom_condition_dialog)
        first = ui.characters[0]
        for condition in ("Poisoned", "Prone", "Frightened", "Invisible"):
            s.run(f"add {condition}", ui._add_condition_to, first, condition)
        s.check("after conditions")
        s.select(first)
        for name in _DIALOGS:
            if hasattr(ui, name):
                s.run(name, getattr(ui, name))
        from Combat.CombatUIQt.player_view import PlayerViewWindow

        for limited in (False, True):
            s.step(f"player screen ({'limited' if limited else 'informative'})")
            ui.settings.limited_player_view = limited
            view = PlayerViewWindow(on_close=lambda: None)
            s.run("player screen", view.show_rows, *ui._player_view_content())
            view.show()
            s.pump()
            view.grab()
            view.close()
        s.step("battle map")
        ui.arena_view_on = True
        s.run("battle map", ui._show_view)
        s.window.grab()
        s.walk(s.window)
        for i in range(len(ui.initiative_order) + 1):
            s.run(f"next turn {i + 1}", ui._advance_turn)
        s.check("after a round of turns")
        s.replay_matches()
    return s


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("sweep", help="open everything the combat window offers once")
    p.add_argument("--scenario", help="scenario id (default: the default campaign's first)")
    p.add_argument("--all", action="store_true", help="one scenario of every campaign")
    p.add_argument("--native", action="store_true", help="the real Windows platform")
    p.add_argument("--no-stacks", action="store_true", help="leave out the stacks")
    sub.add_parser("scenarios", help="list the scenarios, by campaign")
    args = parser.parse_args()

    import Combat.Scenarios as Scenarios

    if args.command == "scenarios":
        for name, campaign in Scenarios.CAMPAIGNS.items():
            print(f"{name}: {', '.join(s.name for s in campaign.scenarios)}")
        return
    names = (
        [c.scenarios[0].name for c in Scenarios.CAMPAIGNS.values() if c.scenarios]
        if args.all
        else [args.scenario]
    )
    failed = False
    for name in names:
        s = sweep(name, args.native)
        print(s.report(stacks=not args.no_stacks))
        print()
        failed |= any(f.kind not in _INFO_KINDS for f in s.rec.of())
    # After a sweep (Player Screen windows, many dialogs and menus) Qt can die tearing them
    # down at interpreter exit, exit code 127 with nothing printed. Skip the teardown, so the
    # exit code is the sweep's: 1 when it found a problem.
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(1 if failed else 0)


if __name__ == "__main__":
    main()
