from Core.Definitions import Ability, WIZARD_HIT_DIE
from Model.Content.Feature import Feature, FeatureTarget
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph


class EvocationSavant(Feature):
    def __init__(self):
        super().__init__(name="Evocation Savant", origin="Evoker Wizard Level 3")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Add Evocation spells to your spellbook for free."),
            Facts(
                (
                    (
                        "Now",
                        "Two Wizard Evocation spells, each no higher than level 2",
                    ),
                    (
                        "New spell slot levels",
                        "Whenever you gain access to a new level of spell slots in this class, one Wizard Evocation spell of a level you have slots for",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Choose two Wizard spells from the Evocation school, each of which must be no higher than level 2, and add them to your spellbook for free.\n"
            "In addition, whenever you gain access to a new level of spell slots in this class, you can add one Wizard spell from the Evocation school to your spellbook for free. The chosen spell must be of a level for which you have spell slots."
        )
        return description


class PotentCantrip(Feature):
    def __init__(self):
        super().__init__(
            name="Potent Cantrip", origin="Evoker Wizard Level 3", usage_tags=["damage"]
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "You cast a cantrip at a creature, and miss with the attack roll or it succeeds on its save",
                    ),
                    (
                        "Effect",
                        "It takes half the cantrip's damage (if any), but no additional effect",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Your damaging cantrips affect even creatures that avoid the brunt of the effect. When you cast a cantrip at a creature and you miss with the attack roll or the target succeeds on a saving throw against the cantrip, the target takes half the cantrip's damage (if any) but suffers no additional effect from the cantrip."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class SculptSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Sculpt Spells", origin="Evoker Wizard Level 6", usage_tags=["buff"]
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Create pockets of relative safety within your evocations."),
            Facts(
                (
                    (
                        "Trigger",
                        "You cast an Evocation spell that affects other creatures you can see",
                    ),
                    ("Protected", "1 + the spell's level of them, your choice"),
                    (
                        "Effect",
                        "They automatically succeed on their saves, and take no damage where they'd take half on a success",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You can create pockets of relative safety within the effects of your evocations. When you cast an Evocation spell that affects other creatures that you can see, you can choose a number of them equal to 1 plus the spell's level. The chosen creatures automatically succeed on their saving throws against the spell, and they take no damage if they would normally take half damage on a successful save."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class EmpoweredEvocation(Feature):
    def __init__(self):
        super().__init__(
            name="Empowered Evocation",
            origin="Evoker Wizard Level 10",
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Applies to", "Wizard spells from the Evocation school"),
                    (
                        "Effect",
                        "Add your Intelligence modifier to one damage roll of the spell",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Whenever you cast a Wizard spell from the Evocation school, you can add your Intelligence modifier to one damage roll of that spell."
        return description


class Overchannel(Feature):
    def __init__(self):
        super().__init__(
            name="Overchannel", origin="Evoker Wizard Level 14", usage_tags=["damage"]
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "You cast a Wizard spell with a level 1-5 spell slot that deals damage",
                    ),
                    ("Effect", "It deals maximum damage on the turn you cast it"),
                    ("First use", "No drawback"),
                    (
                        "Each later use before a Long Rest",
                        "Take 2d12 Necrotic damage per slot level right after casting (ignores Resistance and Immunity); +1d12 per level each further use",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can increase the power of your spells. When you cast a Wizard spell with a spell slot of levels 1-5 that deals damage, you can deal maximum damage with that spell on the turn you cast it.\n"
            "The first time you do so, you suffer no adverse effect. If you use this feature again before you finish a Long Rest, you take 2d12 Necrotic damage for each level of the spell slot immediately after you cast it. This damage ignores Resistance and Immunity.\n"
            "Each time you use this feature again before finishing a Long Rest, the Necrotic damage per spell level increases by 1d12."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF
