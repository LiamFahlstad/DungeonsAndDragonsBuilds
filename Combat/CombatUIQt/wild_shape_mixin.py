"""Wild Shape mixin for CombatAppQt: a Druid taking on one of their Beast
forms and leaving it (the dict side is Combat/WildShape.py).

Wild Shape is used from Enable Feature or from the Druid's card menu, which
lists their forms. It spends a use and a Bonus Action, gives the form's
temporary Hit Points and a "Wild Shape (<form>)" badge, and from then on the
card, the turn column's buttons, attacks against them and their saves are
the form's. They leave it with the card menu or by taking the badge off (a
Bonus Action), or by gaining an incapacitating condition, which a knock-out's
Unconscious is (ConditionsMixin). While in a form, they can't cast spells
(Combat/WildShape.can_cast_in_form). Each change is logged with an action, so
the player log's replay keeps a Druid in their form into the next encounter.
"""

from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QMenu

from CharacterContent.Features.ClassFeatures.Druid.WildShapeForms import (
    format_wild_shape_form,
    wild_shape_temp_hp,
)
from Combat.Definitions import Action
from Combat.Effects.active_effects import FEATURE, describe, note_origin
from Combat.WildShape import (
    assume_form,
    can_cast_in_form,
    current_form,
    form_badge,
    known_forms,
    leave_form,
    wild_shape_feature,
)
from Model.Character import Character

from .conditions_mixin import incapacitates
from .effect_options import feature_action_cost
from .state import CombatWindowState
from .styles import QSS
from .undo import undoable

# A Wild Shape badge's color, apart from other features' blue.
WILD_SHAPE_COLOR = "#4a8a4c"


class WildShapeMixin(CombatWindowState):
    """Mixin for Wild Shape."""

    def _wild_shape_uses_left(self, char: dict) -> int:
        feature = wild_shape_feature(char)
        sheet = char.get("_stat_block")
        if feature is None or not isinstance(sheet, Character):
            return 0
        used = char.get("feature_uses_used", {}).get(feature.name, 0)
        return max(feature.number_of_uses(sheet) - used, 0)

    def _wild_shape_menu(self, char: dict) -> QMenu | None:
        """A menu of char's Wild Shape forms, the one it's in checked, and a
        way out of it. None for a combatant with no forms."""
        sheet = char.get("_stat_block")
        forms = known_forms(sheet) if isinstance(sheet, Character) else {}
        if not forms:
            return None
        left = self._wild_shape_uses_left(char)
        menu = QMenu(f"Wild Shape ({left} left)", self._window)
        menu.setStyleSheet(QSS)
        form_now = current_form(char)
        for form in forms:
            action = menu.addAction(form)
            assert action is not None  # addAction with a text always makes one
            action.setCheckable(True)
            action.setChecked(form == form_now)
            # With no uses left, _assume_wild_shape asks whether to anyway.
            action.triggered.connect(
                lambda _=False, c=char, f=form: self._assume_wild_shape(c, f)
            )
        if form_now is not None:
            menu.addSeparator()
            menu.addAction(
                f"Leave {form_now} form", lambda c=char: self._leave_wild_shape(c)
            )
        return menu

    def _pick_wild_shape_form(self, char: dict):
        """Ask which form char takes, at the mouse (Enable Feature's Wild Shape)."""
        menu = self._wild_shape_menu(char)
        if menu is None:
            self._show_status(f"No Wild Shape: {char['name']} knows no forms.")
            return
        menu.exec(QCursor.pos())

    @undoable
    def _assume_wild_shape(self, char: dict, form: str):
        """char uses Wild Shape to take on `form`: a use and a Bonus Action,
        out of any form it's in, the form's temporary Hit Points and badge."""
        feature = wild_shape_feature(char)
        sheet = char.get("_stat_block")
        if feature is None or not isinstance(sheet, Character):
            return
        # Incapacitated: "You can't take any action, Bonus Action, or Reaction."
        incapacitated = [c for c in char["conditions"] if incapacitates(c)]
        if incapacitated:
            self._show_status(
                f"No Wild Shape: {char['name']} is {min(incapacitated)}"
                " and can't take a Bonus Action."
            )
            return
        action_cost = feature_action_cost(feature)
        lacks = [
            (
                f"{feature.name}: no uses left"
                if self._wild_shape_uses_left(char) <= 0
                else None
            ),
            self._action_lack(char, action_cost),
        ]
        if not self._go_ahead_anyway(char, f"Take {form} form", lacks):
            return
        self._count_feature_use(char, feature.name, counts_uses=True)
        if action_cost is not None:
            self._add_action_use(action_cost, char, ask=False)
        if current_form(char) is not None:
            self._leave_wild_shape(char, reason="Wild Shape again")

        assume_form(char, form)
        self._log_event(
            f"{char['name']} takes {form} form",
            character=char["name"],
            action=Action.WILD_SHAPE,
            value={"form": form},
        )
        self._give_temp_hp(char, wild_shape_temp_hp(sheet), source=None)
        badge = form_badge(form)
        describe(
            char,
            badge,
            format_wild_shape_form(known_forms(sheet)[form], sheet),
            WILD_SHAPE_COLOR,
            FEATURE,
        )
        self._add_condition_to(char, badge, source=char)
        note_origin(char, badge, source=feature.name, caster=char["name"])
        self._rebuild_card(char)
        self._refresh_views()

    @undoable
    def _leave_wild_shape(
        self, char: dict, reason: str | None = None, *, ask: bool = True
    ):
        """char leaves its form: by choice (reason None), a Bonus Action, or
        because of `reason` ("Unconscious", "Wild Shape again"), no action.
        With its Bonus Action used already, the GM is asked whether to leave
        anyway, unless the form's badge is already off (ask=False)."""
        form_now = current_form(char)
        if form_now is None:
            return
        feature = wild_shape_feature(char)
        action_cost = feature_action_cost(feature) if feature is not None else None
        pays = reason is None and action_cost is not None
        if (
            pays
            and ask
            and not self._go_ahead_anyway(
                char, f"Leave {form_now} form", [self._action_lack(char, action_cost)]
            )
        ):
            return
        form = leave_form(char)
        if form is None:
            return
        if pays:
            assert action_cost is not None  # pays says so
            self._add_action_use(action_cost, char, ask=False)
        because = f" ({reason})" if reason else ""
        self._log_event(
            f"{char['name']} leaves {form} form{because}",
            character=char["name"],
            action=Action.LEAVE_WILD_SHAPE,
            value={"form": form},
        )
        self._remove_condition_from(char, form_badge(form), source=char)
        self._rebuild_card(char)
        self._refresh_views()

    def _can_cast_or_say(self, caster: dict, spell_name: str) -> bool:
        """Whether caster can cast `spell_name`, saying why not if it can't."""
        if can_cast_in_form(caster, spell_name):
            return True
        self._show_status(
            f"No spell cast: {caster['name']} can't cast {spell_name}"
            f" in {current_form(caster)} form."
        )
        return False
