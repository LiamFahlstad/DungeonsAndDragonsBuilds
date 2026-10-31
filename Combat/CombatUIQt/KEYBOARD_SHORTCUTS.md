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
| **Shift+C** | Custom Condition | Open the Custom Condition dialog (same as the "Custom..." button under Conditions): type any condition, pick a duration (until removed, until the start/end of the source's or target's next turn, 1 round, 1 minute, ..., or a custom number of rounds/minutes/seconds) and an optional note, and it goes on every target. A timed one shows under "Timed Conditions" on the card and ends by itself. |
| **Ctrl+Z** | Undo | Undo the last thing done — a damage/heal/temp HP (on every target at once), a spell cast with everything it applied, a condition, an action use, Next Turn, an added combatant, ... — putting back the state from before it and removing its lines from the encounter and player logs. Repeat to go further back. |
| **Escape** | Leave Field / Clear Selection | In a text field, leave it so the other shortcuts work again. Otherwise clear both the source and target selection. |
| **Enter / Return** | Next Turn | Advance to the Next Combatant / Next Round, passing over turns where everyone is dead (Settings). Only active once combat has started (initiative phase does nothing); does nothing while a damage/heal/temp-HP field is focused (Enter submits the field instead, and **Esc** leaves it). |
| **Shift+Enter** | Previous Turn | Go back a turn after pressing Next by mistake (same as the "Previous" button). Straight after Next it undoes that press completely, like Ctrl+Z (the round, timers that ticked and action tallies that reset come back); after anything else it only moves the turn back, to the previous round's last turn from a round's first. Does nothing on round 1's first turn, or while a text field is focused. |
| **1-9** | Spend Spell Slot | Spend a spell slot of that level (1-9) for the selected source, for a spell not cast through the Cast Spell dialog (which spends its own slot, so don't press this as well). Says so under Source/Target if the source has no slots left at that level. |
| **N** / **Right arrow** | Next Source | Select the next combatant (in card order) as the source. Wraps around; starts at the first combatant if nothing is selected. |
| **P** / **Left arrow** | Previous Source | Select the previous combatant as the source. Wraps around. |
| **Shift+N** / **Down arrow** | Next Target | Select the next combatant as the sole target (replaces any current target selection). Wraps around. |
| **Shift+P** / **Up arrow** | Previous Target | Select the previous combatant as the sole target. Wraps around. |
| **Space** | Select Active Combatant | Select whoever's turn it currently is as the source — handy right after pressing Enter to advance the turn. Only active once combat has started. With Settings → "Source follows the turn" on (the default), this already happens on every turn change, so Space only matters after picking another source by hand. |
| **D** | Focus Damage Field | Jump the cursor into the Damage amount field (existing text selected, ready to overwrite). |
| **H** | Focus Heal Field | Jump the cursor into the Heal amount field. |
| **T** | Focus Temp HP Field | Jump the cursor into the Temp HP amount field. |
| **S** | Cast Spell | Open the Cast Spell dialog for the source (same as the "Cast Spell" button). |
| **F** | Enable Feature | Open the Enable Feature dialog for the source. |
| **I** | More Info | Open the source's More Info dialog. |
| **Ctrl+N** | Add Combatant | Open the Add Combatant dialog (same as clicking the "+ Add Combatant" button). |
| **Ctrl+O** | Load Encounter | Open the Load Encounter dialog (same as clicking the "Load Encounter..." button). |

The arrow keys are plain aliases for N/P/Shift+N/Shift+P — left/right mirrors the unmodified source shortcuts, up/down mirrors the Shift target shortcuts. A focused text field keeps its own left/right cursor movement regardless (see Notes).

Enter in the Damage field applies the damage with each target's resistance, vulnerability and immunity counted, like the Apply button; **Ignore Resist** applies exactly the amount typed. The Damage, Heal and Temp HP fields take a sum or a halving as well as a number (`8+5`, `24/2`). When something can't be applied, the reason shows under Source/Target instead of nothing happening.

## The Damage field

The type can go with the amount, and shows in the dropdown as you type. One letter is enough for the common types, two for the rest (`fo` Force, `po` Poison, `ps` Psychic), or spell it out.

| Typed | Means |
|-----|--------|
| `12` | 12 of the type in the dropdown (each source remembers the last type it dealt) |
| `12f`, `12 fi`, `12 fire` | 12 Fire |
| `8+5 fire` | 13 Fire |
| `24/2 fi` | 12 Fire (half, rounded down) |
| `7 pi + 3 fi` | 7 Piercing and 3 Fire, as one hit: one undo and one Concentration save, with each type's resistance counted |

**½ Saved** halves the next damage for every target. With several targets, each target's card has its own **½ Saved** instead, for those who made the save. It lasts one hit.

## The dialogs

In Cast Spell and Enable Feature, the cursor starts in the search box: type part of the name, **Enter** picks the first match (the caster's own spells come first), and **Enter** again casts it. Double-clicking an entry casts it too.

A full keyboard turn loop: **Enter** (advance turn; the source follows it, and turns where everyone is dead are skipped) → **Shift+N**/**Shift+P** (pick a target) → **D**/**H**/**T** (jump to an amount field) → type the amount → **Enter** (apply; the field empties and keeps the cursor, for the next hit) → **Esc** (leave the field) → **A**/**B**/**R** (log the action spent).

## Mouse

A left click on a card makes it the source; there is only ever one. A right click picks targets, with Ctrl and Shift working as they do in a Windows file list.

| Click on a card | Action |
|-----|--------|
| **Left click** | Make it the source (Ctrl and Shift make no difference). |
| **Right click** | Make it the only target. It becomes the anchor for Shift. |
| **Ctrl+Right click** | Add it to the targets, or remove it if it is already one. It becomes the anchor. |
| **Shift+Right click** | Target every card from the anchor to this one (in card order, down each column), replacing the current targets. The anchor stays where it was. |
| **Ctrl+Shift+Right click** | Add every card from the anchor to this one to the current targets. |

Right-clicking the card that's already the only target opens its quick menu: Damage, Heal and Temp HP (each jumps to its amount field) and the common conditions, a click to add or remove. It isn't modal, so any click elsewhere closes it.

Damage, heal, temp HP and conditions apply to every target.

## The turn column

Beside the cards during a fight: whose turn it is, who's next, what to remember this turn (a dying player's death save, what recharged, legendary actions coming back, traits that act at the start of a turn), and who has legendary actions ready.

Under that are the source's stat-block actions, for a monster. Click one and it counts the use (a recharge, a per-day use, a legendary action) and rolls: an attack against the one target's AC, using the d20 Roll section's Advantage or Disadvantage, with a natural 20 doubling the dice and a natural 1 missing. The damage every hit deals lands in the Damage field for **Enter** to apply, and a miss leaves it empty. Anything that depends on something (extra damage with Advantage, damage at the start of a turn) is shown as "Also:" for you to judge, and never added by itself. A damage type the monster chooses reads `type`, selected for you to type over. **↺** gives back one use. Recharges roll by themselves at the start of the monster's turn.

Stat blocks don't say how many legendary actions a monster has, so every legendary creature counts 3.

## Initiative

**Roll for Monsters** rolls everyone without a player's dice, leaving what's already typed. **Enter** in a field jumps to the next one that needs a number, and starts combat once they're all filled in.

## The players' screen

**Player Screen** opens the turn order for a second monitor or TV (full screen there, a window if there's only one screen): whose turn it is, who's next, conditions, players' Hit Points, and only Healthy, Bloodied or Defeated for monsters. A monster that's Invisible (or under Invisibility), Hidden, Heavily Obscured, in Darkness or behind Total Cover isn't listed, and spell badges and custom conditions on a monster stay private. **Esc** closes it.

## Notes

- **Text field protection**: Typing into the Damage/Heal/Temp HP amount fields naturally blocks these shortcuts. Qt lets a focused text field consume its own keystrokes, so typing amounts like "15" (or moving the cursor with the left/right arrows) won't accidentally trigger number/letter/arrow shortcuts.

- **Combo box handling**: Combo boxes (Roll Mode, Damage Type, Conditions, Visibility, Spell Slots, Action Economy) don't reserve their own keys the way a text field does, so a matching `QShortcut` would otherwise swallow the keystroke before the combo box ever sees it — silently breaking its native type-ahead search *and* its arrow-key item cycling, even though the shortcut's own handler correctly declines to act. Every shortcut above except Ctrl+Z and Escape is fully disabled (not just made into a no-op) for as long as a combo box has focus, via `QApplication.focusChanged`, and re-enabled the instant focus moves elsewhere — so both the combo box's normal keyboard behavior and the global shortcuts work correctly depending on what's actually focused.

- **Space and focused buttons**: Space normally activates whichever button has keyboard focus. Because the global Space shortcut is registered on the main window, it intercepts the keystroke first — pressing Space to select the active combatant does not also click a focused button.

- **Modal dialogs**: None of these shortcuts fire while a modal dialog is open. Each dialog (Cast Spell, Rules, Encounter Log, Player Log, Statistics, Settings, tie-break) is a separate top-level window, so the main window's shortcuts are inactive during dialog interaction.
