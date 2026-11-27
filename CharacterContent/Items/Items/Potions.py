from dataclasses import replace

from Core.Definitions import Ability, Condition, DamageType
from Model.Content.ActionType import ActionType
from Model.Content.CombatEffect import (
    CombatCondition,
    CombatEffect,
    CombatHitPoints,
    TurnEdge,
    TurnOf,
)
from Model.Content.CombatModifiers import (
    ArmorClass,
    D20Mode,
    D20Test,
    EndEvent,
    EndsWhen,
    Note,
    Resistance,
    RollMode,
    Size,
    Speed,
)
from Model.Content.Item import Item, ItemCategory, ItemRarity
from Model.View import CharacterView

HOUR = 60 * 60
# Drinking a potion, or giving it to a creature within 5 feet, takes a Bonus
# Action (2024 rules). Its count stays on the sheet: the fight doesn't track
# what a character carries (plan step 9.8).
USED_UP = "Drinking it uses one up: take it off the sheet's inventory."


def _drunk(**fields) -> CombatEffect:
    """A potion's row: a Bonus Action, its note that it's used up."""
    notes = (*fields.pop("notes", ()), USED_UP)
    return CombatEffect(action_type=ActionType.BONUS_ACTION, notes=notes, **fields)


def _on_drinker(
    badge: str, *modifiers, seconds: int = HOUR, until=None
) -> CombatEffect:
    """A potion that gives its drinker a badge with `modifiers`."""
    return _drunk(
        conditions=(
            CombatCondition(
                badge,
                duration_seconds=None if until else seconds,
                until=until,
                modifiers=tuple(modifiers),
            ),
        ),
        targets_self=True,
    )


class PotionOfHealing(Item):
    def __init__(self):
        super().__init__(
            "Potion of Healing",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.POTION,
            slots=1,
            description_text=(
                "You regain 2d4 + 2 Hit Points when you drink this potion.\n"
                "Whatever its potency, the potion's red liquid glimmers when agitated."
            ),
            is_homebrew=False,
            value=50,
            is_consumable=True,
        )

    def combat_effects(self, character: CharacterView) -> list[CombatEffect]:
        # "You regain 2d4 + 2 Hit Points when you drink this potion."
        return [_drunk(healing=CombatHitPoints("2d4 + 2"))]


class GreaterHealingPotion(Item):
    def __init__(self):
        super().__init__(
            "Greater Healing Potion",
            rarity=ItemRarity.UNCOMMON,
            category=ItemCategory.POTION,
            slots=1,
            description_text=(
                "You regain 4d4 + 4 Hit Points when you drink this potion.\n"
                "The potion's amber liquid swirls with golden flecks."
            ),
            is_homebrew=False,
            value=150,
            is_consumable=True,
        )

    def combat_effects(self, character: CharacterView) -> list[CombatEffect]:
        # "You regain 4d4 + 4 Hit Points"
        return [_drunk(healing=CombatHitPoints("4d4 + 4"))]


class SuperiorHealingPotion(Item):
    def __init__(self):
        super().__init__(
            "Superior Healing Potion",
            rarity=ItemRarity.RARE,
            category=ItemCategory.POTION,
            slots=1,
            description_text=(
                "You regain 8d4 + 8 Hit Points when you drink this potion.\n"
                "The potion's violet liquid radiates a warm, healing glow."
            ),
            is_homebrew=False,
            value=500,
            is_consumable=True,
        )

    def combat_effects(self, character: CharacterView) -> list[CombatEffect]:
        # "You regain 8d4 + 8 Hit Points"
        return [_drunk(healing=CombatHitPoints("8d4 + 8"))]


class SupremeHealingPotion(Item):
    def __init__(self):
        super().__init__(
            "Supreme Healing Potion",
            rarity=ItemRarity.VERY_RARE,
            category=ItemCategory.POTION,
            slots=1,
            description_text=(
                "You regain 10d4 + 20 Hit Points when you drink this potion.\n"
                "The potion's silver liquid glows with brilliant light."
            ),
            is_homebrew=False,
            value=1500,
            is_consumable=True,
        )

    def combat_effects(self, character: CharacterView) -> list[CombatEffect]:
        # "You regain 10d4 + 20 Hit Points"
        return [_drunk(healing=CombatHitPoints("10d4 + 20"))]


class CleansingPotion(Item):
    def __init__(self):
        super().__init__(
            "Cleansing Potion",
            rarity=ItemRarity.UNCOMMON,
            category=ItemCategory.POTION,
            slots=1,
            description_text=(
                "When you drink this potion, one condition affecting you ends.\n"
                "The potion's clear liquid sparkles with faint magical energy."
            ),
            is_homebrew=True,
            value=150,
            is_consumable=True,
        )


class RefreshingPotion(Item):
    def __init__(self):
        super().__init__(
            "Refreshing Potion",
            rarity=ItemRarity.UNCOMMON,
            category=ItemCategory.POTION,
            slots=1,
            description_text=(
                "When you drink this potion, you gain the benefits of a short rest.\n"
                "The potion tastes of refreshing citrus and herbs."
            ),
            is_homebrew=True,
            value=150,
            is_consumable=True,
        )


class PotionOfFeatherFall(Item):
    def __init__(self):
        super().__init__(
            "Potion of Feather Fall",
            rarity=ItemRarity.UNCOMMON,
            category=ItemCategory.POTION,
            slots=1,
            description_text=(
                "When you drink this potion, you gain the effects of the Feather Fall spell.\n"
                "The effect lasts for 1 minute or until you land, whichever comes first."
            ),
            is_homebrew=True,
            value=150,
            is_consumable=True,
        )


class PotionOfInvisibility(Item):
    def __init__(self):
        super().__init__(
            "Potion of Invisibility",
            rarity=ItemRarity.RARE,
            category=ItemCategory.POTION,
            slots=1,
            description_text=(
                "When you drink this potion, you become invisible for 1 hour.\n"
                "The effect ends if you attack, cast a spell, or become incapacitated."
            ),
            is_homebrew=True,
            value=500,
            is_consumable=True,
        )

    def combat_effects(self, character: CharacterView) -> list[CombatEffect]:
        # "you become invisible for 1 hour. The effect ends if you attack,
        # cast a spell, or become incapacitated."
        ends = EndsWhen(
            (EndEvent.ATTACKS, EndEvent.CASTS_SPELL, EndEvent.INCAPACITATED)
        )
        return [
            _drunk(
                conditions=(
                    CombatCondition(Condition.INVISIBLE, duration_seconds=HOUR),
                    CombatCondition(
                        self.name, duration_seconds=HOUR, modifiers=(ends,)
                    ),
                ),
                targets_self=True,
            )
        ]


class PotionOfDisguise(Item):
    def __init__(self):
        super().__init__(
            "Potion of Disguise",
            rarity=ItemRarity.UNCOMMON,
            category=ItemCategory.POTION,
            slots=1,
            description_text=(
                "When you drink this potion, you can transform to appear as another humanoid of the same size.\n"
                "The disguise lasts for 1 hour or until you dismiss it as a bonus action."
            ),
            is_homebrew=True,
            value=150,
            is_consumable=True,
        )


class PotionOfSwiftness(Item):
    def __init__(self):
        super().__init__(
            "Potion of Swiftness",
            rarity=ItemRarity.UNCOMMON,
            category=ItemCategory.POTION,
            slots=1,
            description_text=(
                "When you drink this potion, your movement speed increases by 10 feet for 1 hour.\n"
                "The effect ends early if you become incapacitated."
            ),
            is_homebrew=True,
            value=150,
            is_consumable=True,
        )

    def combat_effects(self, character: CharacterView) -> list[CombatEffect]:
        # "your movement speed increases by 10 feet for 1 hour. The effect
        # ends early if you become incapacitated."
        return [
            _on_drinker(self.name, Speed(bonus=10), EndsWhen((EndEvent.INCAPACITATED,)))
        ]


class PotionOfEnlarge(Item):
    def __init__(self):
        super().__init__(
            "Potion of Enlarge",
            rarity=ItemRarity.UNCOMMON,
            category=ItemCategory.POTION,
            slots=1,
            description_text=(
                "When you drink this potion, your size increases by one category for 1 hour.\n"
                "You gain advantage on Strength checks and Strength saving throws, and your weapon attacks deal an extra 1d4 damage."
            ),
            is_homebrew=True,
            value=150,
            is_consumable=True,
        )

    def combat_effects(self, character: CharacterView) -> list[CombatEffect]:
        # "your size increases by one category for 1 hour. You gain advantage
        # on Strength checks and Strength saving throws, and your weapon
        # attacks deal an extra 1d4 damage."
        return [
            _on_drinker(
                self.name,
                Size(steps=1),
                D20Mode(
                    (D20Test.ABILITY_CHECK, D20Test.SAVING_THROW),
                    RollMode.ADVANTAGE,
                    (Ability.STRENGTH,),
                ),
                Note("Its weapon attacks deal an extra 1d4 damage"),
            )
        ]


class PotionOfTeleportation(Item):
    def __init__(self):
        super().__init__(
            "Potion of Teleportation",
            rarity=ItemRarity.RARE,
            category=ItemCategory.POTION,
            slots=1,
            description_text=(
                "When you drink this potion, you can teleport to a location you can see within 60 feet.\n"
                "Any equipment you are wearing or carrying teleports with you."
            ),
            is_homebrew=True,
            value=500,
            is_consumable=True,
        )


class PotionOfResistance(Item):
    def __init__(self):
        super().__init__(
            "Potion of Resistance",
            rarity=ItemRarity.UNCOMMON,
            category=ItemCategory.POTION,
            slots=1,
            description_text=(
                "When you drink this potion, you gain resistance to one non-physical damage type of your choice for 1 hour.\n"
                "Non-physical damage types include acid, cold, fire, force, lightning, necrotic, psychic, radiant, and thunder."
            ),
            is_homebrew=True,
            value=150,
            is_consumable=True,
        )

    def combat_effects(self, character: CharacterView) -> list[CombatEffect]:
        # "resistance to one non-physical damage type of your choice for 1
        # hour": a row per type.
        types = (
            DamageType.ACID,
            DamageType.COLD,
            DamageType.FIRE,
            DamageType.FORCE,
            DamageType.LIGHTNING,
            DamageType.NECROTIC,
            DamageType.PSYCHIC,
            DamageType.RADIANT,
            DamageType.THUNDER,
        )
        return [
            replace(
                _on_drinker(f"{self.name}: {kind.value}", Resistance((kind,))),
                name=f"{self.name}: {kind.value}",
            )
            for kind in types
        ]


class PotionOfSpeed(Item):
    def __init__(self):
        super().__init__(
            "Potion of Speed",
            rarity=ItemRarity.UNCOMMON,
            category=ItemCategory.POTION,
            slots=1,
            description_text=(
                "When you drink this potion, your movement speed increases by 5 feet for 1 hour.\n"
                "The effect ends early if you become incapacitated."
            ),
            is_homebrew=True,
            value=150,
            is_consumable=True,
        )

    def combat_effects(self, character: CharacterView) -> list[CombatEffect]:
        # "your movement speed increases by 5 feet for 1 hour ... ends early
        # if you become incapacitated."
        return [
            _on_drinker(self.name, Speed(bonus=5), EndsWhen((EndEvent.INCAPACITATED,)))
        ]


class GreaterPotionOfSpeed(Item):
    def __init__(self):
        super().__init__(
            "Greater Potion of Speed",
            rarity=ItemRarity.UNCOMMON,
            category=ItemCategory.POTION,
            slots=1,
            description_text=(
                "When you drink this potion, your movement speed increases by 10 feet for 1 hour.\n"
                "The effect ends early if you become incapacitated."
            ),
            is_homebrew=True,
            value=150,
            is_consumable=True,
        )

    def combat_effects(self, character: CharacterView) -> list[CombatEffect]:
        # "your movement speed increases by 10 feet for 1 hour ... ends
        # early if you become incapacitated."
        return [
            _on_drinker(self.name, Speed(bonus=10), EndsWhen((EndEvent.INCAPACITATED,)))
        ]


class PotionOfResolve(Item):
    def __init__(self):
        super().__init__(
            "Potion of Resolve",
            rarity=ItemRarity.RARE,
            category=ItemCategory.POTION,
            slots=1,
            description_text=(
                "When you drink this potion, you automatically succeed on the next saving throw you make.\n"
                "The effect ends after you succeed on a save or after 1 hour, whichever comes first."
            ),
            is_homebrew=True,
            value=500,
            is_consumable=True,
        )

    def combat_effects(self, character: CharacterView) -> list[CombatEffect]:
        # "you automatically succeed on the next saving throw you make. The
        # effect ends after you succeed on a save or after 1 hour".
        return [
            _on_drinker(
                self.name, Note("Succeeds automatically on its next saving throw")
            )
        ]


class PotionOfGuarding(Item):
    def __init__(self):
        super().__init__(
            "Potion of Guarding",
            rarity=ItemRarity.UNCOMMON,
            category=ItemCategory.POTION,
            slots=1,
            description_text=(
                "When you drink this potion as a bonus action, you gain +2 to your AC until the start of your next turn.\n"
                "This benefit applies regardless of what armor or shield you are wearing."
            ),
            is_homebrew=True,
            value=150,
            is_consumable=True,
        )

    def combat_effects(self, character: CharacterView) -> list[CombatEffect]:
        # "you gain +2 to your AC until the start of your next turn"
        return [
            _on_drinker(self.name, ArmorClass(2), until=(TurnEdge.START, TurnOf.SOURCE))
        ]
