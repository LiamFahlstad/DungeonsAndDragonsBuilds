from .Base import Item, ItemCategory, ItemRarity


class BasicPoison(Item):
    def __init__(self):
        super().__init__(
            "Basic Poison",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.POISON,
            weight=None,
            slots=1,
            description_text="As a Bonus Action, you can use a vial of Basic Poison to coat one weapon or up to three pieces of ammunition. A creature that takes Piercing or Slashing damage from the poisoned weapon or ammunition takes an extra 1d4 Poison damage. Once applied, the poison retains potency for 1 minute or until its damage is dealt, whichever comes first.",
            is_homebrew=False,
            value=100,
            is_consumable=True,
        )
