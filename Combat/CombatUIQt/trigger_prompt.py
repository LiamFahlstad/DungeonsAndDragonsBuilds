"""The pop-up that asks the GM about what a hit triggers (Notes/combat-effects-plan.md,
step 6.3): one per Apply, a checkbox per (target, triggered row), every one
checked to start with. Apply uses the checked ones, Edit opens the Custom
Effect dialog for each checked one with its row picked, and Skip (or Esc)
uses none. TurnPanelMixin._ask_triggers shows it; tests replace that method,
so no modal event loop runs in them."""

from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from Combat.Effects.triggers import HitFiring, TriggerChoice

from .styles import QSS

_WIDTH = 520


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
        for firing in self._firings:
            box = QCheckBox(firing.question)
            box.setObjectName("triggerBox")
            box.setChecked(True)
            box.setToolTip(getattr(firing.row.option, "tooltip", "") or "")
            layout.addWidget(box)
            self.boxes.append(box)
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
        if self._answer == "apply":
            return TriggerChoice(apply=checked)
        if self._answer == "edit":
            return TriggerChoice(edit=checked)
        return TriggerChoice()


def ask_triggers(parent: QWidget | None, firings: list[HitFiring]) -> TriggerChoice:
    """Ask about `firings` and wait for the answer."""
    prompt = TriggerPrompt(parent, firings)
    prompt.exec()
    return prompt.choice()
