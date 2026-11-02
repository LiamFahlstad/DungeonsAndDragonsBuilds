# Player web view plan

Goal: give players a link they open on a phone or computer, showing a live, read-only view of the current encounter, hosted by the combat UI itself.

Status: built, steps 1-5 and the docs, uncommitted. Step 0 and the phone checks in step 6 are still to do, because nothing has been tried on a real phone or across a network. Written 2026-10-31.

Changed since this was written: the views now show every combatant's exact HP as a bar, and each combatant's size, AC and speed. A player's AC is only the number they have now, because their full text also gives their AC without a Shield. Monsters' HP, AC and speed were secret in the first version and no longer are, by choice. Hidden monsters and the rest of a stat block (its action list, ability scores, saving throws) still stay private.

That's the **Informative** view, the default. Players can also ask to know less, so the GM can pick the **Limited** view, in the Player Link dialog or in Settings. It changes the Player Screen and the link together, and it's the GM's choice, not the page's: if a phone could pick, the numbers would have to reach the phone first.

Limited only changes monsters. A player's row is the same in both views, because players can tell each other all of it anyway. A monster's row shows its name, visible conditions, speed, the damage it has taken, and a word for health:

| Word | HP left |
| --- | --- |
| Healthy | Above 75% |
| Injured | 51-75% |
| Bloodied | 26-50% |
| Dying | 1-25% |
| Defeated | 0 HP |

A monster that makes death saves reads Dying at 0 HP, then Stable or Defeated.

- The bar moves in steps with the word, because a bar with the exact percentage would give the HP away.
- Damage taken is public, because players hear it at the table; the page only keeps the total for them. It's the monster's `stats["damage_taken"]`, which is this encounter's: a monster's stats start with its fight and are saved in its log. So Undo takes a hit back, healing takes nothing off, and damage soaked by temp HP counts, so the total doesn't give the temp HP away. A player's stats go back past this fight, so that wouldn't work for them, but their rows don't show it.
- It counts hits on a monster while it was hidden, which show once it's revealed.
- The total and the word together let players estimate a monster's maximum HP: the total when it turns Bloodied is about half. That follows from showing both, and it's accepted.
- The log is on the link in both views, by the same rules for which lines are public. So in Limited it can still say what the rows hide: a monster's temp HP, its rolled saves, how many Legendary Resistances it has left, and its exact HP if it makes death saves and regains consciousness. That's accepted, by choice.

The page also has an Encounter log. It isn't on the Player Screen, because nobody can open anything on a TV. The log was written for the GM, so each line is judged when it's logged (`may_read_log_line` in `player_view.py`) and marked `public` in the log file if players may read it. That has to happen at that moment, because it depends on who they could perceive then, and a line without the mark stays private. A hidden monster's attack never shows, even after it's revealed. `public_log.py` then rewords only those marked lines for a phone: grouped by round and turn, a hit joined to its damage, totals for a folded round, and no line for losing Bloodied. It reads nothing else of the fight but the combatants' names, so it can't show more than the lines do.

A review found that searching a line's text isn't enough, because a condition may already be gone and "keeps concentration" doesn't say Concentrating. So a line about a monster's effect says what it's about in `value`, and nothing is public before combat starts. **Any new `_log_event` that names a private effect must do the same, or it will show on the link.** Casting a spell and using an action stay public, because players watch those happen; what stays private is an effect still running on a monster.

## Short answer

Yes, this is possible, and without any external website or new packages. Python's standard library can serve a small web page from the combat UI while it runs. Anyone on the same Wi-Fi opens a link like `http://192.168.0.143:8765` and sees the page update within a second.

Most of the work already exists. The Player Screen (`Combat/CombatUIQt/player_view.py`) already decides what players may see: hidden monsters aren't listed, and nothing of a stat block goes through except what it picks. The web page shows those same rows, so the rules for what's secret stay in one place.

**This plan assumes everyone is in the room, on the same Wi-Fi.** Players joining from home is a separate decision: see [Players who aren't in the room](#players-who-arent-in-the-room).

## What players get

- The same content as the Player Screen: the round, the turn order, NOW and NEXT, everyone's HP as a bar, each combatant's size, AC and speed, and visible conditions.
- A page laid out for a phone, in the Player Screen's colors, with no app or account.
- A "Lost connection" banner if the page stops getting updates, so nobody trusts an old view.
- "Waiting for the fight to start" between fights.

They can only look. Nothing on the page changes the fight.

## How it works

```text
Combat UI (Qt thread)                 Server thread              Browsers
─────────────────────                 ─────────────              ────────
_refresh_views()
  └─ player_view_rows()  ──publish──▶  latest JSON + ETag  ◀─poll─  GET /state, every 1s
       (the existing filter)           GET /  → the page
```

The Qt side turns the filtered rows into finished JSON and hands that to the server. **The server never sees the combatants' data**, so it has nothing secret to leak: a bug in the web code can't show a monster's ability scores, its action list or a hidden monster, because they never reach it.

## Decisions

| Decision | Choice | Why |
| --- | --- | --- |
| Server | `http.server.ThreadingHTTPServer` in a daemon thread | Standard library, so `requirements.txt` doesn't change. It handles HTTP parsing, and a daemon thread ends with the app. Flask would add a dependency for two routes, and Qt's `QTcpServer` would mean writing HTTP parsing by hand. |
| Updates | The page polls once a second | Survives phones sleeping and Wi-Fi drops with no reconnect logic, and a second's delay is fine at a table. If it ever feels slow, Server-Sent Events can replace it without touching the Qt side. |
| ETag | A hash of the JSON, not a counter | Polls usually return an empty "nothing changed". It also means a hidden monster's changes produce no update, whereas a counter would tip off anyone watching the traffic. |
| Routes | Exactly `/` and `/state`, everything else 404 | **Never use `SimpleHTTPRequestHandler` or `python -m http.server` on the repo folder:** they would serve every file, monster stats and encounter logs included. |
| Login | None | It's read-only and shows only what players may see. A password would only add friction at the table. |
| HTTPS | None | Nothing secret crosses the network, and home-network certificates would give every player a browser warning. |
| Off by default | The DM starts it with a button | The app opens no network port unless asked. |
| Address | Bind to the chosen Wi-Fi address, not `0.0.0.0` | It listens only on the network the players are on. |
| Port | Fixed at `8765` | A link stays valid between sessions, as long as the PC's address doesn't change. |
| Page assets | One HTML file with inline CSS and JS | No CDN, so it works with no internet connection. |

## Build steps

Commit the current combat UI work first: `app.py`, `state.py` and `window_mixin.py` all have uncommitted changes, and this touches them too. Use the `combat-simulator` agent, then `code-reviewer`.

### Step 0: prove a phone can reach this PC

Do this before building anything. It's the one thing that couldn't be tested from here.

1. Create an empty folder, so nothing in it can be exposed.
2. In that folder, run `python -m http.server 8765 --bind 192.168.0.143`.
3. On a phone on the same Wi-Fi, with mobile data off, open `http://192.168.0.143:8765`.
4. A directory listing means it works. Press Ctrl+C to stop the server.

If it times out, see [Troubleshooting](#troubleshooting).

### Step 1: fix DI-029

End Encounter leaves the Player Screen showing the finished fight, monsters included, because `_leave_encounter` never refreshes the views. On the web page this would stay up on every player's phone. Call `self._refresh_views()` at the end of `_leave_encounter` (`encounters_mixin.py:223`), and add a test.

### Step 2: the server (`Combat/CombatUIQt/player_server.py`, new, no PyQt imports)

- `PlayerFeed`: holds the latest JSON and ETag behind a lock. `publish(title, rows)` replaces them. Publish only finished `bytes`, never live objects.
- `PlayerServer`: `start(host, port)`, `stop()` and `url`.
  - **Set `allow_reuse_address = False`.** `HTTPServer` turns it on, and on Windows that lets a second copy of the app bind the same port without an error. Then a busy port would look like a working one.
  - Override `log_message`, or every poll prints a line to the console.
  - Set `Cache-Control: no-store` on `/state`.
  - Report a busy port to the DM as a plain message, not a traceback.
- `lan_addresses()`: the addresses this PC could offer, best first.
  - **Don't use `socket.gethostbyname(socket.gethostname())`.** On this PC it returns `172.22.80.1`, the WSL adapter, which phones can't reach.
  - Start from the local address of a connected UDP socket, which sends nothing and gives `192.168.0.143` here. Add the other private addresses, drop `169.254.*`, and rank `192.168.*` first, then `10.*`, then `172.16-31.*`, then Tailscale's `100.64-127.*`. A connected VPN (`10.5.0.2` is NordVPN's adapter) or a VirtualBox adapter can still fool the ranking, so the dialog in step 4 lets the DM pick.

### Step 3: the page (`Combat/CombatUIQt/player_page.html`, new)

- Poll with `setTimeout` so requests can't pile up, and give each one a 3-second timeout.
- Poll straight away on `visibilitychange`, so a phone catches up the moment it wakes.
- Show the "Lost connection" banner after three failed polls, and clear it on the next success.
- Render with `textContent`, never `innerHTML`, since condition names can be typed by hand.
- Add `<meta name="viewport" content="width=device-width, initial-scale=1">` and reuse the Player Screen's colors (`#1a1a2e`, `#c9a84c`, `#3a2e00`, `#0f3460`).

### Step 4: connect it to the UI

- `turn_panel_mixin.py`: move the title and rows out of `_refresh_player_view` into one `_player_view_content()`. Then `_refresh_player_view` shows that content on the window if it's open **and** publishes it if the server is running. Today it returns early when the window is closed, so as written it would never publish. Both views use one source, so they can't disagree.
- `window_mixin.py`: add a **Player Link** button beside Player Screen.
- `dialogs_mixin.py`: clicking it starts the server and opens a small dialog with the link, a Copy button, an address dropdown (from `lan_addresses()`) and a Stop button.
- `app.py` and `state.py`: declare `_player_server`, plus stubs for any new methods the mixins call on each other.

`_refresh_views` already picks up the changes that were tested: start of combat, HP, conditions, turn changes, undo and returning to initiative all reach it. End Encounter was the one gap found, and step 1 closes it. Load Encounter wasn't checked when this was written; step 5's test then found the same gap there, fixed in `_open_encounter_log`.

### Step 5: tests (`tests/test_combat_ui_player_server.py`, new)

Run a real server on `127.0.0.1` with port 0, driven through `tests/_combat_ui.make_ui`:

- `/state` returns the same rows as `player_view_rows`.
- A monster's actions, ability scores and saving throws never appear in the JSON.
- A hidden monster isn't listed, and changing its HP leaves the ETag unchanged.
- Repeating a poll with its ETag returns 304.
- Unknown paths, `/../requirements.txt` and repo file names return 404, and `POST` is refused.
- After End Encounter, `/state` says "Waiting for the fight to start" with no rows.
- After Load Encounter, `/state` shows the new fight, not the last one.
- A busy port gives the plain error, not a crash.
- `lan_addresses()` ranks correctly and skips `169.254.*` for a given list of addresses.

No golden snapshot contains the Player Screen button row, so the new button shouldn't change any. If one does fail, read the diff with the `snapshot-diffs` skill before updating it.

### Step 6: try it at the table

Add a "Player link" section to `Notes/combat-ui-tracker.md`, covering:

- Two phones and a laptop open the link, and a damage hit shows up on all three.
- Lock a phone during a turn and unlock it: it catches up.
- Stop the server: the banner appears.
- Open it on both iPhone and Android, since only a real device tests their browsers.

Add the feature to `HOWTO.md` and `KEYBOARD_SHORTCUTS.md` if it gets a shortcut.

### Later, only if wanted

- **QR code** in the Player Link dialog, so nobody types an IP address. This needs one small package (`segno`, pure Python).
- **"This is me"**: a player picks their character, the page remembers it and highlights their row.
- **Turn timer** on the page, already on the tracker for the Player Screen.
- **Hidden monster names** ("Robed figure"), also on the tracker. Real names show on the phones just as they do on the TV.
- **Player actions**, like tapping "End Turn". This changes the design: the server would have to accept input, so it would need to know who's asking. Treat it as a new plan.

## Limits to expect

- **The app must be running and the PC awake.** If the PC sleeps, the banner appears on every phone.
- **Phone screens will still dim.** Keeping one awake from a web page needs HTTPS. The page catches up on wake.
- **The link can change** if the router gives the PC a new address. Reserving an address for this PC in the router settings keeps it stable.
- **Anyone on the Wi-Fi can open the link**, while the server is running. They'd see only what the page shows.
- **Other networks may not work.** Guest Wi-Fi, and shops or hotels, often block devices from reaching each other.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Phone times out, PC works | Phone is on mobile data or a guest network | Join the same Wi-Fi as the PC, with mobile data off. |
| Same, while NordVPN is connected | The VPN is blocking local traffic or changing the address | Disconnect it for the session, or look in its settings for local network access. |
| Same, on another PC or network | Windows Firewall | Allow Python at the first prompt, or add a rule for port 8765 limited to the local subnet. |
| Works at home, not elsewhere | The network keeps devices apart | Use a phone hotspot, with the PC and every player connected to it. |

On this PC the firewall shouldn't get in the way: the Wi-Fi is set to Public, which normally blocks incoming connections, but `python.exe` already has two inbound Allow rules on that profile. Step 0 confirms it.

## Players who aren't in the room

The plan doesn't cover this, because a home network isn't reachable from outside without opening it up. If it's needed, these are the options:

| Option | Outside service? | Cost | Verdict |
| --- | --- | --- | --- |
| Share the Player Screen window on a video call | Yes (Discord, Meet) | Nothing to build | Simplest if you already use a call. |
| Tailscale | Yes, for connecting devices, though game traffic goes directly between them where possible | Every remote player installs an app | The best fit if a real page matters. |
| WireGuard, run yourself | No | A config for each player, plus a forwarded router port | Fully self-hosted, but the most setup. |
| Forward port 8765 on the router | No | A forwarded port, and it fails if the internet provider shares one public address among customers | Avoid: the server would face the whole internet, so it would need a password and HTTPS. |

None of these change the steps above. Only the address in the link would differ.

## What was tested

A throwaway script ran the real `CombatAppQt` offscreen, with this server design on `127.0.0.1` and six polling clients on the same PC.

| Check | Result |
| --- | --- |
| The server thread runs alongside the Qt app | Worked: 42 requests, 0 errors |
| A visible change reaches all six clients | Under 1 second each time (worst 0.80s) |
| Cost per publish to the UI | At most 0.59 ms |
| Monster HP or stat fields in the JSON | None, only health words |
| A hidden monster | Not listed, and its HP change left the ETag unchanged |
| A repo file name or `/../requirements.txt` | 404 |
| Start of combat, HP, conditions, turns, undo, back to initiative, End Encounter | All reached the view except End Encounter (DI-029) |
| Finding the Wi-Fi address | `gethostbyname` gave the wrong one; the UDP socket gave the right one |

That table is the check made before building. The finished page has since run in headless Chrome on this PC against the real server.

**Not tested:** a real phone, a mobile browser, or anything across the network. Step 0 and step 6 cover those. The firewall result comes from reading the rules, not from a connection.
