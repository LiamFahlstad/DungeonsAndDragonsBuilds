"""The combat window's keyboard shortcuts, as data: what each key calls on
the app, and whether it stands down while a combo box has focus
(WindowMixin._build_shortcuts makes them). KEYBOARD_SHORTCUTS.md documents
them for the GM, and tests/test_shortcuts_doc.py keeps the two in step.

No Qt here: a key is the text QKeySequence reads ("Ctrl+Shift+C", "Esc",
"Right")."""

from dataclasses import dataclass

from Combat.Definitions import ActionCost


@dataclass(frozen=True)
class Shortcut:
    """One action and its keys: each key is a QShortcut that calls the
    app's method `action` with `args`. `combo_sensitive` ones are disabled
    while a combo box has focus (WindowMixin._update_combo_sensitive_shortcuts),
    so typing in it doesn't set them off. `name` is how the window finds the
    shortcuts made for it."""

    name: str
    keys: tuple[str, ...]
    action: str
    args: tuple = ()
    combo_sensitive: bool = True


SHORTCUTS: tuple[Shortcut, ...] = (
    # Log an Action / Bonus Action / Reaction use for the source.
    Shortcut("action", ("A",), "_add_action_use", (ActionCost.ACTION,)),
    Shortcut("bonus_action", ("B",), "_add_action_use", (ActionCost.BONUS_ACTION,)),
    Shortcut("reaction", ("R",), "_add_action_use", (ActionCost.REACTION,)),
    # Concentrating on the source, or off it; every target's conditions cleared.
    Shortcut("concentration", ("C",), "_shortcut_add_concentration"),
    Shortcut("remove_concentration", ("Ctrl+C",), "_shortcut_remove_concentration"),
    Shortcut(
        "clear_target_conditions",
        ("Ctrl+Shift+C",),
        "_shortcut_clear_target_conditions",
    ),
    Shortcut("use_cast", ("Shift+C",), "_show_custom_condition_dialog"),
    # Undo, leaving a field or the selection, and the turn work anywhere.
    Shortcut("undo", ("Ctrl+Z",), "_undo_last", combo_sensitive=False),
    Shortcut("clear_selection", ("Esc",), "_escape_pressed", combo_sensitive=False),
    Shortcut(
        "next_turn", ("Return", "Enter"), "_shortcut_next_turn", combo_sensitive=False
    ),
    Shortcut(
        "previous_turn",
        ("Shift+Return", "Shift+Enter"),
        "_shortcut_previous_turn",
        combo_sensitive=False,
    ),
    # 1-9: spend a spell slot of that level for the source.
    *(
        Shortcut("spell_slot", (str(level),), "_cast_spell_slot_level", (level,))
        for level in range(1, 10)
    ),
    # The next / previous combatant as the source, or as the target.
    Shortcut("next_source", ("N", "Right"), "_cycle_source", (1,)),
    Shortcut("previous_source", ("P", "Left"), "_cycle_source", (-1,)),
    Shortcut("next_target", ("Shift+N", "Down"), "_cycle_target", (1,)),
    Shortcut("previous_target", ("Shift+P", "Up"), "_cycle_target", (-1,)),
    # Whoever's turn it is as the source.
    Shortcut("select_active", ("Space",), "_shortcut_select_active_source"),
    # Into the Attack roll field, or the Damage, Heal or Temp HP field.
    Shortcut("focus_attack_roll", ("Shift+A",), "_focus_attack_roll_input"),
    Shortcut("focus_damage", ("D",), "_focus_damage_input"),
    Shortcut("focus_heal", ("H",), "_focus_heal_input"),
    Shortcut("focus_temp_hp", ("T",), "_focus_temp_hp_input"),
    # The source's More Info, the views and the dialogs.
    Shortcut("more_info", ("I",), "_show_more_info"),
    Shortcut("toggle_view", ("G",), "_toggle_view"),
    Shortcut("add_combatant", ("Ctrl+N",), "_show_add_combatant_dialog"),
    Shortcut("map_painter", ("Ctrl+M",), "_show_map_painter"),
    Shortcut("load_encounter", ("Ctrl+O",), "_show_load_encounter_dialog"),
)
