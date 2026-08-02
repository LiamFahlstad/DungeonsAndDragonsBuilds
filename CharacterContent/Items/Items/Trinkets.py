from Core.Definitions import Ability, Skill
from CharacterContent.Features.Core.Improvements import AbilityScoreBonus, SkillBonus
from .Base import Item, ItemCategory, ItemRarity


class FingerGunRing(Item):
    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Ring of Finger Guns",
            rarity=ItemRarity.COMMON,
            category=ItemCategory.TRINKETS,
            slots=0,
            description_text=(
                "While wearing this ring, forming finger guns and saying 'pew' creates a tiny harmless spark "
                "and sound effect. The spark can light candles but deals no damage."
            ),
            is_wearing=is_wearing,
        )


class RingOfIntellect(Item):
    """A mystical ring that increases Intelligence by 2."""

    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Ring of Intellect",
            rarity=ItemRarity.RARE,
            requires_attunement=True,
            category=ItemCategory.TRINKETS,
            description_text=(
                "While wearing this ring, your Intelligence score increases by 2, as does your Intelligence saving throw.\n\n"
                "This silver ring is inscribed with arcane runes that glow faintly when worn."
            ),
            is_wearing=is_wearing,
            improvements=[
                AbilityScoreBonus(
                    bonuses=[(Ability.INTELLIGENCE, 2)],
                    total=2,
                    error_prefix="Ring of Intellect bonus",
                )
            ],
        )


class RingOfInvestigation(Item):
    """A ring that grants +1 to Investigation checks."""

    def __init__(self, is_wearing: bool = True):
        super().__init__(
            "Ring of Investigation",
            rarity=ItemRarity.UNCOMMON,
            requires_attunement=False,
            category=ItemCategory.TRINKETS,
            description_text=(
                "While wearing this ring, you gain a +1 bonus to Intelligence (Investigation) checks.\n\n"
                "A slender copper band set with a tiny magnifying lens that focuses the wearer's attention on overlooked details."
            ),
            is_wearing=is_wearing,
            improvements=[
                SkillBonus(Skill.INVESTIGATION, 1, source="Ring of Investigation")
            ],
        )


# Placeholder Craftable Items (TODO: fill in real stats)
