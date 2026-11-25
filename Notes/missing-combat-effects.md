# Missing combat effects

What the combat effects (`combat_effects()` on spells and features,
`Model/Content/CombatEffect.py`) don't cover yet. It lists spells, features,
monster abilities and items with no effects at all, and described ones whose
rules are only partly applied by the simulator, with the rest left to the GM in
a note. Companion to [combat-effects-plan.md](combat-effects-plan.md).

Audited 2026-11-24 with `.claude/skills/combat-effects/combat_effects.py`
(`coverage`, `check`, `compare`, `notes`, `stats`, `triggers --all`), a dump
of every described row's notes and badge modifiers, a walk of every
`Builds/Examples` build's features, and counts over `Combat/Monsters` and
`CharacterContent/Items`. `check` passes; nothing here is a rubric violation.

## How to read it

**Rank (1-10): how much it matters at the table.**

| Rank | Meaning |
|---|---|
| 9-10 | Comes up in most fights and the simulator's result is silently wrong |
| 7-8 | Common (a staple spell, class feature or monster trait), and wrong or left to memory with a real swing |
| 5-6 | Comes up regularly; a note reminds the GM, or the swing is moderate |
| 3-4 | Occasional, or a small effect |
| 1-2 | Rare, cosmetic, or not about combat |

Gaps in §4-§11 are ranked by hand. The long lists (571 spells, 586 features,
102 monster abilities) are ranked by a heuristic: the item's `usage_tags`
(damage/control > heal/buff/summon > utility), its level (cantrips and levels
1-3 are used most), and hand-set ranks for the staples. A spell with no
effects still gets a row read from its text, so those lists stop at 8.

**Kind: what fixing it takes.**

- **Now**: the fields that exist already could express it; only the content
  needs writing.
- **Field**: needs a new field or modifier on the model.
- **Engine**: needs the simulator (or battle map) to see something it doesn't.
- **Table**: decided at the table by design (principle 6); listed only so it's
  known.

## 1. Coverage at a glance

| What | Described | Nothing to apply (`[]`) | Not described | Notes |
|---|---|---|---|---|
| Spells (all 662 classes) | 75 | 16 | **571** | Only the two parties' spells are done |
| Curse of the Lich party | spells 44/44; features 26 | 34 | 0 | 50 passive (no row); 3 Trigger facts left to the GM. 4 of the `[]` ones do something in a fight (§5) |
| Time Loop PR party | spells 33/33; features 7 | 19 | 0 | 41 passive; 4 Trigger facts left to the GM. Alert is `[]` (§5) |
| Grim's Castle party | none | none | none | No party members yet |
| Features of all 115 example builds (714 classes, each once) | 41 | 28 | **424 read from text, 161 extensions with no row** | 60 passive; 181 Trigger facts with no trigger and no reason (§6) |
| Feature classes in `CharacterContent/Features` (about 1,171) | about 92 define `combat_effects` | | about 1,000 | Rough count: classes whose own body defines the method |
| Monster abilities, official `monsters.py` (2,194) | 291 structured + 775 with effects | | 1,128 freeform | Read from text at runtime (§8) |
| Monster abilities, homebrew (204) | 65 structured + 37 with effects | | 102 freeform | §8 |
| Items: potions, scrolls, poisons, wondrous items (39 classes) | 0 | | **all** | No item reaches the combat picker (§9) |
| Magic weapons and armor (38 classes) | fixed extra damage only | | 21 with text-only riders | §9 |
| Summon spells (`SPELL_SUMMONS`) | 0 | | **all** | The table is empty (§10) |

**Tooling gap (rank 5):** `features`, `triggers`, `coverage` and `notes` only
look at party members. Nothing lists the features no party has, so there is
no `todo` for features class by class (plan 4.3). §6 was made by walking every
`Builds/Examples` build through the same `walk_features` / `feature_state` /
`trigger_state` the tool uses. Suggestion: a `features --examples` mode.

## 2. The worst gaps (rank 7+)

| Rank | Gap | Section | Kind |
|---|---|---|---|
| 9 | Monsters' Magic Resistance (about 74 monsters) isn't counted in saves against spells | §7 | Field |
| 9 | Extra Attack (6 classes) has no row; the GM sets Times by hand | §6 | Engine (action economy) |
| 8 | Pack Tactics (22 monsters): Advantage with an ally within 5 feet isn't counted, though the map knows | §7 | Field/Engine |
| 8 | Aura of Protection: + Charisma modifier to allies' saves within 10 feet isn't counted | §7 | Field/Engine |
| 8 | Sneak Attack has no hit trigger: picked by hand, crit doubling by hand | §4.1 | Now (+ a Finesse gate) |
| 8 | Action Surge, Stunning Strike, Two Extra Attacks: read from text | §6 | Now / Engine |
| 8 | Staple damage cantrips and spells undescribed: Fire Bolt, Ray of Frost, Sorcerous Burst, Hex, Bane, Counterspell, the smites, Spirit Shroud, Hypnotic Pattern, ... (45 at 8) | §3 | Now |
| 7 | War Caster's Advantage on Concentration saves isn't counted, though the simulator rolls them (Clover) | §5, §7 | Field |
| 7 | Regeneration (11 monsters) isn't applied at turn start | §7 | Field |
| 7 | Evasion, Uncanny Dodge: not counted | §7 | Field |
| 7 | Invisibility doesn't end when the bearer attacks or casts, so attackers keep the advantage | §4.2 | Field |
| 7 | Divine Smite / Paladin's Smite have no hit trigger | §4.1 | Now |
| 7 | Spiritual Weapon's repeat attack on later turns | §4.5 | Field |
| 7 | Potions of Healing aren't in the picker | §9 | Field (rows for items) |
| 7 | Breath Weapon, Reckless Attack, Great Weapon Master, Sharpshooter, Superiority Dice: read from text | §6 | Now / Field |

## 3. Spells with no combat effects (571)

The picker reads these from their rules text with regexes, so the GM has to
check every row. `combat_effects.py todo --level N` lists them with where each
one's effects go. Rank counts: 8: 45, 7: 24, 6: 131, 5: 172, 4: 96, 3: 27,
2: 48, 1: 28.

**Rank 7-8 (69), the ones to describe first:** Acid Splash (8), Fire Bolt (8), Frostbite (8), Mind Sliver (8), Poison Spray (8), Primal Savagery (8), Ray of Frost (8), Shocking Grasp (8), Sorcerous Burst (8), Thorn Whip (8), Word of Radiance (8), Bane (8), Cause Fear (8), Chaos Bolt (8), Color Spray (8), Hail of Thorns (8), Hex (8), Inflict Wounds (8), Sanctuary (8), Searing Smite (8), Silvery Barbs (8), Thunderous Smite (8), Wrathful Smite (8), Blindness/Deafness (8), Blur (8), Branding Smite (8), Cloud of Daggers (8), Darkness (8), Flaming Sphere (8), Mind Spike (8), Mirror Image (8), Shining Smite (8), Web (8), Bestow Curse (8), Blinding Smite (8), Call Lightning (8), Conjure Animals (8), Counterspell (8), Elemental Weapon (8), Fear (8), Hypnotic Pattern (8), Slow (8), Spirit Shroud (8), Thunder Step (8), Vampiric Touch (8), Shillelagh (7), Expeditious Retreat (7), Find Familiar (7), Goodberry (7), Magic Weapon (7), Prayer of Healing (7), Ray of Enfeeblement (7), Mass Healing Word (7), Revivify (7), Banishment (7), Evard's Black Tentacles (7), Wall of Fire (7), Cone of Cold (7), Flame Strike (7), Greater Restoration (7), Hold Monster (7), Steel Wind Strike (7), Synaptic Static (7), Wall of Force (7), Chain Lightning (7), Circle of Death (7), Disintegrate (7), Harm (7), Sunbeam (7).

<details><summary>Every spell without effects, by level, highest rank first</summary>

- **Cantrips (31):** Acid Splash (8), Fire Bolt (8), Frostbite (8), Mind Sliver (8), Poison Spray (8), Primal Savagery (8), Ray of Frost (8), Shocking Grasp (8), Sorcerous Burst (8), Thorn Whip (8), Word of Radiance (8), Shillelagh (7), Arcane Pulse (6), Blade Ward (6), Create Bonfire (6), Infestation (6), Lightning Lure (6), Magic Stone (6), Mold Earth (6), Sapping Sting (6), Sword Burst (6), Thunderclap (6), Wrath (6), Control Flames (2), Dancing Lights (2), Druidcraft (2), Encode Thoughts (2), Gust (2), Light (2), Mending (2), Shape Water (2)
- **Level 1 (61):** Bane (8), Cause Fear (8), Chaos Bolt (8), Color Spray (8), Hail of Thorns (8), Hex (8), Inflict Wounds (8), Sanctuary (8), Searing Smite (8), Silvery Barbs (8), Thunderous Smite (8), Wrathful Smite (8), Expeditious Retreat (7), Find Familiar (7), Goodberry (7), Animal Friendship (6), Arms of Hadar (6), Azure Strike (6), Beast Bond (6), Catapult (6), Chains of Ice (6), Compelled Duel (6), Consume Soul (6), Death Grip (6), Earth Tremor (6), Ebon Might (6), Entropic Embrace (6), Fel Rush (6), Freezing Trap (6), Frost Fingers (6), Frost Nova (6), Infernal Strike (6), Insidious Rhythm (6), Jim's Magic Missile (6), Living Flame (6), Magnify Gravity (6), Moonfire (6), Rune Strike (6), Scourge Strike (6), Shadow Word: Pain (6), Snare (6), Spellfire Flare (6), Tasha's Caustic Brew (6), Throw Glaive (6), Wardaway (6), Zephyr Strike (6), Buzzing Bee (5), Gift of Alacrity (5), Illusory Script (5), Jump (5), Purify Food and Drink (5), Vampiric Blood (5), Create or Destroy Water (2), Detect Evil and Good (2), Detect Poison and Disease (2), Distort Value (2), Feign Interest (2), Identify (2), Quick Clothier (2), Tenser's Floating Disk (2), Unseen Servant (2)
- **Level 2 (95):** Blindness/Deafness (8), Blur (8), Branding Smite (8), Cloud of Daggers (8), Darkness (8), Flaming Sphere (8), Mind Spike (8), Mirror Image (8), Shining Smite (8), Web (8), Magic Weapon (7), Prayer of Healing (7), Ray of Enfeeblement (7), Aganazzar's Scorcher (6), Alter Self (6), Consecration (6), Cordon of Arrows (6), Crown of Madness (6), Curse of Agony (6), Death Armor (6), Death and Decay (6), Disruptive Tune (6), Dragon's Breath (6), Dust Devil (6), Enthrall (6), Eruption (6), Eye Beam (6), Fiery Brand (6), Find Steed (6), Flame Blade (6), Frostscythe (6), Gust of Wind (6), Heat Metal (6), Kinetic Jaunt (6), Maximillian's Earthen Grasp (6), Melf's Acid Arrow (6), Phantasmal Force (6), Rime's Binding Ice (6), Roar of Ursoc (6), Searing Orb (6), Shadow Blade (6), Sigil of Flame (6), Snilloc's Snowball Swarm (6), Spray of Cards (6), Tasha's Mind Whip (6), Uncertain Footing (6), Warding Wind (6), Wither and Bloom (6), Arcane Vigor (5), Battle Familiar (5), Borrowed Knowledge (5), Calm Emotions (5), Detect Thoughts (5), Dream Breath (5), Dueling Ground (5), Elminster's Elusion (5), Enhance Ability (5), Feral Prowl (5), Find Traps (5), Flock of Familiars (5), Fortune's Favor (5), Healing Spirit (5), Homunculus Servant (5), Jim's Glowing Coin (5), Levitate (5), Nystul's Magic Aura (5), Pass without Trace (5), Protection from Poison (5), Summon Beast (5), Tortoise Shell (5), Warding Bond (5), Air Bubble (2), Animal Messenger (2), Arcane Lock (2), Augury (2), Beast Sense (2), Conjure Tools (2), Continual Flame (2), Deryan's Helpful Homunculi (2), Earthbind (2), Gentle Repose (2), Gift of Gab (2), Immovable Object (2), Knock (2), Locate Animals or Plants (2), Locate Object (2), Magic Mouth (2), Nathair's Mischief (2), Pinky Swear (2), Pyrotechnics (2), Rope Trick (2), Skywrite (2), Vortex Warp (2), Warp Sense (2), Wristpocket (2)
- **Level 3 (88):** Bestow Curse (8), Blinding Smite (8), Call Lightning (8), Conjure Animals (8), Counterspell (8), Elemental Weapon (8), Fear (8), Hypnotic Pattern (8), Slow (8), Spirit Shroud (8), Thunder Step (8), Vampiric Touch (8), Mass Healing Word (7), Revivify (7), Antagonize (6), Ashardalon's Stride (6), Astral Flood (6), Blistering Scales (6), Cacophonic Shield (6), Conjure Barrage (6), Crusader's Mantle (6), Demon Spikes (6), Enemies Abound (6), Erupting Earth (6), Fast Friends (6), Flame Arrows (6), Flurry (6), Glyph of Warding (6), Hand of Gul'dan (6), Hunger of Hadar (6), Incite Greed (6), Inflict Doubt (6), Laeral's Silver Lance (6), Leeching Strike (6), Life Transference (6), Lightning Arrow (6), Magic Circle (6), Meld into Stone (6), Melf's Minute Meteors (6), Metamorphosis (6), Motivational Speech (6), Plant Growth (6), Pulse Wave (6), Rain of Fire (6), Remorseless Winter (6), Serpent Sting (6), Sleet Storm (6), Soul Reap (6), Speak with Plants (6), Stinking Cloud (6), Sylune's Viper (6), Tidal Wave (6), Wall of Sand (6), Wall of Water (6), Wind Wall (6), Animate Dead (5), Aura of Vitality (5), Beacon of Hope (5), Blink (5), Catnap (5), Clairvoyance (5), Conjure Constructs (5), Emerald Blossom (5), Feign Death (5), Galder's Tower (5), Gaseous Form (5), Guided Prayer (5), Intellect Fortress (5), Leomund's Tiny Hut (5), Phantom Steed (5), Prayer of Mending (5), Regrowth (5), Remove Curse (5), Summon Fey (5), Summon Lesser Demons (5), Summon Shadowspawn (5), Summon Undead (5), Tiny Servant (5), Water Breathing (5), Water Walk (5), Dispel Magic (4), Create Food and Water (2), Daylight (2), Major Image (2), Nondetection (2), Sending (2), Speak with Dead (2), Tongues (2)
- **Level 4 (67):** Banishment (7), Evard's Black Tentacles (7), Wall of Fire (7), Death Ward (6), Dimension Door (6), Greater Invisibility (6), Polymorph (6), Backlash (5), Blight (5), Breath of Eons (5), Chaos Nova (5), Charm Monster (5), Collapsing Star (5), Compulsion (5), Confusion (5), Conjure Minor Elementals (5), Conjure Woodland Beings (5), Control Water (5), Distorted Distance (5), Dominate Beast (5), Doomtide (5), Elemental Bane (5), Emberstorm (5), Festering Blast (5), Find Greater Steed (5), Fount of Moonlight (5), Galder's Speedy Courier (5), Gate Seal (5), Grasping Vine (5), Gravity Sinkhole (5), Guardian of Faith (5), Guardian of Nature (5), Holy Nova (5), Mordenkainen's Faithful Hound (5), Mordenkainen's Private Sanctum (5), Otiluke's Resilient Sphere (5), Phantasmal Killer (5), Psychic Horror (5), Raulothim's Psychic Lance (5), Shadow of Moil (5), Sickening Radiance (5), Spellfire Storm (5), Staggering Smite (5), Starfall (5), Storm Sphere (5), Summon Greater Demon (5), Upheaval (5), Vitriolic Sphere (5), Watery Sphere (5), Arcane Eye (4), Aura of Life (4), Aura of Purity (4), Divine Shield (4), Giant Insect (4), Spirit of Death (4), Sticks to Snakes (4), Summon Aberration (4), Summon Construct (4), Summon Elemental (4), Time Dilation (4), Zone of Amicability (4), Divination (1), Fabricate (1), Hallucinatory Terrain (1), Leomund's Secret Chest (1), Locate Creature (1), Stone Shape (1)
- **Level 5 (80):** Cone of Cold (7), Flame Strike (7), Greater Restoration (7), Hold Monster (7), Steel Wind Strike (7), Synaptic Static (7), Wall of Force (7), Animate Objects (6), Mass Cure Wounds (6), Awaken (5), Banishing Smite (5), Bigby's Hand (5), Bonestorm (5), Cloudkill (5), Conjure Elemental (5), Conjure Volley (5), Contact Other Plane (5), Contagion (5), Control Winds (5), Danse Macabre (5), Dawn (5), Destructive Wave (5), Dispel Evil and Good (5), Dominate Person (5), Dream (5), Enervation (5), Explosive Trap (5), Geas (5), Grave Ground (5), Hallow (5), Holy Weapon (5), Immolation (5), Infernal Calling (5), Insect Plague (5), Jallarzi's Storm of Radiance (5), Maelstrom (5), Modify Memory (5), Negative Energy Flood (5), Planar Binding (5), Shattering Star (5), Sigil of Chains (5), Songal's Elemental Suffusion (5), Spirit Lantern (5), Telekinesis (5), Temporal Shunt (5), Transmute Rock (5), Void Eruption (5), Wall of Light (5), Wall of Stone (5), Waves of Exhaustion (5), Wrath of Nature (5), Yolande's Regal Presence (5), Alustriel's Mooncloak (4), Antilife Shell (4), Circle of Power (4), Dream Flight (4), Innervate (4), Mislead (4), Raise Dead (4), Rary's Telepathic Bond (4), Reincarnate (4), Rescue (4), Summon Celestial (4), Summon Draconic Spirit (4), Summon Dragon (4), Summon Plant (4), Swift Quiver (4), Teleportation Circle (4), Commune (1), Commune with Nature (1), Create Spelljamming Helm (1), Creation (1), Far Step (1), Legend Lore (1), Mordenkainen's Lucubration (1), Passwall (1), Scrying (1), Seeming (1), Skill Empowerment (1), Tree Stride (1)
- **Level 6 (55):** Chain Lightning (7), Circle of Death (7), Disintegrate (7), Harm (7), Sunbeam (7), Heal (6), Azure Sweep (5), Blade Barrier (5), Bones of the Earth (5), Combustion (5), Conjure Fey (5), Create Homunculus (5), Dirge (5), Druid Grove (5), Elminster's Effulgent Spheres (5), Eyebite (5), Fizban's Platinum Shield (5), Flesh to Stone (5), Forbiddance (5), Gravity Fissure (5), Guards and Wards (5), Investiture of Flame (5), Investiture of Ice (5), Investiture of Stone (5), Investiture of Wind (5), Leomund's Lamentable Belaborment (5), Mass Suggestion (5), Mental Prison (5), Move Earth (5), Otiluke's Freezing Sphere (5), Otto's Irresistible Dance (5), Programmed Illusion (5), Tasha's Otherworldly Guise (5), Tenser's Transformation (5), Wall of Ice (5), Wall of Thorns (5), Wind Walk (5), Arcane Gate (4), Contingency (4), Create Undead (4), Globe of Invulnerability (4), Magic Jar (4), Planar Ally (4), Primordial Ward (4), Soul Cage (4), Summon Dinosaur (4), Summon Fiend (4), Tranquility (4), True Seeing (4), Word of Recall (4), Drawmij's Instant Summons (1), Find the Path (1), Scatter (1), Tasha's Bubbling Cauldron (1), Transport via Plants (1)
- **Level 7 (36):** Finger of Death (6), Forcecage (6), Crown of Stars (4), Delayed Blast Fireball (4), Divine Word (4), Draconic Transformation (4), Dream of the Blue Veil (4), Fire Storm (4), Fractured Awareness (4), Lay Waste (4), Mirage Arcane (4), Mordenkainen's Sword (4), Plane Shift (4), Power Word Pain (4), Prismatic Spray (4), Project Image (4), Reverse Gravity (4), Symbol (4), Teleport (4), Temple of the Gods (4), Tether Essence (4), Transfix (4), Void Star (4), Whirlwind (4), Aura of Evasion (3), Conjure Celestial (3), Create Magen (3), Power Word Fortify (3), Regenerate (3), Resurrection (3), Reweave Fate (3), Simbul's Synostodweomer (3), Simulacrum (3), Etherealness (1), Mordenkainen's Magnificent Mansion (1), Sequester (1)
- **Level 8 (31):** Power Word Stun (6), Sunburst (6), Abi-Dalzim's Horrid Wilting (4), Antipathy/Sympathy (4), Befuddlement (4), Dark Star (4), Dominate Monster (4), Earthquake (4), Entrancing Mirrors (4), Feeblemind (4), Holy Aura (4), Holy Star of Mystra (4), Illusory Dragon (4), Incendiary Cloud (4), Lightning Ring (4), Maddening Darkness (4), Maze (4), Reality Break (4), Tsunami (4), Animal Shapes (3), Antimagic Field (3), Clone (3), Demiplane (3), Glibness (3), Iron Body (3), Mighty Fortress (3), Mind Blank (3), Moment of Prescience (3), Telepathy (3), Tree of Life (3), Control Weather (1)
- **Level 9 (27):** Meteor Swarm (6), Power Word Kill (6), Time Stop (5), Wish (5), Blade of Disaster (4), Detonate (4), Foresight (4), Gate (4), Imprisonment (4), Mass Polymorph (4), Power Word Heal (4), Prismatic Wall (4), Psychic Scream (4), Ravenous Void (4), Storm of Vengeance (4), Time Ravage (4), Vision of Elapsing Eons (4), Wail of the Banshee (4), Weird (4), Apotheosis (3), Astral Projection (3), Invulnerability (3), Mass Heal (3), Shapechange (3), True Polymorph (3), True Resurrection (3), Hindsight (1)

</details>

Several need §4's gaps first: the smites need §4.1's hit trigger, Hex needs
the same "move the mark" handling as Hunter's Mark (§4.9), and the summons
need §10.

## 4. Described effects that don't cover the whole rule

Grouped by the capability that's missing. Each row names what the simulator
doesn't do, which is now a note the GM acts on.

### 4.1 Uses "right after you hit" have no trigger

The plan lists Sneak Attack and Paladin's Smite as `HIT` triggers (Trigger
types table), but these rows are still picked by hand after a hit, so a
Critical Hit isn't doubled by itself either.

| Rank | Source | Left to the GM | Kind |
|---|---|---|---|
| 8 | Sneak Attack (Rogue) | Once per turn after a hit with a Finesse or Ranged weapon; needs Advantage or an ally within 5 feet; double dice on a crit | **Now** for `HIT`, `once_per_turn`, crit; **Field** for a Finesse/Ranged weapon gate; the Advantage/ally condition is a `when` |
| 7 | Divine Smite / Paladin's Smite | Cast after a hit with a Melee weapon or Unarmed Strike; double dice on a crit | **Now** (`HIT`, `attacks=MELEE`/`UNARMED`) |
| 4 | Ensnaring Strike | Cast after a weapon hit | **Now** (`HIT`, `attacks=WEAPON`) |
| 4 | Sentinel: Halt | After you hit with an Opportunity Attack | **Engine**: no "was an Opportunity Attack" gate, though `Combat/Arena/arena.py` knows who can make one |
| 4 | Combat Inspiration (Valor Bard) | The bearer spends the die as it hits or is hit | **Field**: a trigger on the bearer's badge (its `untriggered` says so) |

### 4.2 "Ends early when ..." is a note everywhere

This is the most common gap. The `notes` tool misses it because the wording
differs every time. It looks like a missing field, something like
`CombatCondition.ends_on` with events the simulator already sees (takes
damage, makes an attack roll, deals damage, casts a spell, is Incapacitated,
Speed 0, no Temporary Hit Points left).

| Rank | Source | Ends when | Kind |
|---|---|---|---|
| 7 | Invisibility | it attacks, deals damage or casts a spell | **Field** |
| 6 | Sleep | the target wakes when it takes damage (or is shaken: **Table**); forgetting it leaves an Unconscious target taking auto-crits | **Field** |
| 5 | Turn Undead | the creature takes any damage; you're Incapacitated or die | **Field** |
| 5 | Cunning Action: Hide | it attacks or casts a Verbal spell (sound and being found: **Table**) | **Field** |
| 4 | Armor of Agathys | no Temporary Hit Points left | **Field** |
| 4 | Booming Blade | the target willingly moves 5 feet | **Engine**: no "moves" event, though the battle map sees moves |
| 3 | Charm Person, Suggestion | you or your allies damage the target | **Field** (the "allies" part needs the side) |
| 3 | Elemental Attunement, Patient Defense (Dodge) | Incapacitated; Speed 0 | **Field** |
| 2 | Friends | the target takes damage, or you attack, deal damage or force a save | **Field** |
| 1 | Mage Armor | the target dons armor | **Table** |
| 1 | Sacred Weapon | you stop carrying the weapon | **Table** |

### 4.3 Save gates: creature type, size, Advantage on the save

There's no field for "this creature type only", "Advantage/Disadvantage on
this save if ..." or "succeeds automatically if ...". A **Field** each, e.g.
`creature_types` on the effect and a `D20Mode` with a `when` on the save.

| Rank | Source | Left to the GM |
|---|---|---|
| 5 | Hold Person, Charm Person | Humanoids only |
| 5 | Turn Undead | Undead only |
| 4 | Protection from Evil and Good | its condition immunity and the save Advantage apply only against six creature types (`ConditionImmunity` has no gate) |
| 3 | Charm Person | Advantage on the save if you or your allies are fighting it |
| 3 | Shatter | a Construct has Disadvantage |
| 3 | Ensnaring Strike | a Large or larger creature has Advantage (size is known: `largest_target` exists for triggers, not saves) |
| 3 | Sleep | creatures that don't sleep, or are immune to Exhaustion, succeed |
| 2 | Friends | succeeds automatically if not a Humanoid, if you're fighting it, or if cast on it in the last 24 hours |

### 4.4 Later saves and escapes other than "repeat at the end of each turn"

`repeat_save` only covers the end-of-turn repeat. **Field** for each pattern:

| Rank | Source | Left to the GM |
|---|---|---|
| 6 | Grease, Moonbeam | the save again on entering, or ending a turn in, the area (`AtTurnEnd` with a `when` could take the end-of-turn half **now**) |
| 5 | Sleep | a second save at the end of its next turn that turns Incapacitated into Unconscious (an escalation) |
| 5 | Tasha's Hideous Laughter | repeats the save, with Advantage, each time it takes damage; can't end Prone on itself |
| 5 | Entangle, Ensnaring Strike | an action to make a Strength (Athletics) check against your DC to end it |

### 4.5 Damage and effects on later turns

| Rank | Source | Left to the GM | Kind |
|---|---|---|---|
| 7 | Spiritual Weapon | a Bonus Action each later turn moves it 20 feet and attacks again | **Field**: a "use again on a later turn" row (a second row with `spends_use=False` would do the attack **now**) |
| 5 | Ensnaring Strike | 1d6 Piercing (upcast 1d6) at the start of each of the Restrained target's turns | **Now**: an `AtTurnStart` on an "Ensnaring Strike" badge beside Restrained |
| 5 | Moonbeam | a Magic action moves the Cylinder 60 feet; the saves as it moves onto a creature | `CombatArea.move_ft` exists; the move-onto save is **Engine** |
| 5 | Spike Growth | 2d4 Piercing per 5 feet moved in the area | **Engine** (map movement) |
| 4 | Witch Bolt | a Bonus Action each later turn: 1d12 Lightning, no roll; ends out of range or behind Total Cover | as Spiritual Weapon; the range end is **Engine** |
| 4 | Spirit Guardians | its turn-end damage row can't upcast without spending a slot ("type it in") | DI-078 |
| 3 | Produce Flame | casting (Bonus Action) and hurling (Magic action, later) are one row | **Now**: two rows, the hurl `spends_use=False` |

### 4.6 Areas that change the ground or the light

The battle map has painted Difficult Terrain, Darkness and Dim Light, but a
spell's area doesn't add them.

| Rank | Source | Left to the GM | Kind |
|---|---|---|---|
| 5 | Entangle, Grease, Spike Growth, Ice Storm | the area is Difficult Terrain (Ice Storm only to the end of your next turn) | **Field**: `CombatArea.difficult` exists for Walls only |
| 4 | Spirit Guardians | other creatures' Speed is halved in the Emanation | **Engine** |
| 3 | Silence | take Deafened and the badge off as a creature leaves; no Verbal spells inside | **Engine** |
| 3 | Faerie Fire, Starry Wisp, Fire Shield, Sacred Weapon | the target sheds Dim or Bright Light | **Field**/DI-099 |
| 2 | Radiance of the Dawn | dispels magical Darkness in the Emanation | DI-099 |

### 4.7 Movement the target is made to take, and lost turns

| Rank | Source | Left to the GM | Kind |
|---|---|---|---|
| 5 | Command: Halt, Drop, Grovel | takes no action, drops what it holds, ends its turn | **Field**: a "loses its turn / actions" modifier |
| 5 | Haste | one extra limited action per turn | **Field**: the action economy isn't modeled (see Extra Attack, §6) |
| 4 | Dissonant Whispers | uses its Reaction to move as far away as it can | **Engine** |
| 4 | Command: Approach, Flee; Turn Undead | moves toward / away on its next turn | **Engine** (or **Table**) |
| 3 | Elemental Strikes: move | up to 10 feet toward or away on a failed save | **Now**: two rows, `CombatPush(10, up_to=True)` and the same with `toward=True` |

### 4.8 One casting, several targets or a chain

| Rank | Source | Left to the GM |
|---|---|---|
| 6 | Green-Flame Blade, Booming Blade, True Strike | the weapon attack's own bonus and damage are typed in, and the extra cantrip damage (1d8/1d6 at level 5, 11, 17) is a note, not `cantrip` dice (**Field**: "an attack with the weapon used in the casting", taking the wielder's weapon row) |
| 4 | Eldritch Blast, Scorching Ray, Magic Missile | splitting beams, rays or darts: lower Times and apply again (**Field**: per-instance targets) |
| 3 | Chromatic Orb | leaps to another target when two d8s match, up to the slot level (**Engine**: the dice are rolled, the match isn't read) |

### 4.9 Riders on hits and incoming damage

| Rank | Source | Left to the GM | Kind |
|---|---|---|---|
| 5 | Absorb Elements | no trigger: it's a Reaction to taking Acid/Cold/Fire/Lightning/Thunder damage, and its Resistance should count against that damage (now "give back what it would have halved") | **Engine**: a before-damage `TAKES_DAMAGE` with a damage-type gate (`HIT_BY` only covers attack rolls) |
| 5 | Hunter's Mark | a Bonus Action moves the mark when the target drops to 0 | **Field**/**Engine**: `REDUCES_TO_ZERO` fires only for the creature that dealt the knockout, and nothing moves a badge to a new target |
| 4 | Elemental Attunement | Unarmed Strikes get 10 feet more reach | **Field**: no reach modifier |
| 4 | Enlarge/Reduce | +1d4 / -1d4 damage on weapon hits | **Field**: `ExtraDamageOnHit` needs a fixed type and can't subtract |
| 4 | Chill Touch | can't regain Hit Points until the end of your next turn (its badge has no modifier) | **Field**: a "no healing" modifier |
| 3 | Absorb Elements | the first melee hit next turn deals 1d6 more (upcast) and ends it | **Field**: `ExtraDamageOnHit` has no `once` and takes only ANY/WEAPON |
| 3 | Sacred Weapon, Elemental Attunement, True Strike | a hit can deal another damage type instead of its own (3 sources: principle 5's threshold) | **Field** |
| 3 | Shield | no damage from Magic Missile | **Field** (immunity to a named spell) |
| 2 | Resistance (cantrip) | reduces damage of a chosen type by 1d4, once per turn | **Field**: `damage_reduction` exists only on a `HIT_BY` row, not a badge |

### 4.10 Dice the bearer adds later

| Rank | Source | Left to the GM | Kind |
|---|---|---|---|
| 6 | Bardic Inspiration | added after a failed D20 Test, then spent | **Field** (the same badge trigger as Combat Inspiration) |
| 3 | Luck (Halfling) | reroll a 1 on the d20 | **Table** (`untriggered`) |
| 2 | Guidance | 1d4 on ability checks with one chosen skill | **Field**: `D20Bonus` filters by ability, not skill |

### 4.11 Choices the simulator could make itself

| Rank | Source | Left to the GM | Kind |
|---|---|---|---|
| 5 | Haste: lethargy | picked by hand as Haste ends | **Field**: an "as the badge ends" trigger (Fly's fall at the end is the same event) |
| 5 | Spare the Dying | the target becomes Stable; the row applies nothing, though `Combat/Fight/health.py` tracks Stable | **Field**: a "stabilizes" outcome |
| 3 | Toll the Dead | pick the d8 or d12 row by whether the target is missing HP | **Field**: a row gate on the target's HP, which the simulator knows |
| 3 | Steady Aim | only if you haven't moved this turn | **Engine**: the map tracks this turn's movement (`Combat/Arena/arena.py`) |
| 2 | Martial Arts | only unarmed or with Monk weapons, no armor or Shield | **Field**/sheet: equipment gate |

### 4.12 Stat parts still in a badge note

| Rank | Source | Left to the GM | Kind |
|---|---|---|---|
| 3 | Freedom of Movement | magic can't reduce its Speed or give it Paralyzed or Restrained | **Field**: `ConditionImmunity` with a "from magic" gate |
| 2 | Freedom of Movement | Swim Speed equal to Speed | **Now**: `Movement(swims=True)` |
| 2 | Freedom of Movement | 5 feet of movement to escape a grapple | **Field** |
| 1 | Spider Climb | moves across ceilings | Covered by `Movement(climbs=True)`; the note is flavor |

### 4.13 Resources the simulator doesn't count

| Rank | Source | Left to the GM |
|---|---|---|
| 5 | Lay on Hands | the Hit Point pool (typed each time; "20 after a Long Rest") |
| 3 | Jolt to Life | the revived creature's 3 Hit Points, healed by hand (one amount box per row) |
| 2 | Wild Companion | spend a spell slot or a Wild Shape use by hand |
| 1 | "Without a spell slot" | the only note `notes --min 3` flags (6 rows: Mapping Magic, Paladin's Smite, Fiendish Legacy, Magic Initiate, Fey Touched ×2). `uses_per_long_rest` already counts it; the note restates the field. Mapping Magic's and Favored Enemy's rows could be checked for the field too |

### 4.14 Saves only some targets make

| Rank | Source | Left to the GM | Kind |
|---|---|---|---|
| 5 | Enlarge/Reduce | an unwilling target makes a Constitution save first (`compare` shows the text's CON save; the rows have no roll) | **Field**: a save "only if unwilling" |
| 1 | Zone of Truth | `[]`, though the text has a Charisma save; it only matters for lying | **Table** |

### 4.15 Not simulated, by design (rank 1)

Feather Fall and Slow Fall (falling), Fly's fall as it ends, Divine Sense,
Tinker's Magic, Portal Step's teleport, Misty Step's teleport (`[]`; the map
could move the token later), Hunter's Mark's Perception Advantage, Lethargy
Resilience's save at the table, Burning Hands' burning objects, Moonbeam's
revert of a shape-shifter.

## 5. Party features marked "nothing to apply" that do something in a fight

These return `[]`, so they have no picker row, but part of their text does
act in a fight. They are the nearest thing to bugs in this audit: the rubric
keeps `[]` for features with nothing to put on a creature.

| Rank | Feature (member) | What's lost | Kind |
|---|---|---|---|
| 7 | War Caster (Clover) | Advantage on Concentration saves, which the simulator rolls itself | **Field** (§7's always-on modifier) |
| 6 | Tavern Brawler (Kivi) | Push: once per turn, an Unarmed Strike hit in the Attack action also pushes 5 feet | **Now**: a `HIT` row, `attacks=UNARMED`, `once_per_turn`, `CombatPush(5)` |
| 6 | Grappler (Kivi) | Advantage on attack rolls against a creature Grappled by you (the Grappled condition already names its grappler) | **Field** (always-on `AttacksAgainst`-like modifier, `by_caster`) |
| 5 | Grappler (Kivi) | Punch and Grab: once per turn, a hit also grapples | **Now**: a `HIT` row after the Unarmed Strike, like the Grapple row in `Model/Content/UnarmedStrikeEffects.py` |
| 4 | Dwarven Resilience (Obmar) | Advantage on saves against Poisoned (the Resistance is on the sheet) | **Field** (§7) |
| 3 | Stonecunning (Obmar) | Bonus Action: Tremorsense 60 feet for 10 minutes, PB uses | **Field**: `Vision` has no tremorsense |
| 3 | Adventurer's Atlas (Obmar) | each map holder adds 1d4 to Initiative | **Engine** |
| 3 | Resourceful (Clover) | Heroic Inspiration after a Long Rest; Heroic Inspiration isn't tracked at all | **Field** |
| 2 | Alert (Hanna) | Initiative swap with an ally (the PB bonus is applied on the sheet) | **Engine** |
| 2 | Tavern Brawler (Kivi) | reroll 1s on Unarmed Strike damage | **Table** |
| 2 | War Caster (Clover) | a spell instead of an Opportunity Attack | **Table** |
| 1 | Powerful Build (Kivi) | Advantage on checks to end Grappled | **Table** |

## 6. Features of the example builds (beyond the parties)

Every build in `Builds/Examples` (115) was built and its features walked as
the combat UI sees them, each feature class once (714):

| State | Count | Meaning |
|---|---|---|
| described | 41 | has rows |
| nothing to apply | 28 | `[]` |
| passive, no row | 60 | no row, by design |
| **read from its text** | **424** | not passive and no `combat_effects`: the picker guesses a row from the text |
| **extension, no row** | **161** | an extension with neither rows nor `adjust_combat_effect` |
| **Trigger fact, no trigger, no reason** | **181** | the `triggers` check would fail for these if a party had them |

**Quick wins: about 70 of the 424 only need `[]`** (or `passive=True`), rank
2. They grant spells, proficiencies, languages or senses, and still get a row
read from their text: every "<Subclass> Spells" / "Domain Spells" / "Expanded
Spell List" / "Circle Spells", Bonus Proficiencies, Spellcasting (Sorcerer,
Eldritch Knight, Mystic Arts), the Barbarian's Weapon Mastery and Unarmored
Defense, the Orc's Darkvision, the Savants, Magical Secrets, Ritual Adept,
Signature Spells, Spell Mastery, Trance, Sentry's Rest, Tools of the Trade,
Universal and Telepathic Speech, Replacing Cantrips/Invocations, and the like.

Many of the high ones are §4 or §7 gaps: Extra Attack, Two Extra Attacks and
Action Surge are the action economy (§4.7); Uncanny Dodge halves a hit's
damage, which `damage_reduction` can't say; Evasion, Danger Sense and Aura of
Protection are always-on traits (§7).

**Rank 6+ (30 features):**

| Rank | Feature | File(s) |
|---|---|---|
| 9 | Extra Attack | [ClassFeatures/Barbarian/BarbarianFeatures.py](../CharacterContent/Features/ClassFeatures/Barbarian/BarbarianFeatures.py), [ClassFeatures/Fighter/FighterFeatures.py](../CharacterContent/Features/ClassFeatures/Fighter/FighterFeatures.py), [ClassFeatures/Monk/MonkFeatures.py](../CharacterContent/Features/ClassFeatures/Monk/MonkFeatures.py), [ClassFeatures/Paladin/PaladinFeatures.py](../CharacterContent/Features/ClassFeatures/Paladin/PaladinFeatures.py), [ClassFeatures/Ranger/RangerFeatures.py](../CharacterContent/Features/ClassFeatures/Ranger/RangerFeatures.py), [SubClassFeatures2014/Bard/BardSwordsFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Bard/BardSwordsFeatures.py) |
| 8 | Action Surge | [ClassFeatures/Fighter/FighterFeatures.py](../CharacterContent/Features/ClassFeatures/Fighter/FighterFeatures.py) |
| 8 | Aura of Protection | [ClassFeatures/Paladin/PaladinFeatures.py](../CharacterContent/Features/ClassFeatures/Paladin/PaladinFeatures.py) |
| 8 | Stunning Strike | [ClassFeatures/Monk/MonkFeatures.py](../CharacterContent/Features/ClassFeatures/Monk/MonkFeatures.py) |
| 8 | Two Extra Attacks | [ClassFeatures/Fighter/FighterFeatures.py](../CharacterContent/Features/ClassFeatures/Fighter/FighterFeatures.py) |
| 7 | Breath Weapon | [SpeciesFeatures/DragonbornFeatures.py](../CharacterContent/Features/SpeciesFeatures/DragonbornFeatures.py) |
| 7 | Evasion | [ClassFeatures/Monk/MonkFeatures.py](../CharacterContent/Features/ClassFeatures/Monk/MonkFeatures.py), [ClassFeatures/Rogue/RogueFeatures.py](../CharacterContent/Features/ClassFeatures/Rogue/RogueFeatures.py) |
| 7 | Great Weapon Master | [CharacterFeats/GeneralFeats.py](../CharacterContent/Features/CharacterFeats/GeneralFeats.py) |
| 7 | Reckless Attack | [ClassFeatures/Barbarian/BarbarianFeatures.py](../CharacterContent/Features/ClassFeatures/Barbarian/BarbarianFeatures.py) |
| 7 | Sharpshooter | [CharacterFeats/GeneralFeats.py](../CharacterContent/Features/CharacterFeats/GeneralFeats.py) |
| 7 | Superiority Dice | [SubClassFeatures/Fighter/FighterBattleMasterFeatures.py](../CharacterContent/Features/SubClassFeatures/Fighter/FighterBattleMasterFeatures.py) |
| 7 | Uncanny Dodge | [ClassFeatures/Rogue/RogueFeatures.py](../CharacterContent/Features/ClassFeatures/Rogue/RogueFeatures.py) |
| 6 | Aura of Courage | [ClassFeatures/Paladin/PaladinFeatures.py](../CharacterContent/Features/ClassFeatures/Paladin/PaladinFeatures.py) |
| 6 | Bladesong | [SubClassFeatures/Wizard/WizardBladesingerFeatures.py](../CharacterContent/Features/SubClassFeatures/Wizard/WizardBladesingerFeatures.py) |
| 6 | Brutal Strike | [ClassFeatures/Barbarian/BarbarianFeatures.py](../CharacterContent/Features/ClassFeatures/Barbarian/BarbarianFeatures.py) |
| 6 | Celestial Revelation | [SpeciesFeatures/AasimarFeatures.py](../CharacterContent/Features/SpeciesFeatures/AasimarFeatures.py) |
| 6 | Colossus Slayer | [SubClassFeatures/Ranger/RangerHunterFeatures.py](../CharacterContent/Features/SubClassFeatures/Ranger/RangerHunterFeatures.py) |
| 6 | Cunning Strike | [ClassFeatures/Rogue/RogueFeatures.py](../CharacterContent/Features/ClassFeatures/Rogue/RogueFeatures.py) |
| 6 | Cutting Words | [SubClassFeatures/Bard/BardLoreFeatures.py](../CharacterContent/Features/SubClassFeatures/Bard/BardLoreFeatures.py) |
| 6 | Divine Strike | [ClassFeatures/Cleric/ClericFeatures.py](../CharacterContent/Features/ClassFeatures/Cleric/ClericFeatures.py) |
| 6 | Dreadful Strikes | [SubClassFeatures/Ranger/RangerFeyWandererFeatures.py](../CharacterContent/Features/SubClassFeatures/Ranger/RangerFeyWandererFeatures.py) |
| 6 | Frenzy | [SubClassFeatures/Barbarian/BarbarianPathOfTheBerserkerFeatures.py](../CharacterContent/Features/SubClassFeatures/Barbarian/BarbarianPathOfTheBerserkerFeatures.py) |
| 6 | Improved Critical | [SubClassFeatures/Fighter/FighterChampionFeatures.py](../CharacterContent/Features/SubClassFeatures/Fighter/FighterChampionFeatures.py) |
| 6 | Open Hand Technique | [SubClassFeatures/Monk/MonkOpenHandFeatures.py](../CharacterContent/Features/SubClassFeatures/Monk/MonkOpenHandFeatures.py) |
| 6 | Portent | [SubClassFeatures/Wizard/WizardDivinerFeatures.py](../CharacterContent/Features/SubClassFeatures/Wizard/WizardDivinerFeatures.py) |
| 6 | Primal Strike | [ClassFeatures/Druid/DruidFeatures.py](../CharacterContent/Features/ClassFeatures/Druid/DruidFeatures.py) |
| 6 | Radiant Strikes | [ClassFeatures/Paladin/PaladinFeatures.py](../CharacterContent/Features/ClassFeatures/Paladin/PaladinFeatures.py) |
| 6 | Riposte | [CombatFeatures/Maneuvers.py](../CharacterContent/Features/CombatFeatures/Maneuvers.py) |
| 6 | Starry Form | [SubClassFeatures/Druid/DruidStarsFeatures.py](../CharacterContent/Features/SubClassFeatures/Druid/DruidStarsFeatures.py) |
| 6 | Vow of Enmity | [SubClassFeatures/Paladin/PaladinVengeanceFeatures.py](../CharacterContent/Features/SubClassFeatures/Paladin/PaladinVengeanceFeatures.py) |

<details><summary>Read from their text (424), each with its rank</summary>

- [ClassFeatures/Barbarian/BarbarianFeatures.py](../CharacterContent/Features/ClassFeatures/Barbarian/BarbarianFeatures.py): Extra Attack (9), Reckless Attack (7), Danger Sense (5), Indomitable Might (3), Primal Knowledge (2), Unarmored Defense (2), Weapon Mastery (2)
- [ClassFeatures/Fighter/FighterFeatures.py](../CharacterContent/Features/ClassFeatures/Fighter/FighterFeatures.py): Extra Attack (9), Action Surge (8), Studied Attacks (4)
- [ClassFeatures/Monk/MonkFeatures.py](../CharacterContent/Features/ClassFeatures/Monk/MonkFeatures.py): Extra Attack (9), Evasion (7), Empowered Strikes (3), Self-Restoration (3), Acrobatic Movement (2)
- [ClassFeatures/Paladin/PaladinFeatures.py](../CharacterContent/Features/ClassFeatures/Paladin/PaladinFeatures.py): Extra Attack (9), Aura of Protection (8), Radiant Strikes (6), Faithful Steed (3)
- [ClassFeatures/Ranger/RangerFeatures.py](../CharacterContent/Features/ClassFeatures/Ranger/RangerFeatures.py): Extra Attack (9), Nature's Veil (4), Feral Senses (3), Roving (2), Tireless (1)
- [SubClassFeatures2014/Bard/BardSwordsFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Bard/BardSwordsFeatures.py): Extra Attack (9), Blade Flourish (5), Bonus Proficiencies (2)
- [CharacterFeats/GeneralFeats.py](../CharacterContent/Features/CharacterFeats/GeneralFeats.py): Great Weapon Master (7), Sharpshooter (7), Dual Wielder (4), Mage Slayer (4), Mounted Combatant (3), Durable (2), Observant (2)
- [ClassFeatures/Rogue/RogueFeatures.py](../CharacterContent/Features/ClassFeatures/Rogue/RogueFeatures.py): Evasion (7), Uncanny Dodge (7), Reliable Talent (1)
- [SpeciesFeatures/DragonbornFeatures.py](../CharacterContent/Features/SpeciesFeatures/DragonbornFeatures.py): Breath Weapon (7), Draconic Flight (4)
- [SubClassFeatures/Fighter/FighterBattleMasterFeatures.py](../CharacterContent/Features/SubClassFeatures/Fighter/FighterBattleMasterFeatures.py): Superiority Dice (7), Student of War (3)
- [ClassFeatures/Cleric/ClericFeatures.py](../CharacterContent/Features/ClassFeatures/Cleric/ClericFeatures.py): Divine Strike (6), Potent Spellcasting (5), Divine Order: Thaumaturge (4), Divine Intervention (2)
- [ClassFeatures/Druid/DruidFeatures.py](../CharacterContent/Features/ClassFeatures/Druid/DruidFeatures.py): Primal Strike (6), Potent Spellcasting (5)
- [SpeciesFeatures/AasimarFeatures.py](../CharacterContent/Features/SpeciesFeatures/AasimarFeatures.py): Celestial Revelation (6), Healing Hands (5), Light Bearer (3)
- [SubClassFeatures/Druid/DruidStarsFeatures.py](../CharacterContent/Features/SubClassFeatures/Druid/DruidStarsFeatures.py): Starry Form (6), Star Map (3)
- [SubClassFeatures/Fighter/FighterChampionFeatures.py](../CharacterContent/Features/SubClassFeatures/Fighter/FighterChampionFeatures.py): Improved Critical (6), Remarkable Athlete (4)
- [SubClassFeatures/Monk/MonkOpenHandFeatures.py](../CharacterContent/Features/SubClassFeatures/Monk/MonkOpenHandFeatures.py): Open Hand Technique (6), Quivering Palm (5), Wholeness of Body (5), Fleet Step (3)
- [SubClassFeatures/Paladin/PaladinVengeanceFeatures.py](../CharacterContent/Features/SubClassFeatures/Paladin/PaladinVengeanceFeatures.py): Vow of Enmity (6)
- [SubClassFeatures/Ranger/RangerFeyWandererFeatures.py](../CharacterContent/Features/SubClassFeatures/Ranger/RangerFeyWandererFeatures.py): Dreadful Strikes (6), Otherworldly Glamour (3), Fey Wanderer Spells (2)
- [SubClassFeatures/Ranger/RangerHunterFeatures.py](../CharacterContent/Features/SubClassFeatures/Ranger/RangerHunterFeatures.py): Colossus Slayer (6), Hunter's Lore (2)
- [SubClassFeatures/Wizard/WizardBladesingerFeatures.py](../CharacterContent/Features/SubClassFeatures/Wizard/WizardBladesingerFeatures.py): Bladesong (6)
- [SubClassFeatures/Wizard/WizardDivinerFeatures.py](../CharacterContent/Features/SubClassFeatures/Wizard/WizardDivinerFeatures.py): Portent (6), Divination Savant (2)
- [CharacterFeats/OriginFeats.py](../CharacterContent/Features/CharacterFeats/OriginFeats.py): Lucky (5), Healer (4), Savage Attacker (4), Musician (2)
- [ClassFeatures/Sorcerer/SorcererFeatures.py](../CharacterContent/Features/ClassFeatures/Sorcerer/SorcererFeatures.py): Font of Magic (5), Innate Sorcery (5), Metamagic (5), Spellcasting (2)
- [SubClassFeatures/Barbarian/BarbarianPathOfTheElementsFeatures.py](../CharacterContent/Features/SubClassFeatures/Barbarian/BarbarianPathOfTheElementsFeatures.py): Raging Elements (5), Primordial Bond (4), Echo of the Elements (3)
- [SubClassFeatures/Barbarian/BarbarianPathOfTheSpiritualGuardianFeatures.py](../CharacterContent/Features/SubClassFeatures/Barbarian/BarbarianPathOfTheSpiritualGuardianFeatures.py): Spirits' Fury (5), Consult the Spirits (2)
- [SubClassFeatures/Bard/BardDanceFeatures.py](../CharacterContent/Features/SubClassFeatures/Bard/BardDanceFeatures.py): Dazzling Footwork (5)
- [SubClassFeatures/Bard/BardGlamourFeatures.py](../CharacterContent/Features/SubClassFeatures/Bard/BardGlamourFeatures.py): Beguiling Magic (5), Mantle of Inspiration (4)
- [SubClassFeatures/Bard/BardSpiritsFeatures.py](../CharacterContent/Features/SubClassFeatures/Bard/BardSpiritsFeatures.py): Spirits from Beyond (5), Channeler (3)
- [SubClassFeatures/Cleric/ClericDisciplineFeatures.py](../CharacterContent/Features/SubClassFeatures/Cleric/ClericDisciplineFeatures.py): Ultimate Penitence (5), Atonement (4), Discipline Domain Spells (2)
- [SubClassFeatures/Cleric/ClericGraveFeatures.py](../CharacterContent/Features/SubClassFeatures/Cleric/ClericGraveFeatures.py): Circle of Mortality (5)
- [SubClassFeatures/Cleric/ClericShadowFeatures.py](../CharacterContent/Features/SubClassFeatures/Cleric/ClericShadowFeatures.py): Devouring Plague (5), Dispersion (4), Vampiric Embrace (4), Shadow Domain Spells (2)
- [SubClassFeatures/Druid/DruidLandFeatures.py](../CharacterContent/Features/SubClassFeatures/Druid/DruidLandFeatures.py): Land's Aid (5), Nature's Sanctuary (4), Natural Recovery (3), Circle of the Land Spells (2)
- [SubClassFeatures/Druid/DruidSeaFeatures.py](../CharacterContent/Features/SubClassFeatures/Druid/DruidSeaFeatures.py): Wrath of the Sea (5), Circle of the Sea Spells (2)
- [SubClassFeatures/Fighter/FighterArcaneArcherFeatures.py](../CharacterContent/Features/SubClassFeatures/Fighter/FighterArcaneArcherFeatures.py): Arcane Shot (5), Curving Shot (5), Magical Ammunition (5), Masterful Shots (5)
- [SubClassFeatures/Fighter/FighterEldritchKnightFeatures.py](../CharacterContent/Features/SubClassFeatures/Fighter/FighterEldritchKnightFeatures.py): Eldritch Strike (5), War Magic (3), Arcane Charge (2), Spellcasting (2), War Bond (2)
- [SubClassFeatures/Fighter/FighterPsiWarriorFeatures.py](../CharacterContent/Features/SubClassFeatures/Fighter/FighterPsiWarriorFeatures.py): Psionic Power (5), Telekinetic Master (5), Bulwark of Force (4), Guarded Mind (4)
- [SubClassFeatures/Fighter/FighterSorrowKnightFeatures.py](../CharacterContent/Features/SubClassFeatures/Fighter/FighterSorrowKnightFeatures.py): Despairing Strikes (5), Grim Constitution (4), Solemn Gaze (2)
- [SubClassFeatures/Monk/MonkMercyFeatures.py](../CharacterContent/Features/SubClassFeatures/Monk/MonkMercyFeatures.py): Flurry of Healing and Harm (5), Hand of Harm (5), Hand of Healing (5), Hand of Ultimate Mercy (4), Implements of Mercy (3)
- [SubClassFeatures/Monk/MonkMysticArtsFeatures.py](../CharacterContent/Features/SubClassFeatures/Monk/MonkMysticArtsFeatures.py): Focused Strike (5), Mystic Fighting Style (3), Spellcasting (2)
- [SubClassFeatures/Monk/MonkMysticBrewsFeatures.py](../CharacterContent/Features/SubClassFeatures/Monk/MonkMysticBrewsFeatures.py): Tipsy Sway (5)
- [SubClassFeatures/Paladin/PaladinEbonBladeFeatures.py](../CharacterContent/Features/SubClassFeatures/Paladin/PaladinEbonBladeFeatures.py): Death Coil (5), Runeforging (5), Runic Mastery (5), Runic Strikes (5), Aspect of the Horsemen (4), Runic Smite (3), Oath of the Ebon Blade Spells (2)
- [SubClassFeatures/Paladin/PaladinGloryFeatures.py](../CharacterContent/Features/SubClassFeatures/Paladin/PaladinGloryFeatures.py): Glorious Defense (5), Living Legend (4)
- [SubClassFeatures/Ranger/RangerDemonHunterFeatures.py](../CharacterContent/Features/SubClassFeatures/Ranger/RangerDemonHunterFeatures.py): Soul Fragments (5), Improved Spectral Sight (3), Spectral Sight (3), Void Warrior (3), Demon Hunter Spells (2)
- [SubClassFeatures/Ranger/RangerGloomStalkerFeatures.py](../CharacterContent/Features/SubClassFeatures/Ranger/RangerGloomStalkerFeatures.py): Dread Ambusher (5), Umbral Sight (4), Gloom Stalker Spells (2)
- [SubClassFeatures/Ranger/RangerHollowWardenFeatures.py](../CharacterContent/Features/SubClassFeatures/Ranger/RangerHollowWardenFeatures.py): Wrath of the Wild (5), Hollow Warden Spells (2)
- [SubClassFeatures/Ranger/RangerWinterWalkerFeatures.py](../CharacterContent/Features/SubClassFeatures/Ranger/RangerWinterWalkerFeatures.py): Frigid Explorer (5), Hunter's Rime (5), Winter Walker Spells (2)
- [SubClassFeatures/Rogue/RogueAssassinFeatures.py](../CharacterContent/Features/SubClassFeatures/Rogue/RogueAssassinFeatures.py): Assassinate (5), Assassin's Tools (2)
- [SubClassFeatures/Rogue/RoguePhantomFeatures.py](../CharacterContent/Features/SubClassFeatures/Rogue/RoguePhantomFeatures.py): Death's Friend (5), Ghost Walk (4), Tokens of the Departed (4), Whispers of the Dead (3), Voice of Death (2)
- [SubClassFeatures/Rogue/RogueSwashbucklerFeatures.py](../CharacterContent/Features/SubClassFeatures/Rogue/RogueSwashbucklerFeatures.py): Master Duelist (5), Fancy Footwork (4), Rakish Audacity (4)
- [SubClassFeatures/Sorcerer/SorcererAberrantFeatures.py](../CharacterContent/Features/SubClassFeatures/Sorcerer/SorcererAberrantFeatures.py): Warping Implosion (5), Revelation in Flesh (4), Psionic Spells (2), Telepathic Speech (2)
- [SubClassFeatures/Warlock/WarlockArchfeyFeatures.py](../CharacterContent/Features/SubClassFeatures/Warlock/WarlockArchfeyFeatures.py): Steps of the Fey (5), Archfey Spells (2)
- [SubClassFeatures/Warlock/WarlockCelestialFeatures.py](../CharacterContent/Features/SubClassFeatures/Warlock/WarlockCelestialFeatures.py): Radiant Soul (5), Searing Vengeance (5), Healing Light (4), Celestial Spells (2)
- [SubClassFeatures/Wizard/WizardEnchanterFeatures.py](../CharacterContent/Features/SubClassFeatures/Wizard/WizardEnchanterFeatures.py): Alter Memories (5), Hypnotic Presence (5), Instinctive Charm (5), Split Enchantment (5), Enchantment Savant (2)
- [SubClassFeatures/Wizard/WizardNecromancerFeatures.py](../CharacterContent/Features/SubClassFeatures/Wizard/WizardNecromancerFeatures.py): Death's Master (5), Undead Thralls (5), Grave Power (3), Necromancy Savant (2), Necromancy Spellbook (2)
- [SubClassFeatures/Wizard/WizardTransmuterFeatures.py](../CharacterContent/Features/SubClassFeatures/Wizard/WizardTransmuterFeatures.py): Wondrous Alteration (5), Transmuter's Stone (4), Empowered Transmutation (3), Shape-Shifter (3), Transmutation Savant (2)
- [SubClassFeatures2014/Barbarian/BarbarianPathOfTheBattleragerFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Barbarian/BarbarianPathOfTheBattleragerFeatures.py): Battlerager Armor (5)
- [SubClassFeatures2014/Barbarian/BarbarianPathOfTheStormHeraldFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Barbarian/BarbarianPathOfTheStormHeraldFeatures.py): Raging Storm (5), Shielding Storm (4), Storm Soul (4)
- [SubClassFeatures2014/Bard/BardWhispersFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Bard/BardWhispersFeatures.py): Shadow Lore (5), Words of Terror (5), Mantle of Whispers (2)
- [SubClassFeatures2014/Cleric/ClericDeathFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Cleric/ClericDeathFeatures.py): Channel Divinity: Touch of Death (5), Reaper (3), Bonus Proficiency (2), Death Domain Spells (2)
- [SubClassFeatures2014/Cleric/ClericNatureFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Cleric/ClericNatureFeatures.py): Channel Divinity: Charm Animals and Plants (5), Dampen Elements (4), Acolyte of Nature (3), Bonus Proficiency (2), Nature Domain Spells (2)
- [SubClassFeatures2014/Cleric/ClericOrderFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Cleric/ClericOrderFeatures.py): Channel Divinity: Order's Demand (5), Bonus Proficiencies (2), Embodiment of the Law (2), Order Domain Spells (2), Voice of Authority (2)
- [SubClassFeatures2014/Cleric/ClericTempestFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Cleric/ClericTempestFeatures.py): Thunderous Strike (5), Wrath of the Storm (5), Channel Divinity: Destructive Wrath (3), Bonus Proficiencies (2), Stormborn (2), Tempest Domain Spells (2)
- [SubClassFeatures2014/Druid/DruidSporesFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Druid/DruidSporesFeatures.py): Halo of Spores (5), Symbiotic Entity (4), Fungal Infestation (3), Circle of Spores Spells (2)
- [SubClassFeatures2014/Druid/DruidWildfireFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Druid/DruidWildfireFeatures.py): Cauterizing Flames (5), Summon Wildfire Spirit (5), Circle Spells (2)
- [SubClassFeatures2014/Fighter/FighterCavalierFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Fighter/FighterCavalierFeatures.py): Ferocious Charger (5), Hold the Line (5), Unwavering Mark (5), Vigilant Defender (5), Warding Maneuver (4), Bonus Proficiency (2), Born to the Saddle (2)
- [SubClassFeatures2014/Fighter/FighterEchoKnightFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Fighter/FighterEchoKnightFeatures.py): Manifest Echo (5), Unleash Incarnation (5), Reclaim Potential (4), Shadow Martyr (4), Echo Avatar (2)
- [SubClassFeatures2014/Fighter/FighterRuneKnightFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Fighter/FighterRuneKnightFeatures.py): Giant's Might (5), Rune Carver (5), Runic Shield (4)
- [SubClassFeatures2014/Fighter/FighterSamuraiFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Fighter/FighterSamuraiFeatures.py): Rapid Strike (5), Fighting Spirit (4), Strength Before Death (3), Elegant Courtier (2)
- [SubClassFeatures2014/Monk/MonkAstralSelfFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Monk/MonkAstralSelfFeatures.py): Arms of the Astral Self (5), Body of the Astral Self (5), Awakened Astral Self (4)
- [SubClassFeatures2014/Monk/MonkDrunkenMasterFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Monk/MonkDrunkenMasterFeatures.py): Tipsy Sway (5), Drunkard's Luck (4), Intoxicated Frenzy (4), Bonus Proficiencies (2)
- [SubClassFeatures2014/Monk/MonkKenseiFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Monk/MonkKenseiFeatures.py): Deft Strike (5), Kensei's Shot (5), Agile Parry (4), Sharpen the Blade (4), Unerring Accuracy (4), Kensei Weapons (2), Way of the Brush (2)
- [SubClassFeatures2014/Monk/MonkLongDeathFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Monk/MonkLongDeathFeatures.py): Hour of Reaping (5), Touch of the Long Death (5), Mastery of Death (4), Touch of Death (4)
- [SubClassFeatures2014/Monk/MonkSunSoulFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Monk/MonkSunSoulFeatures.py): Radiant Sun Bolt (5), Searing Arc Strike (5), Searing Sunburst (5), Sun Shield (5)
- [SubClassFeatures2014/Paladin/PaladinConquestFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Paladin/PaladinConquestFeatures.py): Aura of Conquest (5), Channel Divinity: Conquering Presence (5), Scornful Rebuke (5), Channel Divinity: Guided Strike (4), Invincible Conqueror (4), Oath of Conquest Spells (2)
- [SubClassFeatures2014/Paladin/PaladinCrownFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Paladin/PaladinCrownFeatures.py): Channel Divinity: Champion Challenge (5), Channel Divinity: Turn the Tide (4), Exalted Champion (4), Unyielding Saint (4), Divine Allegiance (3), Oath of the Crown Spells (2)
- [SubClassFeatures2014/Paladin/PaladinOathbreakerFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Paladin/PaladinOathbreakerFeatures.py): Control Undead (5), Dread Lord (5), Dreadful Aspect (5), Aura of Hate (4), Supernatural Resistance (4), Oathbreaker Spells (2)
- [SubClassFeatures2014/Paladin/PaladinRedemptionFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Paladin/PaladinRedemptionFeatures.py): Channel Divinity: Rebuke the Violent (5), Emissary of Redemption (5), Channel Divinity: Emissary of Peace (4), Protective Spirit (4), Aura of the Guardian (3), Oath of Redemption Spells (2)
- [SubClassFeatures2014/Paladin/PaladinWatchersFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Paladin/PaladinWatchersFeatures.py): Mortal Bulwark (5), Vigilant Rebuke (5), Aura of the Sentinel (4), Oath of the Watchers Spells (2)
- [SubClassFeatures2014/Ranger/RangerDrakewardenFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Ranger/RangerDrakewardenFeatures.py): Drake's Breath (5)
- [SubClassFeatures2014/Ranger/RangerHorizonWalkerFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Ranger/RangerHorizonWalkerFeatures.py): Distant Strike (5), Planar Warrior (5), Spectral Defense (4), Detect Portal (2), Ethereal Step (2), Horizon Walker Spells (2)
- [SubClassFeatures2014/Ranger/RangerMonsterSlayerFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Ranger/RangerMonsterSlayerFeatures.py): Magic-User's Nemesis (5), Slayer's Prey (5), Monster Slayer Magic (3), Hunter's Sense (2)
- [SubClassFeatures2014/Ranger/RangerSwarmkeeperFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Ranger/RangerSwarmkeeperFeatures.py): Gathered Swarm (5), Swarming Dispersal (4), Swarmkeeper Magic (3), Writhing Tide (2)
- [SubClassFeatures2014/Rogue/RogueMastermindFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Rogue/RogueMastermindFeatures.py): Misdirection (5), Master of Tactics (4), Insightful Manipulator (2), Master of Intrigue (2), Soul of Deceit (2)
- [SubClassFeatures2014/Rogue/RogueScoutFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Rogue/RogueScoutFeatures.py): Sudden Strike (5), Ambush Master (4), Skirmisher (2), Superior Mobility (2)
- [SubClassFeatures2014/Rogue/RogueSwashbucklerFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Rogue/RogueSwashbucklerFeatures.py): Panache (5), Elegant Maneuver (4), Fancy Footwork (4), Master Duelist (4)
- [SubClassFeatures2014/Sorcerer/SorcererLunarSorceryFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Sorcerer/SorcererLunarSorceryFeatures.py): Moon Fire (5), Lunar Embodiment (3)
- [SubClassFeatures2014/Sorcerer/SorcererStormSorceryFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Sorcerer/SorcererStormSorceryFeatures.py): Heart of the Storm (5), Storm's Fury (5), Wind Soul (4), Storm Guide (2), Tempestuous Magic (2)
- [SubClassFeatures2014/Warlock/WarlockFathomlessFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Warlock/WarlockFathomlessFeatures.py): Tentacle of the Deep (5), Grasping Tentacles (4), Oceanic Soul (4), Expanded Spell List (2), Fathomless Plunge (2), Gift of the Sea (2)
- [SubClassFeatures2014/Warlock/WarlockHexbladeFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Warlock/WarlockHexbladeFeatures.py): Accursed Specter (5), Hexblade's Curse (5), Hex Warrior (4), Expanded Spell List (2)
- [SubClassFeatures2014/Warlock/WarlockTheGenieFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Warlock/WarlockTheGenieFeatures.py): Genie's Vessel (5), Elemental Gift (4), Expanded Spell List (2)
- [SubClassFeatures2014/Wizard/WizardChronurgyFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Wizard/WizardChronurgyFeatures.py): Momentary Stasis (5), Arcane Abeyance (3), Chronal Shift (3), Convergent Future (3), Temporal Awareness (3)
- [SubClassFeatures2014/Wizard/WizardGraviturgyFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Wizard/WizardGraviturgyFeatures.py): Adjust Density (5), Event Horizon (5), Gravity Well (5), Violent Attraction (5)
- [ClassFeatures/Bard/BardFeatures.py](../CharacterContent/Features/ClassFeatures/Bard/BardFeatures.py): Countercharm (4), Magical Secrets (2), Words of Creation (2)
- [SpeciesFeatures/ElfFeatures.py](../CharacterContent/Features/SpeciesFeatures/ElfFeatures.py): Fey Ancestry (4), Trance (2)
- [SubClassFeatures/Fighter/FighterBanneretFeatures.py](../CharacterContent/Features/SubClassFeatures/Fighter/FighterBanneretFeatures.py): Group Recovery (4), Knightly Envoy (2)
- [SubClassFeatures/Paladin/PaladinGeniesFeatures.py](../CharacterContent/Features/SubClassFeatures/Paladin/PaladinGeniesFeatures.py): Genie's Splendor (4)
- [SubClassFeatures/Paladin/PaladinHolyFeatures.py](../CharacterContent/Features/SubClassFeatures/Paladin/PaladinHolyFeatures.py): Holy Deliverance (4)
- [SubClassFeatures/Warlock/WarlockVestigeFeatures.py](../CharacterContent/Features/SubClassFeatures/Warlock/WarlockVestigeFeatures.py): Semblance of Life (4), Vestige Recovery (4), Vestige Companion (3), Vestige Spells (2)
- [SubClassFeatures/Wizard/WizardConjurerFeatures.py](../CharacterContent/Features/SubClassFeatures/Wizard/WizardConjurerFeatures.py): Durable Summons (4), Focused Conjuration (3), Splintered Summons (3), Benign Transposition (2), Conjuration Savant (2)
- [SubClassFeatures2014/Barbarian/BarbarianPathOfWildMagicFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Barbarian/BarbarianPathOfWildMagicFeatures.py): Bolstering Magic (4), Magic Awareness (2)
- [SubClassFeatures2014/Bard/BardEloquenceFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Bard/BardEloquenceFeatures.py): Silver Tongue (4), Universal Speech (2)
- [SubClassFeatures2014/Cleric/ClericForgeFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Cleric/ClericForgeFeatures.py): Blessing of the Forge (4), Bonus Proficiencies (2), Channel Divinity: Artisan's Blessing (2), Forge Domain Spells (2)
- [SubClassFeatures2014/Cleric/ClericPeaceFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Cleric/ClericPeaceFeatures.py): Channel Divinity: Balm of Peace (4), Emboldening Bond (4), Implement of Peace (3), Peace Domain Spells (2)
- [SubClassFeatures2014/Cleric/ClericTwilightFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Cleric/ClericTwilightFeatures.py): Channel Divinity: Twilight Sanctuary (4), Vigilant Blessing (4), Bonus Proficiencies (2), Eyes of Night (2), Steps of Night (2), Twilight Domain Spells (2)
- [SubClassFeatures2014/Druid/DruidDreamsFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Druid/DruidDreamsFeatures.py): Balm of the Summer Court (4), Hearth of Moonlight and Shadow (4), Walker in Dreams (3), Hidden Paths (2)
- [SubClassFeatures2014/Druid/DruidShepherdFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Druid/DruidShepherdFeatures.py): Faithful Summons (4), Mighty Summoner (4), Spirit Totem (4), Speech of the Woods (2)
- [SubClassFeatures2014/Sorcerer/SorcererDivineSoulFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Sorcerer/SorcererDivineSoulFeatures.py): Empowered Healing (4), Favored by the Gods (4), Unearthly Recovery (4), Angelic Form (2)
- [SubClassFeatures2014/Warlock/WarlockTheUndyingFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Warlock/WarlockTheUndyingFeatures.py): Among the Dead (4), Defy Death (4), Indestructible Life (4), Expanded Spell List (2), Undying Nature (2)
- [CharacterFeats/EpicBoon.py](../CharacterContent/Features/CharacterFeats/EpicBoon.py): Epic Boon (3)
- [SpeciesFeatures/GnomeFeatures.py](../CharacterContent/Features/SpeciesFeatures/GnomeFeatures.py): Forest Gnome Speak with Animals (3), Rock Gnome Prestidigitation (3)
- [SubClassFeatures/Artificer/ArtificerBattleSmithFeatures.py](../CharacterContent/Features/SubClassFeatures/Artificer/ArtificerBattleSmithFeatures.py): Battle Ready (3), Battle Smith spells (3), Steel Defender (3), Tools of the Trade (2)
- [SubClassFeatures/Ranger/RangerBeastMasterFeatures.py](../CharacterContent/Features/SubClassFeatures/Ranger/RangerBeastMasterFeatures.py): Primal Companion (3)
- [SubClassFeatures2014/Bard/BardCreationFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Bard/BardCreationFeatures.py): Animating Performance (3), Performance of Creation (2)
- [ClassFeatures/Warlock/WarlockFeatures.py](../CharacterContent/Features/ClassFeatures/Warlock/WarlockFeatures.py): Contact Patron (2), Mystic Arcanum (2), Replacing Cantrips and Spells (2), Replacing Eldritch Invocations (2), Magical Cunning (1), Regaining Spell Slots (1)
- [ClassFeatures/Wizard/WizardFeatures.py](../CharacterContent/Features/ClassFeatures/Wizard/WizardFeatures.py): Memorize Spell (2), Ritual Adept (2), Signature Spells (2), Spell Mastery (2), Arcane Recovery (1)
- [SpeciesFeatures/OrcFeatures.py](../CharacterContent/Features/SpeciesFeatures/OrcFeatures.py): Darkvision (2)
- [SpeciesFeatures/WarForgedFeatures.py](../CharacterContent/Features/SpeciesFeatures/WarForgedFeatures.py): Sentry's Rest (2), Tireless (1)
- [SubClassFeatures/Bard/BardLoreFeatures.py](../CharacterContent/Features/SubClassFeatures/Bard/BardLoreFeatures.py): Magical Discoveries (2)
- [SubClassFeatures/Cleric/ClericArcanaFeatures.py](../CharacterContent/Features/SubClassFeatures/Cleric/ClericArcanaFeatures.py): Dispelling Recovery (2)
- [SubClassFeatures/Sorcerer/SorcererDraconicFeatures.py](../CharacterContent/Features/SubClassFeatures/Sorcerer/SorcererDraconicFeatures.py): Draconic Spells (2)
- [SubClassFeatures2014/Barbarian/BarbarianPathOfTheAncestralGuardianFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Barbarian/BarbarianPathOfTheAncestralGuardianFeatures.py): Consult the Spirits (2)
- [SubClassFeatures2014/Wizard/WizardOrderOfScribesFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Wizard/WizardOrderOfScribesFeatures.py): Awakened Spellbook (2), Wizardly Quill (2)

</details>

<details><summary>Extensions with no row (161), each with its rank</summary>

- [ClassFeatures/Fighter/FighterFeatures.py](../CharacterContent/Features/ClassFeatures/Fighter/FighterFeatures.py): Two Extra Attacks (8), Tactical Master (4), Tactical Mind (3), Tactical Shift (3)
- [ClassFeatures/Monk/MonkFeatures.py](../CharacterContent/Features/ClassFeatures/Monk/MonkFeatures.py): Stunning Strike (8), Deflect Energy (5), Disciplined Survivor (4), Heightened Focus (4)
- [ClassFeatures/Barbarian/BarbarianFeatures.py](../CharacterContent/Features/ClassFeatures/Barbarian/BarbarianFeatures.py): Brutal Strike (6), Improved Brutal Strike 1 (5), Improved Brutal Strike 2 (5), Fast Movement (3), Instinctive Pounce (3)
- [ClassFeatures/Paladin/PaladinFeatures.py](../CharacterContent/Features/ClassFeatures/Paladin/PaladinFeatures.py): Aura of Courage (6), Aura Expansion (5), Restoring Touch (4)
- [ClassFeatures/Rogue/RogueFeatures.py](../CharacterContent/Features/ClassFeatures/Rogue/RogueFeatures.py): Cunning Strike (6), Devious Strikes (5), Improved Cunning Strike (5)
- [CombatFeatures/Maneuvers.py](../CharacterContent/Features/CombatFeatures/Maneuvers.py): Riposte (6), Goading Attack (5), Pushing Attack (5)
- [SubClassFeatures/Barbarian/BarbarianPathOfTheBerserkerFeatures.py](../CharacterContent/Features/SubClassFeatures/Barbarian/BarbarianPathOfTheBerserkerFeatures.py): Frenzy (6)
- [SubClassFeatures/Bard/BardLoreFeatures.py](../CharacterContent/Features/SubClassFeatures/Bard/BardLoreFeatures.py): Cutting Words (6), Peerless Skill (4)
- [ClassFeatures/Cleric/ClericFeatures.py](../CharacterContent/Features/ClassFeatures/Cleric/ClericFeatures.py): Improved Divine Strike (5), Improved Potent Spellcasting (4), Sear Undead (4), Greater Divine Intervention (2)
- [ClassFeatures/Druid/DruidFeatures.py](../CharacterContent/Features/ClassFeatures/Druid/DruidFeatures.py): Improved Primal Strike (5), Wild Resurgence (3), Beast Spells (2)
- [SubClassFeatures/Barbarian/BarbarianPathOfTheElementsFeatures.py](../CharacterContent/Features/SubClassFeatures/Barbarian/BarbarianPathOfTheElementsFeatures.py): Elemental Overload (5)
- [SubClassFeatures/Barbarian/BarbarianPathOfTheSpiritualGuardianFeatures.py](../CharacterContent/Features/SubClassFeatures/Barbarian/BarbarianPathOfTheSpiritualGuardianFeatures.py): Spiritual Protectors (5), Spirit Shield (4)
- [SubClassFeatures/Cleric/ClericArcanaFeatures.py](../CharacterContent/Features/SubClassFeatures/Cleric/ClericArcanaFeatures.py): Modify Magic (5)
- [SubClassFeatures/Cleric/ClericGraveFeatures.py](../CharacterContent/Features/SubClassFeatures/Cleric/ClericGraveFeatures.py): Path to the Grave (5)
- [SubClassFeatures/Cleric/ClericShadowFeatures.py](../CharacterContent/Features/SubClassFeatures/Cleric/ClericShadowFeatures.py): Shadowform (5)
- [SubClassFeatures/Fighter/FighterArcaneArcherFeatures.py](../CharacterContent/Features/SubClassFeatures/Fighter/FighterArcaneArcherFeatures.py): Banishing Shot (5), Bursting Shot (5), Grasping Shot (5), Piercing Shot (5), Seeking Shot (5), Shadow Shot (5), Indomitable Teleport (2)
- [SubClassFeatures/Fighter/FighterPsiWarriorFeatures.py](../CharacterContent/Features/SubClassFeatures/Fighter/FighterPsiWarriorFeatures.py): Telekinetic Adept (5)
- [SubClassFeatures/Fighter/FighterSorrowKnightFeatures.py](../CharacterContent/Features/SubClassFeatures/Fighter/FighterSorrowKnightFeatures.py): Dreaded Appearance (5), Unsettled Strikes (5), Grieving Mantle (4)
- [SubClassFeatures/Monk/MonkElementsFeatures.py](../CharacterContent/Features/SubClassFeatures/Monk/MonkElementsFeatures.py): Elemental Epitome (5), Stride of the Elements (4)
- [SubClassFeatures/Monk/MonkMercyFeatures.py](../CharacterContent/Features/SubClassFeatures/Monk/MonkMercyFeatures.py): Physician's Touch (5)
- [SubClassFeatures/Monk/MonkMysticBrewsFeatures.py](../CharacterContent/Features/SubClassFeatures/Monk/MonkMysticBrewsFeatures.py): Drunken Technique (5), Intoxicated Frenzy (5), Wizened Brewer (5), Master Brewer (4)
- [SubClassFeatures/Paladin/PaladinAncientsFeatures.py](../CharacterContent/Features/SubClassFeatures/Paladin/PaladinAncientsFeatures.py): Nature's Wrath (5)
- [SubClassFeatures/Paladin/PaladinEbonBladeFeatures.py](../CharacterContent/Features/SubClassFeatures/Paladin/PaladinEbonBladeFeatures.py): Improved Death Coil (5), Runic Power (5), Aura of Deathly Endurance (4), Undead Steed (2)
- [SubClassFeatures/Paladin/PaladinGeniesFeatures.py](../CharacterContent/Features/SubClassFeatures/Paladin/PaladinGeniesFeatures.py): Elemental Smite (5)
- [SubClassFeatures/Ranger/RangerBeastMasterFeatures.py](../CharacterContent/Features/SubClassFeatures/Ranger/RangerBeastMasterFeatures.py): Bestial Fury (5), Exceptional Training (5), Share Spells (2)
- [SubClassFeatures/Ranger/RangerDemonHunterFeatures.py](../CharacterContent/Features/SubClassFeatures/Ranger/RangerDemonHunterFeatures.py): Illidari Knowledge (5), Soul Shatter (5), Torment (5), Demon Hunter Languages (2), Demon Hunter Spellcasting (2)
- [SubClassFeatures/Rogue/RoguePhantomFeatures.py](../CharacterContent/Features/SubClassFeatures/Rogue/RoguePhantomFeatures.py): Wails from the Grave (5)
- [SubClassFeatures/Rogue/RogueSwashbucklerFeatures.py](../CharacterContent/Features/SubClassFeatures/Rogue/RogueSwashbucklerFeatures.py): Panache (5), Dashing Strikes (4)
- [SubClassFeatures2014/Barbarian/BarbarianPathOfTheAncestralGuardianFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Barbarian/BarbarianPathOfTheAncestralGuardianFeatures.py): Ancestral Protectors (5), Vengeful Ancestors (5), Spirit Shield (4)
- [SubClassFeatures2014/Barbarian/BarbarianPathOfTheBattleragerFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Barbarian/BarbarianPathOfTheBattleragerFeatures.py): Spiked Retribution (5), Reckless Abandon (4)
- [SubClassFeatures2014/Barbarian/BarbarianPathOfTheStormHeraldFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Barbarian/BarbarianPathOfTheStormHeraldFeatures.py): Storm Aura (5)
- [SubClassFeatures2014/Barbarian/BarbarianPathOfWildMagicFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Barbarian/BarbarianPathOfWildMagicFeatures.py): Controlled Surge (5), Unstable Backlash (5), Wild Surge (5)
- [SubClassFeatures2014/Bard/BardCreationFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Bard/BardCreationFeatures.py): Mote of Potential (5), Creative Crescendo (2)
- [SubClassFeatures2014/Bard/BardEloquenceFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Bard/BardEloquenceFeatures.py): Unsettling Words (5), Infectious Inspiration (4), Unfailing Inspiration (4)
- [SubClassFeatures2014/Bard/BardWhispersFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Bard/BardWhispersFeatures.py): Psychic Blades (5)
- [SubClassFeatures2014/Cleric/ClericOrderFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Cleric/ClericOrderFeatures.py): Order's Wrath (5)
- [SubClassFeatures2014/Cleric/ClericPeaceFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Cleric/ClericPeaceFeatures.py): Protective Bond (5), Expansive Bond (4)
- [SubClassFeatures2014/Druid/DruidSporesFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Druid/DruidSporesFeatures.py): Spreading Spores (5)
- [SubClassFeatures2014/Fighter/FighterEchoKnightFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Fighter/FighterEchoKnightFeatures.py): Legion of One (5)
- [SubClassFeatures2014/Paladin/PaladinWatchersFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Paladin/PaladinWatchersFeatures.py): Channel Divinity: Abjure the Extraplanar (5), Channel Divinity: Watcher's Will (4), Aura of the Sentinel Expansion (3)
- [SubClassFeatures2014/Ranger/RangerMonsterSlayerFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Ranger/RangerMonsterSlayerFeatures.py): Slayer's Counter (5), Supernatural Defense (4)
- [SubClassFeatures2014/Ranger/RangerSwarmkeeperFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Ranger/RangerSwarmkeeperFeatures.py): Mighty Swarm (5)
- [SubClassFeatures2014/Sorcerer/SorcererLunarSorceryFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Sorcerer/SorcererLunarSorceryFeatures.py): Lunar Phenomenon (5), Lunar Boons (4), Lunar Empowerment (4), Waxing and Waning (2)
- [SubClassFeatures2014/Warlock/WarlockHexbladeFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Warlock/WarlockHexbladeFeatures.py): Master of Hexes (5), Armor of Hexes (4)
- [ClassFeatures/Ranger/RangerFeatures.py](../CharacterContent/Features/ClassFeatures/Ranger/RangerFeatures.py): Foe Slayer (4), Precise Hunter (4), Relentless Hunter (3)
- [ClassFeatures/Sorcerer/SorcererFeatures.py](../CharacterContent/Features/ClassFeatures/Sorcerer/SorcererFeatures.py): Sorcery Incarnate (4), Sorcerous Restoration (1)
- [SubClassFeatures/Barbarian/BarbarianPathOfTheWorldTreeFeatures.py](../CharacterContent/Features/SubClassFeatures/Barbarian/BarbarianPathOfTheWorldTreeFeatures.py): Vitality of the Tree (4)
- [SubClassFeatures/Cleric/ClericDisciplineFeatures.py](../CharacterContent/Features/SubClassFeatures/Cleric/ClericDisciplineFeatures.py): Luminous Barrier (4)
- [SubClassFeatures/Fighter/FighterBanneretFeatures.py](../CharacterContent/Features/SubClassFeatures/Fighter/FighterBanneretFeatures.py): Shared Resilience (4), Team Tactics (4), Rallying Surge (3)
- [SubClassFeatures/Paladin/PaladinGloryFeatures.py](../CharacterContent/Features/SubClassFeatures/Paladin/PaladinGloryFeatures.py): Aura of Alacrity (4), Inspiring Smite (4), Peerless Athlete (4)
- [SubClassFeatures/Paladin/PaladinHolyFeatures.py](../CharacterContent/Features/SubClassFeatures/Paladin/PaladinHolyFeatures.py): Beacon of Light (4), Infusion of Light (4), Lightbringer's Aura (4)
- [SubClassFeatures/Warlock/WarlockCelestialFeatures.py](../CharacterContent/Features/SubClassFeatures/Warlock/WarlockCelestialFeatures.py): Celestial Resilience (4)
- [SubClassFeatures/Warlock/WarlockVestigeFeatures.py](../CharacterContent/Features/SubClassFeatures/Warlock/WarlockVestigeFeatures.py): Vestige Power (4)
- [SubClassFeatures/Wizard/WizardTransmuterFeatures.py](../CharacterContent/Features/SubClassFeatures/Wizard/WizardTransmuterFeatures.py): Master Transmuter (4), Potent Stone (4)
- [SubClassFeatures2014/Bard/BardSwordsFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Bard/BardSwordsFeatures.py): Master's Flourish (4)
- [SubClassFeatures2014/Cleric/ClericForgeFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Cleric/ClericForgeFeatures.py): Saint of Forge and Fire (4)
- [SubClassFeatures2014/Cleric/ClericTwilightFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Cleric/ClericTwilightFeatures.py): Twilight Shroud (4)
- [SubClassFeatures2014/Druid/DruidShepherdFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Druid/DruidShepherdFeatures.py): Guardian Spirit (4)
- [SubClassFeatures2014/Druid/DruidWildfireFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Druid/DruidWildfireFeatures.py): Blazing Revival (4), Enhanced Bond (4)
- [SubClassFeatures2014/Monk/MonkAstralSelfFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Monk/MonkAstralSelfFeatures.py): Visage of the Astral Self (4)
- [SubClassFeatures2014/Ranger/RangerDrakewardenFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Ranger/RangerDrakewardenFeatures.py): Bond of Fang and Scale (4), Perfected Bond (4)
- [SubClassFeatures2014/Rogue/RogueSwashbucklerFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Rogue/RogueSwashbucklerFeatures.py): Rakish Audacity (4)
- [SubClassFeatures2014/Warlock/WarlockFathomlessFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Warlock/WarlockFathomlessFeatures.py): Guardian Coil (4)
- [SubClassFeatures2014/Wizard/WizardOrderOfScribesFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Wizard/WizardOrderOfScribesFeatures.py): One with the Word (4), Manifest Mind (2), Master Scriviner (2)
- [SubClassFeatures/Cleric/ClericKnowledgeFeatures.py](../CharacterContent/Features/SubClassFeatures/Cleric/ClericKnowledgeFeatures.py): Mind Magic (3)
- [SubClassFeatures/Fighter/FighterEldritchKnightFeatures.py](../CharacterContent/Features/SubClassFeatures/Fighter/FighterEldritchKnightFeatures.py): Improved War Magic (3)
- [SubClassFeatures/Monk/MonkMysticArtsFeatures.py](../CharacterContent/Features/SubClassFeatures/Monk/MonkMysticArtsFeatures.py): Improved Mystic Fighting Style (3), Mystic Focus (3)
- [SubClassFeatures/Monk/MonkShadowFeatures.py](../CharacterContent/Features/SubClassFeatures/Monk/MonkShadowFeatures.py): Shadow Arts (3)
- [SubClassFeatures/Sorcerer/SorcererAberrantFeatures.py](../CharacterContent/Features/SubClassFeatures/Sorcerer/SorcererAberrantFeatures.py): Psionic Sorcery (3)
- [SubClassFeatures/Wizard/WizardConjurerFeatures.py](../CharacterContent/Features/SubClassFeatures/Wizard/WizardConjurerFeatures.py): Distant Transposition (3)
- [SubClassFeatures2014/Cleric/ClericDeathFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Cleric/ClericDeathFeatures.py): Improved Reaper (3), Inescapable Destruction (3)
- [SubClassFeatures2014/Cleric/ClericNatureFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Cleric/ClericNatureFeatures.py): Master of Nature (3)
- [SubClassFeatures2014/Fighter/FighterRuneKnightFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Fighter/FighterRuneKnightFeatures.py): Great Stature (3), Master of Runes (3), Runic Juggernaut (3)
- [SubClassFeatures2014/Fighter/FighterSamuraiFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Fighter/FighterSamuraiFeatures.py): Tireless Spirit (3)
- [SubClassFeatures2014/Paladin/PaladinConquestFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Paladin/PaladinConquestFeatures.py): Aura of Conquest Expansion (3)
- [SubClassFeatures2014/Paladin/PaladinOathbreakerFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Paladin/PaladinOathbreakerFeatures.py): Aura of Hate Expansion (3)
- [SubClassFeatures2014/Paladin/PaladinRedemptionFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Paladin/PaladinRedemptionFeatures.py): Aura of the Guardian Expansion (3)
- [SubClassFeatures2014/Sorcerer/SorcererDivineSoulFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Sorcerer/SorcererDivineSoulFeatures.py): Divine Magic (3)
- [ClassFeatures/Bard/BardFeatures.py](../CharacterContent/Features/ClassFeatures/Bard/BardFeatures.py): Font of Inspiration (2)
- [SubClassFeatures2014/Monk/MonkKenseiFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Monk/MonkKenseiFeatures.py): Magic Kensei Weapons (2)
- [SubClassFeatures2014/Warlock/WarlockTheGenieFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Warlock/WarlockTheGenieFeatures.py): Limited Wish (2), Sanctuary Vessel (2)

</details>

<details><summary>Trigger fact with no trigger and no reason (181), each with its rank</summary>

- [ClassFeatures/Monk/MonkFeatures.py](../CharacterContent/Features/ClassFeatures/Monk/MonkFeatures.py): Stunning Strike (8), Evasion (7), Disciplined Survivor (4)
- [ClassFeatures/Barbarian/BarbarianFeatures.py](../CharacterContent/Features/ClassFeatures/Barbarian/BarbarianFeatures.py): Reckless Attack (7), Brutal Strike (6), Instinctive Pounce (3)
- [ClassFeatures/Rogue/RogueFeatures.py](../CharacterContent/Features/ClassFeatures/Rogue/RogueFeatures.py): Evasion (7), Uncanny Dodge (7), Cunning Strike (6)
- [ClassFeatures/Cleric/ClericFeatures.py](../CharacterContent/Features/ClassFeatures/Cleric/ClericFeatures.py): Divine Strike (6), Improved Potent Spellcasting (4), Sear Undead (4)
- [ClassFeatures/Druid/DruidFeatures.py](../CharacterContent/Features/ClassFeatures/Druid/DruidFeatures.py): Primal Strike (6)
- [ClassFeatures/Paladin/PaladinFeatures.py](../CharacterContent/Features/ClassFeatures/Paladin/PaladinFeatures.py): Radiant Strikes (6), Restoring Touch (4)
- [CombatFeatures/Maneuvers.py](../CharacterContent/Features/CombatFeatures/Maneuvers.py): Riposte (6), Goading Attack (5), Pushing Attack (5)
- [SubClassFeatures/Barbarian/BarbarianPathOfTheBerserkerFeatures.py](../CharacterContent/Features/SubClassFeatures/Barbarian/BarbarianPathOfTheBerserkerFeatures.py): Frenzy (6)
- [SubClassFeatures/Bard/BardLoreFeatures.py](../CharacterContent/Features/SubClassFeatures/Bard/BardLoreFeatures.py): Cutting Words (6), Peerless Skill (4)
- [SubClassFeatures/Druid/DruidStarsFeatures.py](../CharacterContent/Features/SubClassFeatures/Druid/DruidStarsFeatures.py): Starry Form (6)
- [SubClassFeatures/Monk/MonkOpenHandFeatures.py](../CharacterContent/Features/SubClassFeatures/Monk/MonkOpenHandFeatures.py): Open Hand Technique (6), Quivering Palm (5), Fleet Step (3)
- [SubClassFeatures/Paladin/PaladinVengeanceFeatures.py](../CharacterContent/Features/SubClassFeatures/Paladin/PaladinVengeanceFeatures.py): Vow of Enmity (6)
- [SubClassFeatures/Ranger/RangerFeyWandererFeatures.py](../CharacterContent/Features/SubClassFeatures/Ranger/RangerFeyWandererFeatures.py): Dreadful Strikes (6)
- [SubClassFeatures/Ranger/RangerHunterFeatures.py](../CharacterContent/Features/SubClassFeatures/Ranger/RangerHunterFeatures.py): Colossus Slayer (6)
- [SubClassFeatures/Barbarian/BarbarianPathOfTheSpiritualGuardianFeatures.py](../CharacterContent/Features/SubClassFeatures/Barbarian/BarbarianPathOfTheSpiritualGuardianFeatures.py): Spirits' Fury (5), Spirit Shield (4)
- [SubClassFeatures/Bard/BardGlamourFeatures.py](../CharacterContent/Features/SubClassFeatures/Bard/BardGlamourFeatures.py): Beguiling Magic (5)
- [SubClassFeatures/Cleric/ClericArcanaFeatures.py](../CharacterContent/Features/SubClassFeatures/Cleric/ClericArcanaFeatures.py): Modify Magic (5), Dispelling Recovery (2)
- [SubClassFeatures/Cleric/ClericShadowFeatures.py](../CharacterContent/Features/SubClassFeatures/Cleric/ClericShadowFeatures.py): Devouring Plague (5), Dispersion (4)
- [SubClassFeatures/Fighter/FighterArcaneArcherFeatures.py](../CharacterContent/Features/SubClassFeatures/Fighter/FighterArcaneArcherFeatures.py): Bursting Shot (5), Curving Shot (5), Masterful Shots (5), Indomitable Teleport (2)
- [SubClassFeatures/Fighter/FighterEldritchKnightFeatures.py](../CharacterContent/Features/SubClassFeatures/Fighter/FighterEldritchKnightFeatures.py): Eldritch Strike (5), Improved War Magic (3), War Magic (3), Arcane Charge (2)
- [SubClassFeatures/Fighter/FighterPsiWarriorFeatures.py](../CharacterContent/Features/SubClassFeatures/Fighter/FighterPsiWarriorFeatures.py): Psionic Power (5), Telekinetic Adept (5)
- [SubClassFeatures/Fighter/FighterSorrowKnightFeatures.py](../CharacterContent/Features/SubClassFeatures/Fighter/FighterSorrowKnightFeatures.py): Despairing Strikes (5), Dreaded Appearance (5), Grieving Mantle (4), Grim Constitution (4)
- [SubClassFeatures/Monk/MonkMercyFeatures.py](../CharacterContent/Features/SubClassFeatures/Monk/MonkMercyFeatures.py): Hand of Harm (5)
- [SubClassFeatures/Monk/MonkMysticArtsFeatures.py](../CharacterContent/Features/SubClassFeatures/Monk/MonkMysticArtsFeatures.py): Focused Strike (5), Improved Mystic Fighting Style (3), Mystic Fighting Style (3)
- [SubClassFeatures/Monk/MonkMysticBrewsFeatures.py](../CharacterContent/Features/SubClassFeatures/Monk/MonkMysticBrewsFeatures.py): Drunken Technique (5), Intoxicated Frenzy (5), Tipsy Sway (5)
- [SubClassFeatures/Paladin/PaladinEbonBladeFeatures.py](../CharacterContent/Features/SubClassFeatures/Paladin/PaladinEbonBladeFeatures.py): Runic Mastery (5), Runic Power (5), Runic Strikes (5)
- [SubClassFeatures/Paladin/PaladinGeniesFeatures.py](../CharacterContent/Features/SubClassFeatures/Paladin/PaladinGeniesFeatures.py): Elemental Smite (5)
- [SubClassFeatures/Paladin/PaladinGloryFeatures.py](../CharacterContent/Features/SubClassFeatures/Paladin/PaladinGloryFeatures.py): Glorious Defense (5), Inspiring Smite (4)
- [SubClassFeatures/Ranger/RangerDemonHunterFeatures.py](../CharacterContent/Features/SubClassFeatures/Ranger/RangerDemonHunterFeatures.py): Soul Fragments (5), Torment (5)
- [SubClassFeatures/Rogue/RoguePhantomFeatures.py](../CharacterContent/Features/SubClassFeatures/Rogue/RoguePhantomFeatures.py): Wails from the Grave (5)
- [SubClassFeatures/Rogue/RogueSwashbucklerFeatures.py](../CharacterContent/Features/SubClassFeatures/Rogue/RogueSwashbucklerFeatures.py): Master Duelist (5), Fancy Footwork (4)
- [SubClassFeatures/Warlock/WarlockCelestialFeatures.py](../CharacterContent/Features/SubClassFeatures/Warlock/WarlockCelestialFeatures.py): Searing Vengeance (5), Celestial Resilience (4)
- [SubClassFeatures/Wizard/WizardEnchanterFeatures.py](../CharacterContent/Features/SubClassFeatures/Wizard/WizardEnchanterFeatures.py): Alter Memories (5), Instinctive Charm (5), Split Enchantment (5)
- [SubClassFeatures/Wizard/WizardNecromancerFeatures.py](../CharacterContent/Features/SubClassFeatures/Wizard/WizardNecromancerFeatures.py): Death's Master (5), Necromancy Spellbook (2)
- [SubClassFeatures2014/Barbarian/BarbarianPathOfTheAncestralGuardianFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Barbarian/BarbarianPathOfTheAncestralGuardianFeatures.py): Ancestral Protectors (5), Vengeful Ancestors (5), Spirit Shield (4)
- [SubClassFeatures2014/Barbarian/BarbarianPathOfTheBattleragerFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Barbarian/BarbarianPathOfTheBattleragerFeatures.py): Spiked Retribution (5), Reckless Abandon (4)
- [SubClassFeatures2014/Barbarian/BarbarianPathOfTheStormHeraldFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Barbarian/BarbarianPathOfTheStormHeraldFeatures.py): Raging Storm (5)
- [SubClassFeatures2014/Barbarian/BarbarianPathOfWildMagicFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Barbarian/BarbarianPathOfWildMagicFeatures.py): Unstable Backlash (5), Wild Surge (5)
- [SubClassFeatures2014/Bard/BardCreationFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Bard/BardCreationFeatures.py): Mote of Potential (5)
- [SubClassFeatures2014/Bard/BardSwordsFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Bard/BardSwordsFeatures.py): Blade Flourish (5), Master's Flourish (4)
- [SubClassFeatures2014/Bard/BardWhispersFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Bard/BardWhispersFeatures.py): Psychic Blades (5), Words of Terror (5), Mantle of Whispers (2)
- [SubClassFeatures2014/Cleric/ClericDeathFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Cleric/ClericDeathFeatures.py): Channel Divinity: Touch of Death (5)
- [SubClassFeatures2014/Cleric/ClericOrderFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Cleric/ClericOrderFeatures.py): Order's Wrath (5), Voice of Authority (2)
- [SubClassFeatures2014/Cleric/ClericPeaceFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Cleric/ClericPeaceFeatures.py): Protective Bond (5)
- [SubClassFeatures2014/Cleric/ClericTempestFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Cleric/ClericTempestFeatures.py): Thunderous Strike (5), Wrath of the Storm (5), Channel Divinity: Destructive Wrath (3)
- [SubClassFeatures2014/Druid/DruidSporesFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Druid/DruidSporesFeatures.py): Halo of Spores (5), Spreading Spores (5), Fungal Infestation (3)
- [SubClassFeatures2014/Druid/DruidWildfireFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Druid/DruidWildfireFeatures.py): Cauterizing Flames (5), Blazing Revival (4)
- [SubClassFeatures2014/Fighter/FighterCavalierFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Fighter/FighterCavalierFeatures.py): Ferocious Charger (5), Unwavering Mark (5), Warding Maneuver (4)
- [SubClassFeatures2014/Fighter/FighterEchoKnightFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Fighter/FighterEchoKnightFeatures.py): Unleash Incarnation (5), Reclaim Potential (4), Shadow Martyr (4)
- [SubClassFeatures2014/Fighter/FighterSamuraiFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Fighter/FighterSamuraiFeatures.py): Rapid Strike (5), Strength Before Death (3), Tireless Spirit (3)
- [SubClassFeatures2014/Monk/MonkDrunkenMasterFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Monk/MonkDrunkenMasterFeatures.py): Tipsy Sway (5), Drunkard's Luck (4), Drunken Technique (4), Intoxicated Frenzy (4)
- [SubClassFeatures2014/Monk/MonkKenseiFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Monk/MonkKenseiFeatures.py): Deft Strike (5), Agile Parry (4), Unerring Accuracy (4)
- [SubClassFeatures2014/Monk/MonkSunSoulFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Monk/MonkSunSoulFeatures.py): Searing Arc Strike (5), Sun Shield (5)
- [SubClassFeatures2014/Paladin/PaladinConquestFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Paladin/PaladinConquestFeatures.py): Scornful Rebuke (5), Channel Divinity: Guided Strike (4)
- [SubClassFeatures2014/Paladin/PaladinRedemptionFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Paladin/PaladinRedemptionFeatures.py): Channel Divinity: Rebuke the Violent (5), Protective Spirit (4), Aura of the Guardian (3)
- [SubClassFeatures2014/Paladin/PaladinWatchersFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Paladin/PaladinWatchersFeatures.py): Vigilant Rebuke (5)
- [SubClassFeatures2014/Ranger/RangerMonsterSlayerFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Ranger/RangerMonsterSlayerFeatures.py): Magic-User's Nemesis (5), Slayer's Counter (5), Supernatural Defense (4)
- [SubClassFeatures2014/Ranger/RangerSwarmkeeperFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Ranger/RangerSwarmkeeperFeatures.py): Gathered Swarm (5), Swarming Dispersal (4)
- [SubClassFeatures2014/Rogue/RogueMastermindFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Rogue/RogueMastermindFeatures.py): Misdirection (5), Insightful Manipulator (2)
- [SubClassFeatures2014/Rogue/RogueScoutFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Rogue/RogueScoutFeatures.py): Sudden Strike (5), Skirmisher (2)
- [SubClassFeatures2014/Sorcerer/SorcererStormSorceryFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Sorcerer/SorcererStormSorceryFeatures.py): Heart of the Storm (5), Storm's Fury (5)
- [SubClassFeatures2014/Warlock/WarlockHexbladeFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Warlock/WarlockHexbladeFeatures.py): Accursed Specter (5), Master of Hexes (5), Armor of Hexes (4)
- [SubClassFeatures2014/Warlock/WarlockTheGenieFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Warlock/WarlockTheGenieFeatures.py): Genie's Vessel (5)
- [SubClassFeatures2014/Wizard/WizardGraviturgyFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Wizard/WizardGraviturgyFeatures.py): Event Horizon (5), Gravity Well (5), Violent Attraction (5)
- [CharacterFeats/OriginFeats.py](../CharacterContent/Features/CharacterFeats/OriginFeats.py): Savage Attacker (4)
- [ClassFeatures/Bard/BardFeatures.py](../CharacterContent/Features/ClassFeatures/Bard/BardFeatures.py): Countercharm (4)
- [ClassFeatures/Fighter/FighterFeatures.py](../CharacterContent/Features/ClassFeatures/Fighter/FighterFeatures.py): Studied Attacks (4), Tactical Master (4), Tactical Mind (3), Tactical Shift (3)
- [SubClassFeatures/Fighter/FighterBanneretFeatures.py](../CharacterContent/Features/SubClassFeatures/Fighter/FighterBanneretFeatures.py): Group Recovery (4), Shared Resilience (4), Team Tactics (4), Rallying Surge (3)
- [SubClassFeatures/Paladin/PaladinHolyFeatures.py](../CharacterContent/Features/SubClassFeatures/Paladin/PaladinHolyFeatures.py): Infusion of Light (4), Lightbringer's Aura (4)
- [SubClassFeatures/Warlock/WarlockVestigeFeatures.py](../CharacterContent/Features/SubClassFeatures/Warlock/WarlockVestigeFeatures.py): Vestige Recovery (4)
- [SubClassFeatures/Wizard/WizardConjurerFeatures.py](../CharacterContent/Features/SubClassFeatures/Wizard/WizardConjurerFeatures.py): Durable Summons (4), Splintered Summons (3)
- [SubClassFeatures2014/Bard/BardEloquenceFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Bard/BardEloquenceFeatures.py): Infectious Inspiration (4), Unfailing Inspiration (4)
- [SubClassFeatures2014/Cleric/ClericNatureFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Cleric/ClericNatureFeatures.py): Dampen Elements (4)
- [SubClassFeatures2014/Cleric/ClericTwilightFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Cleric/ClericTwilightFeatures.py): Channel Divinity: Twilight Sanctuary (4)
- [SubClassFeatures2014/Druid/DruidShepherdFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Druid/DruidShepherdFeatures.py): Faithful Summons (4), Guardian Spirit (4)
- [SubClassFeatures2014/Fighter/FighterRuneKnightFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Fighter/FighterRuneKnightFeatures.py): Runic Shield (4)
- [SubClassFeatures2014/Monk/MonkLongDeathFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Monk/MonkLongDeathFeatures.py): Mastery of Death (4), Touch of Death (4)
- [SubClassFeatures2014/Ranger/RangerHorizonWalkerFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Ranger/RangerHorizonWalkerFeatures.py): Spectral Defense (4)
- [SubClassFeatures2014/Rogue/RogueSwashbucklerFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Rogue/RogueSwashbucklerFeatures.py): Fancy Footwork (4), Master Duelist (4)
- [SubClassFeatures2014/Sorcerer/SorcererDivineSoulFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Sorcerer/SorcererDivineSoulFeatures.py): Empowered Healing (4), Favored by the Gods (4)
- [SubClassFeatures2014/Warlock/WarlockFathomlessFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Warlock/WarlockFathomlessFeatures.py): Guardian Coil (4)
- [SubClassFeatures2014/Warlock/WarlockTheUndyingFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Warlock/WarlockTheUndyingFeatures.py): Defy Death (4)
- [SubClassFeatures2014/Wizard/WizardOrderOfScribesFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Wizard/WizardOrderOfScribesFeatures.py): One with the Word (4)
- [SubClassFeatures/Wizard/WizardTransmuterFeatures.py](../CharacterContent/Features/SubClassFeatures/Wizard/WizardTransmuterFeatures.py): Empowered Transmutation (3)
- [SubClassFeatures2014/Paladin/PaladinCrownFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Paladin/PaladinCrownFeatures.py): Divine Allegiance (3)
- [SubClassFeatures2014/Wizard/WizardChronurgyFeatures.py](../CharacterContent/Features/SubClassFeatures2014/Wizard/WizardChronurgyFeatures.py): Arcane Abeyance (3), Chronal Shift (3), Convergent Future (3)
- [SubClassFeatures/Ranger/RangerBeastMasterFeatures.py](../CharacterContent/Features/SubClassFeatures/Ranger/RangerBeastMasterFeatures.py): Share Spells (2)
- [ClassFeatures/Sorcerer/SorcererFeatures.py](../CharacterContent/Features/ClassFeatures/Sorcerer/SorcererFeatures.py): Sorcerous Restoration (1)

</details>

## 7. Always-on traits the rolls don't count

Save and attack rolls take their modifiers from rules conditions, cover and
badges only (`modifiers_on`, [Combat/Effects/modifiers.py:181](../Combat/Effects/modifiers.py#L181)).
A feature has no always-on equivalent of a badge's modifiers: `Feature` has
`combat_effects`, `adjust_combat_effect` and `movement` only
([Model/Content/Feature.py:399-430](../Model/Content/Feature.py#L399-L430)).
Monster traits are the same: the structured `MagicResistance`, `PackTactics`,
`Regeneration`, `SunlightSensitivity`, `Rampage`, `NimbleEscape`,
`TinySwarm`, `SiegeMonster` and `Illumination` classes exist in
`Model/Creatures/MonsterAbilities.py`, but no file in `Combat/Fight`,
`Combat/Effects`, `Combat/CombatUIQt` or `Combat/Arena` reads them (Flyby and
Pounce are read by name).

| Rank | Trait | What isn't counted | Where it appears |
|---|---|---|---|
| 9 | Magic Resistance | Advantage on saves against spells | 13 structured + 61 freeform monsters |
| 8 | Pack Tactics | Advantage on attacks with an ally within 5 feet of the target (the map knows the distance) | 14 structured + 8 freeform monsters |
| 8 | Aura of Protection | + Charisma modifier to saves of allies within 10 feet (**Engine**: the map knows the distance) | Paladin 6 |
| 7 | Regeneration | Hit Points at the start of its turn, stopped by some damage types | 1 structured + 10 freeform monsters |
| 7 | War Caster | Advantage on Concentration saves | Clover (§5) |
| 7 | Evasion | no damage on a successful Dexterity save for half, half on a failure | Monk, Rogue |
| 7 | Uncanny Dodge | halve an attack's damage (Reaction) | Rogue |
| 6 | Improved Critical | Critical Hit on 19-20 | Champion |
| 5 | Danger Sense | Advantage on Dexterity saves | Barbarian |
| 4 | Brave, Fey Ancestry, Dwarven Resilience | Advantage on saves against Frightened / Charmed / Poisoned | Halfling, Elf, Khoravar, Dwarf |
| 3 | Savage Attacker, Great Weapon Fighting | reroll damage dice | feat, fighting style |
| 3 | Sunlight Sensitivity | Disadvantage in sunlight | 4 monsters |
| 3 | Nimble Escape, Rampage, Tiny Swarm, Siege Monster, Illumination | Bonus Action Disengage/Hide, a move and bite after a kill, swarm rules, double damage to objects, light | 1-4 monsters each |

Suggestion: an always-on `modifiers(character)` on `Feature` and on
`MonsterAbility`, read by `modifiers_on` beside the badges, as `movement()`
already is for the battle map. That one hook covers most of this table
(Regeneration as an `AtTurnStart`).

## 8. Monster abilities

Monster abilities use the same `CombatEffect` model. A plain
`MonsterAbility(name, description)` with no `combat_effects` is read from its
text at runtime: attacks, and riders in a sentence of their own (6.4). Some
are traits with nothing to apply.

| Rank | File | Abilities | Structured subclass | Plain, with effects | Freeform |
|---|---|---|---|---|---|
| 5 | `monsters.py` (generated, official) | 2,194 | 291 | 775 | 1,128 |
| 6 | `monsters_homebrew.py` | 204 | 65 | 37 | 102 |

Official monsters can't be hand-edited (`generate_monsters.py` overwrites
them); their freeform abilities need the generator or the runtime reading
(Q47). The homebrew ones are used in the campaigns and can be converted (the
`monster-ability-converter` agent). Heuristic ranks below: Multiattack,
Legendary Resistance or a save 6, damage 5, a modifier 4, other traits 2,
+1 for Recharge. DI-109 and DI-110 cover the homebrew save prose and
save-rolling traits; DI-061 is Mira's 6 abilities.

<details><summary>Homebrew abilities with no combat effects (102), each with its rank</summary>

- **CR 0 FreshAccursed**: 1 x Mumbling the Curse (6)
- **CR 0 PhysicalAccursed**: Herd-Bound (6)
- **CR 0 ArmoredAccursed**: Herd-Bound (6)
- **CR 0 BrainBloatedAccursed**: Curse-Feeding Mind (6), Horde Retaliation (2)
- **CR 0 CurseHighAccursed**: Curse-Drunk Euphoria (6)
- **CR 0 HaratCR1_2**: Dwarven Resilience (6), Stubborn as Stone (6)
- **CR 0 DwarfLifeCleric**: Dwarven Resilience (6)
- **CR 0 ElfDruidOfTheLand**: Fey Ancestry (6)
- **CR 0 Child**: Just a Child (2)
- **CR 1 CommonCultist**: Fanatic's Surge (4), Marked for the Choir (4), Strength of the Faithful Mob (4), Zealous Communion (4)
- **CR 1 AccursedGroupOf3**: Grab (6), Multiattack (6), Rush (2)
- **CR 1 CurseCracked**: Unstable Vessel (5), Fractured Step (2)
- **CR 1 CurseBodyBroken**: Scream of the Trapped (Recharge 5-6) (7), Still Me (6), Impossible Anatomy (5)
- **CR 1 CurseMindBroken**: Memory Shatter (Recharge 5-6) (7), Broken Mind (6), Leaking Curse (5)
- **CR 1 HaratCR1**: Dwarven Resilience (6), Stubborn as Stone (6), Shield of Stonehill (4)
- **CR 1 GreypawCR1**: Keen Hearing and Smell (2), Relentless Tracker (2)
- **CR 1 GoblinKingCR1**: Redirect Attack (2), Royal Command (2)
- **CR 1 OrcAssassin**: Assassinate and Sneak Attack (5), Cunning Action (2), Relentless Endurance (1/Day) (2)
- **CR 2 PriestOfTheBlackTongues**: Spellcasting (6), Curse-Marked (5), Black Tongue (4), Command the Accursed (2)
- **CR 2 SisterLumenBellWardenOfStillChoirs**: Interrupting Chime (1/Day) (6), Attuned to the Choir (4), Sign of the Covered Mouth (2), Vow of the Cut Tongue (2)
- **CR 2 AccursedGroupOf5**: Grab (6), Multiattack (6), Rush (2)
- **CR 2 HaratCR2**: Dwarven Resilience (6), Stubborn as Stone (6), Shield of Stonehill (4), Too Stubborn to Fall (1/Day) (2)
- **CR 2 GreypawCR2**: Keen Hearing and Smell (2), Relentless Tracker (2)
- **CR 3 CantorOfTheBlackChoir**: Blackened Choir (5), Brink of the Accursed (5), Conduct the Choir (2)
- **CR 3 GarronTheKindly**: Field Surgeon (4), The Reliquary of Voices (4), Unshaken Conviction (2)
- **CR 3 SerCaldusTheVowOfSilence**: Rite of Silence (3/Day) (6), Silent Guard (6), Vow of Silence (6), Undying Vow (1/Day) (5), Names Unspoken (4)
- **CR 3 GreypawCR3**: Bloodied Frenzy (2), Keen Hearing and Smell (2), Relentless Tracker (2)
- **CR 3 MirelleTheGildedKnight**: Royal Resolve (1/Day) (6)
- **CR 4 MarshalVirel**: Multiattack (6), Wordless Coordination (6), Kill the Scream (4), Parry (2), Signal to Strike (2)
- **CR 4 GoblinKingCR4**: Royal Command (2)
- **CR 5 TheChoirmasterOfHollowHymns**: Legendary Resistance (1/Day) (6), Throat-Strain (6), Curse-Marked (5), Hollow Hymn (4)
- **CR 5 MiraPrincessOfTheLoop**: Fractured Timeline (6)
- **CR 6 TheMouthThatWalks**: The Ceaseless Litany (5), Verge of Unmaking (5)
- **CR 6 TheHunter**: Unnerving Calm (6), Cursebound (5), Curse Sense (4), Predator's Reflexes (2)
- **CR 7 TheCrownWithoutAKing**: Coronation (Recharge 5-6) (7), Command the Accursed (2), Discorporate (2)
- **CR 7 TheRoadChoir**: Directions to Salvation (Recharge 5-6) (7), A Hundred Anchors (6), The Long List (6), Endless Reknitting (5)
- **CR 9 TheBellSaint**: Toll of Rising (Recharge 5-6) (7), Muffled Toll (Costs 2 Actions) (6), Undying Vigil (6), Drag (Costs 1 Action) (2)
- **CR 15 TheHeadlessDragon**: Frightful Presence (6), Grasping Hands (6), Wing Buffet (Costs 2 Actions) (6), Cursed Regeneration (5), Detect (2), Sigil of Silence (2)

</details>

## 9. Items

No item class in `CharacterContent/Items` has `combat_effects`, and nothing in
`Combat/Fight`, `Combat/CombatUIQt` or `Combat/PlayerCombatant.py` reads a
character's items other than its weapons.

| Rank | Items | What's missing | Kind |
|---|---|---|---|
| 7 | Potions of Healing (4 sizes) | no row: drinking one is healed by hand | **Field**: items need a `combat_effects()` and a picker section, as features have |
| 5 | Other potions (13): Invisibility, Speed, Resistance, Enlarge, Guarding, Resolve, ... | no row | as above |
| 5 | 17 magic weapons with riders only in their text: Vampiric Edge's healing, Sulvesburg's Folly's Prone save, Bloodlust Blade's Advantage, Rampaging Blade's and Moradin's Wrath's stacks, A Hushed Bell, Lightning, Thunder, The Storm, ... | the weapon row deals its fixed `extra_damage` (Flame Tongue's 2d6 Fire is counted); everything else is the tooltip | **Field**: a weapon's own rider rows, as Weapon Mastery has |
| 4 | Magic armor (4): Dragonscale Plate's Resistance, Stalwart's Aegis's save Advantage, Shadowplate Mail, Veteran's Chain Shirt | text only (AC from the sheet is counted) | §7's always-on modifier |
| 4 | Wondrous items (19): Cloak of Protection, Bracers of Archery, Gauntlets of Strength, Button of Noble Sacrifice, ... | sheet bonuses are counted; any activated effect is text | **Field** |
| 3 | Scrolls (2), Poisons (1) | no row | **Field** |

## 10. Summons

`SPELL_SUMMONS` in [CharacterContent/Summons/SpellSummons.py](../CharacterContent/Summons/SpellSummons.py)
is empty ("Filled in by the plan's Phase 4 steps"), so no summon spell (Find
Familiar, Summon Beast, Conjure Animals, Animate Dead, Spiritual Weapon's
force, ...) brings a combatant with its stat block. Rank 6. Class companions
(Steel Defender, Drake Companion, Reanimated Companion) are built elsewhere
(`Combat/Fight/summons.py`). DI-108 covers the catalog's 2024 summon stat
blocks having no combat effects.

## 11. Rules conditions: parts that are only notes

`CONDITION_RULES` ([Model/Content/RulesConditions.py](../Model/Content/RulesConditions.py))
counts each condition's roll modifiers, Speed 0, auto-fails and Resistance.
These parts are `Note`s:

| Rank | Condition | Note only | Kind |
|---|---|---|---|
| 5 | Exhaustion | Speed 5 feet lower per level (its D20 penalty is counted) | **Now**: a per-level `Speed`, or a `bonus` worked out from the level |
| 4 | Frightened | can't willingly move closer to the source | **Engine** (the map could refuse the move) |
| 4 | Charmed | can't attack or target the charmer with harmful effects | **Engine** (the dialog could warn) |
| 4 | Invisible | Concealed: unaffected by effects that need a seen target | DI-101 |
| 3 | Unconscious | drops what it holds; stays Prone when it ends | DI-067 |
| 3 | Grappled | the grappler drags it at extra cost | **Engine** |
| 2 | Incapacitated | can't speak | **Table** |
| 2 | Prone | crawl only, or half its Speed to stand | check the map (`Movement.stands_up_ft` exists) |

## 12. Tooling findings

- (rank 3) `stats` marks Cunning Action's and Step of the Wind's Dash notes
  **NOTE ONLY**, but the battle map already counts Dash and Disengage
  (`Combat/Arena/arena.py`, `movement_ft` and the Disengage badge). The tool
  doesn't know those badges by name, so these are false alarms.
- (rank 4) `notes` groups by the first words, so it misses repeated rules
  worded differently: "ends early" (§4.2, 12+ sources), "can deal X damage
  instead" (§4.9, 3), "sheds light" (§4.6, 4), creature-type gates (§4.3, 7).
- (rank 5) `features`/`triggers`/`coverage` only cover party members (§1).
- `compare` (described spells against the text reading) shows only
  differences made on purpose, except Enlarge/Reduce's missing save (§4.14).

## 13. Related open issues (Notes/discovered-issues.md)

DI-073 (a non-concentration badge outlasts its duration), DI-078 (a later
step can't upcast without a slot), DI-079 (hand-given badge keeps modifiers
past concentration), DI-095 (pushes still in text), DI-098 (Fly/Swim Speeds
from other sources are text), DI-099 (spell light doesn't light Darkness),
DI-101 (Invisible targets not warned about), DI-108 (2024 summon stat blocks
have no effects), DI-109 / DI-110 (homebrew and trait saves with no effects).
