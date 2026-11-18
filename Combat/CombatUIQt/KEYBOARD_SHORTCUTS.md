# Combat UI Keyboard Shortcuts

All shortcuts listed below are global (registered on the main combat window in `window_mixin.py`) and only fire while the main combat window itself is active — not while a modal dialog (Use / Cast, Rules, Encounter Log, Player Log, Statistics, tie-break) is open. Each dialog is its own top-level window, so the main window's shortcuts aren't active during modal interaction.

## Shortcut Reference

| Key | Action | Description |
|-----|--------|-------------|
| **A** | Log Action | Log an Action use for the selected source. No-op if no source is selected. |
| **B** | Log Bonus Action | Log a Bonus Action use for the selected source. No-op if no source is selected. |
| **R** | Log Reaction | Log a Reaction use for the selected source. No-op if no source is selected. |
| **C** | Concentrating (self) | Add the Concentrating condition to the selected source (self-applied). No-op if no source is selected. |
| **Ctrl+C** | Remove Concentrating | Remove Concentrating from the selected source. No-op if no source is selected. |
| **Ctrl+Shift+C** | Clear Target Conditions | Clear every condition from every target. No-op if no targets are selected. |
| **Shift+C** | Use / Cast | Open the Use / Cast dialog (same as the "Use / Cast..." button beside More Info, or in a card's right-click menu). Pick one of the source's attacks, actions, spells or features, or type any effect, and it applies to every target: a saving throw or an attack roll, damage or healing, a condition with a duration and note, and what it costs the source. See "The Use / Cast dialog" below. A timed condition shows under "Timed Conditions" on the card and ends by itself. |
| **Ctrl+Z** | Undo | Undo the last thing done — a damage/heal/temp HP (on every target at once), a spell cast with everything it applied, a condition, an action use, Next Turn, an added combatant, ... — putting back the state from before it and removing its lines from the encounter and player logs. Repeat to go further back. |
| **Escape** | Leave Field / Clear Selection | In a text field, leave it so the other shortcuts work again. Otherwise clear both the source and target selection. |
| **Enter / Return** | Next Turn | Advance to the Next Combatant / Next Round, passing over turns where everyone is dead (Settings). Only active once combat has started (initiative phase does nothing); does nothing while a damage/heal/temp-HP field is focused (Enter submits the field instead, and **Esc** leaves it). |
| **Shift+Enter** | Previous Turn | Go back a turn after pressing Next by mistake (same as the "Previous" button). Straight after Next it undoes that press completely, like Ctrl+Z (the round, timers that ticked and action tallies that reset come back); after anything else it only moves the turn back, to the previous round's last turn from a round's first. Does nothing on round 1's first turn, or while a text field is focused. |
| **1-9** | Spend Spell Slot | Spend a spell slot of that level (1-9) for the selected source, for a spell not cast through the Use / Cast dialog (which spends its own slot, so don't press this as well). Says so under Source/Target if the source has no slots left at that level. |
| **N** / **Right arrow** | Next Source | Select the next combatant (in card order) as the source. Wraps around; starts at the first combatant if nothing is selected. |
| **P** / **Left arrow** | Previous Source | Select the previous combatant as the source. Wraps around. |
| **Shift+N** / **Down arrow** | Next Target | Select the next combatant as the sole target (replaces any current target selection). Wraps around. |
| **Shift+P** / **Up arrow** | Previous Target | Select the previous combatant as the sole target. Wraps around. |
| **Space** | Select Active Combatant | Select whoever's turn it currently is as the source — handy right after pressing Enter to advance the turn. Only active once combat has started. With Settings → "Source follows the turn" on (the default), this already happens on every turn change, so Space only matters after picking another source by hand. |
| **Shift+A** | Focus Attack Roll Field | Jump the cursor into the Attack roll field, or press **Shift+Tab** from the Damage field. |
| **D** | Focus Damage Field | Jump the cursor into the Damage amount field (existing text selected, ready to overwrite). |
| **H** | Focus Heal Field | Jump the cursor into the Heal amount field. |
| **T** | Focus Temp HP Field | Jump the cursor into the Temp HP amount field. |
| **I** | More Info | Open the source's More Info dialog. |
| **Ctrl+N** | Add Combatant | Open the Add Combatant dialog (same as clicking the "+ Add Combatant" button). |
| **Ctrl+O** | Load Encounter | Open the Load Encounter dialog (same as clicking the "Load Encounter..." button). |
| **Ctrl+M** | Map Painter | Open the Map Painter on the encounter that's open, or the campaign's first (same as the **Map Painter** button). See "The Map Painter" below. |
| **G** | Cards / Arena | Switch between the cards and the battle map (same as the **Arena** / **Cards** button at the top of the turn column). Only during combat; the window opens a fight on the view used last. See "On the battle map" below. |

The arrow keys are plain aliases for N/P/Shift+N/Shift+P — left/right mirrors the unmodified source shortcuts, up/down mirrors the Shift target shortcuts. A focused text field keeps its own left/right cursor movement regardless (see Notes).

Enter in the Damage field applies the damage with each target's resistance, vulnerability and immunity counted, like the Apply button; **Ignore Resist** applies exactly the amount typed. The Damage, Heal and Temp HP fields take a sum or a halving as well as a number (`8+5`, `24/2`). When something can't be applied, the reason shows under Source/Target instead of nothing happening.

## The Attack roll field

Optional, beside Damage. Type the roll someone made and press Enter: it's checked against each target's AC, with Half or Three-Quarters Cover added, the hit or miss goes in the encounter log, and a hit moves on to the Damage field, with only the targets it hit left selected. It takes a total or a sum (`17`, `12+5`), or `nat 20` or `nat 1`, which hit or miss whatever the AC. Those two don't narrow down the AC on the Limited player view, since the AC played no part in them. The roll was made at the table, so conditions don't change it. A hit on a Paralyzed or Unconscious target is a Critical Hit from within 5 feet: with both on the battle map and the map in use (see below), the distance decides it ("Tiger is Paralyzed, attacker 5 ft. away: a Critical Hit"); otherwise the log says to check.

With the roll and the damage both typed, Apply does both: only the targets it hit take the damage. If it missed them all, nothing is applied and the amount stays in the field, so applying again deals it anyway, for damage that lands on a miss, like the Graze mastery's. A roll left in the field is cleared when the turn changes or a monster's action rolls its own.

## The Damage field

The type can go with the amount, and shows in the dropdown as you type. One letter is enough for the common types, two for the rest (`fo` Force, `po` Poison, `ps` Psychic), or spell it out.

| Typed | Means |
|-----|--------|
| `12` | 12 of the type in the dropdown (each source remembers the last type it dealt) |
| `12f`, `12 fi`, `12 fire` | 12 Fire |
| `8+5 fire` | 13 Fire |
| `24/2 fi` | 12 Fire (half, rounded down) |
| `7 pi + 3 fi` | 7 Piercing and 3 Fire, as one hit: one undo and one Concentration save, with each type's resistance counted |

**Saved?** marks every target as having saved: it turns gold, reads **½ Saved**, and the next damage is halved. With several targets, each target's card has its own **Saved?** too, for marking only those who made the save. A mark lasts one hit, or until the turn changes.

## The Use / Cast dialog

For everything a combatant does to others: an attack, a monster's action, a spell, a feature, or an effect typed by hand, on one target or many at once, like a Fireball or a Hold Person. Pick the source and targets as usual, then press **Shift+C**.

The first line says who uses it on whom ("Edmund → Goblin Boss 1, Goblin Boss 2"). On the left is what the source can use, with the highlighted pick's rules text under it. On the right is the form, in four boxes: **Roll**, **Damage**, **Condition** and **Cost**. Under them, a blue line says what Apply will do ("On 3 targets: DC 15 Dexterity save · 8d6 Fire, half on a save · costs Level 3 slot, Action"), so a wrong pick shows before it lands. The dialog is as wide as the screen allows, up to 1200 pixels, and can be resized.

| Key, in the dialog | What it does |
|-----|--------|
| **↑** / **↓** (and **Page Up** / **Page Down**) in the search box | Move through the list, picking as you go: the form fills in for each row. Folded categories and greyed-out rows are skipped. |
| **Enter** in the search box | Pick the top match, and Enter again applies it (or applies the row reached with the arrows). |
| **Esc** | Empty the search box first, if it has text; otherwise close the dialog. |
| Typing with the list focused | Types into the search box. |
| **Ctrl+F** | Back to the search box, its text selected. |
| **Ctrl+Enter** | Apply, from any field. |
| **Enter** in the Name, Notes or Damage field, or in a target's typed roll | Apply. |
| **Alt+N** / **Alt+S** / **Alt+A** | No roll / Saving throw / Attack roll. |
| **Alt+R** | Select targets in area: aim the pick's area on the battle map (see below). |

- **What was used:** the list on the left has everything the source can use: a monster's stat-block actions (by section), a player's attacks, their own spells and their features, then every other spell in the game (All spells starts folded). A feature that says what it does in a fight (its `combat_effects()`, see Model/Content/CombatEffect.py) fills in the form from that and says so under the list ("filled in from the feature's combat data"); one with several uses has a row for each, named for the use (Jolt to Life, of Reanimator's Skill Set), whose uses are still the feature's. A feature with nothing to apply in a fight isn't listed: Spellcasting and other features that grant spells (the spells are listed), languages, Alert, summons (summoned from the card menu) and Wild Shape (from the card menu), nor is a passive one. Any other feature is read from its rules text, as before. A monster's ability is read from its stat-block text; besides its attack or save, that covers the spells it casts ("The lich casts Fear", "uses Spellcasting to cast Mind Spike (level 3 version)": the spell at the monster's spell save DC and that level, its attack bonus the DC - 8 when the stat block gives none, a row per spell when it names several), the action it makes or uses ("makes one Rend attack": the Rend's numbers, spending this action, as a dragon's legendary Tail Swipe), and Hit Points it gives ("regains 9 (2d4 + 4) Hit Points"). Multiattack says to pick each attack in turn. A hand-made monster can write what an ability does on it instead (its `combat_effects`, the same as a feature's), which fills in the form exactly and says "filled in from the stat block's combat data"; a trait is listed only when it has them (a Divine Smite used after a hit). Each row shows its name, then its numbers in a column of their own ("Longsword | +6  1d8 + 4 Slashing"); the rules text of the row picked (or of a greyed-out row highlighted) shows under the list, and on hover. The cursor starts in the search box: type part of a name, **Enter** picks the top match, and **Enter** again applies it. Change the search after a pick and Enter picks the new top match first. With no match, Enter does nothing. Clicking a row picks it, and double-clicking applies it too. An action that's spent, or a legendary action costing more than are left, is greyed out and can't be picked.
- **Standard Actions:** every combatant, player or monster, has the actions anyone can take on their turn under **Standard Actions** (Model/Content/StandardActions.py, the Rules Glossary's text on hover): Dash, Disengage, Dodge, Help (Assist an Attack Roll, on the enemy; Assist an Ability Check, on the ally), Hide, Influence, Ready, Search, Study and Utilize. Attack and Magic are the attacks and spells above. Each spends an Action (switch the Cost to **Bonus Action** for a feature that grants one, though Cunning Action, Patient Defense and Step of the Wind have rows of their own) and logs "Clover takes the Dodge action". A row giving several badges that end at different turns keeps each one's own (Patient Defense's Disengage ends with the turn, its Dodge at the start of the next) unless you change the Duration. **Dodge** goes on the source until the start of its next turn: attack rolls against it have Disadvantage, counted unless the attacker is Invisible or the dodger Blinded (then only noted), and its Dexterity saves have Advantage; it ends if it's Incapacitated or Grappled, and counts for nothing while its Speed is 0. **Dash** gives as much movement again as its Speed on the battle map this turn ("Clover dashes: 60 ft. of movement this turn"), once per Dash, so a Rogue's Dash and Cunning Action Dash make three times its Speed. **Disengage** stops the map's Opportunity Attack reminder this turn. **Help** on an enemy gives the next attack roll against it by one of the helper's allies Advantage (not the helper's own), used up by that roll, until the start of the helper's next turn. **Hide** is Hidden and Invisible together, applied after a DC 15 Dexterity (Stealth) check made at the table (on a failure, log the Action alone); its next attack roll has Advantage and ends both, and an Invisible from a spell stays. **Ready** is a reminder badge until the start of its next turn. Influence, Search, Study and Utilize put nothing on anyone: the check is rolled at the table.
- **What a pick fills in:** the name, the roll (saving throw ability, DC and half on a save, or attack bonus), damage, the condition, the repeat save, the duration, and the cost: the cheapest spell slot that fits, the action and concentration. A weapon costs the Action only if the source hasn't used one this turn: a second attack of Extra Attack is part of the same Action, and an Opportunity Attack is a Reaction to choose. A condition that ends at the start or end of a turn ("until the start of the lich's next turn") gets that duration. Whatever the pick doesn't say is cleared, damage type included, so picking Hold Person after a Fireball leaves no damage. A DC or bonus that isn't known stays as it was. A spell's damage is read from its text, a cantrip's at the character's level, and a spell with nothing else to show gets its own name as the condition (Bless), unless it heals, is over at once, or states damage you'd type in. A monster's hit doesn't give the condition of a save it forces (a Ghoul's Claw): apply that save separately, as the note says. A condition only one of a spell's options gives (Command's Grovel) isn't filled in; the note says which. Anything to check shows under the name: an unclear reading ("the first is filled in"), damage the text has but a roll doesn't, a type to choose, no slot left, a monster's rider ("Also: ..."). **Everything stays editable** before Apply: a pick only fills the form, and typing an effect by hand works as before. Typing another name drops the pick, so nothing is spent for it. Choosing a higher slot upcasts a picked spell's damage, unless you've changed the damage yourself. One pick is one attack or ray: for Scorching Ray or Extra Attack, open the dialog again.
- **What Apply spends:** with a left-clicked source, a picked spell counts as cast ("Edmund casts Fireball", in the source's stats), a feature as used (one of its uses, if it has any), and a monster's action its recharge, its use per day or its legendary actions, shown in the turn column straight away. A feature with uses or an action, but nothing to roll, can be applied by itself, to spend it; one that's always on, like Darkvision, can't. Without a left-clicked source, nothing is spent, as with slots and actions.
- **Select targets in area:** during a fight, with the source on the map, this button closes the dialog and brings up the battle map with the area bar over it. The area's shape and size are read from the pick's rules text ("a 20-foot-radius Sphere", "a 15-foot Cone", "Each creature within 5 feet of you"), or are the last ones used, and can be changed in the bar. Hover to aim it: the cells it covers turn orange, each creature in it gets an orange ring, and the bar names them. A click makes them the targets and opens the dialog again on the same pick; anything you had changed in the form is filled in again from the pick. Right-click, **Esc**, **G** or the bar's **Cancel** goes back to the dialog with the targets it had. The view you had (cards or map) comes back either way. How each shape sits on the grid is under "On the battle map".
- **Name:** optional, for the log and the turn column ("Fireball").
- **Roll:** one click on **No roll**, **Saving throw** or **Attack roll** (Alt+N, Alt+S, Alt+A). No roll hides the roll's controls: everyone takes the damage and the condition. The dialog remembers which you used last. **Neutral**, **Advantage** and **Disadvantage** are a click each too, for every target.
- **Saving throw:** pick the ability from the **STR** to **CHA** chips (clicking one with No roll makes it a saving throw; Saving throw after No roll goes back to the last ability, or Dexterity); each target's row shows its bonus for that save ("DEX +3"); the DC starts at the source's spell save DC when that's known, and stays as you set it until the source changes. Each target rolls with its own save bonus. Every target has a row for a save rolled at the table: type the total with the save bonus in it (`14`, `9+5`), or leave it blank to roll for them. A natural 20 or 1 is nothing special on a save, so `nat 20` is refused: type the total. A typed total still fails automatically when a condition says so, and Legendary Resistance can still turn a typed failure into a success. With many targets, the rows scroll.
- **Attack roll:** the source rolls once against each target's AC, cover included; each target's row shows that AC ("AC 17 (cover)"). The bonus starts at the source's spell attack bonus when that's known, or a monster's first attack, and stays as you set it until the source changes. Each target has a row for a roll made at the table: type the total with the bonus already in it (`17`, `12+5`) or `nat 20`, or leave it blank to roll for the source. A hit takes all the damage and the condition, and a miss takes nothing. A natural 20 always hits and rolls the damage dice twice over (a flat amount stays the same), and a natural 1 always misses. A rolled attack counts the conditions, per target, with the Advantage or Disadvantage you set: Advantage against a Blinded, Paralyzed, Petrified, Restrained, Stunned or Unconscious target, Disadvantage for a Blinded, Poisoned, Prone or Restrained source, and one of each cancels out. The log says why ("Tiger is Restrained: Advantage"), and each target's row shows it for a roll made at the table ("AC 15, Advantage"; its tooltip says why). A Prone target (Advantage within 5 feet, Disadvantage farther) and the Critical Hit on a Paralyzed or Unconscious target from within 5 feet are counted when the source and the target are both on the battle map, by the distance between them ("Tiger is Prone, attacker 5 ft. away: Advantage"), and only noted when either isn't. That is once the map is in use: someone has been moved on it this fight, or the encounter's painted map gave the starting cells. Before then everyone only stands along the edges where the fight put them, so a fight played on the cards alone keeps the notes. What depends on sight isn't counted, only noted: Invisible, Frightened and Grappled. A typed roll is used as it is. The players learn what the roll showed of the AC, as with any attack roll.
- **The rules it counts:** Paralyzed, Petrified, Stunned and Unconscious fail Strength and Dexterity saves (a target's row says "DEX fails"), Restrained gives Disadvantage on Dexterity saves ("DEX +3, Disadvantage"), the attack roll modes above, and a creature immune to the condition doesn't get it. A condition that gives another counts as both (Unconscious is Incapacitated and Prone too). A longer custom name counts too ("Restrained by vines"). The conditions' rules are data, in `Model/Content/RulesConditions.py`.
- **What it doesn't count:** Exhaustion (its level isn't tracked, so the log flags it), Evasion, Magic Resistance and similar features (set Advantage yourself, or adjust by hand), and a badge that is only a spell's name and not a condition (one a spell with nothing else to show gets, such as Bless): it isn't a rules condition to this dialog.
- **Damage:** dice are rolled once, for everyone. Type the type (`8d6 fire`) or pick it from the dropdown, which starts on the source's last type. Each target's resistances count unless you untick that, and a save halves the damage, or avoids it with "Half damage on a save" off.
- **Healing and Temp HP:** the chips over the amount box switch it from **Damage** to **Healing** (Hit Points regained) or **Temp HP** (Temporary Hit Points). Type dice or a total (`2d8 + 3`, `10`); the dice are rolled once, for everyone, and every target that isn't dead gets it, whatever the roll: the roll still decides the condition. Healing works as the Heal button does: up to the maximum, a creature at 0 Hit Points comes to, and a dead one can't be healed. Temporary Hit Points don't stack, so the higher amount stays. A healing spell fills it in (Cure Wounds, Healing Word, Mass Healing Word, False Life), with the spellcasting modifier and more dice for a higher slot; a spell that gives them to its caster ("You gain ...") says to pick the caster as the target. A spell that deals damage too (Conjure Constructs) fills in the damage, and the note gives its Hit Points to apply by hand.
- **Condition:** goes on those who failed or were hit, or on everyone with no saving throw. Click its badge on a card (or hover it) to read what gave it: a picked spell shows its card and rules text, (Guidance, Bless), a picked feature its description, and a picked attack or monster action its stat-block text; notes typed in the dialog come first. A rules condition (Paralyzed) shows its rule instead, and an effect typed by hand shows its notes. A badge named after a spell still opens it after a restart. With no saving throw, a target marked ½ Saved counts as having saved by hand: half damage and no condition.
- **Repeat the save:** at the end of each of its turns, a monster rolls again and a save ends the condition. A player gets a reminder to roll, and you remove the condition if they make it.
- **Cost:** a spell slot and an action to spend (**None**, **Action**, **Bonus Action** or **Reaction**, a click each), so one dialog covers the whole spell. Without a left-clicked source the box is greyed out and says so. "Source concentrates on it" starts Concentrating, ending any other concentration, and when it ends the condition comes off everyone who got it, unless another running effect also holds it. With a duration of a turn, it ends when the last condition does. With no time set, it runs for an hour.
- **Legendary Resistance:** with a target that has any left, a tick box spends it to turn a failed save into a success.

Each target's roll is in the encounter log, and the turn column shows the totals. One Ctrl+Z takes all of it back.

## The dialogs

In the Use / Cast dialog, the cursor starts in the search box: type part of the name, **Enter** picks the first match (the source's own attacks, spells and features come first), and **Enter** again applies it. Double-clicking an entry applies it too.

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

## On the battle map

**G** (or the turn column's **Arena** button) shows the fight as a grid in
the cards' place, with a token per combatant: blue the party's side (the
players, their summons and allies, the encounter's own allies too), red
everyone else; whose turn it is on gold cells with a gold ring, as its card
is gold; the source's white outline and a target's red one; greyed at 0 HP,
dashed while the players can't see it. A Large or bigger creature is a
square over all its cells. The turn column, the panel, selection and Undo
(**Ctrl+Z**) work as with the cards. Everyone starts along an edge as combat
starts, the party's side on the left. Columns are lettered and rows
numbered, so a cell is "C7". Distances are counted in 5-foot squares, up,
down, left and right (a diagonal step costs two squares), from a creature's
nearest cell.

| On the map | Action |
|-----|--------|
| **Left click** a token | Make it the source and pick it up: the cells it can still reach this turn are shaded with what each costs: its Speed in use (Haste doubles it, Grappled makes it 0) less what it has moved. Allies can be walked through, an enemy's space costs double, and a Prone creature crawls at half the reach. Click it again to put it down without moving it; **Esc**, another source or the next turn puts it down too. |
| **Left click** an empty cell | Move the picked-up token there. With nothing picked up, nothing moves. |
| **Drag** a token | Move it in one go, with the same shading while it's held. |
| **Shift** held as you drop a token (the drag's release, or the click on the cell) | Teleport it there (Misty Step, Thunder Step): no movement spent and no Opportunity Attack. |
| **Alt** held as you drop a token | Push it there (a Shove, Thunderwave, Repelling Blast): no movement spent and no Opportunity Attack, as it isn't the creature's own movement. |
| **Right click** a token | Target it, with Ctrl and Shift as on the cards. |
| **Hover** a cell or a token | With a source selected, how far it is from the source, in feet. |
| **Ctrl+wheel** | Zoom. The whole map fits the window until you do. |
| **Drag** empty space | Pan. |

A move is one Undo step and a GM-only line in the encounter log saying
from where to where and what's left: "Clover moves from A7 to C8 (15 ft.;
15 of 30 ft. left this turn)". After a Dash (Use / Cast's Standard
Actions, or Cunning Action's), the reach shaded and what's left count its
Speed again ("15 of 60 ft. left this turn (Dash)"). Walking past it is
allowed (for whatever lets a creature move further) and said in the line
("5 ft. past its 30 ft. Speed") and under Source/Target ("Goblin moved 35
ft., Speed 30 ft."); ending on someone else's space isn't.

A teleport (**Shift**) or a push (**Alt**) isn't the creature's own
movement (Rules Glossary, Teleportation: it "doesn't expend movement ...
and never provokes Opportunity Attacks"): its feet moved this turn stay as
they were, no Opportunity Attack is reminded of or offered, and its line
says which, with the straight distance: "Kivi teleports from A7 to D7 (15
ft.; no movement spent)", "Goblin is pushed from C4 to C5 (5 ft.; no
movement spent)". It's one Undo step too, and an area or a hazard it lands
in is reminded of as for a walk. It still can't end on a wall, a blocking
object or someone else's space: a teleport there "appears in the nearest
unoccupied space of your choice" instead, so drop it on that one. A walk
with no way there (walled in) still counts the straight distance as moved;
hold Shift for a teleport.

A walk on the mover's own turn that starts in an enemy's reach and ends out
of it reminds you of that enemy's Opportunity Attack, under Source/Target
and in a GM-only log line ("Clover leaves Goblin's reach: an Opportunity
Attack, a Reaction, if they can see it"). Only enemies that are up, not
Incapacitated and still have their Reaction count; reach is 5 ft., or the
longest "reach 10 ft." in a monster's stat block, or 10 ft. with a player's
Reach weapon. A Disengaged mover gets "Disengaged: no Opportunity Attack"
instead, and one with Flyby a note that it has none if it flies. Nothing is
rolled: use Use / Cast for the attack. Only where a walk starts and ends is
known, so running past an enemy (into its reach and out again) isn't
caught, nor is a walk that leaves a reach and comes back, nor a walk on
someone else's turn (a correction, or a Reaction's move): remind yourself
of those. With a source and a target both on the map, the
target label reads "Target: Goblin (25 ft.)", on the cards too. Whoever has
no place yet (added during the fight) is in the **Not on the map** row
above the map: click their name to pick them up, then a cell.

**Speeds:** a source on the map with more than one speed (a Giant Eagle's
Fly 80 ft., a dragon's Swim, a Bulette's Burrow, or a Fly Speed from the Fly
spell) has the **speed bar** over the map: **moves by** picks the speed its
moves use, and its reach is shaded by it. What it has moved this turn counts
against the new speed (Speed 30 and Fly 40: fly 10, walk 10, then 20 more
to fly). Flying, Difficult Terrain on the ground, water and heights cost
nothing extra (an enemy's space still does), and **Altitude** sets how high
it flies: going up or down spends its movement, the token shows "↑30 ft.",
and its altitude counts into every distance. It can't switch to another
speed while it's up: bring it down to 0 ft. first. Swimming, it stays in the
water at no extra cost; burrowing, it goes under creatures (ending on
nobody) and Difficult Terrain. A flyer that's knocked Prone, Incapacitated,
Grappled (its Fly Speed 0) or whose Fly ends falls, unless it hovers: it
lands, and the status says how far and what it takes ("falls 30 ft.
(Prone): 3d6 Bludgeoning damage, and it lands Prone unless it takes none").
Apply that damage and Prone yourself.

**Targets in an area** (the Use / Cast dialog's **Select targets in area**):
while an area is aimed, hovering moves it, a left click targets whoever is
in it and a right click cancels; nothing is picked up or moved meanwhile.
A creature is in it when any of its cells is. A cell is in it when the area
covers its middle. A **Sphere** or **Cylinder** is centred on the cell under the
mouse, its radius counted the same way as distances (so a creature the hover
calls "20 ft." away is inside a 20-foot radius), and it can catch the source.
An **Emanation** reaches out from the source's cells and leaves the source
out; it needs no aiming. A **Cone** and a **Line** go from the source
towards the mouse in any direction, and reach no further than their length
by the same count: the Cone as wide at each point as it is far from the
source (a 15-foot Cone is 5 cells), the Line one unbroken row of cells for
each 5 feet of width the bar says. So nothing in a Sphere, Emanation, Cone
or Line is further than its size on the hover. A **Cube** is a number of
cells on a side (3 by 3 for 15 feet), centred on the cell under the mouse,
or, with **From the source** ticked (Thunderwave), set against the side of
the source nearest the mouse. For an area centred on a point (a Fireball),
the bar says how far the point is against the spell's range, and warns
when it's past it; it still lets you click.

A **Wall** (Wall of Fire, Wall of Force, Blade Barrier, Wall of Thorns, read
from their text) is aimed by two clicks, one on each end: the bar says how
long it is so far, and it stops at its length (60 feet is 12 cells along a
row). With **Ring** ticked (the size becomes the ring its text offers,
Wall of Fire's 20 feet across), one click on its middle puts it. It's one
cell thick, and nothing a wall crosses cuts it short. For a wall with a
damaging side (Wall of Fire), a third click on one side picks it: the bar
names it ("the east side", or inside and outside a ring) and shades the
cells within reach of it.

The bar's **colour** list (orange, red, blue, green, purple, yellow, teal,
grey, or **Other...** for any colour) is what the area is shaded in, and the
next area starts with the last colour picked.

**Areas that stay** (Moonbeam, Spirit Guardians, Web, Grease): with the
bar's **Keep on the map** ticked (it starts ticked for a spell that isn't
Instantaneous, or anything needing Concentration), a click also works with
nobody in the area, and the dialog that opens again has **Keep the ... on
the map**. Its Apply puts the area on the map in its colour, as one of the
source's Active Spells on its card:

- With **Source concentrates on it**, the area lasts while the source
  concentrates (its edge is dashed): a failed Concentration save, being
  Incapacitated, a new concentration, **Ctrl+C** or the card's ✕ ends it.
- Without, it lasts the spell's own time (Grease's minute), else the
  dialog's duration, and takes nothing off anyone when it ends.
- An **Emanation** (Spirit Guardians) moves with its caster; anything else
  stays where it was put.
- Whoever walks into one, or is reached by an Emanation as its caster
  moves, is named in the status line, and whoever starts or ends a turn in
  one gets a GM-only log line. Hovering a cell names the areas on it. Undo
  takes an area back with the rest.
- **The area acts by a button.** When its rules text says it acts then
  (Moonbeam: entering it, its area moved onto someone, or ending a turn
  there; Web: entering or starting a turn there), the turn column gets a
  button such as "Clover's Moonbeam on Goblin (entered it)". It opens
  Use / Cast on the area's effect (Spirit Guardians' damage row), the
  caster as the source and that creature the target, at the slot it was
  cast with, and **costs nothing**: no slot, action or concentration. What
  it gives (Web's Restrained) ends with the area's concentration. A walk's
  button goes with Undo, a turn's with the next turn. Wall of Fire's side,
  shaded fainter, gives its button to whoever ends a turn within 10 feet
  of it ("... (ended its turn by its damaging side)"); walking into the
  wall itself gives the usual one.
- **A wall is terrain while it lasts.** Wall of Force (its text calls it a
  barrier) blocks movement and is Total Cover, like a painted wall: no
  walk goes through it, an attack or a Fireball across it is blocked, and
  the target label says so. Blade Barrier is Three-Quarters Cover and
  Difficult Terrain. None of it is written into the painted map, and it's
  gone when the spell ends (or Undo takes it back).

**Selecting an area that stays:** click an empty cell of it (click again
where areas overlap to go to the next one). It's edged brighter, and a panel
over the map says whose it is, where, whether it's concentration and how
long it has left, with its rules text under it:

- the **colour** list changes its colour (one undo step);
- **Target who's in it** makes whoever stands in it the targets;
- **Move** (not for one around its caster, nor a wall) aims it again in the area bar
  from where it is, keeping its time, concentration and colour: the bar
  says how far it moves against its text's "up to" (Moonbeam's 60 ft.,
  warned past it), a click puts it there and spends what its text says
  (Moonbeam's Magic action, Flaming Sphere's Bonus Action), whoever it
  lands on gets its button, and Esc or a right click leaves it where it
  was. One undo step;
- **End spell** ends it, as the card's ✕ does, concentration on it too;
- **Close**, **Esc** or a click on an empty cell outside it deselects it.

An area is never the source: the source and targets stay as they were.

**A painted map** (see "The Map Painter" below) is drawn under the tokens:
walls as stone, Difficult Terrain dotted, water blue, higher ground lighter
with its height in the corner and a pale edge where it drops, objects as
labelled blocks (hazards red), Dim Light and Darkness shaded. Nobody can be
moved onto a wall or an object that blocks movement; the shaded reach counts
Difficult Terrain and climbing; hovering a cell names what's painted on it;
the target label adds "Lightly Obscured" or "Heavily Obscured"; and walking
onto a hazard, or starting a turn on one, is named like an area that stays.

**Cover from the map** (once the map is in use): what stands on the straight
line between the source and the target gives the target cover, the best
line counting (a Large creature shoots past a pillar from its other side).
A wall or a closed door is Total Cover, an object its own (a barrel Half,
a pillar Three-Quarters), and another creature, friend or foe, Half Cover;
one at 0 HP gives none. The most protective counts, the target's own Cover
state too. The target label names it ("Target: Goblin (25 ft., Half Cover
from Barrel at C4)"), and it's added to the AC of every attack roll (the
Use / Cast dialog, a monster's button, the Attack roll field) and to
Dexterity saves in the dialog. An area's save counts it from the area's
point of origin (a Fireball's cell), and an area never reaches behind Total
Cover. Total Cover is warned about ("can't be targeted directly"), not
refused. What says it ignores cover (Sacred Flame) gets none of the map's
Half or Three-Quarters Cover. Height isn't counted.

**Reach and range** (once the map is in use), for a pick whose reach or
range is known (a weapon, a stat block's "reach 10 ft." or "range 80/320
ft.", a spell attack): a ranged attack past its normal range has
Disadvantage ("Long range, 90 ft. of 80/320 ft."), and so has one made
within 5 feet of an enemy that isn't Incapacitated (one that may not see
the attacker, Blinded or facing an Invisible attacker, is only noted). A
melee attack past its reach, or a ranged one past its long range, is warned
about on the target's row and in the log, not refused. A thrown weapon is
melee within its reach and thrown past it. A spell aimed at a creature past
its range says so on the save row.

**Distances in triggers** (once the map is in use, with both creatures on
it): a trigger that asks how far the other creature is is counted from the
map. Fire Shield burns a creature that hits from 5 feet without asking, and
not one with a reach weapon from 10; Hellish Rebuke past 60 feet isn't
offered, and within them asks only whether the Warlock can see the
attacker ("if you can see it (25 ft. away)"); Dark One's Blessing also
gives its Temporary Hit Points when someone else drops an enemy within 10
feet of the Warlock. Off the map they ask, as before.

## The Map Painter

**Ctrl+M** or the **Map Painter** button opens it on the encounter that's
open (the list at the top switches to another). Pick a tab, then paint on
the map:

| Mouse / key | What it does |
|---|---|
| **Left-drag** | Paint the tab's choice on every cell dragged over. |
| **Right-drag** | Clear what this tab paints (open ground, height 0, Bright Light, no object). |
| **Shift+drag** | Fill the block between where the drag starts and ends (shown as it's dragged). |
| **Ctrl+wheel** | Zoom. |
| **Ctrl+Z** | Undo the last stroke (or size change). |
| **Ctrl+S** | Save and close. |
| **Enter** | Save and close too (Save is the default button), also from the Width / Height boxes. |
| **Esc** / **Cancel** | Close, asking first when something isn't saved. |

- **Ground:** Wall (nobody enters it), Difficult Terrain, Water (swum: each
  foot costs 1 extra, 2 in Difficult Terrain such as an enemy's space, none
  swimming by a Swim Speed or flying over it).
- **Height:** the ground's height in feet, up or down. Height counts into
  distances, and a step up or down is a climb (each foot costs 1 extra, 2
  in Difficult Terrain, none with a Climb Speed).
- **Light:** Dim Light (Lightly Obscured) or Darkness (Heavily Obscured).
- **Objects:** a preset (Table, Barrel, Pillar, Door, Campfire, ...) or your
  own: whether it blocks movement, is Difficult Terrain, is a hazard, and
  the cover it gives (shown on the hover, not counted into attacks).
- **Start:** the encounter's combatants. Pick one and click the cell it
  starts on; the next one not placed is picked for you. Click a token to
  pick it again, right-click it to take its start away. Whoever has no
  start is placed as before, the party on the left and the rest on the
  right.
- **Width** / **Height** at the top size the map, in 5-foot cells.

**Save** keeps the map in `Combat/Campaigns/<Campaign>/Maps/<encounter
id>.json`. A fight that starts plays on it, everyone where the map says.
Saving the map of the encounter that's open changes its fight too: before
it starts, it's the map it starts on; during it, it's one undo step, and
anyone standing where a wall now is moves to the nearest free cell. A fight
in progress keeps the map it has when it's continued later.

## The turn column

Beside the cards during a fight: whose turn it is, who's next, what to remember this turn (a dying player's death save, what recharged, legendary actions coming back, traits that act at the start of a turn), and who has legendary actions ready.

Under that are the source's stat-block actions, for a monster. Click one and it counts the use (a recharge, a per-day use, a legendary action) and rolls: an attack against the one target's AC, using the d20 Roll section's Advantage or Disadvantage, with a natural 20 doubling the dice and a natural 1 missing. The damage every hit deals lands in the Damage field for **Enter** to apply, and a miss leaves it empty. Anything that depends on something (extra damage with Advantage, damage at the start of a turn) is shown as "Also:" for you to judge, and never added by itself. A damage type the monster chooses reads `type`, selected for you to type over. **↺** gives back one use. Recharges roll by themselves at the start of the monster's turn.

Stat blocks don't say how many legendary actions a monster has, so every legendary creature counts 3.

The bottom of the column is the encounter log, always open, with the newest line last. It's the whole log, including lines the player link hides. Scroll up to read back: it stays there while new lines arrive, and follows them again once you scroll back to the end. Drag the bar above it to give the log or the actions more room.

## Initiative

**Roll for Monsters** rolls everyone without a player's dice, leaving what's already typed. **Enter** in a field jumps to the next one that needs a number, and starts combat once they're all filled in.

## Other dialogs

Every dialog closes with **Esc**, as Cancel does.

| Dialog | Key | What it does |
|---|---|---|
| Add Combatant (**Ctrl+N**) | **Enter** in the name field | Add the combatant. |
| Load Encounter (**Ctrl+O**) | **Enter**, or **double-click** an encounter | Start the encounter picked (Start Encounter is the default button). |
| What a hit triggers (the pop-up after an Apply) | **Enter** / **Esc** | Apply the checked rows / Skip them all. |
| Player Link | **Enter** | Close. |

## The players' screen

**Player Screen** opens the turn order for a second monitor or TV (full screen there, a window if there's only one screen): whose turn it is, who's next, conditions, everyone's Hit Points as a bar colored like the cards (a bar for each member of an initiative group), each combatant's size and speed, and monsters' AC. A monster that's Invisible (or under Invisibility), Hidden, Heavily Obscured, in Darkness or behind Total Cover isn't listed, and spell badges and custom conditions on a monster stay private. **Esc** closes it.

## Notes

- **Text field protection**: Typing into the Damage/Heal/Temp HP amount fields naturally blocks these shortcuts. Qt lets a focused text field consume its own keystrokes, so typing amounts like "15" (or moving the cursor with the left/right arrows) won't accidentally trigger number/letter/arrow shortcuts. **Ctrl+Z** is the exception: in the Attack roll, Damage, Heal and Temp HP fields it is still the window's Undo, not the field's own text undo, so undoing a monster's action that left the cursor there works.

- **Combo box handling**: Combo boxes (Roll Mode, Damage Type, Conditions, Visibility, Spell Slots, Action Economy) don't reserve their own keys the way a text field does, so a matching `QShortcut` would otherwise swallow the keystroke before the combo box ever sees it — silently breaking its native type-ahead search *and* its arrow-key item cycling, even though the shortcut's own handler correctly declines to act. Every shortcut above except Ctrl+Z and Escape is fully disabled (not just made into a no-op) for as long as a combo box has focus, via `QApplication.focusChanged`, and re-enabled the instant focus moves elsewhere — so both the combo box's normal keyboard behavior and the global shortcuts work correctly depending on what's actually focused.

- **Space and focused buttons**: Space normally activates whichever button has keyboard focus. Because the global Space shortcut is registered on the main window, it intercepts the keystroke first — pressing Space to select the active combatant does not also click a focused button.

- **Modal dialogs**: None of these shortcuts fire while a modal dialog is open. Each dialog (Use / Cast, Rules, Encounter Log, Player Log, Statistics, Settings, tie-break) is a separate top-level window, so the main window's shortcuts are inactive during dialog interaction.
