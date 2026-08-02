from .Base import ConsumableItem, ItemCategory, ItemRarity


class PotionOfHealing(ConsumableItem):
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
        )


class GreaterHealingPotion(ConsumableItem):
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
        )


class SuperiorHealingPotion(ConsumableItem):
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
        )


class SupremeHealingPotion(ConsumableItem):
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
        )


class CleansingPotion(ConsumableItem):
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
        )


class RefreshingPotion(ConsumableItem):
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
        )


class PotionOfFeatherFall(ConsumableItem):
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
        )


class PotionOfInvisibility(ConsumableItem):
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
        )


class PotionOfDisguise(ConsumableItem):
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
        )


class PotionOfSwiftness(ConsumableItem):
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
        )


class PotionOfEnlarge(ConsumableItem):
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
        )


class PotionOfTeleportation(ConsumableItem):
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
        )


class PotionOfResistance(ConsumableItem):
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
        )


class PotionOfSpeed(ConsumableItem):
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
        )


class GreaterPotionOfSpeed(ConsumableItem):
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
        )


class PotionOfResolve(ConsumableItem):
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
        )


class PotionOfGuarding(ConsumableItem):
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
        )
