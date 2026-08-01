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
from .Enums import WeaponMastery, WeaponProperty, WeaponType, WeaponsDamageRolls, WeaponsDamageTypes
from .Improvements import AddAttackRollBonus, AddDamageRollBonus, AddExtraDamage, AddWeaponProperty, ExtraDamage, SetAttackRollBonus, SetDamageDie, SetDamageRollBonus, SetDamageType
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
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D8
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
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D8
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
        self.damage_type = WeaponsDamageTypes.PIERCING
        self.damage_roll = WeaponsDamageRolls.D10
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
        self.properties = [WeaponProperty.FINESSE]
        self.mastery = WeaponMastery.NICK
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D6
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
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D8
        self.description_text = description
        self.is_homebrew = True


class ElementalSword(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Elemental Sword"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.VERSATILE_10]
        self.mastery = WeaponMastery.GRAZE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D8
        self.description_text = (
            "As a bonus action, choose acid, cold, fire, lightning, or thunder. "
            "The weapon deals an extra 1d6 damage of the chosen type on hit."
        )
        self.extra_damage = [
            ExtraDamage(
                damage_roll=WeaponsDamageRolls.D6,
                damage_type=WeaponsDamageTypes.FIRE,
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
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D8
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
        self.properties = [WeaponProperty.FINESSE]
        self.mastery = WeaponMastery.NICK
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D6
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
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D12
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
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D8
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
        self.add_weapon_improvement(SetDamageDie(WeaponsDamageRolls.D12x2))
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
        self.add_weapon_improvement(SetDamageType(WeaponsDamageTypes.COLD))
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
            AddItemDescription("An inquisitive blade that whispers secrets to its wielder.")
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
                WeaponsDamageRolls.D6,
                WeaponsDamageTypes.LIGHTNING,
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
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D8
        self.description_text = (
            "This sword is wreathed in magical flames. "
            "It deals an extra 2d6 fire damage on a hit. "
            "Requires attunement (rare)."
        )
        self.extra_damage = [
            ExtraDamage(
                damage_roll=WeaponsDamageRolls.D6x2,
                damage_type=WeaponsDamageTypes.FIRE,
                note="magical flames",
            )
        ]
        self.rarity = ItemRarity.RARE
        self.requires_attunement = True
        self.add_character_improvement(
            AbilityScoreBonus(
                [(Ability.STRENGTH, 1)], total=1, error_prefix="Flame Tongue Sword bonus"
            )
        )


class SkirmishersShortsword(Shortsword):
    """A magical Shortsword demonstrating a character-affecting improvement
    (`character_improvements`, i.e. the weapon's own `improvements=` - the
    same mechanism RingOfIntelligence uses) rather than a WeaponImprovement: it
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
        self.add_character_improvement(InitiativeRollCondition(DiceRollCondition.ADVANTAGE))

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(
            Reskin(
                "Vanguard's Spear",
                "This spear hums with a restless energy, sharpening its wielder's "
                "reflexes. While wielding it, you have Advantage on Initiative rolls.",
            )
        )


### Utility functions
