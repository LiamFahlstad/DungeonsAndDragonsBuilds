# Summon framework plan

How to turn the combat simulator's current companion support (Drake Companion,
Reanimated Companion) into one framework that every summoning feature **and
spell** uses: Find Familiar, the Summon X spells, Animate Dead, Steel
Defender, Wildfire Spirit, Primal Companion, and so on.

This is a working plan: steps (section 4) and questions (section 5) are
added as the work goes; section 6 says how.

## 1. Where we are

The companion work (commit 8044cc59: Combat/Companions.py,
Combat/CombatUIQt/companions_mixin.py, tests/test_combat_ui_companions.py)
already solves the hard parts for one kind of summon. The table describes
it as it was before this plan; Phase 1 has since replaced the three
`companion*` hooks and `CompanionRules` with `Feature.summons()` and
`SummonSpec`.

| Piece | Today |
|---|---|
| Model hook | `Feature.companion(character, choice) -> ExtendedCombatantData`, `Feature.companion_choices(character) -> list[str]`, `Feature.companion_rules(character) -> CompanionRules` (Model/Content/Feature.py) |
| Rules | `CompanionRules(summon_again_replaces, ends_on_long_rest)`: the drake replaces itself and outlasts a long rest; the Reanimated Companion can't be made while one is out and ends on a long rest |
| Owner link | `BasicCombatantData.companion_of` → `"companion_of"` on the combatant dict, already in the four committed TimeLoopPR combat logs |
| Getting into an encounter | `companions_of()` pre-adds one hidden combatant per feature, named `"<character>'s Companion"`; Add Combatant can add a missing one (`_missing_party_companions`) |
| Summoning | `Companions.summon()`: rebuild card with the choice, full HP, reveal to players |
| Cost | Hard-coded: one feature use, else the **lowest** spell slot; plus the feature's action cost |
| Turn order | `place_after_owners`: right after the owner, no initiative of its own |
| Lifetime | `carried_state` carries HP/conditions/choice into the next encounter; `_carry_companions_over` finds it **by combatant name** (`last_seen`) in the earlier combat logs the player log lists, skipping logs before a long rest when `ends_on_long_rest` |
| Owner dies | `_companions_die_with`: drops to 0 HP (Death Burst noted) |
| Matching card → feature | `companion_feature()`, by `combatant_type` |

What it can't do yet:

1. **Spells.** Spells are JSON data (`spells_*.json` + `_extended.json`); they
   have no hook that returns a stat block. 23 + 15 spells carry the `summon`
   usage tag.
2. **More than one summon per owner.** Every companion is called
   `"<character>'s Companion"`, so a Battle Smith with Find Familiar gets two
   combatants with one name (names are how effects find targets).
3. **Different lifetimes.** `CompanionRules` covers "until long rest" and
   "until 0 HP / recast". Missing: concentration (Summon Beast) and a fixed
   duration (Wildfire Spirit: 1 hour; Animate Dead: control for 24 hours).
4. **Different costs.** A specific slot level and upcasting (Summon Beast's
   stat block scales with the slot), another feature's use (Wildfire Spirit
   spends a Wild Shape use), free (Steel Defender comes with the Long Rest).
5. **Several creatures per cast** (Animate Dead: one creature, plus two for
   each slot level above 3; Undead Thralls adds one more).
6. **Different turn rules.** Most 2024 summons act right after their owner;
   some roll their own initiative (2024 Find Familiar: "It rolls its own
   Initiative and acts on its own turn").
6b. **Summoned before the fight.** Find Familiar (1 hour), Animate Dead
   (1 minute) and Steel Defender (at a long rest) are cast or made outside
   combat, so "cast it in the encounter" isn't how they usually arrive.
7. **Modifier features** that change other summons: Undead Thralls (Animate
   Dead), Mighty Summoner (Shepherd), Elemental/Otherworldly Familiar feats,
   Pact of the Chain's extra familiar forms.
8. **Recasting replaces, or is refused.** `CompanionRules` already does both
   for one creature (drake replaces; Reanimated Companion refuses while one
   is out). The framework needs it for several creatures and for spells.

## 2. Goals and non-goals

**Goals**

- One description of "what this source summons" (`SummonSpec`) that a
  `Feature` *or* a `Spell` returns, with no Qt and no combat-dict knowledge.
- One combat-side lifecycle (`Combat/Summons.py`) for create → act → end,
  driven entirely by the spec.
- One UI entry point: casting the spell or enabling the feature summons;
  the card menu summons again, dismisses or picks a choice.
- Drake Companion and Reanimated Companion keep working, with their tests,
  and become the first two users of the framework.

**Non-goals (first pass)**

- Summon "effects" without a stat block stay ordinary spell effects:
  Spiritual Weapon, Healing Spirit, Spirit Totem auras, 2024 Conjure Animals
  (a pack that's an area, not creatures), Negative Energy Flood, Tentacle of
  the Deep. They keep the `summon` usage tag; they just don't make a
  combatant. Classify each tagged entry once (see Phase 4).
- Out-of-combat use of familiars (scouting, telepathy, touch spells through
  them) is just text on the card.
- Automating a summon's AI. The GM still plays its turn.

## 3. Design

### 3.1 Model: `SummonSpec` (new, `Model/Content/Summons.py`)

Dataclasses, like the rest of Model/Content (Feature.py's `CompanionRules`,
`FeatureUses`): pure data plus builders. No Qt, no Combat imports, and no
import of Feature.py (Feature.py imports this module; the layering test
forbids `TYPE_CHECKING` workarounds). So the spec has no action cost of its
own: a feature's comes from `feature_action_cost(feature)` as today, a
spell's from its casting time.

```python
class SummonLifetime(Enum):
    UNTIL_LONG_REST = "until long rest"     # Reanimated Companion, Steel Defender
    UNTIL_DISMISSED = "until dismissed"     # Drake, Find Familiar (gone at 0 HP / recast)
    CONCENTRATION = "concentration"         # Summon X spells (also has a duration)
    DURATION = "duration"                   # Wildfire Spirit 1 hour, Animate Dead 24 hours

class SummonTurn(Enum):
    AFTER_OWNER = "after owner"             # shares the owner's initiative
    OWN_INITIATIVE = "own initiative"       # 2024 Find Familiar

class OnZeroHp(Enum):
    VANISHES = "vanishes"                   # removed from the fight (most summons)
    DIES = "dies"                           # stays as a corpse (Reanimated Companion, Animate Dead's undead)

class WhenFull(Enum):
    """What summoning again does when max_out are already out."""
    REPLACES = "replaces"                   # the oldest goes (drake, Find Familiar, Find Steed)
    REFUSED = "refused"                     # can't (Reanimated Companion: "can't create one while your companion is present")

@define
class SummonCost:
    """One way to pay for a feature's summon; a spec lists them in the order
    to try. Spells don't use it: casting already spends the slot."""
    feature_use: str | None = None          # a feature's name whose use is spent ("Wild Shape"; None: this feature)
    spell_slot: int | None = None           # minimum slot level (None: no slot)

@define
class SummonSpec:
    name: str                               # "Drake Companion", "Bestial Spirit"
    build: Callable[[CharacterView, SummonContext], ExtendedCombatantData]
    choices: Callable[[CharacterView], list[str]] = lambda _: []
    choice_label: str = ""                  # "Draconic Essence", "Environment", "Form"
    count: Callable[[CharacterView, SummonContext], int] = lambda *_: 1
    max_out: int | None = 1                 # None: no limit (Animate Dead)
    when_full: WhenFull = WhenFull.REPLACES
    lifetime: SummonLifetime = SummonLifetime.UNTIL_LONG_REST
    duration_seconds: int | None = None
    turn: SummonTurn = SummonTurn.AFTER_OWNER
    costs: list[SummonCost] = field(default_factory=list)   # [] = free
    on_zero_hp: OnZeroHp = OnZeroHp.VANISHES
    drops_with_owner: bool = False          # Reanimated Companion's "if you die"; the drake's "or until you die"

@define
class SummonContext:
    choice: str | None = None
    slot_level: int | None = None           # what was spent; drives upcast scaling
```

Why a spec object instead of more `Feature` overrides: spells need the exact
same description, and the combat code then reads one object instead of
asking a feature five questions.

### 3.2 Hooks: features and spells return specs

- `Feature.summons(character) -> list[SummonSpec]` replaces `companion()` /
  `companion_choices()`. Default `[]`. Drake Companion and Reanimated
  Companion are migrated in the same change (they're the only overrides).
- `Spell.summons(character) -> list[SummonSpec]` on the `Spell` base class,
  looked up by spell name in a Python registry,
  `CharacterContent/Summons/SpellSummons.py`:
  `SPELL_SUMMONS: dict[str, Callable[[], SummonSpec]]`. Spell JSON stays
  untouched (it's scraped data); the registry is the hand-written part, like
  `_extended.json` is for tags.
- Stat blocks come from three places, all already used in the repo:
  1. hand-built `_build_*` functions in the feature files (Drake, Steel
     Defender, Wildfire Spirit, Vestige, Reanimated);
  2. Combat/Monsters classes for fixed creatures (Find Familiar's CR 0
     beasts, Animate Dead's Skeleton/Zombie), the same `CreatureForm`
     callables Wild Shape uses;
  3. new builders for the scaling spell stat blocks (Bestial Spirit, Fey
     Spirit, ...), each `(character, ctx) -> ExtendedCombatantData` using
     `ctx.slot_level`. These spells share one shape (AC/HP/attacks scale with
     slot level, a choice of variant), so write one helper and one small
     table per spell.

### 3.3 Modifier features

Modifiers change two different things, so there are two hooks, both default
no-ops and both order-insensitive, like `apply()`:

- `Feature.adjust_summon(character, spec) -> SummonSpec`: returns the spec
  with more creatures (`count`) or more `choices`. Run on every owner
  feature before anything is built.
- `Feature.modify_summon(character, spec, stat_block, ctx) -> None`: edits
  each built stat block in place.

Each modifier must check `spec.name` / the source itself, since it sees
every summon. Known users:

- Undead Thralls: Animate Dead makes one more creature (`adjust_summon`);
  HP + Wizard level, damage + PB (`modify_summon`).
- Mighty Summoner: +2 HP per Hit Die, magical natural weapons.
- Durable Summons (Conjurer 6): Temporary HP equal to twice the Wizard level
  and resistances, for creatures from Conjuration spells cast with a slot.
- Splintered Summons (Conjurer 14): two creatures instead of one, once per
  long rest. This one is a player's choice at cast time, not automatic, so
  it's a prompt in S4.3 that spends the use, not an `adjust_summon`.
- Elemental / Otherworldly Familiar feats: Find Familiar gets the energy
  trait / extra creature types.
- Pact of the Chain: extra Find Familiar forms. It's an invocation
  (`character.invocations`, an enum in CharacterContent/Invocations), not a
  `Feature`, so neither hook reaches it: Find Familiar's own `choices`
  reads `character.invocations`.

(Focused Conjuration is a concentration rule, not a summon modifier; it
belongs with the concentration checks, not here.)

### 3.4 Combat side: `Combat/Summons.py` (generalises Combat/Companions.py)

Pure dict functions, no Qt, as today. Keys on a summon's combatant dict:

| Key | Meaning |
|---|---|
| `summon_of` | owner's character name (renamed from `companion_of`, read both while old logs exist) |
| `summon_source` | `"feature:Drake Companion"` / `"spell:Summon Beast"`, to find the spec again |
| `summon_choice`, `summon_slot` | the `SummonContext` it was made with |
| `summon_lifetime`, `summon_turn`, `summon_on_zero_hp` | copied from the spec, so a saved log replays without the sheet |

Functions:

- `spec_for(sheet, combatant) -> SummonSpec | None` (replaces
  `companion_feature`): looks up by `summon_source`, not `combatant_type`.
- `create(owner_sheet, spec, ctx) -> list[dict]`: builds `count` dicts,
  applies modifiers, names them uniquely: `"<owner>'s <spec.name>"`, then
  `" 2"`, `" 3"` (reuse `_unique_name`). The carry-over finds a summon in
  earlier logs **by name** (`last_seen`), and those logs call it
  `"<owner>'s Companion (<type>)"` (`old_name`), so `last_seen` also tries
  the old name (`aliases`) for the first summon of each spec. `source_for`
  (beside `spec_for`) returns the feature too, and finds an older log's
  summon, which has no `summon_source`, by its stat block's type; `mark`
  sets the keys on one (also on an older log's hidden companion that the
  carry-over brings out).
- `place_after_owners` stays; only `AFTER_OWNER` summons go through it.
  `OWN_INITIATIVE` ones get an initiative row (rolled at summon time in
  combat, `_add_initiative_row` before it).
- `make_room(existing, spec, new) -> list[dict] | None`: with `REPLACES`,
  the oldest ones past `max_out` (to remove); with `REFUSED`, None when
  there's no room (the menu greys the entry out). `existing` is only the
  ones that are out (`is_out`: not hidden, above 0 HP). Summoning also
  drops the spec's leftovers that aren't out and won't be back: an older
  log's hidden companion, or a `VANISHES` one at 0 HP. A `DIES` one's body
  stays, so the new one is numbered (`" 2"`).
- `carried_state` stays for `UNTIL_LONG_REST` / `UNTIL_DISMISSED` /
  long-`DURATION` summons; `CONCENTRATION` summons don't carry (see Q2).

**Created on demand, not pre-added.** Today each encounter is prepared with a
hidden companion. That doesn't scale to spells (which summon? how many?).
Instead, summoning creates the combatant; the next encounter re-creates the
persistent ones from the player log (the carry-over already reads the
previous logs). Keep reading old logs' hidden companions so existing
TimeLoopPR logs still load.

Summons made **before** the fight (Find Familiar, Animate Dead, Steel
Defender; see 1.6b) need a way in that isn't a cast during the encounter:
generalise today's Add Combatant entry for a missing party companion into
"Already summoned…", which adds any of the party's specs (with its choice
and slot) at full HP and spends nothing, logged as `Action.SUMMON` with
`"before_combat": true`.

### 3.5 Lifecycle in the UI (`companions_mixin.py` → `summons_mixin.py`)

| Event | What happens | Where it hooks in |
|---|---|---|
| Cast a summon spell | after the slot is chosen: ask the choice (menu at the mouse, as `_pick_companion_summon` does), create, add to turn order | `_apply_cast_spell` (spells_mixin) checks `spell.summons(sheet)` |
| Enable a summon feature | pay the first affordable `SummonCost`, spend `action_type`, create | `_pick_companion_summon` generalised |
| Card menu | "Summon again (cost)", choice submenu, "Dismiss" | `_add_summon_actions` generalised |
| Concentration ends | every summon tied to that spell vanishes | `_end_spell_effects`: store summon names in the `active_spells` entry (`"summoned": [...]`) next to `"applied"` |
| Duration runs out | same, from `_tick_active_spells` | same entry |
| 0 HP | `VANISHES`: removed (logged); `DIES`: stays, dead | damage_mixin's knock-out path |
| Owner dies | `drops_with_owner` summons drop to 0 HP (Death Burst) | `_companions_die_with` generalised |
| Long rest | `UNTIL_LONG_REST` summons end; feature uses come back | rests_mixin |
| Undo | all of it is `@undoable` dict changes, as now | |

**Logging.** Add `Action.SUMMON` / `Action.DISMISS` with
`{source, choice, slot, names}` so the player log's replay knows which
summons are out and which slots/uses were spent (today the use and slot are
logged separately; keep those too).

### 3.6 Cost resolution

Replace `_summon_uses_left` / `_lowest_slot` with one function over
`spec.costs`: try each `SummonCost` in order, offer the cheapest valid one by
default and let the card menu pick another. "Lowest slot" stays the default
for the drake/reanimator, which matches today's behaviour.

This is for features only. A spell's summon is paid by casting it: the
existing cast flow picks and spends the slot (and its level is the upcast
level in `SummonContext.slot_level`), so a spell's spec has `costs=[]` and
the minimum level comes from the spell itself. Never charge both.

## 4. Steps

Each phase leaves the app working and the tests green. Agents are suggested
per CLAUDE.md, with disjoint file sets per step. Steps have stable ids
(`S<phase>.<n>`) so commits, agent briefs and questions can refer to them;
section 6 says how to add, change or drop steps.

Status: `[ ]` to do, `[x]` done. Append *(in progress)*, *(blocked by Qn)*
or *(dropped: reason)* after the id when it applies.

After each phase: `verify-agent-work`, then `code-reviewer`; phases 4 and 5
also get `rules-checker` against the spell and feature texts.

### Phase 1: model, and the two existing companions moved onto it

- [x] **S1.1** Add `Model/Content/Summons.py` (`SummonSpec`,
  `SummonContext`, `SummonCost`, the enums) with unit tests.
  *Agent:* character-engine-dev.
- [x] **S1.2** Add `Feature.summons()`, `Feature.adjust_summon()` and
  `Feature.modify_summon()` defaults to Model/Content/Feature.py.
  *Agent:* character-engine-dev.
- [x] **S1.3** Move DrakeCompanion and ReanimatedCompanion to `summons()`;
  delete `companion()` / `companion_choices()` / `companion_rules()` and
  `CompanionRules` (their lifetime and `when_full` say the same thing:
  drake `UNTIL_DISMISSED` + `REPLACES`, Reanimated `UNTIL_LONG_REST` +
  `REFUSED`). Point every Combat caller at `summons()`: `companions_of`
  (PlayerCombatant.py), `companion_feature` and `set_stat_block`
  (Companions.py), `_may_summon_again`, `_carry_companions_over` and
  `_missing_party_companions` (companions_mixin.py), and the Enable check in
  features_mixin.py. Names and combat behaviour don't change yet.
  *Agent:* character-engine-dev for the Model and feature files, with the
  Combat files named as in scope (they're one change: the old hooks go).
  *Done when:* the sheet snapshots pass without an update,
  tests/test_combat_ui_companions.py passes with only its direct
  `companion()` / `companion_choices()` calls moved to the spec, and a test
  builds both specs with each choice.

### Phase 2: the combat side, generalised

*Agent:* combat-simulator for every step in this phase.

- [x] **S2.1** Rename `Combat/Companions.py` to
  `Combat/Summons.py` and the mixin to match; add the new dict keys (3.4);
  rename the `companion_of` key to `summon_of`, rewrite it in the four
  committed TimeLoopPR combat logs, and keep reading `companion_of` (Q4).
- [x] **S2.2** Give each summon its own name, so one owner can have several;
  the carry-over still finds summons under their old `"<owner>'s
  Companion"` name in earlier logs (3.4).
- [x] **S2.3** Create summons on demand; re-create the
  persistent ones from the earlier logs; "Already summoned…" for ones made
  before the fight (3.4); old TimeLoopPR logs still load.
- [x] **S2.4** `make_room` for `max_out` / `when_full`; add "Dismiss" to the
  card menu.
- [ ] **S2.5** Resolve costs from `spec.costs` (3.6).
- [ ] **S2.6** Log `Action.SUMMON` / `Action.DISMISS`, and replay them from
  the player log.
- [ ] **S2.7** Give `OWN_INITIATIVE` summons an initiative row, rolled with
  the GM's monster roll button (Q3).
- [ ] **S2.8** Tests: two summons on one owner, replacing on resummon,
  dismiss, replay. Screenshot with the `run-apps` skill.
- [ ] **S2.9** A player's own summon shows its full card in the player
  view once it's out (Q11).

### Phase 3: the remaining features with stat blocks

Each is a `summons()` override around the feature's existing `_build_*`.
*Agent:* character-engine-dev, then combat-simulator for anything in the UI.

- [ ] **S3.1** Steel Defender (Battle Smith).
- [ ] **S3.2** Wildfire Spirit, paid with a Wild Shape use.
- [ ] **S3.3** Vestige Companion (Vestige Warlock).
- [ ] **S3.4** Primal Companion (Beast Master), with the Land/Sea/Sky choice.
- [ ] **S3.5** Go through the other `summon`-tagged features and add a step
  here for each one that makes a creature.

### Phase 4: spells

- [ ] **S4.1** Classify the 38 `summon`-tagged spells (23 in
  spells_dnd2024_extended.json, 15 in spells_dnd5e_extended.json) as a
  *creature* (gets a registry entry) or an *effect* (stays a spell effect),
  into Appendix A. Also sweep for creature spells that lack the tag: Find
  Steed (2024) isn't tagged, though S4.8 is about it; tag those through
  the `usage-tags` skill. Add a step below for each creature spell.
- [ ] **S4.2** Add `Spell.summons()` and the registry
  `CharacterContent/Summons/SpellSummons.py`.
- [ ] **S4.3** Make casting a summon spell summon: slot, then choice, then
  create (3.5). The slot is the cast's own; nothing else is charged (3.6).
- [ ] **S4.4** Tie summons to their concentration and duration
  (`"summoned"` on the `active_spells` entry). A concentration summon ends
  with the encounter; the next encounter of its owner offers "keep it" (Q2).
- [ ] **S4.5** Find Familiar (CR 0 beast forms, `OWN_INITIATIVE`;
  recasting replaces the old familiar; Pact of the Chain's forms come from
  `character.invocations`, 3.3).
- [ ] **S4.6** The Summon X family: one shared helper that scales with the
  slot, then one entry per spell.
  *Done when:* Summon Beast cast with a level 3 slot and a level 4 slot has
  different HP, and losing concentration removes it.
- [ ] **S4.7** Animate Dead (Skeleton or Zombie; one creature plus two per
  slot level above 3; usually brought in with "Already summoned…").
- [ ] **S4.8** Find Steed. Decide how a steed works without mounted combat
  when this starts (Q10); until then it stays a spell effect.

### Phase 5: modifier features

- [ ] **S5.1** Undead Thralls.
- [ ] **S5.2** Mighty Summoner.
- [ ] **S5.3** Elemental Familiar and Otherworldly Familiar feats.
- [ ] **S5.4** Pact of the Chain's extra familiar forms.
- [ ] **S5.5** *(dropped: Focused Conjuration only protects Concentration,
  it doesn't change a summon; see 3.3)*
- [ ] **S5.6** Durable Summons (Conjurer 6).
- [ ] **S5.7** Splintered Summons (Conjurer 14): the cast-time prompt
  (3.3).

### Later (not scheduled)

Steps that a question's answer may call for. Move one into a phase, with a
new id, when it's picked up.

- [ ] **SL.1** Render the sheets' summon stat blocks from the spec (Q5).
- [ ] **SL.2** Commanding a summon on the owner's turn (Q6).
- [ ] **SL.3** Bringing a destroyed persistent summon back (Q8).

## 5. Questions

Each question names the steps it blocks, a recommendation, and an answer
line. When it's answered, fill in the answer and date, update the steps it
affects, and leave the question here so the reasoning stays on record.

### Q1. Pre-added hidden companions, or created on demand? *(blocks S2.3)*
- **Why it matters:** today each encounter is prepared with a hidden
  companion. That can't work for spells (which summon? how many?).
- **Recommendation:** create on demand, add "Already summoned…" for
  summons made before the fight (3.4), and keep loading old logs.
- **Answer:** 2026-11-05: the recommendation.

### Q2. Do concentration summons last past one encounter? *(blocks S4.4)*
- **Why it matters:** a 1-hour Summon Beast can outlast a fight, but the
  simulator doesn't track the time between encounters.
- **Recommendation:** end it with the encounter, and offer "keep it" when
  the next encounter starts.
- **Answer:** 2026-11-05: the recommendation.

### Q3. Who rolls initiative for an `OWN_INITIATIVE` summon? *(blocks S2.7)*
- **Why it matters:** players roll their own dice; monsters use the GM's
  roll button.
- **Recommendation:** the GM's monster roll button.
- **Answer:** 2026-11-05: the recommendation.

### Q4. Rename `companion_of` to `summon_of`? *(blocks S2.1)*
- **Why it matters:** the key is in the four committed TimeLoopPR combat
  logs already (the companion work is committed, in 8044cc59).
- **Recommendation:** rename, rewrite those four logs in the same change
  (a one-off scratch script), and keep reading the old key for logs outside
  the repo. Or keep `companion_of` as the key's name and only rename the
  code; that costs nothing.
- **Answer:** 2026-11-05: the recommendation's first option: rename the key to
  `summon_of`, rewrite the four committed TimeLoopPR combat logs in the same
  change, and keep reading `companion_of`.

### Q5. Should the character sheet draw summon stat blocks from the spec? *(SL.1)*
- **Why it matters:** each feature has a separate `format_*` function for
  the sheet beside its `_build_*` for combat, so the two can disagree.
- **Recommendation:** yes, after Phase 3, as its own step with a snapshot
  review.
- **Answer:** 2026-11-05: the recommendation.

### Q6. Should the UI track commanding a summon? *(SL.2)*
- **Why it matters:** Steel Defender, Primal Companion and Drake Companion
  only act when the owner spends a Bonus Action to command them (otherwise
  they Dodge). The simulator doesn't check that.
- **Recommendation:** not in the first pass; the rule stays text on the
  card.
- **Answer:** 2026-11-05: the recommendation.

### Q7. Does any summon make death saving throws? *(affects `OnZeroHp`)*
- **Why it matters:** `OnZeroHp` has only "vanishes" and "dies". If a source
  text says otherwise, the enum needs another value.
- **Recommendation:** check while doing S3.x and S4.x; add a value only when
  a text needs it.
- **Answer:** 2026-11-05: the recommendation.

### Q8. How is a destroyed persistent summon brought back? *(SL.3)*
- **Why it matters:** some features restore a destroyed companion (with a
  spell slot, Mending or similar), which is not the same as summoning it
  anew (it may keep its choice, or come back with some Hit Points).
- **Recommendation:** model it as a second action on the spec once a
  feature in Phase 3 needs it.
- **Answer:** 2026-11-05: the recommendation.

### Q9. How much of a familiar's out-of-combat magic is modelled?
- **Why it matters:** shared senses, delivering touch spells and the like
  are part of Find Familiar, but don't change a combat card.
- **Recommendation:** text on the card only.
- **Answer:** 2026-11-05: the recommendation.

### Q10. How does a steed work with mounted combat? *(blocks S4.8)*
- **Why it matters:** the simulator has no mounted combat, so it isn't clear
  whether a steed is a separate turn or acts with its rider.
- **Recommendation:** decide when S4.8 starts; until then Find Steed stays a
  spell effect.
- **Answer:** 2026-11-05: the recommendation.

### Q11. What do players see of their summons?
- **Why it matters:** the player view hides stat blocks of monsters; a
  player's own summon is theirs to know.
- **Recommendation:** show its full card to the players once it's out.
- **Answer:** 2026-11-05: the recommendation.

### Q12. What happens to summons that stop being controlled?
- **Why it matters:** Animate Dead's undead turn hostile when control lapses;
  Planar Binding can end with a hostile creature.
- **Recommendation:** out of scope; the GM turns it into an ordinary monster.
- **Answer:** 2026-11-05: the recommendation.

### Q13. Replaying an old log after the owner levelled up
- **Why it matters:** a summon's stat block depends on the owner's level, and
  modifier features can be gained between sessions.
- **Recommendation:** the log keeps the card as it was built; it's only
  rebuilt when it's summoned again.
- **Answer:** 2026-11-05: the recommendation, since re-summoning is possible:
  the card menu's "Summon again" rebuilds the card from the current sheet.

## 6. Keeping this plan up to date

This is a working plan: steps and questions are added as the work turns
them up.

- **New step:** add it at the end of its phase with the next free id
  (`S3.6` after `S3.5`), or in "Later" (`SL.n`) if it isn't scheduled. Never
  renumber, so ids in commits and agent briefs keep pointing at the right
  step. A new phase gets the next number and goes before "Later".
- **Changed step:** edit it in place, and say why in the changelog.
- **Dropped step:** keep it, marked *(dropped: reason)*.
- **New question:** add it at the end of section 5 with the next `Q` number,
  in the same form, and mark the steps it blocks *(blocked by Qn)*.
- **Answered question:** fill in its answer and date, unblock or change the
  steps it affected, and add a changelog line.
- **Design changes** (section 3) that a step or answer causes are made in
  section 3 too, so it always describes what's being built.
- Agents doing a step update its status and the changelog. They may add
  steps and questions but not answer questions: answers come from the user.

## 7. Changelog

- 2026-11-04: Plan written.
- 2026-11-04: Phases split into numbered steps; unanswered questions
  section (Q1-Q13); rules for keeping the plan up to date.
- 2026-11-04: Reviewed against the code. Section 1 now says the companion
  work is committed and lists `CompanionRules` and the by-name carry-over.
  Drake's lifetime is `UNTIL_DISMISSED` (it outlasts a long rest). Added
  `WhenFull` (the Reanimated Companion refuses a second one, it doesn't
  replace), `adjust_summon` beside `modify_summon` (count/choice changes
  aren't stat-block edits), "Already summoned…" for summons made before
  the fight, and that spells never pay through `SummonCost`. S1.3 lists all
  six Combat callers. Find Familiar is `OWN_INITIATIVE` (2024 text). S4.1
  also sweeps untagged creature spells (Find Steed). S5.5 dropped (Focused
  Conjuration isn't a summon modifier); S5.6 Durable Summons and S5.7
  Splintered Summons added. Pact of the Chain is an invocation, not a
  Feature. Q4's reasoning updated.
- 2026-11-04: S1.1-S1.3 done: Model/Content/Summons.py (frozen dataclasses),
  the three Feature hooks, Drake and Reanimated Companion on `summons()`,
  the old `companion*` hooks and `CompanionRules` deleted; Combat callers
  take each feature's first spec (`Companions.companion_spec`).

- 2026-11-05: Q1-Q13 answered (the recommendations; Q4 takes the rename
  and rewrites the four logs). S2.1, S2.3, S2.7 and S4.4 unblocked and
  given their answers; S4.8 says Q10's decision comes first; S2.9 added
  for Q11 (players see their summon's full card).
- 2026-11-05: S2.1-S2.4 done: Combat/Summons.py and summons_mixin.py (renamed),
  the `summon_*` keys (old logs' `companion_of` / `companion_choice` still
  read; the four TimeLoopPR logs rewritten), names `"<owner>'s <spec name>"`,
  summons made on demand (no hidden ones in prepared logs; `prepared_log`'s
  `sheets` argument is now unused), "Already summoned…", `make_room` and
  Dismiss. 3.4 says what `make_room` counts and what summoning drops.

## Appendix A. Spell classification

Filled in by S4.1: each `summon`-tagged spell, whether it makes a creature or
is an effect, and the step that implements it.

| Spell | Source | Creature or effect | Step |
|---|---|---|---|
