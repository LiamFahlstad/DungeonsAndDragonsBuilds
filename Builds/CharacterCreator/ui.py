"""PyQt6 character creation UI.

Launch with:  python Builds/CharacterCreatorUI.py
Preload:      python Builds/CharacterCreatorUI.py --load-build Builds/OptimizedBarbarianBerserker.py

"Generate" writes a normal build file under Builds/GeneratedBuilds/ and
verifies it by importing it and running .build() in a subprocess.
"""

import ast
import inspect
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QCompleter,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from Builds.CharacterCreator import codegen, loader
from Builds.CharacterCreator import registry as registry_module
from Builds.CharacterCreator.model import BuildSpec, default_file_name
from Builds.CharacterCreator.registry import EditorKind, resolve_annotation

GENERATED_DIR = registry_module.REPO_ROOT / "Builds" / "GeneratedBuilds"

ABILITY_NAMES = (
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
)

# ---------------------------------------------------------------------------
# Global stylesheet — dark fantasy theme (matches Combat/CombatUIQt.py)
# ---------------------------------------------------------------------------
QSS = """
QMainWindow, QDialog, QWidget {
    background-color: #1a1a2e;
    color: #eaeaea;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 12px;
}

/* Section boxes */
QGroupBox {
    background-color: #16213e;
    border: 1px solid #0f3460;
    border-radius: 6px;
    margin-top: 10px;
    padding: 8px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    color: #c9a84c;
    font-weight: bold;
}

QLabel#sectionHeader {
    color: #c9a84c;
    font-weight: bold;
    font-size: 11px;
}
QLabel#secondary {
    color: #a0a0b0;
    font-size: 11px;
}
QLabel#hint {
    color: #666a80;
    font-size: 11px;
}

QFrame#divider {
    background-color: #0f3460;
    max-height: 1px;
    min-height: 1px;
}

/* Inputs */
QLineEdit {
    background-color: #0f3460;
    border: 1px solid #1a4a80;
    border-radius: 3px;
    color: #eaeaea;
    padding: 3px 5px;
}
QLineEdit:focus {
    border: 1px solid #c9a84c;
}

QComboBox {
    background-color: #0f3460;
    border: 1px solid #0f3460;
    border-radius: 3px;
    color: #eaeaea;
    padding: 2px 5px;
}
QComboBox:focus {
    border: 1px solid #c9a84c;
}
QComboBox::drop-down {
    border: none;
    width: 16px;
}
QComboBox QAbstractItemView {
    background-color: #16213e;
    color: #eaeaea;
    selection-background-color: #0f3460;
}

QSpinBox {
    background-color: #0f3460;
    border: 1px solid #1a4a80;
    border-radius: 3px;
    color: #eaeaea;
    padding: 2px 5px;
}
QSpinBox:focus {
    border: 1px solid #c9a84c;
}

QCheckBox {
    spacing: 6px;
}
QCheckBox::indicator {
    width: 13px;
    height: 13px;
    border: 1px solid #1a4a80;
    border-radius: 3px;
    background-color: #0f3460;
}
QCheckBox::indicator:checked {
    background-color: #c9a84c;
    border-color: #c9a84c;
}

QListWidget, QTextEdit {
    background-color: #0f3460;
    border: 1px solid #1a4a80;
    border-radius: 3px;
    color: #eaeaea;
}

/* Buttons */
QPushButton {
    background-color: #0f3460;
    color: #eaeaea;
    border: 1px solid #1a4a80;
    border-radius: 4px;
    padding: 4px 10px;
    min-height: 24px;
}
QPushButton:hover {
    background-color: #1a4a80;
}
QPushButton:pressed {
    background-color: #0a2540;
}
QPushButton:disabled {
    background-color: #0a1a30;
    color: #555;
    border-color: #0a2540;
}
QPushButton#primaryBtn {
    background-color: #1a3d2e;
    border: 1px solid #4caf82;
    color: #4caf82;
    font-weight: bold;
}
QPushButton#primaryBtn:hover {
    background-color: #204d38;
}
QPushButton#primaryBtn:pressed {
    background-color: #102a1e;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #0f3460;
    border-radius: 4px;
}
QTabBar::tab {
    background: #16213e;
    color: #a0a0b0;
    border: 1px solid #0f3460;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 5px 14px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #0f3460;
    color: #c9a84c;
    font-weight: bold;
}
QTabBar::tab:hover {
    color: #eaeaea;
}

/* Scrollbars */
QScrollBar:vertical {
    background: #1a1a2e;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #0f3460;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { height: 8px; background: #1a1a2e; }
QScrollBar::handle:horizontal {
    background: #0f3460;
    border-radius: 4px;
    min-width: 20px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

QStatusBar {
    color: #a0a0b0;
}
"""


def _clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        elif item.layout() is not None:
            _clear_layout(item.layout())


# ============================================================ value editors


class Editor:
    """Edits one value, exposed as a Python expression string (or None)."""

    def __init__(self):
        self.widget = QWidget()

    def get_expr(self):
        raise NotImplementedError

    def set_expr(self, expr):
        raise NotImplementedError


class RawEditor(Editor):
    def __init__(self, placeholder=""):
        super().__init__()
        layout = QHBoxLayout(self.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.line = QLineEdit()
        if placeholder:
            self.line.setPlaceholderText(placeholder)
        layout.addWidget(self.line)

    def get_expr(self):
        text = self.line.text().strip()
        return text or None

    def set_expr(self, expr):
        self.line.setText(expr or "")


class EnumEditor(Editor):
    """Editable combobox with type-to-filter completion over enum members."""

    def __init__(self, enum_classes, optional=False):
        super().__init__()
        layout = QHBoxLayout(self.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        options = [""] if optional else []
        for enum_class in enum_classes:
            options.extend(
                f"{enum_class.__name__}.{member.name}" for member in enum_class
            )
        self.combo = QComboBox()
        self.combo.addItems(options)
        self.combo.setEditable(True)
        self.combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        completer = self.combo.completer()
        if completer is not None:
            completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        if optional:
            self.combo.setCurrentText("")
        layout.addWidget(self.combo)

    def get_expr(self):
        text = self.combo.currentText().strip()
        return text or None

    def set_expr(self, expr):
        self.combo.setCurrentText(expr or "")


class BoolEditor(Editor):
    def __init__(self, default=False):
        super().__init__()
        layout = QHBoxLayout(self.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.check = QCheckBox()
        self.check.setChecked(default)
        layout.addWidget(self.check)
        layout.addStretch()

    def get_expr(self):
        return "True" if self.check.isChecked() else "False"

    def set_expr(self, expr):
        self.check.setChecked((expr or "").strip() == "True")


class IntEditor(Editor):
    def __init__(self, default=0, lower=0, upper=30):
        super().__init__()
        layout = QHBoxLayout(self.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.spin = QSpinBox()
        self.spin.setRange(lower, upper)
        self.spin.setValue(default)
        layout.addWidget(self.spin)
        layout.addStretch()

    def get_expr(self):
        return str(self.spin.value())

    def set_expr(self, expr):
        try:
            self.spin.setValue(int((expr or "").strip()))
        except ValueError:
            pass


class StrEditor(Editor):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.line = QLineEdit()
        layout.addWidget(self.line)

    def get_expr(self):
        text = self.line.text()
        return repr(text) if text else None

    def set_expr(self, expr):
        expr = (expr or "").strip()
        try:
            value = ast.literal_eval(expr)
            self.line.setText(value if isinstance(value, str) else expr)
        except (SyntaxError, ValueError):
            self.line.setText(expr)


class SkillListEditor(Editor):
    """A checkbox per skill; value is e.g. "[Skill.HISTORY, Skill.STEALTH]"."""

    def __init__(self, columns=3):
        super().__init__()
        from Definitions import Skill

        grid = QGridLayout(self.widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setVerticalSpacing(2)
        self.checks = {}
        for index, skill in enumerate(Skill):
            check = QCheckBox(skill.value)
            self.checks[skill.name] = check
            grid.addWidget(check, index // columns, index % columns)

    def selected(self):
        return [name for name, check in self.checks.items() if check.isChecked()]

    def get_expr(self):
        names = self.selected()
        if not names:
            return None
        return "[" + ", ".join(f"Skill.{name}" for name in names) + "]"

    def set_expr(self, expr):
        for check in self.checks.values():
            check.setChecked(False)
        if not expr:
            return
        try:
            tree = ast.parse(expr.strip(), mode="eval")
            if isinstance(tree.body, ast.List):
                for element in tree.body.elts:
                    if isinstance(element, ast.Attribute):
                        if element.attr in self.checks:
                            self.checks[element.attr].setChecked(True)
        except SyntaxError:
            pass

    def set_names(self, names):
        for check in self.checks.values():
            check.setChecked(False)
        for name in names:
            if name in self.checks:
                self.checks[name].setChecked(True)


class AbilityBonusListEditor(Editor):
    """Rows of (Ability, +N); value e.g. "[(Ability.WISDOM, 2), (Ability.STRENGTH, 1)]"."""

    def __init__(self, defaults=()):
        super().__init__()
        outer = QVBoxLayout(self.widget)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(2)
        self.rows_layout = QVBoxLayout()
        self.rows_layout.setSpacing(2)
        outer.addLayout(self.rows_layout)
        buttons = QHBoxLayout()
        add_btn = QPushButton("+ bonus")
        add_btn.setFixedWidth(70)
        add_btn.clicked.connect(lambda: self.add_row())
        remove_btn = QPushButton("- bonus")
        remove_btn.setFixedWidth(70)
        remove_btn.clicked.connect(self.remove_row)
        buttons.addWidget(add_btn)
        buttons.addWidget(remove_btn)
        buttons.addStretch()
        outer.addLayout(buttons)
        self.rows = []
        for ability_name, amount in defaults:
            self.add_row(ability_name, amount)

    def add_row(self, ability_name="STRENGTH", amount=1):
        from Definitions import Ability

        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        combo = QComboBox()
        combo.addItems([a.name for a in Ability])
        combo.setCurrentText(ability_name)
        spin = QSpinBox()
        spin.setRange(1, 3)
        spin.setValue(int(amount))
        layout.addWidget(combo)
        layout.addWidget(spin)
        layout.addStretch()
        self.rows_layout.addWidget(row)
        self.rows.append((row, combo, spin))

    def remove_row(self):
        if self.rows:
            row, _, _ = self.rows.pop()
            row.deleteLater()

    def get_pairs(self):
        return [(combo.currentText(), spin.value()) for _, combo, spin in self.rows]

    def get_expr(self):
        pairs = self.get_pairs()
        if not pairs:
            return None
        inner = ", ".join(f"(Ability.{name}, {amount})" for name, amount in pairs)
        return f"[{inner}]"

    def set_pairs(self, pairs):
        while self.rows:
            self.remove_row()
        for name, amount in pairs:
            self.add_row(name, amount)

    def set_expr(self, expr):
        pairs = []
        if expr:
            try:
                tree = ast.parse(expr.strip(), mode="eval")
                if isinstance(tree.body, ast.List):
                    for element in tree.body.elts:
                        if isinstance(element, ast.Tuple) and len(element.elts) == 2:
                            ability, amount = element.elts
                            if isinstance(ability, ast.Attribute) and isinstance(
                                amount, ast.Constant
                            ):
                                pairs.append((ability.attr, amount.value))
            except SyntaxError:
                pass
        self.set_pairs(pairs)


class OptionalEditor(Editor):
    """Checkbox that reveals the wrapped editor; unchecked means "omit"."""

    def __init__(self, make_inner, label="set"):
        super().__init__()
        layout = QVBoxLayout(self.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.check = QCheckBox(label)
        self.check.toggled.connect(self._toggle)
        layout.addWidget(self.check)
        self.inner = make_inner()
        self.inner.widget.setContentsMargins(18, 0, 0, 0)
        layout.addWidget(self.inner.widget)
        self.inner.widget.setVisible(False)

    def _toggle(self, checked):
        self.inner.widget.setVisible(checked)

    def get_expr(self):
        if not self.check.isChecked():
            return None
        return self.inner.get_expr()

    def set_expr(self, expr):
        has_value = bool(expr and expr.strip())
        self.check.setChecked(has_value)
        if has_value:
            self.inner.set_expr(expr)


class ClassPickerEditor(Editor):
    """Pick a concrete subclass (e.g. a feat) and fill in its parameters.

    Falls back to a raw expression entry via the "«code»" choice when the
    expression cannot be represented structurally.
    """

    RAW_CHOICE = "«code»"

    def __init__(self, base_class, context=None, optional=False):
        super().__init__()
        self.base_class = base_class
        self.context = context or {}
        self.optional = optional
        registry = registry_module.get_registry()
        self.classes = {
            cls.__name__: cls for cls in registry.concrete_subclasses(base_class)
        }
        if not self.classes and not inspect.isabstract(base_class):
            self.classes = {base_class.__name__: base_class}
        self.module_prefix = base_class.__module__.split(".")[-1]

        layout = QVBoxLayout(self.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        options = ([""] if optional else []) + sorted(self.classes) + [self.RAW_CHOICE]
        self.combo = QComboBox()
        self.combo.addItems(options)
        self.combo.setEditable(True)
        self.combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        completer = self.combo.completer()
        if completer is not None:
            completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.combo.currentTextChanged.connect(lambda _text: self._rebuild_params())
        layout.addWidget(self.combo)

        self.params_widget = QWidget()
        self.params_widget.setContentsMargins(18, 0, 0, 0)
        self.params_layout = QVBoxLayout(self.params_widget)
        self.params_layout.setContentsMargins(18, 0, 0, 0)
        self.params_layout.setSpacing(2)
        layout.addWidget(self.params_widget)

        self.param_editors = {}
        self.raw_editor = None
        if not optional and self.classes:
            self.combo.setCurrentText(sorted(self.classes)[0])
        self._rebuild_params()

    def _rebuild_params(self):
        _clear_layout(self.params_layout)
        self.param_editors = {}
        self.raw_editor = None
        choice = self.combo.currentText()
        if choice == self.RAW_CHOICE:
            self.raw_editor = RawEditor(placeholder="raw Python expression")
            self.params_layout.addWidget(self.raw_editor.widget)
            return
        cls = self.classes.get(choice)
        if cls is None:
            return
        for name, annotation, required in registry_module.signature_params(cls):
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            label = QLabel(name)
            label.setObjectName("secondary")
            label.setFixedWidth(160)
            label.setAlignment(Qt.AlignmentFlag.AlignTop)
            row_layout.addWidget(label)
            editor = make_editor(
                annotation, self.context, param_name=name, required=required
            )
            row_layout.addWidget(editor.widget, stretch=1)
            self.params_layout.addWidget(row)
            self.param_editors[name] = editor

    def get_expr(self):
        choice = self.combo.currentText()
        if not choice:
            return None
        if choice == self.RAW_CHOICE:
            return self.raw_editor.get_expr() if self.raw_editor else None
        if choice not in self.classes:
            return choice  # free-typed text: pass through as raw code
        parts = []
        for name, editor in self.param_editors.items():
            expr = editor.get_expr()
            if expr is not None:
                parts.append(f"{name}={expr}")
        return f"{self.module_prefix}.{choice}({', '.join(parts)})"

    def set_expr(self, expr):
        expr = (expr or "").strip()
        if not expr:
            self.combo.setCurrentText("")
            self._rebuild_params()
            return
        try:
            tree = ast.parse(expr, mode="eval")
            call = tree.body
            assert isinstance(call, ast.Call)
            class_name = _dotted(call.func).split(".")[-1]
            cls = self.classes[class_name]
            self.combo.setCurrentText(class_name)
            self._rebuild_params()
            params = registry_module.signature_params(cls)
            values = {kw.arg: ast.unparse(kw.value) for kw in call.keywords if kw.arg}
            for index, argument in enumerate(call.args):
                if index < len(params):
                    values[params[index][0]] = ast.unparse(argument)
            for name, value in values.items():
                if name in self.param_editors:
                    self.param_editors[name].set_expr(value)
                else:
                    raise KeyError(name)
        except Exception:
            # Anything unusual: keep it verbatim as code.
            self.combo.setCurrentText(self.RAW_CHOICE)
            self._rebuild_params()
            if self.raw_editor is not None:
                self.raw_editor.set_expr(expr)


def _dotted(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_dotted(node.value)}.{node.attr}"
    return ""


def make_editor(annotation, context, param_name=None, required=True):
    """Choose an editor widget for a constructor parameter annotation."""
    resolved = resolve_annotation(annotation) if annotation is not None else None
    optional = (resolved.optional if resolved else False) or not required

    def build():
        if resolved is None:
            return RawEditor()
        if resolved.kind == EditorKind.ENUM:
            return EnumEditor(resolved.payload, optional=False)
        if resolved.kind == EditorKind.INT:
            default = context.get("level", 1) if param_name == "character_level" else 0
            return IntEditor(default=default)
        if resolved.kind == EditorKind.BOOL:
            return BoolEditor()
        if resolved.kind == EditorKind.STR:
            return StrEditor()
        if resolved.kind == EditorKind.SKILL_LIST:
            return SkillListEditor()
        if resolved.kind == EditorKind.ABILITY_BONUS_LIST:
            # Start with one +2 row so the default is a valid Ability Score
            # Improvement (its bonuses must sum to 2).
            return AbilityBonusListEditor(defaults=[("STRENGTH", 2)])
        if resolved.kind == EditorKind.CLASS:
            return ClassPickerEditor(resolved.payload, context)
        return RawEditor()

    if optional:
        return OptionalEditor(build)
    return build()


# =============================================================== scroll tabs


def _make_scroll_tab():
    """Returns (scroll_area, content_layout)."""
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    content = QWidget()
    layout = QVBoxLayout(content)
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setSpacing(6)
    layout.addStretch()
    scroll.setWidget(content)
    return scroll, layout


def _insert_before_stretch(layout, widget):
    layout.insertWidget(layout.count() - 1, widget)


# =================================================================== the app


class CreatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.registry = registry_module.get_registry()
        self.setWindowTitle("D&D Character Creator")
        self.resize(1200, 880)

        self.level_editors = {}  # ("base"|"sub", level, param) -> Editor
        self.class_skill_checks = {}
        self.species_param_editors = {}
        self._level_cache = {}
        self._applying = False

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(8, 8, 8, 8)
        root_layout.setSpacing(6)

        root_layout.addWidget(self._build_header())
        root_layout.addWidget(self._build_notebook(), stretch=1)
        self.statusBar().showMessage(f"Builds are generated into {GENERATED_DIR}")

        self.on_class_changed(initial=True)

    # ---------------------------------------------------------------- header

    def _build_header(self):
        header = QWidget()
        grid = QGridLayout(header)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(2)

        def add_label(text, column):
            label = QLabel(text)
            label.setObjectName("sectionHeader")
            grid.addWidget(label, 0, column)

        add_label("NAME", 0)
        self.name_edit = QLineEdit("New Character")
        self.name_edit.setFixedWidth(220)
        grid.addWidget(self.name_edit, 1, 0)

        add_label("CLASS", 1)
        self.class_combo = QComboBox()
        self.class_combo.addItems(sorted(self.registry.classes()))
        self.class_combo.setCurrentText("Fighter")
        self.class_combo.setFixedWidth(110)
        # `activated` fires only on user interaction, so programmatic
        # setCurrentText during apply_spec does not retrigger rebuilds.
        self.class_combo.activated.connect(lambda _index: self.on_class_changed())
        grid.addWidget(self.class_combo, 1, 1)

        add_label("SUBCLASS", 2)
        self.subclass_combo = QComboBox()
        self.subclass_combo.setFixedWidth(220)
        self.subclass_combo.activated.connect(lambda _index: self.rebuild_levels())
        grid.addWidget(self.subclass_combo, 1, 2)

        add_label("LEVEL", 3)
        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 20)
        self.level_spin.setValue(4)
        self.level_spin.setFixedWidth(60)
        self.level_spin.valueChanged.connect(self._on_level_changed)
        grid.addWidget(self.level_spin, 1, 3)

        add_label("SPECIES", 4)
        self.species_combo = QComboBox()
        self.species_combo.addItems(sorted(self.registry.species()))
        self.species_combo.setCurrentText("HumanSpeciesBuilder")
        self.species_combo.setFixedWidth(230)
        self.species_combo.activated.connect(
            lambda _index: self.rebuild_species_params()
        )
        grid.addWidget(self.species_combo, 1, 4)

        buttons = QWidget()
        buttons_layout = QHBoxLayout(buttons)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        load_btn = QPushButton("Load build…")
        load_btn.clicked.connect(self.on_load)
        preview_btn = QPushButton("Preview code")
        preview_btn.clicked.connect(self.on_preview)
        generate_btn = QPushButton("Generate")
        generate_btn.setObjectName("primaryBtn")
        generate_btn.clicked.connect(self.on_generate)
        buttons_layout.addWidget(load_btn)
        buttons_layout.addWidget(preview_btn)
        buttons_layout.addWidget(generate_btn)
        grid.addWidget(buttons, 1, 5, Qt.AlignmentFlag.AlignRight)
        grid.setColumnStretch(5, 1)
        return header

    def _on_level_changed(self, _value):
        if not self._applying:
            self.rebuild_levels()

    # -------------------------------------------------------------- notebook

    def _build_notebook(self):
        self.tabs = QTabWidget()
        basics_scroll, self.basics_layout = _make_scroll_tab()
        levels_scroll, self.levels_layout = _make_scroll_tab()
        equipment_scroll, self.equipment_layout = _make_scroll_tab()
        advanced_scroll, self.advanced_layout = _make_scroll_tab()
        self.tabs.addTab(basics_scroll, "Basics")
        self.tabs.addTab(levels_scroll, "Level features")
        self.tabs.addTab(equipment_scroll, "Equipment")
        self.tabs.addTab(advanced_scroll, "Advanced")

        self._build_basics()
        self._build_equipment()
        self._build_advanced()
        return self.tabs

    def _build_basics(self):
        layout = self.basics_layout

        abilities_box = QGroupBox("Ability scores")
        abilities_grid = QGridLayout(abilities_box)
        self.ability_spins = {}
        defaults = BuildSpec().abilities
        for index, ability in enumerate(ABILITY_NAMES):
            label = QLabel(ability.capitalize())
            label.setObjectName("secondary")
            abilities_grid.addWidget(label, 0, index)
            spin = QSpinBox()
            spin.setRange(3, 20)
            spin.setValue(defaults[ability])
            spin.setFixedWidth(60)
            abilities_grid.addWidget(spin, 1, index)
            self.ability_spins[ability] = spin
        self.standard_array_check = QCheckBox(
            "Standard array (must be exactly 15, 14, 13, 12, 10, 8)"
        )
        self.standard_array_check.setChecked(True)
        abilities_grid.addWidget(self.standard_array_check, 2, 0, 1, 6)
        _insert_before_stretch(layout, abilities_box)

        background_box = QGroupBox("Background")
        background_layout = QVBoxLayout(background_box)
        bonus_label = QLabel("Ability bonuses (+2/+1 or +1/+1/+1):")
        bonus_label.setObjectName("secondary")
        background_layout.addWidget(bonus_label)
        self.background_bonuses = AbilityBonusListEditor(
            defaults=[("STRENGTH", 2), ("CONSTITUTION", 1)]
        )
        background_layout.addWidget(self.background_bonuses.widget)
        skills_label = QLabel("Skill proficiencies (pick 2):")
        skills_label.setObjectName("secondary")
        background_layout.addWidget(skills_label)
        self.background_skills = SkillListEditor(columns=6)
        self.background_skills.set_names(["PERCEPTION", "SURVIVAL"])
        background_layout.addWidget(self.background_skills.widget)
        _insert_before_stretch(layout, background_box)

        self.class_skills_box = QGroupBox("Class skill proficiencies")
        self.class_skills_layout = QVBoxLayout(self.class_skills_box)
        _insert_before_stretch(layout, self.class_skills_box)

        origin_box = QGroupBox("Origin feat")
        origin_layout = QVBoxLayout(origin_box)
        from Features.CharacterFeats import OriginFeats

        self.origin_feat = ClassPickerEditor(
            OriginFeats.OriginFeat, context=self._context()
        )
        self.origin_feat.set_expr("OriginFeats.Tough()")
        origin_layout.addWidget(self.origin_feat.widget)
        _insert_before_stretch(layout, origin_box)

        self.species_box = QGroupBox("Species options")
        self.species_layout = QVBoxLayout(self.species_box)
        _insert_before_stretch(layout, self.species_box)
        self.rebuild_species_params()

    def _build_equipment(self):
        layout = self.equipment_layout
        self.add_default_equipment_check = QCheckBox(
            "Add the class' default equipment"
        )
        self.add_default_equipment_check.setChecked(True)
        _insert_before_stretch(layout, self.add_default_equipment_check)

        from Features.Equipment import Armor, Weapons

        self.weapons_list = EquipmentList(
            self, "Weapons", Weapons.AbstractWeapon, self._context()
        )
        _insert_before_stretch(layout, self.weapons_list.box)
        self.armor_list = EquipmentList(
            self, "Armor", Armor.AbstractArmor, self._context()
        )
        _insert_before_stretch(layout, self.armor_list.box)

    def _build_advanced(self):
        layout = self.advanced_layout
        note = QLabel(
            "Optional raw Python expressions, exactly as they would appear in a "
            "build file. Leave empty to omit."
        )
        note.setObjectName("hint")
        _insert_before_stretch(layout, note)

        self.replace_spells_editor = self._advanced_row(
            "replace_spells",
            "e.g. {ClericLevel1Spells.HEALING_WORD: ClericLevel2Spells.AUGURY}",
        )
        self.items_editor = self._advanced_row("items", "e.g. [(Items.Potion(), 2)]")
        self.tools_editor = self._advanced_row(
            "tool_proficiencies", "e.g. ToolProficiency(...)"
        )
        self.starter_extra_editor = self._advanced_text(
            "Extra subclass starter args (one per line, name=expression)"
        )
        self.extra_kwargs_editor = self._advanced_text(
            "Extra StarterClassBuilder kwargs (one per line, name=expression)"
        )
        self.extra_imports_editor = self._advanced_text(
            "Extra import lines (one per line)"
        )

    def _advanced_row(self, title, hint):
        box = QGroupBox(title)
        box_layout = QVBoxLayout(box)
        editor = RawEditor(placeholder=hint)
        box_layout.addWidget(editor.widget)
        _insert_before_stretch(self.advanced_layout, box)
        return editor

    def _advanced_text(self, title):
        box = QGroupBox(title)
        box_layout = QVBoxLayout(box)
        text = QTextEdit()
        text.setFixedHeight(64)
        box_layout.addWidget(text)
        _insert_before_stretch(self.advanced_layout, box)
        return text

    # -------------------------------------------------------------- rebuilds

    def _context(self):
        return {"level": self.current_level()}

    def current_level(self):
        return self.level_spin.value()

    def on_class_changed(self, initial=False):
        class_key = self.class_combo.currentText()
        subclasses = sorted(self.registry.subclasses_for(class_key))
        self.subclass_combo.clear()
        self.subclass_combo.addItems(subclasses)
        if subclasses:
            self.subclass_combo.setCurrentText(subclasses[0])
        self.rebuild_class_skills()
        if not initial:
            self._level_cache = {}
        self.rebuild_levels(preserve=initial)

    def rebuild_class_skills(self, keep=None):
        _clear_layout(self.class_skills_layout)
        self.class_skill_checks = {}
        info = self.registry.classes()[self.class_combo.currentText()].skills_block
        if info is None:
            self.class_skills_layout.addWidget(QLabel("(unknown)"))
            return
        count_label = QLabel(f"Pick exactly {info.num_proficiencies}:")
        count_label.setObjectName("secondary")
        self.class_skills_layout.addWidget(count_label)
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setVerticalSpacing(2)
        for index, skill in enumerate(info.allowed_skills):
            check = QCheckBox(skill.value)
            check.setChecked(bool(keep and keep.get(skill.name)))
            self.class_skill_checks[skill.name] = check
            grid.addWidget(check, index // 6, index % 6)
        self.class_skills_layout.addWidget(grid_widget)

    def rebuild_species_params(self, values=None):
        _clear_layout(self.species_layout)
        self.species_param_editors = {}
        info = self.registry.species().get(self.species_combo.currentText())
        if info is None:
            return
        params = registry_module.signature_params(info.cls)
        if not params:
            none_label = QLabel("(no options)")
            none_label.setObjectName("secondary")
            self.species_layout.addWidget(none_label)
        for name, annotation, required in params:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            label = QLabel(name)
            label.setObjectName("secondary")
            label.setFixedWidth(160)
            label.setAlignment(Qt.AlignmentFlag.AlignTop)
            row_layout.addWidget(label)
            editor = make_editor(
                annotation, self._context(), param_name=name, required=required
            )
            row_layout.addWidget(editor.widget, stretch=1)
            self.species_layout.addWidget(row)
            self.species_param_editors[name] = editor
        if values:
            for name, expr in values.items():
                if name in self.species_param_editors:
                    self.species_param_editors[name].set_expr(expr)

    def rebuild_levels(self, preserve=True):
        # Remember whatever is currently filled in so changing the level or
        # subclass does not wipe the user's choices. Callers that just set
        # the cache themselves (loading a build, switching class) pass
        # preserve=False so stale editors do not clobber it.
        if preserve:
            for key, editor in self.level_editors.items():
                try:
                    expr = editor.get_expr()
                except RuntimeError:  # underlying Qt widget already deleted
                    continue
                if expr is not None:
                    self._level_cache[key] = expr

        _clear_layout(self.levels_layout)
        self.levels_layout.addStretch()
        self.level_editors = {}

        class_key = self.class_combo.currentText()
        class_info = self.registry.classes()[class_key]
        subclass_info = self.registry.subclasses().get(
            self.subclass_combo.currentText()
        )
        level = self.current_level()
        context = self._context()

        sections = []
        for lvl, cls in sorted(class_info.level_classes.items()):
            if lvl <= level:
                sections.append((lvl, 0, "base", f"{class_key} level {lvl}", cls))
        if subclass_info is not None:
            for lvl, cls in sorted(subclass_info.level_classes.items()):
                if lvl <= level:
                    sections.append(
                        (
                            lvl,
                            1,
                            "sub",
                            f"{subclass_info.key} level {lvl} (subclass)",
                            cls,
                        )
                    )
        sections.sort(key=lambda item: (item[0], item[1]))

        for lvl, _, kind, title, cls in sections:
            box = QGroupBox(title)
            box_layout = QVBoxLayout(box)
            box_layout.setSpacing(2)
            params = self.registry.level_params(cls)
            if not params:
                none_label = QLabel("(no choices at this level)")
                none_label.setObjectName("secondary")
                box_layout.addWidget(none_label)
            for name, annotation, required in params:
                row = QWidget()
                row_layout = QHBoxLayout(row)
                row_layout.setContentsMargins(0, 0, 0, 0)
                label = QLabel(name)
                label.setObjectName("secondary")
                label.setFixedWidth(160)
                label.setAlignment(Qt.AlignmentFlag.AlignTop)
                row_layout.addWidget(label)
                editor = make_editor(
                    annotation,
                    dict(context, level=lvl),
                    param_name=name,
                    required=required,
                )
                row_layout.addWidget(editor.widget, stretch=1)
                box_layout.addWidget(row)
                key = (kind, lvl, name)
                self.level_editors[key] = editor
                if key in self._level_cache:
                    editor.set_expr(self._level_cache[key])
            _insert_before_stretch(self.levels_layout, box)

    # ------------------------------------------------------------ spec <-> UI

    def to_spec(self):
        spec = BuildSpec()
        problems = []
        spec.name = self.name_edit.text().strip() or "New Character"
        spec.class_key = self.class_combo.currentText()
        spec.subclass_key = self.subclass_combo.currentText()
        if not spec.subclass_key:
            problems.append("No subclass selected.")
        spec.level = self.current_level()

        spec.abilities = {
            ability: spin.value() for ability, spin in self.ability_spins.items()
        }
        spec.use_standard_array = self.standard_array_check.isChecked()
        if spec.use_standard_array and sorted(spec.abilities.values()) != [
            8, 10, 12, 13, 14, 15,
        ]:
            problems.append(
                "Standard array is checked but scores are not 15/14/13/12/10/8."
            )

        info = self.registry.classes()[spec.class_key].skills_block
        spec.class_skills = {
            name: check.isChecked() for name, check in self.class_skill_checks.items()
        }
        if info is not None:
            picked = sum(1 for value in spec.class_skills.values() if value)
            if picked != info.num_proficiencies:
                problems.append(
                    f"{spec.class_key} needs exactly {info.num_proficiencies} class "
                    f"skills ({picked} selected)."
                )

        spec.background_bonuses = self.background_bonuses.get_pairs()
        spec.background_skills = self.background_skills.selected()
        if len(spec.background_skills) != 2:
            problems.append("Backgrounds normally grant exactly 2 skill proficiencies.")

        origin = self.origin_feat.get_expr()
        if origin is None:
            problems.append("No origin feat selected.")
        spec.origin_feat_expr = origin or "OriginFeats.Tough()"

        spec.add_default_equipment = self.add_default_equipment_check.isChecked()
        spec.weapon_exprs = self.weapons_list.get_exprs()
        spec.armor_exprs = self.armor_list.get_exprs()

        spec.base_level_params = {}
        spec.subclass_level_params = {}
        for (kind, level, name), editor in self.level_editors.items():
            expr = editor.get_expr()
            target = (
                spec.base_level_params if kind == "base" else spec.subclass_level_params
            )
            target.setdefault(level, {})
            if expr is not None:
                target[level][name] = expr

        # Report required level params that are still empty.
        class_info = self.registry.classes()[spec.class_key]
        subclass_info = self.registry.subclasses().get(spec.subclass_key)
        for kind, info_levels in (
            ("base", class_info.level_classes),
            ("sub", subclass_info.level_classes if subclass_info else {}),
        ):
            params_by_level = (
                spec.base_level_params if kind == "base" else spec.subclass_level_params
            )
            for level, cls in info_levels.items():
                if level > spec.level:
                    continue
                for name, _annotation, required in self.registry.level_params(cls):
                    if required and not params_by_level.get(level, {}).get(name):
                        problems.append(
                            f"{cls.__name__}: required choice {name!r} is empty."
                        )

        spec.species_class = self.species_combo.currentText()
        spec.species_params = {}
        for name, editor in self.species_param_editors.items():
            expr = editor.get_expr()
            if expr is not None:
                spec.species_params[name] = expr

        spec.replace_spells_expr = self.replace_spells_editor.get_expr()
        spec.items_expr = self.items_editor.get_expr()
        spec.tool_proficiencies_expr = self.tools_editor.get_expr()
        spec.starter_args_extra = _parse_kv_lines(self.starter_extra_editor)
        spec.extra_starter_kwargs = _parse_kv_lines(self.extra_kwargs_editor)
        spec.extra_imports = [
            line.strip()
            for line in self.extra_imports_editor.toPlainText().splitlines()
            if line.strip()
        ]
        return spec, problems

    def apply_spec(self, spec):
        self._applying = True
        try:
            self.name_edit.setText(spec.name)
            self.level_spin.setValue(spec.level)
            if spec.class_key in self.registry.classes():
                self.class_combo.setCurrentText(spec.class_key)
            subclasses = sorted(
                self.registry.subclasses_for(self.class_combo.currentText())
            )
            self.subclass_combo.clear()
            self.subclass_combo.addItems(subclasses)
            if spec.subclass_key in subclasses:
                self.subclass_combo.setCurrentText(spec.subclass_key)
            elif subclasses:
                self.subclass_combo.setCurrentText(subclasses[0])

            for ability, spin in self.ability_spins.items():
                spin.setValue(spec.abilities.get(ability, 10))
            self.standard_array_check.setChecked(spec.use_standard_array)

            self.rebuild_class_skills(keep=spec.class_skills)
            self.background_bonuses.set_pairs(spec.background_bonuses)
            self.background_skills.set_names(spec.background_skills)
            self.origin_feat.set_expr(spec.origin_feat_expr)
            self.add_default_equipment_check.setChecked(spec.add_default_equipment)
            self.weapons_list.set_exprs(spec.weapon_exprs)
            self.armor_list.set_exprs(spec.armor_exprs)

            if spec.species_class in self.registry.species():
                self.species_combo.setCurrentText(spec.species_class)
            self.rebuild_species_params(values=spec.species_params)

            self.replace_spells_editor.set_expr(spec.replace_spells_expr or "")
            self.items_editor.set_expr(spec.items_expr or "")
            self.tools_editor.set_expr(spec.tool_proficiencies_expr or "")
            _set_kv_lines(self.starter_extra_editor, spec.starter_args_extra)
            _set_kv_lines(self.extra_kwargs_editor, spec.extra_starter_kwargs)
            self.extra_imports_editor.setPlainText("\n".join(spec.extra_imports))

            self._level_cache = {}
            for level, params in spec.base_level_params.items():
                for name, expr in params.items():
                    self._level_cache[("base", level, name)] = expr
            for level, params in spec.subclass_level_params.items():
                for name, expr in params.items():
                    self._level_cache[("sub", level, name)] = expr
            self.rebuild_levels(preserve=False)
        finally:
            self._applying = False

    # --------------------------------------------------------------- actions

    def on_load(self):
        path, _filter = QFileDialog.getOpenFileName(
            self,
            "Load a build",
            str(registry_module.REPO_ROOT / "Builds"),
            "Python build files (*.py)",
        )
        if not path:
            return
        self.load_build(path)

    def load_build(self, path):
        try:
            spec, warnings = loader.load_build_file(path)
        except Exception as error:
            QMessageBox.critical(self, "Load failed", str(error))
            return
        self.apply_spec(spec)
        self.statusBar().showMessage(f"Loaded {Path(path).name}")
        if warnings:
            QMessageBox.warning(
                self,
                "Loaded with warnings",
                "\n".join(f"• {w}" for w in warnings),
            )

    def on_preview(self):
        spec, problems = self.to_spec()
        try:
            text = codegen.generate(spec)
        except Exception as error:
            QMessageBox.critical(self, "Cannot generate", str(error))
            return
        if problems:
            text = (
                "# NOTE: unresolved issues:\n"
                + "".join(f"#   - {p}\n" for p in problems)
                + "\n"
                + text
            )
        dialog = QDialog(self)
        dialog.setWindowTitle("Generated build code")
        dialog.resize(900, 700)
        layout = QVBoxLayout(dialog)
        view = QTextEdit()
        view.setReadOnly(True)
        view.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        view.setPlainText(text)
        view.setFontFamily("Consolas")
        layout.addWidget(view)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        dialog.exec()

    def on_generate(self):
        spec, problems = self.to_spec()
        if problems:
            answer = QMessageBox.question(
                self,
                "Issues found",
                "The build has issues:\n\n"
                + "\n".join(f"• {p}" for p in problems)
                + "\n\nGenerate anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        try:
            text = codegen.generate(spec)
        except Exception as error:
            QMessageBox.critical(self, "Cannot generate", str(error))
            return

        GENERATED_DIR.mkdir(parents=True, exist_ok=True)
        file_name = default_file_name(spec.name)
        path = GENERATED_DIR / file_name
        if path.exists():
            answer = QMessageBox.question(
                self,
                "Overwrite?",
                f"{path.name} already exists. Overwrite it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        path.write_text(text, encoding="utf-8")

        self.statusBar().showMessage(f"Wrote {path} — verifying…")
        QApplication.processEvents()
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            ok, output = codegen.validate_build_file(path)
        finally:
            QApplication.restoreOverrideCursor()
        if ok:
            self.statusBar().showMessage(f"Generated and verified {path}")
            QMessageBox.information(
                self,
                "Build generated",
                f"Wrote {path}\n\nVerified: the build imports and .build() runs.",
            )
        else:
            self.statusBar().showMessage(f"Generated {path}, but verification FAILED")
            tail = "\n".join(output.splitlines()[-15:])
            QMessageBox.warning(
                self,
                "Verification failed",
                f"Wrote {path}, but running .build() failed:\n\n{tail}",
            )


class EquipmentList:
    """List of equipment expressions with add/edit/remove dialogs."""

    def __init__(self, parent_window, title, base_class, context):
        self.parent_window = parent_window
        self.base_class = base_class
        self.context = context
        self.box = QGroupBox(title)
        layout = QVBoxLayout(self.box)
        self.list_widget = QListWidget()
        self.list_widget.setFixedHeight(110)
        layout.addWidget(self.list_widget)
        buttons = QHBoxLayout()
        add_btn = QPushButton("Add…")
        add_btn.clicked.connect(self.on_add)
        edit_btn = QPushButton("Edit…")
        edit_btn.clicked.connect(self.on_edit)
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.on_remove)
        buttons.addWidget(add_btn)
        buttons.addWidget(edit_btn)
        buttons.addWidget(remove_btn)
        buttons.addStretch()
        layout.addLayout(buttons)

    def get_exprs(self):
        return [
            self.list_widget.item(index).text()
            for index in range(self.list_widget.count())
        ]

    def set_exprs(self, exprs):
        self.list_widget.clear()
        for expr in exprs:
            self.list_widget.addItem(expr)

    def on_add(self):
        self._dialog(None)

    def on_edit(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            self._dialog(row)

    def on_remove(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            self.list_widget.takeItem(row)

    def _dialog(self, row):
        dialog = QDialog(self.parent_window)
        dialog.setWindowTitle("Equipment")
        dialog.setMinimumWidth(520)
        layout = QVBoxLayout(dialog)
        editor = ClassPickerEditor(self.base_class, self.context)
        layout.addWidget(editor.widget)
        layout.addStretch()
        if row is not None:
            editor.set_expr(self.list_widget.item(row).text())

        buttons = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.setObjectName("primaryBtn")
        cancel_btn = QPushButton("Cancel")
        buttons.addStretch()
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

        def confirm():
            expr = editor.get_expr()
            if expr:
                if row is None:
                    self.list_widget.addItem(expr)
                else:
                    self.list_widget.item(row).setText(expr)
            dialog.accept()

        ok_btn.clicked.connect(confirm)
        cancel_btn.clicked.connect(dialog.reject)
        dialog.exec()


def _parse_kv_lines(text_widget):
    result = {}
    for line in text_widget.toPlainText().splitlines():
        line = line.strip()
        if not line or "=" not in line:
            continue
        name, _, expr = line.partition("=")
        result[name.strip()] = expr.strip()
    return result


def _set_kv_lines(text_widget, mapping):
    text_widget.setPlainText(
        "\n".join(f"{name}={expr}" for name, expr in mapping.items())
    )


def run(load_build_path=None):
    import sys

    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    window = CreatorApp()
    window.show()
    if load_build_path:
        window.load_build(load_build_path)
    sys.exit(app.exec())
