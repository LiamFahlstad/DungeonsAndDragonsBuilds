# Feature-Extension Audit Report

Tracks the `dnd-feature-extender` audit sweep converting rider/upgrade features from standalone
`data.add_feature(X())` calls to `parent.extend_feature(X())`, per `.claude/agents/dnd-feature-extender.md`.

Status column: **converted N** = N features rewired; **clean** = audited, no changes needed (either no riders found, or already correctly wired).

## 2014 Subclasses (SubClasses2014/)

| Subclass | Status | Conversions |
|---|---|---|
| Artificer - Alchemist (2014) | clean | no valid riders (same conclusion as 2024) |
| Artificer - Armorer (2014) | converted 2 | `ArmorModifications` → extends `ArcaneArmor`; `PerfectedArmor` → extends `ArmorModel` |
| Artificer - Artillerist (2014) | converted 2 | `ExplosiveCannon`, `FortifiedPosition` → extend `EldritchCannon` |
| Artificer - Battle Smith (2014) | converted 1 | `ImprovedDefender` → extends `ArcaneJolt` |
| Barbarian - Path of the Ancestral Guardian | converted 3 | `AncestralProtectors`, `SpiritShield`, `VengefulAncestors` → extend `Rage` |
| Barbarian - Path of the Battlerager | converted 3 | `RecklessAbandon` → extends `RecklessAttack`; `BattleragerCharge` → extends `Rage`; `SpikedRetribution` → extends `BattleragerArmor` |
| Barbarian - Path of the Berserker (2014) | clean | already correctly wired (`Frenzy`, `MindlessRage` → extend `Rage`) |
| Barbarian - Path of the Storm Herald | converted 1 | `StormAura` → extends `Rage` |
| Barbarian - Path of the Totem Warrior | clean | already correctly wired (`TotemSpirit`, `TotemicAttunement` → extend `Rage`) |
| Barbarian - Path of Wild Magic | converted 3 | `WildSurge`, `UnstableBacklash`, `ControlledSurge` → extend `Rage` |
| Bard - College of Creation | converted 2 | `MoteOfPotential` → extends `BardicInspiration`; `CreativeCrescendo` → extends `PerformanceOfCreation` |
| Bard - College of Eloquence | converted 3 | `UnsettlingWords`, `UnfailingInspiration`, `InfectiousInspiration` → all extend `BardicInspiration` |
| Bard - College of Lore (2014) | converted 2 | `CuttingWords`, `PeerlessSkill` → extend `BardicInspiration` |
| Bard - College of Swords | converted 1 | `MastersFlourish` → extends `BladeFlourish` |
| Bard - College of Whispers | converted 1 | `PsychicBlades` → extends `BardicInspiration` |
| Cleric - Arcana Domain | converted 1 | `ArcaneMastery` → extends `ArcanaDomainSpells` |
| Cleric - Death Domain | converted 2 | `InescapableDestruction` → extends `TouchOfDeathChannelDivinity`; `ImprovedReaper` → extends `Reaper` |
| Cleric - Forge Domain | converted 1 | `SaintOfForgeAndFire` → extends `SoulOfTheForge` |
| Cleric - Life Domain (2014) | clean | no riders found |
| Cleric - Nature Domain | converted 1 | `MasterOfNature` → extends `CharmAnimalsAndPlantsChannelDivinity` |
| Cleric - Order Domain | converted 1 | `OrdersWrath` → extends `DivineStrike` |
| Cleric - Peace Domain | converted 2 | `ProtectiveBond`, `ExpansiveBond` → extend `EmboldeningBond` |
| Cleric - Tempest Domain | clean | no riders found |
| Cleric - Twilight Domain | converted 1 | `TwilightShroud` → extends `TwilightSanctuaryChannelDivinity` |
| Druid - Circle of Dreams | clean | no riders found |
| Druid - Circle of Spores | converted 1 | `SpreadingSpores` → extends `SymbioticEntity` |
| Druid - Circle of the Shepherd | converted 1 | `GuardianSpirit` → extends `SpiritTotem` |
| Druid - Circle of Wildfire | converted 2 | `EnhancedBond`, `BlazingRevival` → extend `SummonWildfireSpirit` |
| Fighter - Arcane Archer | converted 1 | `EverReadyShot` → extends `ArcaneShot` |
| Fighter - Battle Master (2014) | converted 2 | `ImprovedCombatSuperiority`, `GreaterCombatSuperiority` → extend `CombatSuperiority` |
| Fighter - Cavalier | clean | no riders found |
| Fighter - Champion (2014) | converted 2 | `AdditionalFightingStyle` → extends base `FightingStyle`; `SuperiorCritical` → extends `ImprovedCritical` |
| Fighter - Echo Knight | converted 1 | `LegionOfOne` → extends `ManifestEcho` |
| Fighter - Eldritch Knight (2014) | converted 1 | `ArcaneCharge` → extends base `ActionSurge` (`ImprovedWarMagic` was already correctly wired) |
| Fighter - Rune Knight | converted 3 | `GreatStature`, `RunicJuggernaut` → extend `GiantsMight`; `MasterOfRunes` → extends `RuneCarver` |
| Fighter - Samurai | converted 1 | `TirelessSpirit` → extends `FightingSpirit` |
| Monk - Way of the Astral Self | converted 1 | `VisageOfTheAstralSelf` → extends `ArmsOfTheAstralSelf` |
| Monk - Way of the Drunken Master | clean | `FlurryOfBlows` riders have no valid parent (base `FlurryOfBlows` is itself an extension) |
| Monk - Way of the Kensei | converted 1 | `MagicKenseiWeapons` → extends `KenseiWeapons` |
| Monk - Way of the Long Death | clean | no riders found |
| Monk - Way of the Open Hand (2014) | clean | `OpenHandTechnique` rides Flurry of Blows but no valid nestable parent (same reason as Drunken Master) |
| Monk - Way of the Sun Soul | clean | no riders found |
| Paladin - Oath of Conquest | clean | Channel Divinity options kept standalone (established 2014 convention); `AuraOfConquestExpansion` already correctly wired |
| Paladin - Oath of Devotion (2014) | clean | Channel Divinity options kept standalone; `AuraOfDevotionExpansion` already correctly wired |
| Paladin - Oath of the Crown | clean | Channel Divinity options kept standalone to match established 2014 Paladin/Cleric convention |
| Paladin - Oath of the Watchers | converted 2 | `WatchersWill`, `AbjureTheExtraplanar` → extend `ChannelDivinity` |
| Paladin - Oath of Redemption | clean | already correctly wired (`AuraOfTheGuardianExpansion` → extends `AuraOfTheGuardian`) |
| Paladin - Oath of Vengeance (2014) | converted 1 | `SoulOfVengeance` → extends `VowOfEnmity` |
| Paladin - Oathbreaker | clean | already correctly wired (`AuraOfHateExpansion` → extends `AuraOfHate`) |
| Ranger - Drakewarden | converted 2 | `BondOfFangAndScale`, `PerfectedBond` → extend `DrakeCompanion` |
| Ranger - Gloom Stalker (2014) | clean | `IronMind` has a real `apply()` override, must stay standalone; rest independent |
| Ranger - Horizon Walker | clean | no riders found |
| Ranger - Hunter (2014) | clean | independent level choices, no riders |
| Ranger - Monster Slayer | converted 2 | `SupernaturalDefense`, `SlayersCounter` → extend `SlayersPrey` |
| Ranger - Swarmkeeper | converted 1 | `MightySwarm` → extends `GatheredSwarm` |
| Rogue - Assassin (2014) | clean | matches 2024 Rogue Assassin precedent of keeping `DeathStrike` standalone |
| Rogue - Mastermind | clean | no riders found |
| Rogue - Scout | clean | no riders found (`SuddenStrike`'s Sneak Attack mention is a caveat, not a rider) |
| Rogue - Swashbuckler | converted 1 | `RakishAudacity` → extends base `SneakAttack` |
| Rogue - Thief (2014) | converted 1 | `FastHands` → extends base `CunningAction` (2014 `SupremeSneak` text differs from 2024, unrelated to Sneak Attack) |
| Sorcerer - Aberrant Mind | converted 1 | `PsionicSorcery` → extends `PsionicSpells` |
| Sorcerer - Divine Soul | converted 1 | `DivineMagic` → extends base `Spellcasting` |
| Sorcerer - Lunar Sorcery | converted 4 | `LunarBoons` → extends `Metamagic`; `WaxingAndWaning`, `LunarEmpowerment`, `LunarPhenomenon` → extend `LunarEmbodiment` |
| Sorcerer - Storm Sorcery | clean | no riders found |
| Warlock - Archfey Patron (2014) | clean | no riders found |
| Warlock - Fiend Patron (2014) | clean | no riders found |
| Warlock - Great Old One Patron (2014) | clean | no riders found |
| Warlock - Hexblade Patron | converted 2 | `ArmorOfHexes`, `MasterOfHexes` → extend `HexbladesCurse` |
| Warlock - The Celestial | clean | no riders found |
| Warlock - The Fathomless | converted 1 | `GuardianCoil` → extends `TentacleOfTheDeep` |
| Warlock - The Genie | converted 2 | `SanctuaryVessel`, `LimitedWish` → extend `GeniesVessel` |
| Warlock - The Undying | clean | no riders found |
| Wizard - Chronurgy Magic | clean | no riders found |
| Wizard - Graviturgy Magic | clean | no riders found (`AdjustDensity` bakes its own L10 scaling inline) |
| Wizard - Order of Scribes | converted 3 | `ManifestMind`, `MasterScriviner`, `OneWithTheWord` → all extend `AwakenedSpellbook` |
| Wizard - School of Abjuration | converted 1 | `ProjectedWard` → extends `ArcaneWard` |
| Wizard - School of Conjuration | clean | no riders found |
| Wizard - School of Divination | converted 1 | `GreaterPortent` → extends `Portent` |
| Wizard - School of Enchantment | clean | no riders found |
| Wizard - School of Evocation (2014) | clean | no riders found |
| Wizard - School of Illusion | clean | no riders found |
| Wizard - School of Necromancy | clean | no riders found (`UndeadThralls` rides on the Animate Dead spell, not a Feature) |

## 2024 Subclasses (SubClasses2024/)

| Subclass | Status | Conversions |
|---|---|---|
| Artificer - Alchemist | clean | no riders found |
| Artificer - Armorer | converted 2 | `ImprovedArmorer`, `PerfectedArmor` → extend `ArmorModel` |
| Artificer - Artillerist | converted 2 | `ExplosiveCannon`, `FortifiedPosition` → extend `EldritchCannon` |
| Artificer - Battle Smith | converted 1 | `ImprovedDefender` → extends `ArcaneJolt` |
| Artificer - Cartographer | converted 3 | `GuidedPrecision` → extends `CartographerSpells`; `IngeniousMovement` → extends base `FlashofGenius`; `SuperiorAtlas` → extends `AdventurersAtlas` |
| Artificer - Reanimator | converted 3 | `StrangeModifications`, `ImprovedReanimation`, `MacabreModifications` → all extend `ReanimatedCompanion` |
| Barbarian - Path of the Berserker (2024) | clean | already correctly wired (`Frenzy`, `MindlessRage`, `IntimidatingPresence` → extend `Rage`); `Retaliation` independently standalone |
| Barbarian - Path of the Wild Heart | clean | already correctly wired from earlier work |
| Barbarian - Path of the World Tree | clean | already correctly wired from earlier work |
| Barbarian - Path of the Zealot | clean | already correctly wired from earlier work |
| Bard - College of Dance | clean | no riders found |
| Bard - College of Glamour | clean | no riders found |
| Bard - College of Lore (2024) | converted 1 | `CuttingWords` → extends `BardicInspiration` (`PeerlessSkill` was already correctly wired) |
| Bard - College of Spirits | converted 1 | `MysticalConnection` → extends `SpiritsFromBeyond` |
| Bard - College of the Moon (2024) | converted 2 | `MoonsInspiration`, `EventidesSplendor` → extend `BardicInspiration` |
| Bard - College of Valor | converted 1 | `CombatInspiration` → extends `BardicInspiration` |
| Cleric - Grave Domain | clean | already correctly wired (`PathToTheGrave` → extends `ChannelDivinity`) |
| Cleric - Knowledge Domain | clean | already correctly wired (`MindMagic` → extends `ChannelDivinity`) |
| Cleric - Life Domain (2024) | clean | already correctly wired (`PreserveLife` → extends `ChannelDivinity`) |
| Cleric - Light Domain | clean | already correctly wired (`RadianceOfTheDawn` → extends `ChannelDivinity`; `ImprovedWardingFlare` → extends `WardingFlare`) |
| Cleric - Trickery Domain | converted 2 | `TrickstersTransposition`, `ImprovedDuplicity` → extend `ChannelDivinity` |
| Cleric - War Domain | clean | already correctly wired (`GuidedStrike`, `WarGodsBlessing` → extend `ChannelDivinity`) |
| Druid - Circle of the Land | clean | no riders found |
| Druid - Circle of the Moon | converted 1 | `LunarForm` → extends `MoonlightStep` |
| Druid - Circle of the Sea | converted 3 | `AquaticAffinity`, `Stormborn`, `OceanicGift` → extend `WrathOfTheSea` |
| Druid - Circle of the Stars | converted 2 | `TwinklingConstellations`, `FullOfStars` → extend `StarryForm` |
| Fighter - Banneret (Purple Dragon Knight) | converted 3 | `TeamTactics` → extends `GroupRecovery`; `RallyingSurge` → extends base `ActionSurge`; `SharedResilience` → extends base `Indomitable` |
| Fighter - Battle Master | converted 2 | `ImprovedCombatSuperiority`, `UltimateCombatSuperiority` → extend `SuperiorityDice` (`Relentless` was already correctly wired) |
| Fighter - Champion | converted 2 | `AdditionalFightingStyle` → extends base `FightingStyle`; `SuperiorCritical` → extends `ImprovedCritical` |
| Fighter - Eldritch Knight | clean | already correctly wired (`ImprovedWarMagic` → extends `WarMagic`) |
| Fighter - Psi Warrior | converted 1 | `TelekineticAdept` → extends `PsionicPower` |
| Monk - Mercy | converted 1 | `PhysiciansTouch` → extends `HandOfHarm` |
| Monk - Mystic Arts | converted 1 | `MysticFocus` → extends `MonksFocus` |
| Monk - Open Hand (2024) | clean | `OpenHandTechnique` rides Flurry of Blows, no valid nestable parent (same as 2014) |
| Monk - Shadow | clean | already correctly wired (`ShadowArts`, `CloakOfShadows` → extend `MonksFocus`; `ImprovedShadowStep` → extends `ShadowStep`) |
| Monk - Warrior of the Elements | converted 2 | `StrideOfTheElements`, `ElementalEpitome` → both extend `MonksFocus` (same parent as sibling `ElementalAttunement`, since nesting is one level deep) |
| Paladin - Oath of Devotion | converted 4 | `SacredWeapon` → extends `ChannelDivinity`; `AuraOfDevotion`, `SmiteOfProtection`, `HolyNimbus` → extend `AuraOfProtection` |
| Paladin - Oath of Glory | clean | already correctly wired (`InspiringSmite`/`PeerlessAthlete` → extend `ChannelDivinity`; `AuraOfAlacrity` → extends `AuraOfProtection`) |
| Paladin - Oath of the Ancients | converted 2 | `AuraOfWarding`, `ElderChampion` → extend `AuraOfProtection` (Channel Divinity option `NaturesWrath` already correctly wired) |
| Paladin - Oath of the Genies | converted 1 | `AuraOfElementalShielding` → extends `AuraOfProtection` (Channel Divinity option `ElementalSmite` already correctly wired) |
| Paladin - Oath of Vengeance | converted 1 | `SoulOfVengeance` → extends `VowOfEnmity` |
| Ranger - Beast Master | converted 3 | `ExceptionalTraining`, `BestialFury`, `ShareSpells` → all extend `PrimalCompanion` |
| Ranger - Fey Wanderer | clean | riders target spells (Summon Fey, Misty Step), not Feature objects — no valid parent |
| Ranger - Gloom Stalker (2024) | converted 1 | `StalkersFlurry` → extends `DreadAmbusher` |
| Ranger - Hollow Warden | converted 3 | `HungeringMight`, `RotAndViolence`, `AncientMight` → all extend `WrathOfTheWild` |
| Ranger - Hunter (2024) | clean | "Superior" features don't mechanically hook into their level-3 counterparts |
| Ranger - Winter Walker | clean | riders target the Hunter's Mark spell, not a Feature — no valid parent |
| Rogue - Arcane Trickster | converted 1 | `VersatileTrickster` → extends `SneakAttack` |
| Rogue - Assassin (2024) | converted 1 | `EnvenomWeapons` → extends `SneakAttack` (`CunningStrike` was already correctly wired) |
| Rogue - Phantom | converted 1 | `WailsFromTheGrave` → extends `SneakAttack` |
| Rogue - Scion of the Three | converted 1 | `AuraOfMalevolence` → extends `Bloodthirst` (`StrikeFear` was already correctly wired) |
| Rogue - Soulknife | converted 2 | `SoulBlades`, `RendMind` → extend `PsychicBlades` |
| Rogue - Thief (2024) | clean | already correctly wired (`SupremeSneak` → extends `SneakAttack`) |
| Sorcerer - Aberrant Sorcery (2024) | converted 1 | `PsionicSorcery` → extends `PsionicSpells` |
| Sorcerer - Clockwork Soul | clean | no riders found |
| Sorcerer - Draconic Sorcery | clean | no riders found (`DraconicSpells`, `DraconicResilience`, `ElementalAffinity`, `DragonWings`, `DragonCompanion` all independent) |
| Sorcerer - Shadow Magic | converted 1 | `UmbralForm` → extends base `InnateSorcery` |
| Sorcerer - Spellfire | converted 2 | `HonedSpellfire` → extends `SpellfireBurst`; `CrownOfSpellfire` → extends base `InnateSorcery` |
| Sorcerer - Wild Magic | converted 3 | `WildMagicSurgeTable`, `ControlledChaos`, `TamedSurge` → all extend `WildMagicSurge` (`TidesOfChaos`, `BendLuck` left standalone — independent primary benefits) |
| Warlock - Archfey Patron | converted 1 | `MistyEscape` → extends `StepsOfTheFey` |
| Warlock - Celestial Patron | converted 1 | `CelestialResilience` → extends base `MagicalCunning` |
| Warlock - Fiend Patron | clean | no riders found |
| Warlock - Great Old One Patron | converted 1 | `ClairvoyantCombatant` → extends `AwakenedMind` |
| Warlock - Undead Patron | converted 1 | `SuperiorDread` → extends `FormOfDread` |
| Wizard - Abjurer | converted 1 | `ProjectedWard` → extends `ArcaneWard` |
| Wizard - Bladesinger | converted 1 | `SongOfDefense` → extends `Bladesong` |
| Wizard - Diviner | clean | already correctly wired (`GreaterPortent` → extends `Portent`) |
| Wizard - Evoker | clean | no riders found (independent spell/damage benefits) |
| Wizard - Illusionist | clean | no riders found (independent illusion benefits) |
| Wizard - Transmuter | converted 1 | `MasterTransmuter` → extends `TransmutersStone` (`PotentStone` was already correctly wired) |

## Base Classes (BaseClasses/) — within-progression riders only

Audits riders *within* a base class's own level progression (a later base-class level upgrading an
earlier base-class level of the same class) — separate from subclass-on-base riders, which were
caught during the subclass sweep above.

| Base Class | Status | Conversions |
|---|---|---|
| Artificer | converted 3 | `MagicItemTinker` → extends `ReplicateMagicItem`; `AdvancedArtifice`, `SoulOfArtifice` → extend `FlashofGenius` (`MagicItemAdept`/`MagicItemMaster` attunement bumps left standalone — no explicit mechanical hook) |
| Barbarian | clean | already fully converted in prior work (`Rage`, `RecklessAttack`, `FastMovement` extensions) |
| Bard | clean | already fully converted in prior work (`BardicInspiration` extensions) |
| Cleric | converted 1 | `SearUndead` → extends `ChannelDivinity` |
| Druid | converted 3 | `WildResurgence`, `BeastSpells`, `Archdruid` → all extend `WildShape` |
| Fighter | converted 1 | `TacticalMaster` → extends `WeaponMastery` |
| Monk | converted 2 | `HeightenedFocus`, `DeflectEnergy` → extend `MonksFocus` |
| Paladin | clean | already fully converted in prior work (`AuraOfProtection`, `LayOnHands` extensions) |
| Ranger | clean | already fully converted in prior work (`FavoredEnemy` extensions) |
| Rogue | clean | already correctly wired (`CunningStrike`, `ImprovedCunningStrike`, `DeviousStrikes` → extend `SneakAttack`); rest independent |
| Sorcerer | converted 3 | `SorcerousRestoration` → extends `FontOfMagic`; `SorceryIncarnate`, `ArcaneApotheosis` → extend `InnateSorcery` |
| Warlock | converted 1 | `EldritchMaster` → extends `MagicalCunning` (`MysticArcanum` self-extension chain was already correctly wired) |
| Wizard | clean | no riders found (`SpellMastery`, `SignatureSpells` are independent capstones) |

## Sweep status: COMPLETE

Every subclass file in the repo (2014 and 2024) plus all 13 base classes have been audited:
82 2014 subclasses + 70 2024 subclasses + 13 base classes = **165 files audited**, **161 features
converted** to extensions.
Verified after every batch with `python RunCharacterCreator.py` (clean exit, no `IndexError`).
