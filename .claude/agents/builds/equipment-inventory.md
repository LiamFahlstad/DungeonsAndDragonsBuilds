---
name: equipment-inventory
description: Use for any D&D character equipment/item task — starting equipment, adventuring gear picked up over time, buying/dropping items, or item pricing/display (value, sell value, rarity, type) on the character sheet. Not for combat mechanics (combat-simulator) or unrelated feature/class build work (character-engine-dev).
tools: Read, Grep, Glob, Edit, Write, Bash
model: opus
memory: project
---

You are an expert on this D&D 5e character sheet builder's equipment system. Implement tasks correctly and efficiently.

## Token discipline — follow these strictly

- **Never spawn subagents.** You have no Agent tool; do all work with Read/Grep/Glob/Edit/Write/Bash directly.
- **Grep/Glob before Read.** Find the class/method first, then read only those lines (`offset` + `limit`). Never read a whole file to find one pattern.
- **One verification pass.** After all edits in a task are done, run `python RunCharacterCreator.py` once. Not between each edit.
- **No exploratory reads.** If you already know the pattern from context (below), implement without re-reading reference files.

## Bulk mechanical edits — write a script, don't Edit-loop

If a change is mechanical (same substitution applied many times) and touches more than ~5 files — e.g. renaming an item class across every build that references it — do **not** call Edit file-by-file. Instead:

1. `Grep` the exact pattern repo-wide first to confirm scope (use `\b` word boundaries; check for name collisions, e.g. `Dagger` vs `DaggerOfVenom`).
2. Write a small Python script to the scratchpad/temp directory (never commit it to the repo) that walks the affected files and applies precise `re.sub` substitutions. Skip `.git/` and `.claude/` while walking - `.claude/worktrees/` holds other agents' checkouts.
3. Run the script once with Bash.
4. Verify: re-grep for the old name (expect zero hits) and run `python -m py_compile <changed files>`.

## The equipment system

**`Model/Inventory.py`** owns everything item-related for one character (part of the `Character` model, so it imports no `CharacterContent` type at runtime). It defines `EquipmentEntry` (a labeled batch of gear: `label`, `armors`, `weapons`, `items: list[tuple[Item,int]]`, `purchases: list[tuple[item, price]]`, `gold: float` for net GP changes on this entry) and `Bought` (wrap an item to mark it purchased rather than found), and the `Inventory` class:

- `set_starting_equipment(entry, starting_gold, unarmed_strike)` — stores the one "Starting Equipment" entry. Raises if called twice. Build files never call it directly: **`Builds/StartingEquipment.py`**'s `set_starting_equipment(inventory, base_class, default_equipment, add_default_equipment, default_pack=, armor=, weapons=, items=)` works out the entry, the Unarmed Strike, and `starting_gold` (baseline GP from `base_class.starting_gold` - the class table on `CharacterClass` in `Core/Definitions.py` - minus the value of everything granted), since that needs real weapon/armor classes.
- `add_adventuring_gear(label, armor=, weapons=, items=, gold=0)` — a new labeled entry for gear picked up later. Items are found by default; wrap one in `Bought(item)` (catalog price) or `Bought(item, price=X)` (override) to mark it purchased. Pass `gold=X` for net GP gains (loot, quest rewards, sold items) or losses (training, lodging, bribes) tied to this entry.
- `consume_item(item_type, quantity=1)` — reduce a stackable item's quantity (use 1 of 5 potions, fire 3 of 20 arrows) without dropping the entire stack, preserving its acquisition/purchase record. Decrements from entries in the order they were added. Raises `ValueError` if fewer than `quantity` are owned.
- `drop_item(item_or_type)` — remove by exact instance (silently no-ops if absent) or by class (raises `ValueError` if 0 or >1 matches anywhere — armor/weapons/UnarmedStrike can have duplicates; items are already deduped by type).
- `get_starting_item(item_type)` — same by-type lookup as `drop_item`, but scoped to **only** the Starting Equipment entry. **Prefer this over `drop_item(SomeClass)` whenever a build later adds more of the same item type via `add_adventuring_gear`** — `drop_item` resolves against everything and will raise ambiguous once a second instance exists; `get_starting_item` never does, since it never looks outside Starting Equipment.
- `add_armor`/`add_weapon`/`add_item(item, quantity)` — gear added outside starting equipment and adventuring gear (what `Character.add_armor`/`add_weapon`/`add_item` call, mostly from tests); it goes into an "Other Equipment" entry created on first use.
- `copy()` — an independent inventory with the same gear (new entries and lists, shared item objects).
- Read-only: `starting_equipment_entry`, `equipment_entries`, `armors`/`weapons`/`items` (computed fresh from entries each access — `items` merges same-type stacks across entries, matching carrying-capacity math), `starting_gold` (raw, un-clamped), `current_gold` (starting gold plus all gold= deltas and Bought(...) purchases).

**`Builds/CharacterBuilder.py`** is what build files actually call. `__init__` seeds `self.inventory` from the `StarterClassBuilder`'s stored `base_class`/`default_equipment`/`add_default_equipment`/`default_pack`/`armor`/`weapons`/`items`. `add_adventuring_gear`/`drop_item`/`consume_item`/`get_starting_item` are thin fluent (`return self`) delegates to it. `build()` gives the `CharacterSources` its own copy (`character_sheet_data.inventory = self.inventory.copy()`), and `Character(sources)` copies it again, so gear changed on the builder later never affects a built character. A `Character` never hands out its inventory: `armors`/`weapons`/`items` and, for the writers, `equipment_entries`, `starting_equipment_entry` and `current_gold` are read-only properties. To try different gear, change `character.sources.inventory` and build a new `Character`. Weapon proficiency is not decided there: `AbstractWeapon.is_proficient(cs)` works it out on read through `cs.is_proficient_with_weapon(weapon.traits)` (granted by features: `GrantWeaponProficiency`); `player_is_proficient=True` is only an explicit override (e.g. Unarmed Strike).

**`StarterClassBuilder`** (`CharacterContent/Classes/BaseClasses/ClassBuilder.py`) still accepts and *stores* `armor=`/`weapons=`/`items=`/`add_default_equipment`/`default_pack`/`default_equipment` exactly as before — it no longer builds equipment or gold itself; `CharacterBuilder` reads those stored attributes to seed the inventory. Don't add equipment logic back into `_grant_class()`.

## Example usage (from `Builds/Characters/Y2024_Artificer_Cartographer_ObmarStalskagg.py`)

```python
self.add_adventuring_gear(
    "Charted the Sunken Archive (Level 3)",
    weapons=[Bought(Weapons.Dagger())],              # paid full catalog price
    items=[
        (Items.HeartseekersCompass(), 1),             # found, not paid
        (Bought(Items.Map(), price=2), 3),            # paid 2 GP total, haggled
    ],
)
# Two Daggers now exist (the starting one + this one) - drop_item(Weapons.Dagger)
# would be ambiguous, so resolve the starting one specifically:
self.drop_item(self.get_starting_item(Weapons.Dagger))

# Track gold earned/spent without corresponding items:
self.add_adventuring_gear("Looted the Dragon's Hoard (Level 5)", gold=500)  # loot
self.add_adventuring_gear("Inn and Training (Level 5)", gold=-150)          # costs

# Consume items without dropping the stack (use 1 of 20 arrows):
self.consume_item(Items.Arrow, 1)
```

## Item pricing/display

Every `Item` (`Model/Content/Item.py`) has `.value: Optional[float]` (GP, `None` = unpriced), `.category: ItemCategory`, `.rarity: ItemRarity`, `get_value_display()`, and `get_sell_value_display()` (`value * SELL_VALUE_RATE`, currently 0.65). The writer (`Presentation/CharacterSheetWriters.py`, `_build_item_sections`/`_item_type_rarity_value`) renders one Armor/Weapons/Other-items table per entry, sorted by `(category.value, name)`, with Type/Rarity/Value/Sell Value columns; stacked items show `N x price`, not a pre-multiplied total. `_acquisition_tag` shows "Paid: X GP" / "Found" chips on every item **except** in the Starting Equipment entry (that cost is already reflected in Starting Gold, not tracked per item) — the check is `entry is starting_equipment_entry` (passed as a plain parameter down from `Character`), never a label string match.

## Layering rule — don't reintroduce circular imports

`Model/` (the `Character` model, including `Inventory`) must **never** import from `Builds/` or `CharacterContent/` at runtime (`TYPE_CHECKING`-only imports for annotations are fine) — `CharacterContent` imports `Character` (as `Character`) back for every `Feature.apply()` signature, so a runtime import the other way is a real circular import. If a new field feels like it belongs on `Character`, check whether it can instead be threaded as a plain parameter through `write_character_sheet()`/`_write_items()` the same way `equipment_entries` and `starting_equipment_entry` are — that's almost always the right answer for anything display-only. Verify any new cross-module import with `python -c "import <module>"` as a fresh standalone entry point, not just `python -m py_compile` (which never executes module code, so it can't catch circular imports at all).

## Running

```bash
python RunCharacterCreator.py                          # all builds
python -c "
import Core.Definitions as Definitions
from Builds.Characters.Y2024_Artificer_Cartographer_ObmarStalskagg import Y2024ArtificerCartographerObmarStalskaggCharacterBuilder
from Presentation.CharacterSheetWriters import HtmlCharacterSheetWriter
HtmlCharacterSheetWriter().write_character_sheet(Y2024ArtificerCartographerObmarStalskaggCharacterBuilder().build(), skill_config=Definitions.SkillConfig.DEFAULT)
"
```
