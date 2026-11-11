"""The pop-up that asks the GM about what a hit triggers (Notes/combat-effects-plan.md,
step 6.3): one per Apply, a checkbox per (target, triggered row), every one
checked to start with. Apply uses the checked ones, Edit opens the Custom
Effect dialog for each checked one with its row picked, and Skip (or Esc)
uses none. A row that rolls (Deflect Attacks' 1d10 + 8) has a box for what was
rolled at the table; blank rolls it (plan principle 13).
TurnPanelMixin._ask_triggers shows it; tests replace that method, so no modal
event loop runs in them."""

import re

from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator

from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from Combat.Effects.triggers import HitFiring, TriggerChoice

from .styles import QSS

_WIDTH = 520
# What a box for a roll made at the table takes: a total, or a sum ("7+8").
_TOTAL = r"\d+(\s*\+\s*\d+)*"


class TriggerPrompt(QDialog):
    """The question about `firings`; choice() is the answer once it's
    closed."""

    def __init__(self, parent: QWidget | None, firings: list[HitFiring]):
        super().__init__(parent)
        self.setObjectName("triggerPrompt")
        self.setWindowTitle("Use it now?")
        self.setStyleSheet(QSS)
        self.setMinimumWidth(_WIDTH)
        self._firings = list(firings)
        self._answer = ""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)
        heading = QLabel("This hit can trigger:")
        heading.setObjectName("triggerHeading")
        layout.addWidget(heading)
        self.boxes: list[QCheckBox] = []
        # A box for each firing's own roll, by its index in firings.
        self.rolls: dict[int, QLineEdit] = {}
        for index, firing in enumerate(self._firings):
            box = QCheckBox(firing.question)
            box.setObjectName("triggerBox")
            box.setChecked(True)
            box.setToolTip(getattr(firing.row.option, "tooltip", "") or "")
            self.boxes.append(box)
            dice = firing.row.damage_reduction
            if not dice:
                layout.addWidget(box)
                continue
            line = QHBoxLayout()
            line.addWidget(box, stretch=1)
            rolled = QLineEdit()
            rolled.setObjectName("triggerRolled")
            rolled.setPlaceholderText(f"{dice}, blank rolls")
            rolled.setToolTip(
                f"What was rolled at the table for {firing.row.name} ({dice}),"
                " the total taken off the damage. Blank rolls it here."
            )
            rolled.setValidator(
                QRegularExpressionValidator(QRegularExpression(_TOTAL), rolled)
            )
            rolled.setFixedWidth(130)
            line.addWidget(rolled)
            layout.addLayout(line)
            self.rolls[index] = rolled
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        self.apply_button = QPushButton("Apply")
        self.apply_button.setObjectName("triggerApply")
        self.apply_button.setDefault(True)
        self.apply_button.setToolTip(
            "Use each checked one, as picking it in the Custom Effect dialog"
            " would: it's spent and logged, and undone with the hit."
        )
        self.skip_button = QPushButton("Skip")
        self.skip_button.setObjectName("triggerSkip")
        self.skip_button.setToolTip("Use none of them. The log notes it for the GM.")
        self.edit_button = QPushButton("Edit...")
        self.edit_button.setObjectName("triggerEdit")
        self.edit_button.setToolTip(
            "Open the Custom Effect dialog for each checked one, with it picked."
        )
        for button in (self.apply_button, self.skip_button, self.edit_button):
            buttons.addWidget(button)
        layout.addLayout(buttons)
        self.apply_button.clicked.connect(lambda: self._close_with("apply"))
        self.edit_button.clicked.connect(lambda: self._close_with("edit"))
        self.skip_button.clicked.connect(self.reject)

    def _close_with(self, answer: str):
        self._answer = answer
        self.accept()

    def choice(self) -> TriggerChoice:
        checked = tuple(
            f for f, box in zip(self._firings, self.boxes) if box.isChecked()
        )
        rolled = tuple(
            (self._firings[index], _total(box.text()))
            for index, box in self.rolls.items()
            if re.fullmatch(_TOTAL, box.text().strip())
        )
        if self._answer == "apply":
            return TriggerChoice(apply=checked, rolled=rolled)
        if self._answer == "edit":
            return TriggerChoice(edit=checked)
        return TriggerChoice()


def _total(text: str) -> int:
    """A total typed in ("15") or a sum ("7 + 8")."""
    return sum(int(part) for part in text.split("+"))


def ask_triggers(parent: QWidget | None, firings: list[HitFiring]) -> TriggerChoice:
    """Ask about `firings` and wait for the answer."""
    prompt = TriggerPrompt(parent, firings)
    prompt.exec()
    return prompt.choice()
