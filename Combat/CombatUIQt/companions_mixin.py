"""Companions mixin for CombatAppQt: a player's companions (the dict side is
Combat/Companions.py) being summoned, dying with their owner, coming back in
the next encounter as they were, and joining a fight that didn't have them.

A companion is summoned from its owner's Enable Feature (Drake Companion,
Reanimated Companion) or from its card's or its owner's card menu, which also
offers the choices made when it's summoned (a drake's Draconic Essence). It
spends the feature's use and its Action, or a spell slot once the use is
spent, as the features allow, and brings the companion out at full Hit Points.
Unchecking "Hidden from players" instead shows one that's already out without
spending anything. The feature's use and the slot are logged with actions, so
the player log's replay spends them for the rest of the day too.
"""

import json
from pathlib import Path

from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QMenu

import Combat.PlayerLog as PlayerLog
from Combat.Companions import (
    CHOICE_KEY,
    carried_state,
    companion_feature,
    last_seen,
    owner_name,
    place_after_owners,
    set_stat_block,
    summon,
)
from Combat.EncounterLogs import LogJSONEncoder
from Combat.PlayerCombatant import combatant_from_stat_block, companions_of
from Model.Character import Character
from Model.Content.Feature import Feature
from Model.Creatures.Combatants import BasicCombatantData

from .effect_options import feature_action_cost
from .state import CombatWindowState
from .stats import _default_stats
from .styles import QSS
from .undo import undoable


class CompanionsMixin(CombatWindowState):
    """Mixin for players' companions."""

    def _companion_owner(self, char: dict) -> dict | None:
        """The player in the window whose companion char is, if any."""
        name = owner_name(char)
        if name is None:
            return None
        return next(
            (c for c in self.characters if c.get("_is_player") and c["name"] == name),
            None,
        )

    def _owner_companions(self, owner: dict) -> list[dict]:
        return [c for c in self.characters if owner_name(c) == owner["name"]]

    def _companion_source(
        self, companion: dict
    ) -> tuple[dict, Character, Feature] | None:
        """(owner, the owner's character, the feature that summons it)."""
        owner = self._companion_owner(companion)
        sheet = owner.get("_stat_block") if owner is not None else None
        if owner is None or not isinstance(sheet, Character):
            return None
        feature = companion_feature(sheet, companion)
        return None if feature is None else (owner, sheet, feature)

    def _summon_uses_left(self, owner: dict, feature: Feature) -> int:
        used = owner.get("feature_uses_used", {}).get(feature.name, 0)
        return max(feature.number_of_uses(owner["_stat_block"]) - used, 0)

    @staticmethod
    def _lowest_slot(owner: dict) -> int | None:
        """The lowest level owner has a spell slot (or Pact Magic slot) of."""
        levels = [
            int(level)
            for pool in ("spell_slots", "pact_slots")
            for level, left in owner.get(pool, {}).items()
            if left > 0 and int(level) >= 1
        ]
        return min(levels, default=None)

    def _summon_cost_text(self, owner: dict, feature: Feature) -> str:
        if self._summon_uses_left(owner, feature) > 0:
            return "1 use left"
        level = self._lowest_slot(owner)
        return f"a level {level} slot" if level is not None else "no uses or slots"

    def _add_summon_actions(self, menu: QMenu, char: dict):
        """On a companion's card, or its owner's: summon it, with a choice
        (Draconic Essence) when the feature has them, the current one checked."""
        if owner_name(char) is not None:
            companions = [char]
        elif char.get("_is_player"):
            companions = self._owner_companions(char)
        else:
            companions = []
        for companion in companions:
            found = self._companion_source(companion)
            if found is None:
                continue
            owner, sheet, feature = found
            if not self._may_summon_again(companion, feature, sheet):
                continue
            label = f"Summon {feature.name} ({self._summon_cost_text(owner, feature)})"
            choices = feature.companion_choices(sheet)
            menu.addSeparator()
            if not choices:
                menu.addAction(
                    label, lambda _=False, c=companion: self._summon_companion(c, None)
                )
                continue
            submenu = menu.addMenu(label)
            assert submenu is not None  # addMenu with a title always makes one
            submenu.setStyleSheet(QSS)
            for choice in choices:
                action = submenu.addAction(choice)
                assert action is not None  # addAction with a text always makes one
                action.setCheckable(True)
                action.setChecked(companion.get(CHOICE_KEY) == choice)
                action.triggered.connect(
                    lambda _=False, c=companion, ch=choice: self._summon_companion(
                        c, ch
                    )
                )

    @staticmethod
    def _may_summon_again(companion: dict, feature: Feature, sheet: Character) -> bool:
        """False while companion is out, when its feature can't make another
        one while it's present (a Reanimated Companion)."""
        out = not companion.get("hidden_from_players") and companion["hp"] > 0
        return not out or feature.companion_rules(sheet).summon_again_replaces

    def _pick_companion_summon(self, owner: dict, feature: Feature):
        """Enable Feature's summon: ask the choice at the mouse when there is
        one, else summon right away."""
        sheet = owner["_stat_block"]
        stat_block = feature.companion(sheet)
        assert stat_block is not None
        companion = next(
            (
                c
                for c in self._owner_companions(owner)
                if c.get("combatant_type") == stat_block.combatant_type
            ),
            None,
        )
        if companion is None:
            self._show_status(
                f"No {stat_block.combatant_type} in this encounter:"
                " add it with Add Combatant first."
            )
            return
        if not feature.companion_choices(sheet):
            self._summon_companion(companion, None)
            return
        menu = QMenu(self._window)
        menu.setStyleSheet(QSS)
        self._add_summon_actions(menu, companion)
        menu.exec(QCursor.pos())

    @undoable
    def _summon_companion(self, companion: dict, choice: str | None):
        """The owner summons companion anew (with `choice`): the feature's use
        or, with none left, their lowest spell slot, and its Action; the
        companion comes out at full Hit Points, for the players to see."""
        found = self._companion_source(companion)
        if found is None:
            return
        owner, sheet, feature = found
        if self._char_death_state(owner) != "alive":
            self._show_status(f"No summon: {owner['name']} is down.")
            return
        if not self._may_summon_again(companion, feature, sheet):
            self._show_status(
                f"No summon: {companion['name']} is still out, and"
                f" {feature.name} can't make another while it is."
            )
            return
        if self._summon_uses_left(owner, feature) > 0:
            self._count_feature_use(owner, feature.name, counts_uses=True)
        else:
            level = self._lowest_slot(owner)
            if level is None:
                self._show_status(
                    f"No summon: {owner['name']} has no use of {feature.name}"
                    " and no spell slot left."
                )
                return
            # Not a use of the feature: the replay would count it as one.
            self._spend_slot(owner, level)
        action_cost = feature_action_cost(feature)
        if action_cost is not None:
            self._add_action_use(action_cost, owner)
        summon(companion, sheet, feature, choice)
        chosen = f" ({choice})" if choice else ""
        self._log_event(
            f"{owner['name']} summons {companion['name']}{chosen}",
            character=companion["name"],
        )
        self._rebuild_cards()
        self._refresh_views()

    def _companions_die_with(self, owner: dict):
        """owner died: each companion of theirs that's out drops to 0 Hit
        Points (a Reanimated Companion's Death Burst goes off; a drake is
        gone)."""
        for companion in self._owner_companions(owner):
            if companion.get("hidden_from_players") or companion["hp"] <= 0:
                continue
            companion["hp"] = 0
            companion["temp_hp"] = 0
            self._apply_bloodied_condition(companion)
            traits = companion.get("traits") or []
            burst = any(_ability_name(t) == "Death Burst" for t in traits)
            self._log_event(
                f"{companion['name']} drops to 0 HP: {owner['name']} died"
                + (" (its Death Burst goes off)" if burst else ""),
                character=companion["name"],
            )
            self._rebuild_card(companion)

    def _carry_companions_over(self, log_path: Path):
        """Start the companions in the encounter log at `log_path` (one not
        started yet) as the party's last encounter left them: still out or
        not, their Hit Points, conditions and choice. A long rest since ends a
        Reanimated Companion and rests a drake (Feature.companion_rules)."""
        if not self.player_log_file:
            return
        ref = PlayerLog.log_ref(self.player_log_file, log_path)
        # Each encounter log played, with whether a long rest came after it.
        played: list[tuple[dict, bool]] = []
        for session in self.player_log_data["sessions"]:
            if session.get("type") == PlayerLog.LONG_REST:
                played = [(data, True) for data, _ in played]
                continue
            if not session.get("log") or session["log"] == ref:
                continue
            path = PlayerLog.resolve_log(self.player_log_file, session["log"])
            if path.exists():
                played.append((json.loads(path.read_text(encoding="utf-8")), False))
        for companion in self.characters:
            # Without its owner here there's no feature to say what it is.
            found = self._companion_source(companion)
            if found is None:
                continue
            _, sheet, feature = found
            rules = feature.companion_rules(sheet)
            logs = [(d, r) for d, r in played if not (r and rules.ends_on_long_rest)]
            seen = last_seen(companion["name"], logs)
            if seen is None:
                continue
            state = carried_state(*seen)
            if state.get(CHOICE_KEY):
                set_stat_block(companion, sheet, feature, state[CHOICE_KEY])
            companion.update(state)
            if not companion["hidden_from_players"]:
                del companion["hidden_from_players"]

    def _missing_party_companions(self) -> list[tuple[str, BasicCombatantData]]:
        """(the name it'd have, its stat block) for each companion of a player
        in the window that this encounter doesn't have."""
        names = {c["name"] for c in self.characters}
        missing = []
        for player in self.characters:
            sheet = player.get("_stat_block")
            if not player.get("_is_player") or not isinstance(sheet, Character):
                continue
            for stat_block in companions_of(sheet):
                name = combatant_from_stat_block(stat_block)["name"]
                if name not in names:
                    missing.append((name, stat_block))
        return missing

    @undoable
    def _add_party_companion(self, stat_block: BasicCombatantData):
        """Add a player's companion the encounter didn't have (Add Combatant),
        hidden until it's summoned, after its owner in the turn order."""
        char = json.loads(
            json.dumps(combatant_from_stat_block(stat_block), cls=LogJSONEncoder)
        )
        char["stats"] = _default_stats()
        self.characters.append(char)
        self._log_event(
            f"{char['name']} added to the encounter", note_turn=False, public=False
        )
        if self.phase == "COMBAT":
            # Whoever's turn it is keeps it.
            current = self.initiative_order[self.current_turn_idx]
            others = [c for c in self.initiative_order if c is not char]
            self.initiative_order = place_after_owners(others, [char])
            self.characters[:] = place_after_owners(
                [c for c in self.characters if c is not char], [char]
            )
            at = next(i for i, c in enumerate(self.initiative_order) if c is current)
            self.current_turn_idx = self._turn_span(at)[0]
            self._rebuild_cards()
            self._refresh_turn()
            self._refresh_views()
        elif self._companion_owner(char) is None:
            self._add_initiative_row([char])
            self._check_start_button()


def _ability_name(ability) -> str | None:
    """A stat-block ability's name, as a MonsterAbility or as a log stores it."""
    if isinstance(ability, dict):
        return ability.get("name")
    return getattr(ability, "name", None)
