"""d20 roll mixin for CombatAppQt (advantage/neutral/disadvantage)."""

import random


class RollsMixin:
    """Mixin for ad-hoc d20 rolls with advantage/disadvantage support."""

    def _roll_d20(self):
        mode = self.roll_mode_combo.currentText()

        if mode == "Neutral":
            roll = random.randint(1, 20)
            self.roll_result_label.setText(
                f'<span style="color:#eaeaea;">{roll}</span>'
            )
            return

        first, second = random.randint(1, 20), random.randint(1, 20)
        if mode == "Advantage":
            keep, drop = max(first, second), min(first, second)
            keep_color = "#2ecc71"
        else:  # Disadvantage
            keep, drop = min(first, second), max(first, second)
            keep_color = "#e74c3c"

        self.roll_result_label.setText(
            f'<span style="color:{keep_color}; font-weight:bold;">{keep}</span>'
            f'&nbsp;&nbsp;<span style="color:#666;">{drop}</span>'
        )
