# Core Features Report

A "core feature" here means a `Feature` class that is the **target** of at least one
`parent.extend_feature(child())` call somewhere in the codebase — i.e. a feature that some later
class/subclass feature hooks into, upgrades, or draws resources from. This is the mirror image of
`Notes/feature-extension-audit.md`, which tracked the *riders*; this report tracks their *parents*.
Riders (`Rage → Frenzy`, `BardicInspiration → CuttingWords`, etc.) are intentionally excluded unless
a rider is itself later extended by something else, in which case it also gets its own row.

Compiled by grepping every `.extend_feature(...)` call site across `CharacterContent/Classes/`
(base classes + `SubClasses2014/` + `SubClasses2024/`), cross-referenced against
`Notes/feature-extension-audit.md`, then verifying each feature's limited-use numbers against the
raw rules text in `SourceTexts/ClassTexts/` and `SourceTexts/SubclassTexts2014|2024/`.

**Number of Uses** column key:
- A concrete number/formula = a genuine limited-use resource (uses per Long/Short Rest, a point
  pool, a die pool, etc.), sourced against the rulebook text.
- "N/A — passive/unlimited" = the feature is always-on or has no charge/use tracking.
- "Draws from `<OtherFeature>`" = the feature doesn't have its own pool; it spends uses from
  another core feature's pool (e.g. many subclass Channel Divinity options spend the base
  `ChannelDivinity` uses rather than tracking their own).

---

## Artificer

| Feature | Introduced | Description | Number of Uses |
|---|---|---|---|
| `ReplicateMagicItem` | Artificer (base), Level 2 | Craft temporary magic items from known plans using Tinker's Tools, recreated after each Long Rest. | Cap on items held at once: 2 at level 2, 3 at level 6, 4 at level 10, 5 at level 14, 6 at level 18. *(SourceTexts/ClassTexts/artificer.txt)* |
| `FlashofGenius` | Artificer (base), Level 7 | Reaction to add your Intelligence modifier to a failed ability check or saving throw within 30 feet. | Intelligence modifier (min 1) uses per Long Rest. *(SourceTexts/ClassTexts/artificer.txt)* Riders: `AdvancedArtifice` (L15) regains 1 use/Short Rest; `SoulOfArtifice` (L20) regains all uses/Short Rest while attuned. |
| `ArcaneArmor` | Artificer — Armorer (2014), Level 3 | Turn worn armor into Arcane Armor: no Strength requirement, usable as a spellcasting focus, can't be removed against your will. | N/A — passive/unlimited. |
| `ArmorModel` | Artificer — Armorer (2014 & 2024), Level 3 | Customize Arcane Armor into Guardian, Infiltrator, or (2024) Dreadnaught, each granting a special weapon and perk. | N/A on the choice itself; individual model perks carry their own separate pools (e.g. Defensive Field = proficiency-bonus uses/Long Rest). |
| `EldritchCannon` | Artificer — Artillerist (2014 & 2024), Level 3 | Magic action to summon a Small/Tiny cannon that can Flamethrower, Force Ballista, or Protector each turn. | 1 cannon per Long Rest, renewable early by expending a spell slot. *(SourceTexts/SubclassTexts2024/artillerist.txt)* `FortifiedPosition` (L15) raises the cap to two cannons at once. |
| `ArcaneJolt` | Artificer — Battle Smith (2014 & 2024), Level 9 | Channel magic through a hit (yours or your Steel Defender's) to deal +2d6 Force damage or heal 2d6 HP. | Intelligence modifier (min 1) uses per Long Rest, max once/turn. *(SourceTexts/SubclassTexts2024/battle_smith.txt)* `ImprovedDefender` (L15) raises the dice to 4d6. |
| `CartographerSpells` | Artificer — Cartographer (2024), Level 3 | Always-prepared subclass spell list that expands at levels 5, 9, 13, 17. | N/A — passive/unlimited. |
| `AdventurersAtlas` | Artificer — Cartographer (2024), Level 3 | Create linked magical maps that grant initiative and mutual-targeting benefits to carriers. | 1 map-set per Long Rest; recipients scale with 1 + Intelligence modifier (min 2). |
| `ReanimatedCompanion` | Artificer — Reanimator (2024), Level 3 | Magic action to animate an undead companion that fights alongside you. | 1 companion per Long Rest, renewable early by expending a spell slot. *(SourceTexts/SubclassTexts2024/reanimator.txt)* |

## Barbarian

| Feature | Introduced | Description | Number of Uses |
|---|---|---|---|
| `Rage` | Barbarian (base), Level 1 | Bonus action to enter a Rage: resistance to bludgeoning/piercing/slashing, advantage on Strength checks/saves, bonus damage on Strength attacks. | 2 uses at L1–2, 3 at L3–5, 4 at L6–11, 5 at L12–16, 6 at L17–20. Regain 1 on Short Rest, all on Long Rest. *(SourceTexts/ClassTexts/barbarian.txt)* |
| `RecklessAttack` | Barbarian (base), Level 2 | Trade defense for offense: advantage on Strength attacks this turn, but attacks against you also gain advantage. | N/A — passive/unlimited. |
| `UnarmoredDefenseText` | Barbarian (base), Level 1 | While unarmored, AC = 10 + Dex mod + Con mod (a Shield can still be used). | N/A — passive/unlimited. |
| `BattleragerArmor` | Barbarian — Path of the Battlerager (2014), Level 3 | While raging in spiked armor, make a bonus-action armor-spike attack and deal bonus piercing damage on grapples. | N/A — passive/unlimited (tied to being in Rage). |

## Bard

| Feature | Introduced | Description | Number of Uses |
|---|---|---|---|
| `BardicInspiration` | Bard (base), Level 1 | Bonus action to give an ally a die they can add to one failed d20 Test within the hour. | Charisma modifier (min 1) uses per Long Rest. Die: d6 (L1–4) → d8 (5–9) → d10 (10–14) → d12 (15+). *(SourceTexts/ClassTexts/bard.txt)* Riders: `FontOfInspiration` (L5) — regain on Short *or* Long Rest, or spend a spell slot for 1 use; `SuperiorInspiration` (L18) — regain up to 2 on rolling Initiative. |
| `PerformanceOfCreation` | Bard — College of Creation (2014), Level 3 | Action to conjure a temporary nonmagical item (value capped by Bard level). | 1 use per Long Rest, or spend a 2nd-level+ spell slot to reuse. *(SourceTexts/SubclassTexts2014/creation.txt)* Size cap grows at L6 (Large), L14 (Huge); `CreativeCrescendo` (L14) allows Charisma-modifier (min 2) simultaneous items. |
| `BladeFlourish` | Bard — College of Swords (2014), Level 3 | Attacking grants +10 ft speed for the turn; a hit lets you spend a Bardic Inspiration die for a flourish effect. | N/A of its own — spends `BardicInspiration` uses. `MastersFlourish` (L14) lets you roll a free d6 instead. |
| `SpiritsFromBeyond` | Bard — College of Spirits (2024), Level 3 | Spend a Bardic Inspiration use to channel a spirit, then later unleash its effect on a target. | N/A of its own — draws from `BardicInspiration` pool. |

## Cleric

| Feature | Introduced | Description | Number of Uses |
|---|---|---|---|
| `ChannelDivinity` | Cleric (base), Level 2 | Channels divine energy to fuel Divine Spark (heal/damage), Turn Undead, and unlocked domain options. | 2 uses at L2, 3 at L6, 4 at L18. Regain 1 on Short Rest, all on Long Rest. *(SourceTexts/ClassTexts/cleric.txt)* Extended by base `SearUndead` (L5) plus 2024 domain options (Grave, Knowledge, Life, Light, Trickery, War). |
| `BlessedStrikes` | Cleric (base), Level 7 | Choose Divine Strike (extra weapon damage) or Potent Spellcasting (Wis mod to cantrip damage). | N/A — passive, once-per-turn trigger. Upgraded by `ImprovedBlessedStrikes` (L14). |
| `DivineIntervention` | Cleric (base), Level 10 | Cast any Cleric spell of 5th level or lower for free by calling on your deity. | 1 use, regains on Long Rest. `GreaterDivineIntervention` (L20) adds Wish as an option but only recharges after 2d4 Long Rests. |
| `ArcanaDomainSpells` | Cleric — Arcana Domain (2014), Level 1/3 | Fixed list of arcane-flavored spells always prepared. | N/A — passive/unlimited. |
| `TouchOfDeathChannelDivinity` | Cleric — Death Domain (2014), Level 3 | Channel Divinity option: melee hit deals extra necrotic damage (5 + 2× Cleric level). | Draws from `ChannelDivinity`. |
| `Reaper` | Cleric — Death Domain (2014), Level 3 | Learn a necromancy cantrip; single-target necromancy cantrips can hit a second adjacent creature. | N/A — passive/unlimited. |
| `SoulOfTheForge` | Cleric — Forge Domain (2014), Level 6 | Fire resistance and +1 AC while wearing heavy armor. | N/A — passive/unlimited. |
| `CharmAnimalsAndPlantsChannelDivinity` | Cleric — Nature Domain (2014), Level 3 | Channel Divinity option: charm beasts/plants in a 30-ft radius on a failed Wisdom save. | Draws from `ChannelDivinity`. |
| `DivineStrike` (Order) | Cleric — Order Domain (2014), Level 8 | Once per turn on a weapon hit, extra 1d8 psychic damage (2d8 at L14). | N/A — passive, once-per-turn trigger. |
| `EmboldeningBond` | Cleric — Peace Domain (2014), Level 3 | Bonds allies for 10 minutes; each can add a d4 to a roll per turn while near another bonded ally. | Uses = proficiency bonus, regain all on Long Rest. |
| `TwilightSanctuaryChannelDivinity` | Cleric — Twilight Domain (2014), Level 3 | Channel Divinity option: 30-ft dim-light sphere grants temp HP or removes charm/fear each turn. | Draws from `ChannelDivinity`. |
| `WardingFlare` | Cleric — Light Domain (2024), Level 3 | Reaction to impose Disadvantage on an attack roll against a creature you can see. | Wisdom modifier (min 1) uses, regain all on Long Rest. `ImprovedWardingFlare` (L6) adds Short-Rest recharge. |

## Druid

| Feature | Introduced | Description | Number of Uses |
|---|---|---|---|
| `WildShape` | Druid (base), Level 2 | Bonus action to shape-shift into a learned Beast form. | 2 uses at L2, 3 at L6, 4 at L17. Regain 1 on Short Rest, all on Long Rest. *(SourceTexts/ClassTexts/druid.txt)* Extended by `WildResurgence` (L5), `BeastSpells` (L18), `Archdruid` (L20). |
| `ElementalFury` | Druid (base), Level 7 | Choose Potent Spellcasting (Wis to cantrip damage) or Primal Strike (bonus elemental damage once/turn). | N/A — passive/unlimited. Upgraded by `ImprovedElementalFury` (L15). |
| `SymbioticEntity` | Druid — Circle of Spores (2014), Level 3 | Expend a Wild Shape use to awaken spores for temp HP and bonus necrotic damage for 10 minutes. | Draws from `WildShape`. |
| `SpiritTotem` | Druid — Circle of the Shepherd (2014), Level 3 | Bonus action to summon a spirit totem aura (Bear/Hawk/Unicorn) that buffs allies inside it. | 1 use, regain on Short or Long Rest. |
| `SummonWildfireSpirit` | Druid — Circle of Wildfire (2014), Level 3 | Expend a Wild Shape use to summon a fire-spirit companion instead of shapeshifting. | Draws from `WildShape`. |
| `CircleForms` | Druid — Circle of the Moon (2024), Level 3 | While Wild Shaped: raises max form CR, sets an AC floor, and grants extra temp HP. | N/A — passive/unlimited. |
| `MoonlightStep` | Druid — Circle of the Moon (2024), Level 10 | Bonus action to teleport 30 ft and gain advantage on the next attack. | Wisdom modifier (min 1) uses, regain all on Long Rest (or restore by burning a 2nd+ level spell slot). |
| `WrathOfTheSea` | Druid — Circle of the Sea (2024), Level 3 | Expend Wild Shape use(s) to manifest a cold-damage, push-effect ocean-spray Emanation. | Draws from `WildShape` (1, or 2 at higher level). |
| `StarryForm` | Druid — Circle of the Stars (2024), Level 3 | Expend a Wild Shape use to take a starry form with Archer/Chalice/Dragon constellation benefits. | Draws from `WildShape`. |

## Fighter

| Feature | Introduced | Description | Number of Uses |
|---|---|---|---|
| `SecondWind` | Fighter (base), Level 1 | Bonus action to heal 1d10 + Fighter level. | 2 uses at L1, 3 at L4, 4 at L10. Regain 1 on Short Rest, all on Long Rest. *(SourceTexts/ClassTexts/fighter.txt)* Extended by `TacticalMind` (L2), `TacticalShift` (L5). |
| `WeaponMastery` | Fighter (base), Level 1 | Use the mastery properties of a set number of weapon types, swappable on a Long Rest. | Weapons mastered: 3 at L1, 4 at L4, 5 at L10, 6 at L16 (not per-rest). Extended by `TacticalMaster` (L9). |
| `ExtraAttack` | Fighter (base), Level 5 | Attack twice instead of once with the Attack action. | N/A — passive; scales to 3 attacks at L11 (`TwoExtraAttacks`), 4 at L20 (`ThreeExtraAttacks`). |
| `ActionSurge` | Fighter (base), Level 2 | Take one additional action (not the Magic action) on your turn. | 1 use at L2, 2 at L17 (max once/turn). Regain all on Short or Long Rest. Extended by `ArcaneCharge` (2014 Eldritch Knight) and `RallyingSurge` (2024 Banneret). |
| `Indomitable` | Fighter (base), Level 9 | Reroll a failed saving throw, adding your Fighter level. | 1 use at L9, 2 at L13, 3 at L17. Regain all on Long Rest. Extended by `SharedResilience` (2024 Banneret). |
| `FightingStyle` | Fighter (base), Level 1 | Grants a Fighting Style feat, swappable whenever you gain a Fighter level. | N/A — passive/unlimited. Extended by `AdditionalFightingStyle` (Champion, 2014 & 2024). |
| `CombatSuperiority` | Fighter — Battle Master (2014), Level 3 | Learn combat maneuvers fueled by Superiority Dice. | 4 dice at L3, 5 at L7, 6 at L15. Regain all on Short or Long Rest. *(SourceTexts/SubclassTexts2014/battle_master.txt)* Extended by maneuvers, `ImprovedCombatSuperiority` (L7), `Relentless` (L10), `GreaterCombatSuperiority` (L15). |
| `SuperiorityDice` | Fighter — Battle Master (2024), Level 3 | 2024-rules version of the same maneuver-fueling dice pool. | Same progression as `CombatSuperiority` above. *(SourceTexts/SubclassTexts2024/battle_master.txt)* Extended by maneuvers, `ImprovedCombatSuperiority`, `Relentless`, `UltimateCombatSuperiority`. |
| `ArcaneShot` | Fighter — Arcane Archer (2014), Level 3 | Apply a magical Arcane Shot option to a bow shot, once per turn. | 2 uses (constant); known options scale at L7/10/15/18. Regain all on Short or Long Rest. Extended by `EverReadyShot`. |
| `ImprovedCritical` | Fighter — Champion (2014 & 2024), Level 3 | Weapon/Unarmed Strike attacks crit on a 19–20. | N/A — passive/unlimited. Extended by `SuperiorCritical`. |
| `WarMagic` | Fighter — Eldritch Knight (2014 & 2024), Level 7 | 2024: replace one Attack-action attack with a cantrip. 2014: casting a cantrip grants a bonus weapon attack. | N/A — passive/unlimited. Extended by `ImprovedWarMagic`. |
| `ManifestEcho` | Fighter — Echo Knight (2014), Level 3 | Bonus action to manifest a translucent echo of yourself you can swap places with. | N/A — passive/unlimited (persistent, no per-rest charge). Extended by `LegionOfOne`. |
| `GiantsMight` | Fighter — Rune Knight (2014), Level 3 | Bonus action to grow Large, gain Strength advantage, and bonus weapon damage for 1 minute. | Uses = proficiency bonus, regain all on Long Rest. Extended by `GreatStature` (L7), `RunicJuggernaut` (L18). |
| `RuneCarver` | Fighter — Rune Knight (2014), Level 3 | Inscribe magic runes onto gear, each with a passive benefit plus a once-per-rest invoked effect. | Runes known: 2 at L3, 3 at L7, 4 at L10, 5 at L15 (each rune's invoked effect separately usable once per Short or Long Rest). Extended by `MasterOfRunes`. |
| `FightingSpirit` | Fighter — Samurai (2014), Level 3 | Bonus action for advantage on weapon attacks plus temp HP for the turn. | 3 uses (constant; temp HP scales 5/10/15 at L3/10/15). Regain all on Long Rest. Extended by `TirelessSpirit`. |
| `PsionicPower` | Fighter — Psi Warrior (2024), Level 3 | Pool of Psionic Energy Dice fueling Protective Field, Psionic Strike, and Telekinetic Movement. | 4d6 at L3, 6d8 at L5, 8d8 at L9, 8d10 at L11, 10d10 at L13, 12d12 at L17. Regain 1 on Short Rest, all on Long Rest. Extended by `TelekineticAdept`. |
| `GroupRecovery` | Fighter — Banneret (2024), Level 3 | When you use Second Wind, chosen allies within 30 ft also heal 1d4 + Fighter level. | 1 use, regain on Short or Long Rest. Extended by `TeamTactics` (L7). |

## Monk

| Feature | Introduced | Description | Number of Uses |
|---|---|---|---|
| `MonksFocus` | Monk (base), Level 2 | Pool of Focus Points fueling Flurry of Blows, Patient Defense, Step of the Wind, and later ki-fueled features. | 2 pts at L2, +1/level up to 20 at L20. Regain all on Short or Long Rest. *(SourceTexts/ClassTexts/monk.txt)* |
| `ArmsOfTheAstralSelf` | Monk — Way of the Astral Self (2014), Level 3 | Spend a Focus Point (ki) as a bonus action to summon spectral arms letting you use Wisdom for Strength checks/saves and unarmed strikes. | Draws from `MonksFocus`. |
| `KenseiWeapons` | Monk — Way of the Kensei (2014), Level 3 | Designate melee and ranged "kensei weapon" types, gaining proficiency and Kensei features; add a type at L6/11/17. | N/A — passive/unlimited (weapon selection, no charges). |
| `HandOfHarm` | Monk — Warrior of Mercy (2024), Level 3 | Once per turn, spend a Focus Point on a successful Unarmed Strike for extra necrotic damage. | Draws from `MonksFocus`. |
| `ShadowStep` | Monk — Warrior of Shadow (2024), Level 6 | While in dim light/darkness, bonus action teleport 60 ft and gain advantage on your next melee attack. | N/A at base rank (no Focus cost); `ImprovedShadowStep` (L11) can spend 1 Focus Point to waive the darkness requirement. |
| `MysticFightingStyle` | Monk — Warrior of the Mystic Arts (2024), Level 6 | On the Attack action, replace one Unarmed Strike with a Sorcerer cantrip (action casting time). | N/A — passive/unlimited, limited only by normal cantrip rules. |

## Paladin

| Feature | Introduced | Description | Number of Uses |
|---|---|---|---|
| `LayOnHands` | Paladin (base), Level 1 | Touch-healing pool restoring HP (or curing poison at 5 HP/use) as a Bonus Action. | Pool = 5 × Paladin level, fully replenishes on Long Rest (L1=5 … L20=100). *(SourceTexts/ClassTexts/paladin.txt)* |
| `ChannelDivinity` | Paladin (base), Level 3 | Shared resource fueling Channel Divinity options (Divine Sense at base, plus later class/subclass options). | 2 uses at L3, 3 at L11. Regain 1 on Short Rest, all on Long Rest. *(SourceTexts/ClassTexts/paladin.txt)* |
| `AuraOfProtection` | Paladin (base), Level 6 | 10-ft emanation giving you and allies a saving-throw bonus equal to Charisma modifier (min +1). | N/A — passive/unlimited, continuous while not Incapacitated. |
| `AuraOfConquest` | Paladin — Oath of Conquest (2014), Level 7 | Constant frightening aura (10 ft, 30 ft at L18): frightened creatures take psychic damage each turn. | N/A — passive/unlimited. |
| `AuraOfDevotion` | Paladin — Oath of Devotion (2014), Level 7 | You and friendly creatures within 10 ft can't be charmed while you're conscious. | N/A — passive/unlimited. |
| `AuraOfTheGuardian` | Paladin — Oath of Redemption (2014), Level 7 | Reaction: magically take damage meant for an ally within 10 ft in their place. | N/A — passive/unlimited (bounded only by the normal 1-reaction economy). |
| `AuraOfTheSentinel` | Paladin — Oath of the Watchers (2014), Level 7 | You and chosen creatures within 10 ft (30 ft at L18) gain an initiative bonus equal to proficiency bonus. | N/A — passive/unlimited. |
| `AuraOfHate` | Paladin — Oathbreaker (2014), Level 7 | You and nearby fiends/undead gain a melee weapon damage bonus equal to Charisma modifier (min +1). | N/A — passive/unlimited. |
| `VowOfEnmity` | Paladin — Oath of Vengeance (2014 & 2024), Level 3 | Swear enmity against a creature for advantage on attacks against it for 1 minute. | Draws from `ChannelDivinity`. |

## Ranger

| Feature | Introduced | Description | Number of Uses |
|---|---|---|---|
| `FavoredEnemy` | Ranger (base), Level 1 | Always has Hunter's Mark prepared, castable a number of times per Long Rest without a spell slot. | 2 uses at L1–4, 3 at L5–8, 4 at L9–12, 5 at L13–16, 6 at L17–20. All regained on Long Rest. *(SourceTexts/ClassTexts/ranger.txt)* |
| `PrimalCompanion` | Ranger — Beast Master (2024), Level 3 | Summons a primal beast companion (Land/Sea/Sky) that fights alongside you, re-themeable on a Long Rest. | N/A — persists until it dies/is dismissed; reviving costs a spell slot, not a tracked charge. |
| `SlayersPrey` | Ranger — Monster Slayer (2014), Level 3 | Bonus action: mark a creature within 60 ft; the first hit against it each turn deals extra damage. | N/A — designation lasts until rest/re-designation, no activation cost. |
| `DrakeCompanion` | Ranger — Drakewarden (2014), Level 3 | Action: summon your bonded drake, growing more powerful at L7 and L15. | 1 use, regains on Long Rest; re-summonable early via a 1st-level+ spell slot. |
| `DreadAmbusher` | Ranger — Gloom Stalker (2024), Level 3 | Speed boost + initiative bonus on the first turn of combat, plus Dreadful Strike (extra damage once/turn). | Dreadful Strike: Wisdom modifier (min 1) uses, all regained on Long Rest. |
| `GatheredSwarm` | Ranger — Swarmkeeper (2014), Level 3 | A bonded swarm of nature spirits assists once per turn after you hit. | N/A at base rank (once-per-turn trigger, not a charge). |
| `WrathOfTheWild` | Ranger — Hollow Warden (2024), Level 3 | Bonus action transformation (1 minute) granting AC, a fear aura, and an opportunity-attack trigger. | Draws from `FavoredEnemy` (Hunter's Mark uses). |

## Rogue

| Feature | Introduced | Description | Number of Uses |
|---|---|---|---|
| `SneakAttack` | Rogue (base), Level 1 | Once per turn, extra weapon damage on a Finesse/Ranged attack made with Advantage (or an ally adjacent). | N/A — not a resource pool, limited to once per turn. Damage die scales: 1d6 (L1–2) up to 10d6 (L19–20). *(SourceTexts/ClassTexts/rogue.txt)* |
| `CunningAction` | Rogue (base), Level 2 | Bonus action to Dash, Disengage, or Hide. | N/A — passive/unlimited (usable every turn). |
| `Bloodthirst` | Rogue — Scion of the Three (2024), Level 3 | Reaction: teleport next to a bloodied enemy and make a melee attack. | Intelligence modifier (min 1) uses per Long Rest. *(SourceTexts/SubclassTexts2024/scion_of_the_three.txt)* At L17 also regains 1 use per Short Rest. |
| `PsychicBlades` | Rogue — Soulknife (2024), Level 3 | Manifest a psychic-energy blade replacing weapon attacks. | N/A on the blade itself; powers built on it (Soul Blades, Rend Mind) draw from the subclass's Psionic Energy Dice pool (4 dice at L3, up to 12 by L17). |

## Sorcerer

| Feature | Introduced | Description | Number of Uses |
|---|---|---|---|
| `Spellcasting` | Sorcerer (base), Level 1 | Baseline spellcasting rules (cantrip/spell swapping, slot regain, Charisma as spellcasting ability). | N/A — passive framework feature; spell slots regain fully on Long Rest. |
| `InnateSorcery` | Sorcerer (base), Level 1 | Bonus action: 1 minute of +1 spell save DC and advantage on Sorcerer spell attack rolls. | 2 uses, regain all on Long Rest. *(SourceTexts/ClassTexts/sorcerer.txt)* Riders re-flavor/extend it: `SorceryIncarnate` (L7) lets you pay 2 Sorcery Points to reactivate once exhausted; Spellfire's `CrownOfSpellfire` (L18) pays 5 points; Shadow Sorcery's `UmbralForm` similarly re-flavors a use. |
| `FontOfMagic` | Sorcerer (base), Level 2 | Sorcery Points pool, convertible to/from spell slots and spent on Metamagic/subclass features. | Points = Sorcerer level (2 at L2, up to 20 at L20); full regain on Long Rest. *(SourceTexts/ClassTexts/sorcerer.txt)* `SorcerousRestoration` (L5) additionally recoups up to half your level (round down) once per Short Rest. |
| `Metamagic` | Sorcerer (base), Level 2 | Spend Sorcery Points to apply a known Metamagic option as you cast a spell. | Options known (not uses): 2 at L2, 4 at L10, 6 at L17; each application still costs Sorcery Points. *(SourceTexts/ClassTexts/sorcerer.txt)* `LunarBoons` (Lunar Sorcery, L6) discounts cost by 1 point, proficiency-bonus times per Long Rest. |
| `PsionicSpells` | Sorcerer — Aberrant Mind / Aberrant Sorcery, Level 3 | Always-prepared bonus spells at Sorcerer levels 3/5/7/9. | N/A — passive/unlimited. `PsionicSorcery` (L6) lets you cast them with Sorcery Points instead of slots. |
| `LunarEmbodiment` | Sorcerer — Lunar Sorcery (2014), Level 3 | Bonus spells by lunar phase (Full/New/Crescent Moon), plus one free 1st-level phase-spell cast. | 1 free phase-spell cast per Long Rest. *(SourceTexts/SubclassTexts2014/lunar_sorcery.txt)* Riders scale this at L6/14/18, some refreshable with Sorcery Points. |
| `SpellfireBurst` | Sorcerer — Spellfire, Level 3 | Spend ≥1 Sorcery Point on a Magic/Bonus Action to add a temp-HP or damage burst. | N/A of its own (once per turn); spends `FontOfMagic` points. |
| `WildMagicSurge` | Sorcerer — Wild Magic, Level 3 | Once per turn, roll d20 after casting with a slot; natural 20 triggers the Wild Magic Surge table. | N/A — passive trigger, capped at once per turn. Rider `TamedSurge` (L18) is 1 use per Long Rest. |

## Warlock

| Feature | Introduced | Description | Number of Uses |
|---|---|---|---|
| `MagicalCunning` | Warlock (base), Level 2 | 1-minute rite to regain up to half your Pact Magic slots. | 1 use per Long Rest. *(SourceTexts/ClassTexts/warlock.txt)* `EldritchMaster` (L20) upgrades that use to restore ALL expended slots; Celestial Patron's `CelestialResilience` (2024) adds a passive temp-HP trigger when it's used. |
| `MysticArcanum` | Warlock (base), Level 11 (self-extends at 13/15/17) | Cast a chosen high-level spell once without expending a slot. | One free cast per chosen spell level: 6th at L11, +7th at L13, +8th at L15, +9th at L17. All regained on Long Rest. *(SourceTexts/ClassTexts/warlock.txt)* |
| `HexbladesCurse` | Warlock — Hexblade Patron (2014), Level 3 | Bonus action to curse a target for 1 minute: bonus damage, expanded crit range, life drain on kill. | 1 use, regains on Short or Long Rest. *(SourceTexts/SubclassTexts2014/hexblade.txt)* Riders `ArmorOfHexes`/`MasterOfHexes` add passive bonuses while active. |
| `TentacleOfTheDeep` | Warlock — The Fathomless (2014), Level 3 | Bonus action: summon a spectral tentacle for a cold-damage melee spell attack, repositionable. | N/A — recreatable at will; damage grows from 1d8 to 2d8 at L10. `GuardianCoil` (L6) adds a Reaction damage-reduction use. |
| `GeniesVessel` | Warlock — The Genie Patron (2014), Level 3 | A magical vessel usable as a focus, with Bottled Respite (enter it) and Genie's Wrath (bonus damage on hit). | Bottled Respite: 1 use per Long Rest. Genie's Wrath: N/A, once per turn. *(SourceTexts/SubclassTexts2014/the_genie.txt)* `SanctuaryVessel` (L10) expands Bottled Respite to shelter allies; `LimitedWish` (L14) is a separate 1-use-per-1d4-Long-Rests feature. |
| `StepsOfTheFey` | Warlock — Archfey Patron (2024), Level 3 | Cast Misty Step without a spell slot, plus an added rider effect. | Charisma modifier (min 1) uses per Long Rest. *(SourceTexts/SubclassTexts2024/archfey_patron.txt)* `MistyEscape` (L6) consumes one of these same uses. |
| `AwakenedMind` | Warlock — Great Old One Patron (2024), Level 3 | Bonus action to open a telepathic link with a creature you can see, lasting minutes equal to Warlock level. | N/A — no charge cost to open the link. `ClairvoyantCombatant` (L6) adds its own once-per-Short/Long-Rest effect, separate from Awakened Mind itself. |
| `FormOfDread` | Warlock — Undead Patron (2024), Level 3 | Bonus action: transform into an avatar of dread for 1 minute (temp HP, Frightened immunity, frighten-on-hit). | Charisma modifier (min 1) uses per Long Rest. *(SourceTexts/SubclassTexts2024/undead_patron.txt)* `SuperiorDread` (L10) only adds passive benefits while active. |

## Wizard

| Feature | Introduced | Description | Number of Uses |
|---|---|---|---|
| `AwakenedSpellbook` | Wizard — Order of Scribes (2014), Level 3 | Sentient spellbook: usable as a focus, re-flavors a spell's damage type, casts rituals at normal speed once per Long Rest. | Ritual-speed benefit: 1 use per Long Rest. *(SourceTexts/SubclassTexts2014/order_of_scribes.txt)* `ManifestMind` (L6) — proficiency-bonus uses/day; `MasterScrivener` (L10) — 1 scroll/Long Rest; `OneWithTheWord` (L14) — passive, triggers once then needs 1d6 Long Rests to reset. |
| `ArcaneWard` | Wizard — Abjuration (2014) / Abjurer (2024), Level 3 | Casting an Abjuration spell creates/refuels a damage-absorbing ward. | Not a charge count — ward HP = 2 × Wizard level + Intelligence modifier; can only be (re-)created once per Long Rest, but recharges 2 HP per Abjuration spell level cast. *(SourceTexts/SubclassTexts2014/abjuration.txt; SourceTexts/SubclassTexts2024/abjurer.txt)* `ProjectedWard` lets you redirect absorption to an ally via Reaction. |
| `Portent` | Wizard — Divination (2014) / Diviner (2024), Level 3 | Roll two d20s on a Long Rest; replace any attack/save/check roll (yours or a seen creature's) with one, once per turn. | 2 dice per Long Rest, unused dice lost (not accumulated). *(SourceTexts/SubclassTexts2014/divination.txt; SourceTexts/SubclassTexts2024/diviner.txt)* `GreaterPortent` (L14) raises the pool to 3 dice. |
| `Bladesong` | Wizard — Bladesinger (2024), Level 3 | Bonus action buff (1 minute): AC/Speed, Intelligence-based weapon attacks, Concentration bonus — only while unarmored/shieldless. | Intelligence modifier (min 1) uses per Long Rest; one use is refunded whenever you use Arcane Recovery. *(SourceTexts/SubclassTexts2024/bladesinger.txt)* `SongOfDefense` (L10) spends a spell slot, not a Bladesong use, as a Reaction. |
| `TransmutersStone` | Wizard — Transmuter, Level 3 (code) / 6 (2014 text) | Create a stone granting Darkvision, elemental Resistance, or +10 ft Speed, plus Con-save proficiency. | N/A as a "uses" resource — one stone exists at a time, freely re-created. *(SourceTexts/SubclassTexts2014/transmutation.txt)* `PotentStone` adds passive scaling; `MasterTransmuter` lets you expend the stone itself for a one-time effect. |

---

## Notable resource-pool patterns

A handful of core features act as **shared resource pools** that many riders draw from rather than
tracking their own uses — worth knowing since their "number of uses" numbers govern several other
features at once:

- **`ChannelDivinity`** (Cleric *and* Paladin, separately) — nearly every domain/oath's Channel
  Divinity option spends from this same pool instead of having its own counter.
- **`WildShape`** (Druid) — several 2024 Circle subclasses (Sea, Stars) and 2014 Circle of Wildfire
  spend Wild Shape uses on their subclass transformation instead of shapeshifting.
- **`MonksFocus`** (Monk) — the base ki-point pool that Flurry of Blows, Patient Defense, Step of
  the Wind, and several subclass features (Hand of Harm, Arms of the Astral Self) all draw from.
- **`BardicInspiration`** (Bard) — several subclasses (Swords, Spirits) spend Bardic Inspiration
  uses to fuel their own subclass mechanic rather than adding a new pool.
- **`FontOfMagic`** Sorcery Points (Sorcerer) — fuels `Metamagic`, `SpellfireBurst`, and several
  subclass reactivation riders on top of its own slot-conversion use.
- **`FavoredEnemy`** (Ranger) — Hollow Warden's `WrathOfTheWild` spends Hunter's Mark casts from
  this pool instead of tracking its own.
