# Campaign setup: encounters.py and the logs

Every campaign lives in `Combat/Campaigns/<Campaign>/`:

| File | What it is | Written by |
|---|---|---|
| `encounters.py` | `CONFIG`: the campaign's party and every encounter it can run | You |
| `Campaign.py` | One line that makes the campaign from `encounters.py` | Nobody (leave it) |
| `CombatLogs/<encounter id>.json` | One log per encounter: who takes part, the monsters, every event of the fight | `{}` until the encounter is opened; then the combat window sets it up from `encounters.py` and logs the fight into it |
| `PlayerLogs/main_party.json` | The party's journal: where they've been (encounters, short and long rests) | The combat window |
| `CHEATSHEET.md` | The commands for this campaign | You |

The combat window only plays encounters listed in `encounters.py`. The
encounter's `EncounterSpec` sets it up, not its log: the log stays an empty
`{}` until the encounter is opened, and then records the fight.

## encounters.py

The config imports the stat blocks and character builders it uses and names them
directly, so a misspelled monster or build fails as soon as the file is imported.

```python
from Builds.Characters.Y2024_Bard_Valor_Clover import Y2024BardValorCloverCharacterBuilder
from Builds.Characters.Y2024_Paladin_Devotion_Edmund import (
    Y2024PaladinDevotionEdmundCharacterBuilder,
)
from Combat.EncounterConfig import CampaignSpec, CombatantSpec, EncounterSpec
from Combat.Monsters.CR_0.monsters import GoblinWarrior
from Combat.Monsters.CR_1.monsters import GoblinBoss
from Combat.Monsters.CR_1.monsters_homebrew import GreypawCR1

CONFIG = CampaignSpec(
    name="curse_of_the_lich",
    title="Curse of the Lich",
    description="Free text about the campaign.",
    party=[
        Y2024PaladinDevotionEdmundCharacterBuilder,
        Y2024BardValorCloverCharacterBuilder,
    ],
    encounters=[
        EncounterSpec(
            id="goblin_scouting_party",
            title="Goblin Scouting Party",
            description="A goblin scouting party, with Greypaw fighting alongside the party.",
            difficulty="Balanced for three level 3 players.",
            players=["Edmund", "Clover", "Kivi"],
            monsters=[
                CombatantSpec(GoblinBoss, "Goblin Boss", count=2),
                CombatantSpec(GoblinWarrior, "Goblin Warrior", count=4, group="Goblin Warriors"),
            ],
            allies=[CombatantSpec(GreypawCR1, "Greypaw (Ally)")],
            combatants_per_column=5,
        ),
    ],
)
```

### The campaign: `CampaignSpec`

| Field | Required | Meaning |
|---|---|---|
| `name` | yes | The campaign's id, snake_case. It's what `--campaign` takes. |
| `title` | yes | How it's shown, e.g. in the statistics report. |
| `description` | yes | Free text (may be `""`). |
| `party` | yes | The tracked party, as `CharacterBuilder` classes imported from `Builds/Characters/`. `[]` for a campaign without character sheets. |
| `encounters` | yes | The encounters, in the order Load Encounter lists them. The first one is what `RunCombatSimulator.py` runs with no flags. |

### An encounter: `EncounterSpec`

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | snake_case, unique across all campaigns. It names the log (`CombatLogs/<id>.json`) and is what `--scenario` takes. Don't rename an encounter that has been played: its log and the player log's line for it go by this id. |
| `title` | yes | How Load Encounter, the window title and the player log show it. |
| `description` | no | What the encounter is, shown in Load Encounter. |
| `difficulty` | no | A note on how hard it is, shown in Load Encounter. `--difficulty` computes the real rating. |
| `players` | no | Who of the party takes part, by character name or a part of one ("Kivi" for "Kivi Jätti"). Leave it out for the whole party. |
| `monsters` | no | The hostile side (see below). They count toward XP and difficulty. |
| `allies` | no | Friendly NPCs fighting with the party (see below). They're subtracted from the difficulty. |
| `combatants_per_column` | no | How many cards per column in the window (default 4). |

### Monsters and allies: `CombatantSpec`

Each line is one stat block, optionally several of it:
`CombatantSpec(monster, name=None, count=1, group=None, hidden_from_players=False)`.

| Field | Required | Meaning |
|---|---|---|
| `monster` | yes | The stat block's class, imported from `Combat/Monsters/CR_<x>/` (official `monsters.py` or `monsters_homebrew.py`), e.g. `GoblinBoss`, `GreypawCR1`. A few old ones live in `Combat/Combatants.py` (`Bull`, `Player1`); when two modules share a class name, import one under another name, e.g. `import Combat.Combatants as Combatants` and `Combatants.Priest`. |
| `name` | no | What it's called in the fight. With a `count`, they're numbered: `"Goblin Boss"` ×2 → Goblin Boss 1, Goblin Boss 2. Leave it out to use the stat block's own name. |
| `count` | no | How many (default 1). |
| `group` | no | Lines with the same `group` share one turn, as a GM runs a pack of the same monster: one initiative roll (with the first one's modifier), one row on the initiative screen ("Goblin Warriors (4)"), and they all take their turn together. Each keeps its own card and stat block. Monsters and allies can't share a group. |
| `hidden_from_players` | no | `True` for one that joins the fight later: it rolls initiative and has its card like the rest, but the players' screen and link don't show it (nor its turn, nor log lines about it) until the GM reveals it. Right-click its card as the only target and uncheck **Hidden from players**; the log then says it appears. Checking it again hides one mid-fight. |

### Players' summons

A player whose sheet has a feature that creates or summons a creature to fight
beside them (one that overrides `Feature.summons()`, so far the Reanimator
Artificer's Reanimated Companion and the Drakewarden Ranger's Drake Companion)
can summon it in any encounter they take part in, without a line in
`encounters.py`. It isn't in the log when it's set up: it joins the fight when it's
summoned, as "<character>'s <feature>" (e.g. "Hanna's Drake Companion",
numbered " 2", " 3" when one owner has several). Combat/Summons.py has the
details.

- **Initiative:** it has no row of its own. It takes its turn right after its
  owner's, also when it's summoned mid-fight (whoever's turn it is keeps it).
- **Summoning:** the owner's **Enable Feature** (Drake Companion, Reanimated
  Companion), or **Summon ...** in its owner's (or its own) right-click menu,
  which also offers the choice made each time (the drake's Draconic Essence:
  Acid, Cold, Fire, Lightning or Poison). It spends the feature's use and its
  Action, or the owner's lowest spell slot once the use is gone, and brings it
  out at full Hit Points for the players to see. Summoning a drake again
  replaces it (the old one vanishes); a Reanimated Companion can't be made
  while one is out (the menu entry is greyed out).
- **Dismiss:** in the summon's right-click menu; it leaves the fight (logged;
  Undo brings it back).
- **Its owner dies:** it drops to 0 Hit Points (a Reanimated Companion's Death
  Burst goes off).
- **The next encounter:** one that's out joins it from the start, with the Hit
  Points, conditions and choice the last encounter left it (conditions ending
  on a timer or a save don't carry). One that died is gone until it's
  summoned again. A long rest ends a Reanimated Companion; a drake stays out,
  rested to full (the lifetime of the feature's `SummonSpec`).
- **Summoned before the fight:** **Add Combatant** lists every summon of the
  party (with each choice) under "Already summoned…"; it joins at full Hit
  Points and spends nothing.
- **Older logs** were prepared with a hidden "<character>'s Companion
  (<feature>)" for each player and use the keys `companion_of` /
  `companion_choice`. They still load: a hidden one isn't out, and summoning
  replaces it.

To find a class, search the stat blocks for the monster's name, e.g.
`grep -rn 'combatant_type="Goblin Boss"' Combat/Monsters`: the class is the
`class ...:` line above the match, and the file is the module to import it from.

## Checking the config and emptying the logs

After adding or changing an encounter, check the config. Every log whose fight
hasn't started is made an empty `{}`, so the changed config sets it up when the
encounter is opened:

```
python -m Combat.Tools.prepare_encounters --campaign curse_of_the_lich
python -m Combat.Tools.prepare_encounters --all              # every campaign
python -m Combat.Tools.prepare_encounters --check            # check the config only
python -m Combat.Tools.prepare_encounters wrath_of_durmor    # just these encounters
```

It checks the whole config first (players are in the party, ids are valid and
unique, counts and groups make sense) and writes nothing while anything is wrong. Then,
for each encounter:

| The log | What happens |
|---|---|
| doesn't exist | **created empty**: `{}` |
| `{}` | left **empty** |
| set up (the encounter was opened), fight not started | **emptied** back to `{}` |
| fight in progress or ended | left as it is (**in progress** / **ended**) |
| not valid JSON | left as it is (**can't be read**), with how to get it back; the check fails |

It also lists any log in `CombatLogs/` named after no encounter id
(**NO ENCOUNTER**), e.g. after renaming an id: rename the log to the new id, or
delete it. The window never opens such a log.

Logs are written all at once: the window writes a temporary `<log>.json.tmp`
and renames it over the log, so a crash mid-write leaves the old log, never
half of one. A log that still can't be read (edited by hand, say) stops the
window with the file's name and the `git checkout` that gets it back.

When the window opens an encounter whose log is `{}` (or missing), it sets the
log up from the config (a log from before this setup that holds a fight only
gets the header it lacks). A log set up that way starts as:

```json
{
  "encounter": "goblin_scouting_party",
  "title": "Goblin Scouting Party",
  "players": ["Edmund", "Clover", "Kivi Jätti"],
  "round_number": 1,
  "combatants": [ ...companions, allies and monsters at full HP... ]
}
```

While the fight is played, the window keeps `combatants` and `round_number`
current, saves the turn order (`initiative_order`, everyone's names, players
too) and whose turn it is (`turn`), and adds one `round_<n>` list of events per
round. Continuing the fight picks up in that order, on that turn. Players' HP and
conditions aren't stored in it: they're replayed from the events (see below).

## Playing

- `--scenario <id>` opens that encounter (asking to continue or restart a fight in
  progress), with the players its log lists.
- Without `--scenario`, `--player-log` opens the party **between encounters**: their
  current HP, slots and conditions, with Load Encounter (Ctrl+O), Short Rest and
  Long Rest. Nothing is logged between encounters.
- **Restart** sets the log up again from the config and
  undoes the fight for the party. The old log is kept as
  `<id>_restarted_<timestamp>.json` (git-ignored).
- **End Encounter** marks the fight as ended (`ended_at`) and goes back to the party.
  Continuing it later reopens it.

## The player log

`PlayerLogs/main_party.json` lists where the party has been, in order:

```json
{"sessions": [
  {"type": "encounter", "scenario": "ashelm_church", "log": "../CombatLogs/ashelm_church.json",
   "started_at": "2026-09-08T19:28:25", "ended_at": "2026-09-08T20:30:23"},
  {"type": "long_rest", "started_at": "2026-10-10T19:33:13"},
  {"type": "short_rest", "started_at": "...", "events": [ ...heals, regained features... ]},
  {"type": "encounter", "scenario": "goblin_scouting_party", "log": "../CombatLogs/goblin_scouting_party.json",
   "started_at": "2026-10-15T18:54:57"}
]}
```

An encounter gets its line the first time something happens in it. A short rest
has no log of its own: its few events are on its line. The party's current state is
their character sheets with the events of every line since the last long rest
replayed onto them. Statistics count every line.

Both logs are committed: the party's state comes from them.
