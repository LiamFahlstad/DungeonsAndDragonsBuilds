---
name: usage-tags
description: The rubric and tooling for usage_tags ("heal", "buff", "control", "damage", "utility", "summon"), the role chips on D&D feature and spell cards - where they are stored (Feature __init__ kwargs; spells_<source>_extended.json, never the source spell JSON), how to decide them, and a script that validates them and shows how similar features were tagged. Use whenever adding, auditing, fixing or reviewing usage_tags, writing a new Feature or spell that should carry them, or when someone asks why a card shows (or lacks) a Damage/Heal/Buff/Control/Utility/Summon chip.
---

# usage_tags

The same six tags (`"heal"`, `"buff"`, `"control"`, `"damage"`, `"utility"`, `"summon"`) render as the same chip on feature cards and on spell cards, so a player reads them the same way on both. This skill is the one place their rules live. Features and spells each have their own section, because the two sets of rules differ in a few deliberate ways (listed at the end).

## Where tags live

- **Features:** the `usage_tags=[...]` keyword of the feature's `__init__` call (`super().__init__(...)` or `Feature.__init__(self, ...)`). Leave it out when nothing applies.
- **Spells:** `CharacterContent/Spells/spells_<source>_extended.json`, keyed by spell name (`{"Fireball": {"usage_tags": ["damage"], "target": "area"}}`). `SpellFactory` merges each extended record **over** its source record, so a `usage_tags` key written into `spells_<source>.json` itself is overridden and never renders. Tag the extended file of the source that wins for that spell. Sources win in the order dnd2024, then aidedd, then dnd5e; `tag_report.py spells` names the right file.

## Tools (run them; don't guess)

```bash
python .claude/skills/usage-tags/tag_report.py check              # validate every tag; run before you report
python .claude/skills/usage-tags/tag_report.py file <path.py>...   # each feature in a file with its tags, untagged ones as "-"
python .claude/skills/usage-tags/tag_report.py with buff control   # everything tagged with all of these
python .claude/skills/usage-tags/tag_report.py spells --untagged   # spells that render without chips, and where to tag them
```

**Consistency is the hard part.** Across 1200+ tagged items, the main failure has been the same mechanic tagged differently in different batches. Before settling a borderline call, run `with` on your candidate tags and compare against two or three existing items that do the same thing. If precedent and rubric disagree, follow the rubric and mention the precedent in your report.

## Shared principles

- Tag what the item's **own text does**, never its flavor, school, class or subclass theme.
- **Combine freely.** Most attacks or saves with a rider need two tags.
- Leave it untagged when nothing applies. For a Feature, omit the kwarg rather than passing `[]`.
- **Be consistent within your batch.** Two items that do the same thing get the same tags. If a mechanic reminds you of a pattern elsewhere that you can't check, say so in your report rather than guessing.
- Gut check: would a player learn something from this chip? A tag on a near-universal trait (e.g. every species' Darkvision) kills the signal.

## Features

Tag a feature with zero or more of `"heal"`, `"buff"`, `"control"`, `"damage"`, `"utility"`, `"summon"` based on what its own effect *does*, not on flavor text. Pass a list; omit the kwarg entirely (or leave it `None`) rather than passing an empty list when nothing applies. Read `get_description()` fully — a feature is often more than one thing at once.

- `"damage"`: the feature's own use deals damage (a number of dice, a flat amount, or "damage equal to X") to one or more targets. Passive damage riders count too (e.g. "your Extra Attack deals an extra 1d6 Fire damage") — the trigger doesn't need its own action_type for the usage tag to apply.
- `"heal"`: the feature restores hit points, grants temporary hit points, or removes a harmful condition/restores a dying creature (e.g. Lay on Hands, Preserve Life, a feature that stabilizes a creature).
- `"buff"`: the feature grants a beneficial, non-damage, non-healing effect to a willing target — advantage on a roll, a bonus to AC/a save/an attack, resistance/immunity to damage or a condition, extra speed, temporary hit points *given alongside* another benefit that isn't itself the headline (if HP-only, prefer `"heal"`), an aura that helps allies, etc. Self-buffs count (e.g. Rage, Bladesong). **This applies whether the benefit is always-on or activated** — an always-on "you have Resistance to Poison damage" or "your AC increases by 1" is still `"buff"`; it doesn't need to be triggered by an action to count.
- `"control"`: the feature imposes a condition, restricts movement/actions, or otherwise constrains what a target (usually a hostile one) can do — frightened, restrained, stunned, prone, forced movement/teleportation of an enemy, disadvantage imposed on an enemy, a save-or-suffer effect that isn't damage.
- `"utility"`: the feature grants a stated non-combat functional capability that isn't itself a combat AC/save/attack/HP/condition effect — a movement mode (a climbing, swimming, or flying speed), the ability to breathe or move across a hazardous medium, a ritual-casting grant, an at-will or limited-use spell-like ability whose own effect is informational/exploratory (detect traps or magic, decipher languages, communicate telepathically), or an explicitly-stated craft/utility action (identify an item, pick a lock without tools, purify food and water). The bar is the same as the other tags: the feature's own text must state the concrete capability, not just imply it from flavor.
- `"summon"`: the feature's own use calls into being a creature, object, or construct that then acts under the user's control, or binds/calls a creature into temporary service — e.g. a Wild Shape-style companion summon, a class feature that lets you cast a Summon-X or Find Familiar-style spell as its own effect, animating an object or corpse. Combine with other tags freely (a summon feature whose own text also states a direct effect, like the summoned creature dealing stated damage or granting a stated buff, gets `"summon"` plus that other tag). A feature that only grants a spell/spell slot elsewhere (the spell being what actually summons) is not itself `"summon"` — reserve this for a feature whose own text performs the summoning, not one that merely unlocks a spell that does.
- Combine freely: an attack that deals damage and frightens the target is `["damage", "control"]`; a heal that also grants temporary AC is `["heal", "buff"]`.
- Do NOT tag any of the six: features with genuinely no stated effect — a skill or tool proficiency, an ability score increase by itself, a language, a resource pool by itself with no listed effect (e.g. "you gain 2 Sorcery Points" with no attached benefit text), features that only grant a spell/spell slot (the spell carries its own role, not this granting feature). The line: does the feature's own text state a concrete benefit or capability (AC/save/attack/resistance/immunity/speed/HP, a condition granted/removed, a creature/object summoned, or a stated non-combat capability)? If yes, tag it — even if it's passive and always-on. If it's just a number/proficiency with no stated effect, don't.
- Do NOT tag `"utility"` (or `"buff"`) for a granted sense by itself (Darkvision, Blindsight, Tremorsense, Truesight) — these are near-universal and tagging them adds noise rather than signal, the same reasoning that excludes them from `"buff"`. Exception: if the same feature's text also states a genuine additional benefit alongside the sense (a resistance, an attack bonus, or a distinct utility capability), tag for that other benefit, not for the sense itself.
- Do NOT stretch: "you can move through allies' spaces" is not `"buff"` or `"utility"` just because it's convenient — it has to be a stated, concrete effect (a bonus, advantage, HP, a condition granted/removed, or a named capability like a movement mode or detection ability), not incidental narrative flavor.
- This tag is about the feature's own mechanical output, same standard as `action_type`/`range` — don't guess from the class or subclass theme (e.g. a "Death" domain feature isn't automatically `"damage"` unless its own text deals damage).

## Spells

Same standard as the Feature version of this tag: read the spell's `description` fully and tag what its own text *does*, not what its flavor implies. Combine freely — most attack/save spells with a secondary rider need two tags.

- `"damage"`: the spell deals damage (an attack roll or a saving throw) to one or more targets, on any tier of its scaling. The vast majority of Evocation spells and many Necromancy/Conjuration spells qualify. Example: *Fireball*, *Scorching Ray*, *Guiding Bolt*.
- `"heal"`: the spell restores hit points, grants temporary hit points, removes a harmful condition, or stabilizes/revives a creature. Example: *Cure Wounds*, *Mass Healing Word*, *Revivify*.
- `"buff"`: the spell grants a beneficial, non-damage, non-healing effect to a willing target — advantage on a roll, a bonus to AC/a save/an attack, resistance/immunity, extra speed, an extra action (Haste-style), invisibility, or an aura that helps allies. Applies whether it's the caster buffing themself or another creature. Example: *Bless*, *Haste*, *Shield*, *Aid* (also `"heal"` — it both raises max HP and heals a matching amount).
- `"control"`: the spell imposes a condition or restricts what a target (usually hostile) can do — frightened, restrained, paralyzed, stunned, prone, charmed-as-hostile-effect, banished, polymorphed-as-a-debuff, forced movement/teleportation of an unwilling creature, or battlefield control that hinders enemies (difficult terrain, a wall that blocks them, magical darkness over them). Example: *Hold Person*, *Web*, *Wall of Force*, *Banishment*.
- `"utility"`: the spell's own text provides a non-combat functional capability that isn't itself a damage/heal/buff/control effect — divination/information (detecting, identifying, locating, scrying, understanding languages), communication (*Message*, *Sending*), exploration/movement (passing through obstacles, breathing or moving across a hazardous medium, teleportation used for travel rather than to control an enemy), object/environment manipulation (creating light, food, or objects; altering terrain; crafting), or other out-of-combat problem-solving. Example: *Detect Magic*, *Identify*, *Comprehend Languages*, *Light*, *Knock*, *Water Breathing*. Covers most of what would otherwise go untagged — apply it whenever the spell's own text states a concrete non-combat function, even a minor one.
- `"summon"`: the spell calls into being a creature, object, or construct that then acts under the caster's control — it doesn't matter whether the spell's own text also states an additional effect (a direct damage/utility grant, etc.); the act of summoning itself always earns this tag. Example: *Summon Beast*, *Animate Dead*, *Animate Objects*, *Conjure Animals*, *Find Familiar*, *Planar Ally*, *Planar Binding* (binds/calls a creature into service). Combine with other tags freely: a summon spell that also states a direct effect (e.g. it deals damage on arrival, or the summoned creature grants the caster a specific stated benefit) gets `"summon"` plus whatever else its own text states. A spell that merely *targets* an existing creature (charm, polymorph, banish) is not a summon — reserve this tag for spells that bring a new creature/object into being or bind one into temporary service.
- Do NOT tag `"utility"` (or anything else) for a spell whose own text states no function worth flagging at all — this is rare (nearly every spell does *something*), but a spell that's pure reskinned flavor with no independent mechanical text of its own would qualify. If in doubt, ask: does this spell's own text change a creature's HP, impose/remove a condition, grant/deny a mechanical bonus, summon/animate/bind a creature or object, or state a concrete non-combat capability? If none of those, leave it untagged.
- If a spell has both a stated combat effect and a stated non-combat capability (e.g. it deals damage *and* also, as written, lets you see through walls afterward), combine tags — `"damage"` doesn't preclude also carrying `"utility"`. This is uncommon; most spells are cleanly one or the other.
- Multi-option spells (many spells offer several distinct effects, e.g. different damage types or a save-or-suffer menu): tag the union of every category the spell's own text can produce, same as a multi-tier Feature.
- Cantrip-upgrade and higher-level-slot scaling text almost never introduces a new category — it just intensifies an existing tag (more damage dice, more targets). Don't add a tag based on scaling text alone unless the scaled version genuinely adds a new kind of effect the base spell doesn't have.

## Deliberate differences between the two sections

- **`"utility"`**: broad for spells ("covers most of what would otherwise go untagged"), strict for features (the feature's own text must state the concrete capability). Many features are passive bookkeeping, which the strict bar keeps untagged.
- **Senses** (Darkvision, Blindsight, ...): a feature that only grants a sense is never tagged, because nearly every character has one. The carve-out is features-only. A spell such as *Darkvision* is a deliberate choice to cast, so it is tagged under the spell rules.
- **Grants**: a feature that only grants a spell or spell slot is untagged (the spell carries its own tags).

If you think one of these differences is wrong, raise it in your report instead of changing the rule mid-batch.
