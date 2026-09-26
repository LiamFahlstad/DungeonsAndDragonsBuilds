from Core.Definitions import Ability, DiceRollCondition, Skill
from CharacterContent.Features.Core.Improvements import (
    AbilityScoreBonus,
    AddItemDescription,
    InitiativeRollCondition,
    Reskin,
    SetItemHomebrew,
    SetItemName,
    SetItemValue,
    SkillBonus,
)
from CharacterContent.Items.Items import ItemRarity
from .Base import AbstractWeapon
from .Enums import (
    WeaponMastery,
    WeaponProperty,
    WeaponType,
    WeaponDamageRolls,
    WeaponDamageTypes,
)
from .Improvements import (
    AddAttackRollBonus,
    AddDamageRollBonus,
    AddExtraDamage,
    AddWeaponProperty,
    ExtraDamage,
    SetAttackRollBonus,
    SetDamageDie,
    SetDamageRollBonus,
    SetDamageType,
)
from .MartialMelee import Longsword, Maul, Rapier, Shortsword
from .Ranged import Longbow
from .SimpleMelee import Dagger, Greatclub, Mace, Spear


class Nullblade(AbstractWeapon):
    def base_stats(self) -> None:
        description = (
            "Antimagic Edge. When you attack with this weapon:\n"
            "    * Ignore AC bonuses granted by spells or magical effects.\n"
            "    * Ignore magical effects that cause attacks to miss (illusions, duplicates, displacement).\n"
            "    * Ignore disadvantage imposed by magical effects.\n"
            "The Nullblade counts as nonmagical for interactions with magical effects."
        )
        self.name = "Nullblade"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.VERSATILE_10]
        self.mastery = WeaponMastery.GRAZE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D8
        self.description_text = description
        self.is_homebrew = True


class Bloodletter(AbstractWeapon):
    def base_stats(self) -> None:
        description = (
            "Wounds from this blade refuse to close.\n"
            "On hit, the target must succeed on a CON save "
            "(DC = 8 + Proficiency Bonus + STR/DEX mod) or begin bleeding.\n"
            "A bleeding creature takes 1d4 damage at the start of each turn.\n"
            "It can repeat the save at the end of its turn, or the effect ends "
            "if it receives magical healing or an ally uses an action to staunch the wound."
        )
        self.name = "Bloodletter"
        self.ability = Ability.STRENGTH
        self.properties = []
        self.mastery = WeaponMastery.GRAZE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D8
        self.description_text = description
        self.is_homebrew = True


class HuntersHarpoon(AbstractWeapon):
    def base_stats(self) -> None:
        description = (
            "On hit, you may tether the target (DEX save).\n"
            "While tethered, you may use a bonus action to pull the target 10 ft toward you."
        )
        self.name = "Hunter’s Harpoon"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.THROWN]
        self.mastery = WeaponMastery.SLOW
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.PIERCING
        self.damage_roll = WeaponDamageRolls.D10
        self.description_text = description
        self.is_homebrew = True


class RicochetBlade(AbstractWeapon):
    def base_stats(self) -> None:
        description = (
            "On hit, you may bounce the attack to another creature within 5 ft.\n"
            "Make a new attack roll. The new target takes half damage (rounded down).\n"
            "The attack can bounce up to two times."
        )
        self.name = "Ricochet Blade"
        self.ability = Ability.DEXTERITY
        self.properties = [WeaponProperty.FINESSE, WeaponProperty.LIGHT]
        self.mastery = WeaponMastery.NICK
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D6
        self.description_text = description
        self.is_homebrew = True


class RampagingBlade(AbstractWeapon):
    def base_stats(self) -> None:
        description = (
            "Momentum. Each time you hit without missing since your last turn, gain a stack.\n"
            "Each stack grants +1d4 damage (max 5 stacks).\n"
            "Stacks reset if you miss, go a full turn without hitting, or combat ends."
        )
        self.name = "Rampaging Blade"
        self.ability = Ability.STRENGTH
        self.properties = []
        self.mastery = WeaponMastery.CLEAVE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D8
        self.description_text = description
        self.is_homebrew = True


class ElementalSword(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Elemental Sword"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.VERSATILE_10]
        self.mastery = WeaponMastery.GRAZE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D8
        self.description_text = (
            "As a bonus action, choose acid, cold, fire, lightning, or thunder. "
            "The weapon deals an extra 1d6 damage of the chosen type on hit."
        )
        self.extra_damage = [
            ExtraDamage(
                damage_roll=WeaponDamageRolls.D6,
                damage_type=WeaponDamageTypes.FIRE,
                note="chosen type, activate as bonus action",
            )
        ]
        self.is_homebrew = True


class BloodlustBlade(AbstractWeapon):
    def base_stats(self) -> None:
        description = (
            "Predator’s Instinct. You have advantage on attack rolls against bloodied creatures.\n"
            "If a bloodied creature is visible and you attack another target, you have disadvantage.\n"
            "This never applies when targeting allies.\n"
            "A creature is bloodied when at half HP or lower."
        )
        self.name = "Bloodlust Blade"
        self.ability = Ability.STRENGTH
        self.properties = []
        self.mastery = WeaponMastery.GRAZE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D8
        self.description_text = description
        self.is_homebrew = True


class CoinflipCutBlade(AbstractWeapon):
    def base_stats(self) -> None:
        description = (
            "After you hit, flip a coin:\n"
            "Heads — deal +2d6 force damage.\n"
            "Tails — you take 1d6 force damage."
        )
        self.name = "Coinflip Cut"
        self.ability = Ability.DEXTERITY
        self.properties = [WeaponProperty.FINESSE, WeaponProperty.LIGHT]
        self.mastery = WeaponMastery.NICK
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D6
        self.description_text = description
        self.is_homebrew = True


class Sundersteel(AbstractWeapon):
    def base_stats(self) -> None:
        description = (
            "Damage ignores resistance.\n"
            "Creatures immune to this damage instead take damage as if resistant."
        )
        self.name = "Sundersteel"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.HEAVY]
        self.mastery = WeaponMastery.CLEAVE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D12
        self.description_text = description
        self.is_homebrew = True


class VampiricEdge(AbstractWeapon):
    def base_stats(self) -> None:
        description = (
            "When you hit a creature, regain 1d4 hit points.\n"
            "You cannot regain more HP than the damage dealt."
        )
        self.name = "Vampiric Edge"
        self.ability = Ability.STRENGTH
        self.properties = []
        self.mastery = WeaponMastery.GRAZE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D8
        self.description_text = description
        self.is_homebrew = True


# ──────────────────────────────────────────────────────────────────────────────
# WeaponImprovement showcase: one weapon per improvement, demonstrating how
# `weapon_improvements=[...]` composes on top of a weapon's base_stats().
# ──────────────────────────────────────────────────────────────────────────────


class UnerringBlade(Longsword):
    """A Longsword variant demonstrating SetAttackRollBonus: attack rolls
    always use a fixed bonus, ignoring ability modifier, proficiency, and any
    additive bonuses."""

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(SetAttackRollBonus(7))
        self.add_weapon_improvement(
            Reskin(
                "Unerring Blade",
                "This blade's strikes are guided by fate: it always hits with a "
                "+7 bonus to attack rolls, ignoring your ability scores and proficiency.",
            )
        )


class MarksmansLongbow(Longbow):
    """A Longbow variant demonstrating AddAttackRollBonus: a flat bonus stacks
    on top of the normal attack roll."""

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(AddAttackRollBonus(2, "Marksman's Scope"))
        self.add_weapon_improvement(
            Reskin(
                "Marksman's Longbow",
                "A precision-crafted scope grants a +2 bonus to attack rolls with "
                "this bow, on top of the normal ability and proficiency bonuses.",
            )
        )


class Skullcrusher(Maul):
    """A Maul variant demonstrating SetDamageRollBonus: the damage bonus is
    fixed, ignoring ability modifier."""

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(SetDamageRollBonus(10))
        self.add_weapon_improvement(
            Reskin(
                "Skullcrusher",
                "Enchanted to strike with unwavering force, this maul always deals "
                "a +10 damage bonus, regardless of your Strength.",
            )
        )


class VenomfangDagger(Dagger):
    """A Dagger variant demonstrating AddDamageRollBonus: a flat bonus stacks
    on top of the normal damage bonus."""

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(AddDamageRollBonus(3, "Venom Coating"))
        self.add_weapon_improvement(
            Reskin(
                "Venomfang Dagger",
                "Coated in a potent, self-replenishing venom that adds +3 to every "
                "damage roll, on top of your normal ability modifier.",
            )
        )


class Colossustrike(Greatclub):
    """A Greatclub variant demonstrating SetDamageDie: the damage die is
    overridden to something larger than the base weapon's own die."""

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(SetDamageDie(WeaponDamageRolls.D12x2))
        self.add_weapon_improvement(
            Reskin(
                "Colossustrike",
                "This oversized greatclub has been reinforced with iron bands, "
                "upgrading its damage die to 2d12.",
            )
        )


class FrostbrandBlade(Longsword):
    """A Longsword variant demonstrating SetDamageType: the damage type is
    overridden from the base weapon's."""

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(SetDamageType(WeaponDamageTypes.COLD))
        self.add_weapon_improvement(
            Reskin(
                "Frostbrand Blade",
                "Forged from enchanted ice, this longsword deals Cold damage "
                "instead of Slashing damage.",
            )
        )


class LungingLongsword(Longsword):
    """A Longsword variant demonstrating AddWeaponProperty: a property is
    added on top of the base weapon's own list."""

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(AddWeaponProperty(WeaponProperty.REACH))
        self.add_weapon_improvement(
            Reskin(
                "Lunging Longsword",
                "A telescoping blade mechanism grants this longsword the Reach "
                "property, letting you strike foes 10 feet away.",
            )
        )


class LoremastersRapier(Rapier):
    """A Rapier variant demonstrating AddWeaponDescription: extra text is
    appended to the base weapon's description."""

    def setup_improvements(self) -> None:
        # SetItemName/SetItemValue/SetItemHomebrew individually here, rather
        # than the Reskin bundle, since Reskin's description would *replace*
        # rather than *append to* the base description below.
        self.add_weapon_improvement(SetItemName("Loremaster's Rapier"))
        self.add_weapon_improvement(SetItemValue(None))
        self.add_weapon_improvement(SetItemHomebrew())
        self.add_weapon_improvement(
            AddItemDescription(
                "An inquisitive blade that whispers secrets to its wielder."
            )
        )
        self.add_weapon_improvement(
            AddItemDescription(
                "Once per long rest, you can ask the blade a question about a "
                "creature it has struck; it answers with a single true fact."
            )
        )


class StormcallerMace(Mace):
    """A Mace variant demonstrating AddExtraDamage: bonus damage dice are
    layered on top of the base weapon's."""

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(
            AddExtraDamage(
                WeaponDamageRolls.D6,
                WeaponDamageTypes.LIGHTNING,
                note="crackles with static charge",
            )
        )
        self.add_weapon_improvement(
            Reskin(
                "Stormcaller Mace",
                "Crackling with pent-up static, this mace deals an extra 1d6 "
                "Lightning damage on every hit.",
            )
        )


# ──────────────────────────────────────────────────────────────────────────────
# Magical Weapons
# ──────────────────────────────────────────────────────────────────────────────


class FlameTongueSword(AbstractWeapon):
    """A magical sword wreathed in flames, dealing extra fire damage on hit."""

    def base_stats(self) -> None:
        self.name = "Flame Tongue Sword"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.VERSATILE_10]
        self.mastery = WeaponMastery.TOPPLE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D8
        self.description_text = (
            "This sword is wreathed in magical flames. "
            "It deals an extra 2d6 fire damage on a hit. "
            "Requires attunement (rare)."
        )
        self.extra_damage = [
            ExtraDamage(
                damage_roll=WeaponDamageRolls.D6x2,
                damage_type=WeaponDamageTypes.FIRE,
                note="magical flames",
            )
        ]
        self.rarity = ItemRarity.RARE
        self.requires_attunement = True
        self.add_character_improvement(
            AbilityScoreBonus(
                [(Ability.STRENGTH, 1)],
                total=1,
                error_prefix="Flame Tongue Sword bonus",
            )
        )


class SkirmishersShortsword(Shortsword):
    """A magical Shortsword demonstrating a character-affecting improvement
    (`character_improvements`, i.e. the weapon's own `improvements=` - the
    same mechanism RingOfIntellect uses) rather than a WeaponImprovement: it
    hones the wielder's own footwork, not the blade itself."""

    def base_stats(self) -> None:
        super().base_stats()
        self.rarity = ItemRarity.UNCOMMON
        self.add_character_improvement(
            SkillBonus(Skill.ACROBATICS, 2, source="Skirmisher's Shortsword")
        )

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(
            Reskin(
                "Skirmisher's Shortsword",
                "This lightweight blade trains its wielder's footwork. "
                "While wielding it, you gain a +2 bonus to Dexterity (Acrobatics) checks.",
            )
        )


class VanguardsSpear(Spear):
    """A magical Spear demonstrating a different character-affecting
    improvement (InitiativeRollCondition): it keeps its wielder a half-step
    ahead of danger, granting Advantage on Initiative rolls rather than
    changing anything about the spear's own attack or damage."""

    def base_stats(self) -> None:
        super().base_stats()
        self.rarity = ItemRarity.UNCOMMON
        self.add_character_improvement(
            InitiativeRollCondition(DiceRollCondition.ADVANTAGE)
        )

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(
            Reskin(
                "Vanguard's Spear",
                "This spear hums with a restless energy, sharpening its wielder's "
                "reflexes. While wielding it, you have Advantage on Initiative rolls.",
            )
        )


class HalflingssTrick(Shortsword):
    """A magical shortsword with a +1 bonus to attack and damage rolls.
    Can be hidden within a sleeve and used for silent attacks.
    Forged for stealth and precision."""

    def base_stats(self) -> None:
        super().base_stats()
        self.rarity = ItemRarity.UNCOMMON
        self.description_text = (
            "This finely crafted shortsword is designed to be concealed within a sleeve. "
            "It grants a +1 bonus to attack and damage rolls. When you use it to make "
            "a silent attack, you have advantage on Stealth checks made to conceal the attack."
        )

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(AddAttackRollBonus(1, "Halfling's Trick"))
        self.add_weapon_improvement(AddDamageRollBonus(1, "Halfling's Trick"))
        self.add_weapon_improvement(SetItemName("Halfling's Trick"))


class ModarinsWrath(Maul):
    """A sacred maul from Moradin's altar, empowered by divine fury.
    Has 3 Wrath stacks that degrade when the wielder rolls a 1-3 on attack rolls.
    Deals radiant damage and grows weaker as it degrades, until finally destroyed.

    Stack system: starts at +3 total bonus (distributed across stages).
    Each attack roll of 1-3 destroys the weapon by one stage (loses one Wrath stack).
    At 0 stacks, the weapon is destroyed completely."""

    def base_stats(self) -> None:
        super().base_stats()
        self.rarity = ItemRarity.VERY_RARE
        self.requires_attunement = True
        self.description_text = (
            "A sacred symbol of Moradin, torn from its altar by an outsider cleric. "
            "This maul has 3 Wrath stacks, each granting +1 to attack and damage rolls. "
            "When you roll a 1-3 on an attack roll with this weapon, it is destroyed by one stage, "
            "losing one Wrath stack. At 3 stacks: +3 bonus. At 2 stacks: +2 bonus. At 1 stack: +1 bonus. "
            "At 0 stacks: weapon is destroyed completely. "
            "Damage type: you may choose between Radiant or Bludgeoning damage."
        )

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(AddAttackRollBonus(3, "Wrath Stacks (3/3)"))
        self.add_weapon_improvement(AddDamageRollBonus(3, "Wrath Stacks (3/3)"))
        self.add_weapon_improvement(SetItemName("Moradin's Wrath"))


class AHushedBell(Mace):
    """A magical mace forged to silence curses, with +1 to attack and damage.
    Can disrupt speech and prevent creatures from using abilities requiring
    intelligible speech. Usable twice per short rest."""

    def base_stats(self) -> None:
        super().base_stats()
        self.rarity = ItemRarity.UNCOMMON
        self.requires_attunement = True
        self.description_text = (
            "Forged by the Yellow Capes to silence those who speak the Curse, this massive "
            "bell-shaped mace twists the words of anyone it strikes. Its ringing is never heard—"
            "only the broken speech of its victims. It grants a +1 bonus to attack and damage rolls. "
            "Distorted Speech: When you hit a creature with this mace, you can disrupt its speech for 1 turn. "
            "Until the end of its next turn, it can't speak coherently or use abilities requiring intelligible speech. "
            "You can use this ability twice per short rest."
        )

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(AddAttackRollBonus(1, "A Hushed Bell"))
        self.add_weapon_improvement(AddDamageRollBonus(1, "A Hushed Bell"))
        self.add_weapon_improvement(SetItemName("A Hushed Bell"))


class SulvesburgsFolly(AbstractWeapon):
    """A one-of-a-kind versatile weapon crafted by Clan Sulvesburg, a mining clan
    with no warriors or smiths. Has three modes: Dual Hammer, Two-Handed Hammer, and Segway.
    Switching modes costs a bonus action.

    Dual Hammer mode: two hammers dealing 1d6 each with +1 bonus.
    Two-Handed Hammer mode: deals 1d8 with +1 bonus.
    Segway mode: doubles speed, can only use action for Dismount, Ram, or movement.
    Ram ability (Segway mode): spend movement to ram; target makes DEX save or falls prone.
    """

    def base_stats(self) -> None:
        self.name = "Sulvesburg's Folly"
        self.ability = Ability.STRENGTH
        self.properties = []
        self.mastery = WeaponMastery.PUSH
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.BLUDGEONING
        self.damage_roll = WeaponDamageRolls.D8
        self.weight = 6
        self.rarity = ItemRarity.LEGENDARY
        self.requires_attunement = True
        self.description_text = (
            "A one-of-a-kind weapon crafted by Clan Sulvesburg, a mining clan with neither "
            "warriors nor smiths among its ranks. Born from ingenuity rather than martial expertise, "
            "it is their best—and most unconventional—attempt at building a weapon.\n\n"
            "Versatile Engineering: Switch between three modes as a bonus action.\n"
            "1) Dual Hammer: Wielded as two hammers, each 1d6 damage with +1 attack and damage.\n"
            "2) Two-Handed Hammer: 1d8 damage with +1 attack and damage.\n"
            "3) Segway: Doubles your speed. Can only use your action for Dismount, Ram, or movement.\n\n"
            "Ram (Segway mode only): Spend movement to ram a creature. The target makes a Dexterity "
            "saving throw (DC = 8 + floor(movement spent ÷ 5)) or falls prone."
        )
        self.is_homebrew = True

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(AddAttackRollBonus(1, "Sulvesburg's Folly"))
        self.add_weapon_improvement(AddDamageRollBonus(1, "Sulvesburg's Folly"))


class Lightning(AbstractWeapon):
    """One of a pair of twin magic hammers forged by Clan Stormwill.
    Deals 1d6 damage with +1 to attack and damage rolls.
    Wielder chooses bludgeoning or lightning damage per hit.
    On a hit, gain 1 Storm Charge (max 3, shared with Thunder).
    Twinbound: Can summon Thunder into free hand (within 60 ft)."""

    def base_stats(self) -> None:
        self.name = "Lightning"
        self.ability = Ability.STRENGTH
        self.properties = []
        self.mastery = WeaponMastery.NICK
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponDamageTypes.BLUDGEONING
        self.damage_roll = WeaponDamageRolls.D6
        self.weight = 2
        self.rarity = ItemRarity.VERY_RARE
        self.requires_attunement = True
        self.description_text = (
            "One of a pair of twin hammers forged by Clan Stormwill, the fortress's warrior clan. "
            "This hammer, called Lightning, deals 1d6 damage with +1 to attack and damage rolls. "
            "You may choose bludgeoning or lightning damage per hit. On a hit, gain 1 Storm Charge "
            "(max 3, shared with Thunder).\n"
            "Twinbound: While wielding this hammer, you can summon Thunder into your free hand as long "
            "as it is within 60 feet of you. The two hammers can combine into The Storm when wielded together."
        )
        self.is_homebrew = True

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(AddAttackRollBonus(1, "Lightning"))
        self.add_weapon_improvement(AddDamageRollBonus(1, "Lightning"))
        self.add_weapon_improvement(SetItemName("Lightning"))


class Thunder(AbstractWeapon):
    """One of a pair of twin magic hammers forged by Clan Stormwill.
    Deals 1d6 damage with +1 to attack and damage rolls.
    Wielder chooses bludgeoning or thunder damage per hit.
    On a hit, may expend any number of Storm Charges to deal additional 1d6 damage per charge.
    Twinbound: Can summon Lightning into free hand (within 60 ft)."""

    def base_stats(self) -> None:
        self.name = "Thunder"
        self.ability = Ability.STRENGTH
        self.properties = []
        self.mastery = WeaponMastery.NICK
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponDamageTypes.BLUDGEONING
        self.damage_roll = WeaponDamageRolls.D6
        self.weight = 2
        self.rarity = ItemRarity.VERY_RARE
        self.requires_attunement = True
        self.description_text = (
            "One of a pair of twin hammers forged by Clan Stormwill, the fortress's warrior clan. "
            "This hammer, called Thunder, deals 1d6 damage with +1 to attack and damage rolls. "
            "You may choose bludgeoning or thunder damage per hit. On a hit with Thunder, you may expend "
            "any number of Storm Charges to deal additional 1d6 thunder or lightning damage per charge expended "
            "(max 3 charges total, shared with Lightning).\n"
            "Twinbound: While wielding this hammer, you can summon Lightning into your free hand as long "
            "as it is within 60 feet of you. The two hammers can combine into The Storm when wielded together."
        )
        self.is_homebrew = True

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(AddAttackRollBonus(1, "Thunder"))
        self.add_weapon_improvement(AddDamageRollBonus(1, "Thunder"))
        self.add_weapon_improvement(SetItemName("Thunder"))


class TheStorm(AbstractWeapon):
    """The combined form of Lightning and Thunder when wielded together in both hands.
    Deals 2d6 damage with +1 to attack and damage rolls.
    Each hit grants 1 Storm Charge (max 3).
    Can expend 3 Storm Charges to unleash a storm bolt at a creature within 60 feet:
    5d6 lightning or thunder damage, and the target is knocked prone."""

    def base_stats(self) -> None:
        self.name = "The Storm"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.TWO_HANDED, WeaponProperty.HEAVY]
        self.mastery = WeaponMastery.PUSH
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.BLUDGEONING
        self.damage_roll = WeaponDamageRolls.D6x2
        self.weight = 4
        self.rarity = ItemRarity.LEGENDARY
        self.requires_attunement = True
        self.description_text = (
            "The combined form of Lightning and Thunder when wielded together (both hands). "
            "Forged by Clan Stormwill, the fortress's warrior clan, Thunder and Lightning are a pair of twin "
            "hammers designed to be wielded as one. Their mastery of storm-forged weaponry allows the hammers "
            "to build and unleash devastating power, culminating in their most feared form: The Storm.\n"
            "This two-handed weapon deals 2d6 damage with +1 to attack and damage rolls. "
            "Each hit grants 1 Storm Charge (max 3). You can expend 3 Storm Charges to unleash a storm bolt "
            "at a creature within 60 feet: 5d6 lightning or thunder damage, and the target is knocked prone."
        )
        self.is_homebrew = True

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(AddAttackRollBonus(1, "The Storm"))
        self.add_weapon_improvement(AddDamageRollBonus(1, "The Storm"))
        self.add_weapon_improvement(SetItemName("The Storm"))


### Utility functions
