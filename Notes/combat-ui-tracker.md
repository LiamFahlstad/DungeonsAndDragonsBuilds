# Combat UI tracker

What to test in the combat UI, and what could come next. Tick items off as you go, and add new ones here. Bugs found along the way belong in [discovered-issues.md](discovered-issues.md), the shared bug list; the DI numbers below point to it.

Started 2026-10-31, after the work in commit `cedb8819`. All automated tests ran offscreen, so nothing below had been tried in the real window yet. Start with section 1: most of the keyboard flow depends on it.

## Test

### 1. Test first (real window only)

- [ ] Click in Damage, type `3 fi`, press Enter: damage applies and the turn does not advance.
- [ ] Heal and Temp HP: type an amount, press Enter: it applies.
- [ ] Initiative: type a number, press Enter: the cursor jumps to the next empty field.
- [ ] Initiative: Enter on the last field starts combat.
- [ ] In a text field, press Esc: you leave the field and keep source and target.
- [ ] Press Enter after Esc: the turn advances.
- [ ] Press Esc with no field focused: source and target clear.
- [ ] Click a monster action so the cursor lands in Damage, then press Ctrl+Z: the action is undone.

### 2. Damage and resistances

- [ ] `12f`, `12 fi` and `12 fire` all give 12 Fire. The dropdown changes as you type.
- [ ] `fo` gives Force, `po` Poison, `ps` Psychic.
- [ ] `8+5 fire` gives 13 Fire.
- [ ] `24/2 fi` gives 12 Fire.
- [ ] `7 pi + 3 fi` gives two log lines, one undo and one Concentration save.
- [ ] `2d6` or `12 zz`: nothing applies and the status line says why.
- [ ] The field empties after applying, so a second Enter does not hit again.
- [ ] Each source remembers its type: deal Fire with one source, switch, switch back.
- [ ] A source with no remembered type shows a blank dropdown, not the last source's type.
- [ ] Hit a resistant monster with Apply: half damage, and the log says "(resisted)".
- [ ] Same hit with Ignore Resist: full damage.
- [ ] Deal 10 Poison to Obmar, Gabriel or Thum: they take 5.
- [ ] Deal 10 Necrotic to Edmund: he takes 5.
- [ ] Check their cards now show a Resist row.

### 3. ½ Saved

- [ ] One target: press the panel's Saved?, then apply: half damage.
- [ ] Several targets: each card has its own Saved?, and only marked ones take half.
- [ ] A marked button turns gold and reads ½ Saved; unmarked ones read Saved?.
- [ ] The mark clears after one hit.
- [ ] Undo a saved hit: the mark and the typed amount both come back.
- [ ] Saved plus resistance: 25 Fire becomes 12, then 6.

### 4. Spells and features

- [ ] Press S: Cast Spell opens with the caster's own spells first.
- [ ] Type part of a name, press Enter: it picks the first match. Enter again casts.
- [ ] Double-click a spell: it casts.
- [ ] Casting spends the lowest slot that fits.
- [ ] Picking a higher slot logs "at level N".
- [ ] "No slot" spends nothing. A cantrip spends nothing.
- [ ] With no slots left, the button reads "Cast without a slot".
- [ ] Undo a cast: the slot and the spell both come back in one step.
- [ ] Open Cast Spell on a Yellow Cape Enforcer. This used to crash the app.
- [ ] Press F: Enable Feature opens, and Enter and double-click work the same way.
- [ ] Press I: More Info opens.
- [ ] Habit check: don't press 1-9 after casting, because Cast Spell has already spent the slot.

### 4b. Custom Effect (saves for several targets)

- [ ] Pick several targets, press Shift+C or Custom: the dialog fits your screen.
- [ ] The DC starts at the source's spell save DC.
- [ ] A Fireball: Dexterity, `8d6 fire`, half on save, Apply: each target rolls and takes the right amount.
- [ ] A target resistant to the damage takes half as well.
- [ ] A Hold Person: Wisdom, condition Paralyzed, duration: only those who fail get it.
- [ ] A player's row: type their total, or leave it blank to roll for them.
- [ ] A Stunned target fails a Dexterity save without rolling.
- [ ] A Restrained target rolls Dexterity with Disadvantage.
- [ ] A creature immune to the condition doesn't get it.
- [ ] Legendary Resistance box turns a failed save into a success.
- [ ] One Ctrl+Z takes back all of it.
- [ ] Each target's roll is in the encounter log.
- [ ] The dialog remembers the last ability and half-on-save setting.
- [ ] Name shows in the log and the turn column.
- [ ] The damage type dropdown starts on the source's last type, and typing `fire` changes it.
- [ ] A spell slot and an action are spent, and undo with the effect.
- [ ] "Source concentrates": losing concentration takes the condition off the targets.
- [ ] A Cast Spell concentration spell's badge also comes off when concentration ends.
- [ ] Repeat save: a monster rolls at the end of its turn, and a save ends the condition.
- [ ] Repeat save: a player gets a reminder in the turn column instead.
- [ ] Untick "Count resistances": full damage on a resistant target.
- [ ] The dialog still fits with a full party as targets.
- [ ] Two casters hold the same condition: it stays until both end.
- [ ] A condition you gave by hand stays when an effect ends.
- [ ] A late caster's 1-round effect lasts a full round.
- [ ] A player's reminder still shows when a dead monster's turn follows theirs.
- [ ] Close the app mid-fight and continue: a player's spells, timers and repeat saves come back.
- [ ] A ½ Saved mark with no saving throw: half damage and no condition.

### 5. Concentration

- [ ] Hit a concentrating creature: a strip appears on its card with no popup.
- [ ] The strip shows the right DC: half the damage, minimum 10.
- [ ] Roll, Kept and Lost each work and are logged.
- [ ] Lost ends the spell.
- [ ] Two hits give two strips.
- [ ] Knocking the creature out clears the strip.
- [ ] Casting a new concentration spell clears the old strip.
- [ ] Leave a player's save unresolved, close the app, continue the fight: the strip comes back.
- [ ] With the setting on, monsters roll their own saves and players' stay on the card.

### 6. Monster turns

- [ ] On a monster's turn, its actions appear in the turn column with their numbers.
- [ ] Attack click: "vs AC", HIT or MISS, and the damage is filled in for Enter to apply.
- [ ] A miss leaves the Damage field empty.
- [ ] Natural 20 doubles the dice, not the bonus. Natural 1 always misses.
- [ ] The d20 Roll dropdown's Advantage and Disadvantage apply to attacks.
- [ ] Goblin Warrior Scimitar rolls only `1d6 + 2`, with the Advantage bonus shown as "Also:".
- [ ] Stirge rolls only the bite.
- [ ] Behir Swallow fills in no damage.
- [ ] A monster-chosen type shows `type`, selected, and Enter refuses until you type over it.
- [ ] Recharge abilities go spent when used and roll by themselves at the start of its turn.
- [ ] ↺ gives back one use. Try a 3/Day ability.
- [ ] Legendary actions count down, come back at the start of its turn, and show on other turns as ready.
- [ ] Legendary Resistance counts down and undoes cleanly.
- [ ] Undo a turn and press Next: a failed recharge keeps the same roll.
- [ ] An unapplied roll doesn't carry into the next turn.

### 7. Turns and reminders

- [ ] Source follows the turn, and a group's first member becomes the source.
- [ ] Targets clear on each turn.
- [ ] "Now", "Next" and "then" read correctly, including wrapping into the next round.
- [ ] Next passes dead monsters. A dying player still gets a turn.
- [ ] Previous skips the same dead turns.
- [ ] The Next button says "Next Round" when only dead combatants are left this round.
- [ ] Reminders appear: dying player, recharge results, legendary actions back, start-of-turn traits like Regeneration.

### 8. Initiative

- [ ] Roll for Monsters leaves players blank and keeps anything already typed.
- [ ] The cursor lands on the first player's field afterwards.
- [ ] With the tie setting off, ties go by Dexterity with no popup.

### 9. Player screen

- [ ] It opens full screen on your second monitor or TV.
- [ ] With one screen, it opens as a normal window.
- [ ] The text is readable from the table. Sizes were a guess, so note it here if they're wrong.
- [ ] Everyone shows an HP bar with numbers, in the same colors as your cards, and Defeated once dead.
- [ ] An initiative group shows a bar for each member it can see.
- [ ] Everyone shows size and speed under their name, and monsters show their AC too.
- [ ] A big fight still fits on the TV. Rows are taller now and the screen can't scroll, so 10+ rows or a large group may run off the bottom.
- [ ] Invisible and Invisibility hide a monster.
- [ ] Heavily Obscured, Darkness and Total Cover hide it too. See "Decisions to make".
- [ ] Spell badges and custom conditions on monsters don't show.
- [ ] On a hidden monster's turn, NOW stays on the last visible row.
- [ ] Player Screen button closes it. X closes it too, and the button then reopens it first try.
- [ ] Closing the main window closes it and ends the app.
- [ ] Esc closes it only if that window has keyboard focus, which it may not on a TV.

### 9b. Player link

The page ran in headless Chrome on this PC, but nothing has crossed a network or run on a phone yet. Do step 0 of [player-web-view-plan.md](player-web-view-plan.md) first: if a phone can't reach this PC, nothing below will work.

- [ ] Player Link opens with the Wi-Fi address picked, not a VPN, WSL or VirtualBox one. If it's wrong, picking another address moves the link.
- [ ] Copy puts the link on the clipboard.
- [ ] Two phones and a laptop open the link, and a damage hit shows up on all three within a second or two.
- [ ] Lock a phone during a turn and unlock it: it catches up.
- [ ] Stop the server: the Lost connection banner appears within a few seconds. Open Player Link again: it clears.
- [ ] Close the dialog: the phones keep updating. Player Link then shows the same link.
- [ ] A second copy of the app says the port is in use, in the dialog.
- [ ] End Encounter: every phone says "Waiting for the fight to start", with no rows.
- [ ] Load Encounter: every phone drops the last fight.
- [ ] A hidden monster doesn't show on any phone.
- [ ] Encounter log opens on a phone, newest first, and stays open as lines arrive.
- [ ] A hit from a hidden monster isn't in the log, and doesn't appear after it's revealed. The target's HP still drops, so players can tell something happened.
- [ ] A custom condition on a monster isn't in the log; Prone and Bloodied are.
- [ ] Add Combatant, during setup or a fight, isn't announced in the log.
- [ ] Reading older lines on a phone, a new line doesn't move what you're reading.
- [ ] Undo takes the line back off the phones.
- [ ] Open it on both iPhone and Android, since only a real device tests their browsers.
- [ ] iPhone: leave a quiet fight open for a minute. No banner should appear, which shows Safari handles "nothing changed" properly.
- [ ] Put the PC to sleep and wake it, then turn its Wi-Fi off and on: do phones reconnect? If not, Stop and reopen Player Link should recover them.

### 10. Panel, menu and settings

- [ ] Right-click a card, then right-click it again: the quick menu opens.
- [ ] Menu conditions add and remove in one click.
- [ ] Menu Damage, Heal and Temp HP jump to the right field.
- [ ] "More: Visibility, Slots, Actions" expands and stays that way after a restart.
- [ ] The buttons don't move when a status message appears.
- [ ] Every setting survives a restart.
- [ ] Unchecked and checked boxes are easy to tell apart.
- [ ] The window fits your screen with the new turn column. Cards have less room on a small display.

## Decisions to make

- [ ] **Halving a two-type hit.** ½ Saved halves each type, so a saved `7 pi + 3 fi` deals 4. Halving the total would give 5.
- [ ] **Legendary actions per round.** Stat blocks don't store this, so every legendary creature gets 3.
- [ ] **Who gets hidden from players.** Heavily Obscured, Darkness and Total Cover hide a monster, so a dark room could empty the list.
- [ ] **Settings left at the old behavior.** These stay off unless you turn them on:
   - Roll monsters' Concentration saves
   - Jump to Damage after picking a target
   - Skip the initiative tie dialog

## Possible improvements

### Rules still missing

- [ ] **Death rules (DI-002, DI-003, DI-005).** Not built yet:
   - Damage at 0 HP should add a failed death save.
   - Massive damage should kill outright.
   - Death saves need natural 20 and natural 1 buttons.
- [ ] **Warlock pact slots (DI-025).** Not tracked in combat. They need their own short-rest handling, and multiclass characters have both kinds. No current party member needs it.
- [ ] **Bloodied at 0 HP (DI-007).** It's removed when a creature drops to 0 HP. A card set to 0 HP by hand kept Bloodied in a test shot, so check this one.

### Faster play

- [x] **Roll monsters' saves for you.** Done as the Custom Effect dialog.
- [ ] **Save ability on spells.** Cast Spell could open Custom Effect with the spell's ability, damage and condition filled in.
- [ ] **End the turn from the Damage field.** After a monster's last hit you need Esc, then Enter. Enter in an empty field could advance the turn, but a double press would skip a turn, so it was left out.
- [ ] **Reset Advantage after each attack.** The dropdown stays on Advantage, which is easy to forget.
- [ ] **Several targets for an attack.** With 2+ targets it rolls but can't call HIT or MISS. It could judge each target.
- [ ] **Lair and mythic actions in the turn column.** Only actions, bonus actions, reactions and legendary actions show today.
- [ ] **Player weapons in the turn column.** The data is loaded, and it would help when you roll for an NPC ally.
- [ ] **Show a monster's conditions and riders better.** "Also:" text is cut at 130 characters, with the full text in the tooltip.

- [ ] **Per-target save features.** Evasion, Magic Resistance and similar aren't counted; the dialog has one roll mode for all targets.
- [ ] **Exhaustion levels.** Only the condition is tracked, so saves can't subtract 2 per level, and a second Exhaustion doesn't stack.
- [ ] **Cast Spell badges as conditions.** A Hold Person badge isn't Paralyzed to the rules code; a spell-to-condition mapping would fix that.

### Player screen

- [ ] **Show the turn timer** on the player screen.
- [ ] **Close from the main window with a key**, since a TV has no X button and Esc needs focus there.
- [ ] **Optional names for monsters**, so players see "Robed figure" until they know more.

### Tidying

- [ ] **Fix wording in some stat blocks.** Sphinx entries like "First Roar: ." show a stray full stop in the turn column.
- [ ] **Add `--push none` to the commit-plan script.** "Don't push" currently has to be recorded as `ask` with a note.
