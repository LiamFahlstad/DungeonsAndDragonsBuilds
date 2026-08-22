# Combat UI Keyboard Shortcuts

All shortcuts listed below are global (registered on the main combat window in `window_mixin.py`) and only fire while the main combat window itself is active — not while a modal dialog (Cast Spell, Rules, Encounter Log, Player Log, Statistics, tie-break) is open. Each dialog is its own top-level window, so the main window's shortcuts aren't active during modal interaction.

## Shortcut Reference

| Key | Action | Description |
|-----|--------|-------------|
| **A** | Log Action | Log an Action use for the selected source. No-op if no source is selected. |
| **B** | Log Bonus Action | Log a Bonus Action use for the selected source. No-op if no source is selected. |
| **R** | Log Reaction | Log a Reaction use for the selected source. No-op if no source is selected. |
| **C** | Concentrating (self) | Add the Concentrating condition to the selected source (self-applied). No-op if no source is selected. |
| **Ctrl+C** | Remove Concentrating | Remove Concentrating from the selected source. No-op if no source is selected. |
| **Ctrl+Shift+C** | Clear Target Conditions | Clear every condition from every target. No-op if no targets are selected. |
| **Ctrl+Z** | Undo | Undo the last logged action. |
| **Escape** | Clear Selection | Clear both the source and target selection. |
| **Enter / Return** | Next Turn | Advance to the Next Combatant / Next Round. Only active once combat has started (initiative phase does nothing); does nothing while a damage/heal/temp-HP field is focused (Enter submits the field instead). |
| **1-9** | Cast Spell Slot | Cast a spell slot of that level (1-9) for the selected source. No-op if the source has no remaining slots at that level. |
| **N** / **Right arrow** | Next Source | Select the next combatant (in card order) as the source. Wraps around; starts at the first combatant if nothing is selected. |
| **P** / **Left arrow** | Previous Source | Select the previous combatant as the source. Wraps around. |
| **Shift+N** / **Down arrow** | Next Target | Select the next combatant as the sole target (replaces any current target selection). Wraps around. |
| **Shift+P** / **Up arrow** | Previous Target | Select the previous combatant as the sole target. Wraps around. |
| **Space** | Select Active Combatant | Select whoever's turn it currently is as the source — handy right after pressing Enter to advance the turn. Only active once combat has started. |
| **D** | Focus Damage Field | Jump the cursor into the Damage amount field (existing text selected, ready to overwrite). |
| **H** | Focus Heal Field | Jump the cursor into the Heal amount field. |
| **T** | Focus Temp HP Field | Jump the cursor into the Temp HP amount field. |
| **Ctrl+N** | Add Combatant | Open the Add Combatant dialog (same as clicking the "+ Add Combatant" button). |

The arrow keys are plain aliases for N/P/Shift+N/Shift+P — left/right mirrors the unmodified source shortcuts, up/down mirrors the Shift target shortcuts. A focused text field keeps its own left/right cursor movement regardless (see Notes).

A full keyboard turn loop: **Enter** (advance turn) → **Space** (select the new active combatant as source) → **Shift+N**/**Shift+P** (pick a target) → **D**/**H**/**T** (jump to an amount field) → type the amount → **Enter** (apply) → **A**/**B**/**R** (log the action spent).

## Notes

- **Text field protection**: Typing into the Damage/Heal/Temp HP amount fields naturally blocks these shortcuts. Qt lets a focused text field consume its own keystrokes, so typing amounts like "15" (or moving the cursor with the left/right arrows) won't accidentally trigger number/letter/arrow shortcuts.

- **Combo box handling**: Combo boxes (Roll Mode, Damage Type, Conditions, Visibility, Spell Slots, Action Economy) don't reserve their own keys the way a text field does, so a matching `QShortcut` would otherwise swallow the keystroke before the combo box ever sees it — silently breaking its native type-ahead search *and* its arrow-key item cycling, even though the shortcut's own handler correctly declines to act. Every shortcut above except Ctrl+Z and Escape is fully disabled (not just made into a no-op) for as long as a combo box has focus, via `QApplication.focusChanged`, and re-enabled the instant focus moves elsewhere — so both the combo box's normal keyboard behavior and the global shortcuts work correctly depending on what's actually focused.

- **Space and focused buttons**: Space normally activates whichever button has keyboard focus. Because the global Space shortcut is registered on the main window, it intercepts the keystroke first — pressing Space to select the active combatant does not also click a focused button.

- **Modal dialogs**: None of these shortcuts fire while a modal dialog is open. Each dialog (Cast Spell, Rules, Encounter Log, Player Log, Statistics, tie-break) is a separate top-level window, so the main window's shortcuts are inactive during dialog interaction.
