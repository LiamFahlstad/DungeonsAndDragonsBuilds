from Core.Definitions import Ability
from CharacterContent.Features.Core.Improvements import AbilityScoreBonus
from .Base import Item, ItemCategory, ItemRarity


class ButterflyKnife(Item):
    def __init__(self):
        super().__init__(
            "Butterfly Knife",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.WEAPON,
            slots=1,
            description_text=(
                "A small folding knife that can be quickly deployed. "
                "Functions as a light melee weapon."
            ),
        )


class Makarov(Item):
    def __init__(self):
        super().__init__(
            "Makarov",
            rarity=ItemRarity.UNCOMMON,
            category=ItemCategory.WEAPON,
            slots=1,
            description_text=(
                "In a fantasy realm, this pistol becomes a magical ranged weapon.\n\n"
                "It has 4 charges. Each shot deals 2d6 + your Dexterity modifier damage. "
                "The weapon regains all charges after a long rest."
            ),
        )


class PlusOneWeapon(Item):
    """A magical weapon that grants +1 to ability scores (e.g. Dexterity for finesse weapons)."""

    def __init__(
        self, weapon_name: str = "Longsword", ability: Ability = Ability.DEXTERITY
    ):
        self.ability = ability
        super().__init__(
            f"+1 {weapon_name}",
            rarity=ItemRarity.UNCOMMON,
            category=ItemCategory.WEAPON,
            description_text=(
                f"This magical {weapon_name.lower()} grants you a +1 bonus to attack rolls and damage rolls made with it.\n\n"
                "The blade gleams with enchantment."
            ),
            improvements=[
                AbilityScoreBonus(
                    bonuses=[(ability, 1)],
                    total=1,
                    error_prefix=f"+1 {weapon_name} bonus",
                )
            ],
            is_homebrew=False,
        )


class Net(Item):
    def __init__(self):
        super().__init__(
            "Net",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.WEAPON,
            weight=3,
            slots=1,
            description_text="When you take the Attack action, you can replace one of your attacks with throwing a Net. Target a creature you can see within 15 feet of yourself. The target must succeed on a Dexterity saving throw (DC 8 plus your Dexterity modifier and Proficiency Bonus) or have the Restrained condition until it escapes. To escape, the target or a creature within 5 feet of it must take an action to make a DC 10 Strength (Athletics) check, freeing the Restrained creature on a success.",
            is_homebrew=False,
            value=1,
        )
