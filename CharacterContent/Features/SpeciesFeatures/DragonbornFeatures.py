from enum import Enum

import Core.Definitions as Definitions
from CharacterContent.Features.Core.BaseFeatures import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from CharacterContent.Features.Core.Improvements import (
    DamageResistance as DamageResistanceImprovement,
)
from Core.Definitions import CreatureSize
from Model.Effects import Effects
from Core.Rules import MAX_PROFICIENCY_BONUS
from Model.View import CharacterView

SPEED = 30  # Given by your species
SIZE = CreatureSize.MEDIUM  # Given by your species


class DragonColor(str, Enum):
    BLACK = "Black"
    BLUE = "Blue"
    BRASS = "Brass"
    BRONZE = "Bronze"
    COPPER = "Copper"
    GOLD = "Gold"
    GREEN = "Green"
    RED = "Red"
    SILVER = "Silver"
    WHITE = "White"


class DamageResistance(Feature):
    def __init__(self, dragon_color: DragonColor):
        self.color = dragon_color
        self.damage_type = get_damage_type_from_color(dragon_color)
        super().__init__(
            name="Damage Resistance",
            origin="Dragonborn Trait",
            skippable_in_concise=True,
            usage_tags=["buff"],
        )
        self._resistance = DamageResistanceImprovement(self.damage_type, self.name)

    def apply(self, effects: Effects):
        self._resistance.apply(effects)

    def get_description(self, character: CharacterView) -> str:
        return f"You have Resistance against {self.damage_type.value} damage because your Draconic Ancestry is {self.color.value} dragon."


class BreathWeapon(Feature):
    def __init__(self, dragon_color: DragonColor):
        self.color = dragon_color
        self.damage_type = get_damage_type_from_color(dragon_color)
        super().__init__(
            name="Breath Weapon",
            origin="Dragonborn Trait",
            activation=FeatureActivation(range="15-Foot Cone or 30-Foot Line"),
            usage_tags=["damage"],
            uses=FeatureUses(
                max_uses=MAX_PROFICIENCY_BONUS,
                current_formula="Current amount: equal to your proficiency bonus.",
            ),
        )

    def get_description(self, character: CharacterView) -> str:
        text = (
            "When you take the Attack action on your turn, you can replace one of your attacks with an exhalation of magical energy in either a 15-foot Cone or a 30-foot Line that is 5 feet wide (choose the shape each time). Each creature in that area must make a Dexterity saving throw (DC 8 plus your Constitution modifier and Proficiency Bonus).\n"
            f"On a failed save, a creature takes {self.damage_type.value} damage because your Draconic Ancestry is {self.color.value} dragon. The damage increases as you gain levels, as shown in the Breath Weapon column of the Dragonborn Features table. On a successful save, a creature takes half as much damage.\n"
            "You can use this Breath Weapon a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest."
        )
        return text

    def calculate_dc(self, character: CharacterView) -> int:
        constitution_modifier = character.get_constitution_modifier()
        proficiency_bonus = character.get_proficiency_bonus()
        return 8 + constitution_modifier + proficiency_bonus

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.AREA

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def get_table_description(self, character: CharacterView) -> list[tuple[str, str]]:
        proficiency_bonus = character.get_proficiency_bonus()

        if character.character_level < 5:
            damage = "1d10"
        elif character.character_level < 11:
            damage = "2d10"
        elif character.character_level < 17:
            damage = "3d10"
        else:
            damage = "4d10"

        save_dc = self.calculate_dc(character)

        return [
            ("Trigger", "Replace one attack when taking Attack action"),
            ("Shape", "15-foot Cone or 30-foot Line (5 feet wide)"),
            ("Save", f"Dexterity DC {save_dc} (8 + CON mod + proficiency)"),
            ("Damage", f"{damage} {self.damage_type.value}"),
            ("Effect", "Full damage on failed save, half on success"),
            ("Uses", f"{proficiency_bonus} per Long Rest"),
        ]


class DraconicFlight(Feature):
    def __init__(self):
        super().__init__(
            name="Draconic Flight",
            origin="Dragonborn Trait",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, duration="10 Minutes"
            ),
            usage_tags=["buff", "utility"],
        )

    def get_description(self, character: CharacterView) -> str:
        text = "When you reach character level 5, you can channel draconic magic to give yourself temporary flight. As a Bonus Action, you sprout spectral wings on your back that last for 10 minutes or until you retract the wings (no action required) or have the Incapacitated condition. During that time, you have a Fly Speed equal to your Speed. Your wings appear to be made of the same energy as your Breath Weapon. Once you use this trait, you can't use it again until you finish a Long Rest."
        return text

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


def get_damage_type_from_color(dragon_color: DragonColor) -> Definitions.DamageType:
    dragon_damage_type = {
        DragonColor.BLACK: Definitions.DamageType.ACID,
        DragonColor.BLUE: Definitions.DamageType.LIGHTNING,
        DragonColor.BRASS: Definitions.DamageType.FIRE,
        DragonColor.BRONZE: Definitions.DamageType.LIGHTNING,
        DragonColor.COPPER: Definitions.DamageType.ACID,
        DragonColor.GOLD: Definitions.DamageType.FIRE,
        DragonColor.GREEN: Definitions.DamageType.POISON,
        DragonColor.RED: Definitions.DamageType.FIRE,
        DragonColor.SILVER: Definitions.DamageType.COLD,
        DragonColor.WHITE: Definitions.DamageType.COLD,
    }
    return dragon_damage_type[dragon_color]
