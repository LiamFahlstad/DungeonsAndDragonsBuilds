from enum import Enum

from Core.Definitions import CreatureSize
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from Core.Rules import PROFICIENCY_BONUS_GAINED_AT, MAX_PROFICIENCY_BONUS
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph
from Model.Content.CombatEffect import (
    CombatCondition,
    CombatDamage,
    CombatEffect,
    TurnEdge,
    TurnOf,
)
from Model.Content.CombatModifiers import D20Mode, D20Test, RollMode
from Model.Content.CombatTriggers import CombatTrigger, TriggerEvent
from Core.Definitions import Ability, Condition, DamageType

SPEED = 35  # Given by your species
SIZE = CreatureSize.MEDIUM  # Given by your species


class GiantAncestryType(str, Enum):
    CLOUD_GIANT = "Cloud Giant"
    FIRE_GIANT = "Fire Giant"
    FROST_GIANT = "Frost Giant"
    HILL_GIANT = "Hill Giant"
    STONE_GIANT = "Stone Giant"
    STORM_GIANT = "Storm Giant"


class LargeForm(Feature):
    def __init__(self):
        super().__init__(
            name="Large Form",
            origin="Goliath Trait",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, duration="10 Minutes"
            ),
            usage_tags=["buff"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Paragraph("From character level 5, grow to Large if there's room."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    (
                        "Duration",
                        "10 minutes, or until you end it (no action required)",
                    ),
                    ("Effect", "Advantage on Strength checks, and Speed +10 feet"),
                    ("Limit", "Once per Long Rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return "Starting at character level 5, you can change your size to Large as a Bonus Action if you're in a big enough space. This transformation lasts for 10 minutes or until you end it (no action required). For that duration, you have Advantage on Strength checks, and your Speed increases by 10 feet. Once you use this trait, you can't use it again until you finish a Long Rest."

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def combat_effects(self, character: CharacterView) -> list[CombatEffect]:
        if character.character_level < 5:
            return []  # not before character level 5
        return [
            CombatEffect(
                conditions=(
                    CombatCondition(
                        "Large Form",
                        modifiers=(
                            D20Mode(
                                (D20Test.ABILITY_CHECK,),
                                RollMode.ADVANTAGE,
                                (Ability.STRENGTH,),
                            ),
                        ),
                    ),
                ),
                notes=(
                    "Pick yourself as the target, if there's room to be Large."
                    " Your size is Large and your Speed increases by 10 feet. You"
                    " can end it early (no action).",
                ),
            )
        ]


class PowerfulBuild(Feature):
    def __init__(self):
        super().__init__(
            name="Powerful Build", origin="Goliath Trait", usage_tags=["buff"]
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Grappled", "Advantage on ability checks to end the condition"),
                    (
                        "Carrying capacity",
                        "You count as one size larger when determining it",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return "You have Advantage on any ability check you make to end the Grappled condition. You also count as one size larger when determining your carrying capacity."

    def combat_effects(self, character: CharacterView) -> list[CombatEffect]:
        # Its owner's own ability checks and carrying capacity.
        return []


# The benefits that take a Bonus Action or a Reaction; the rest ride on a hit.
_GIANT_ANCESTRY_ACTION = {
    GiantAncestryType.CLOUD_GIANT: ActionType.BONUS_ACTION,
    GiantAncestryType.STONE_GIANT: ActionType.REACTION,
    GiantAncestryType.STORM_GIANT: ActionType.REACTION,
}


class GiantAncestry(Feature):
    def __init__(self, giant_ancestry_type: GiantAncestryType):
        self.giant_ancestry_type = giant_ancestry_type
        super().__init__(
            name="Giant Ancestry",
            origin="Goliath Trait",
            activation=FeatureActivation(
                action_type=_GIANT_ANCESTRY_ACTION.get(giant_ancestry_type)
            ),
            usage_tags=["buff", "damage", "control"],
            uses=FeatureUses(
                max_uses=MAX_PROFICIENCY_BONUS,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your proficiency bonus.",
                gained_at=PROFICIENCY_BONUS_GAINED_AT,
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses are in the panel below.
        benefit = {
            GiantAncestryType.CLOUD_GIANT: (
                "Cloud's Jaunt",
                (
                    ("Action", "Bonus Action"),
                    (
                        "Effect",
                        "Teleport up to 30 feet to an unoccupied space you can see",
                    ),
                ),
            ),
            GiantAncestryType.FIRE_GIANT: (
                "Fire's Burn",
                (
                    (
                        "Trigger",
                        "You hit a target with an attack roll and deal damage to it",
                    ),
                    ("Damage", "+1d10 Fire damage"),
                ),
            ),
            GiantAncestryType.FROST_GIANT: (
                "Frost's Chill",
                (
                    (
                        "Trigger",
                        "You hit a target with an attack roll and deal damage to it",
                    ),
                    (
                        "Effect",
                        "+1d6 Cold damage, and its Speed drops by 10 feet until the start of your next turn",
                    ),
                ),
            ),
            GiantAncestryType.HILL_GIANT: (
                "Hill's Tumble",
                (
                    (
                        "Trigger",
                        "You hit a Large or smaller creature with an attack roll and deal damage to it",
                    ),
                    ("Effect", "It has the Prone condition"),
                ),
            ),
            GiantAncestryType.STONE_GIANT: (
                "Stone's Endurance",
                (
                    ("Action", "Reaction"),
                    ("Trigger", "You take damage"),
                    ("Effect", "Reduce the damage by 1d12 + Constitution modifier"),
                ),
            ),
            GiantAncestryType.STORM_GIANT: (
                "Storm's Thunder",
                (
                    ("Action", "Reaction"),
                    ("Trigger", "A creature within 60 feet of you damages you"),
                    ("Damage", "1d8 Thunder damage to that creature"),
                ),
            ),
        }[self.giant_ancestry_type]
        name, rows = benefit
        return [
            Paragraph(
                f"A supernatural boon from your {self.giant_ancestry_type.value} ancestry."
            ),
            Option(name, (Facts(rows),)),
        ]

    def get_description(self, character: CharacterView) -> str:
        text = "You are descended from Giants. You chose the following benefit, a supernatural boon from your ancestry.\n"
        if self.giant_ancestry_type == GiantAncestryType.CLOUD_GIANT:
            text += "Cloud's Jaunt (Cloud Giant). As a Bonus Action, you magically teleport up to 30 feet to an unoccupied space you can see.\n"
        if self.giant_ancestry_type == GiantAncestryType.FIRE_GIANT:
            text += "Fire's Burn (Fire Giant). When you hit a target with an attack roll and deal damage to it, you can also deal 1d10 Fire damage to that target.\n"
        if self.giant_ancestry_type == GiantAncestryType.FROST_GIANT:
            text += "Frost's Chill (Frost Giant). When you hit a target with an attack roll and deal damage to it, you can also deal 1d6 Cold damage to that target and reduce its Speed by 10 feet until the start of your next turn.\n"
        if self.giant_ancestry_type == GiantAncestryType.HILL_GIANT:
            text += "Hill's Tumble (Hill Giant). When you hit a Large or smaller creature with an attack roll and deal damage to it, you can give that target the Prone condition.\n"
        if self.giant_ancestry_type == GiantAncestryType.STONE_GIANT:
            text += "Stone's Endurance (Stone Giant). When you take damage, you can take a Reaction to roll 1d12. Add your Constitution modifier to the number rolled and reduce the damage by that total.\n"
        if self.giant_ancestry_type == GiantAncestryType.STORM_GIANT:
            text += "Storm's Thunder (Storm Giant). When you take damage from a creature within 60 feet of you, you can take a Reaction to deal 1d8 Thunder damage to that creature.\n"
        text += "You can use the chosen benefit a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest."
        if self.giant_ancestry_type == GiantAncestryType.STONE_GIANT:
            text += f"\nRight now you reduce the damage by 1d12 + {character.get_constitution_modifier()}."
        return text

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        if self.giant_ancestry_type == GiantAncestryType.CLOUD_GIANT:
            return FeatureTarget.SELF
        if self.giant_ancestry_type == GiantAncestryType.STONE_GIANT:
            return FeatureTarget.SELF
        return FeatureTarget.ENEMY

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def combat_effects(self, character: CharacterView) -> list[CombatEffect]:
        # "When you hit a target with an attack roll and deal damage to it,
        # you can ...": asked as the hit lands (Combat/Effects/triggers.py).
        on_hit = CombatTrigger(TriggerEvent.HIT, needs_damage=True)
        effect = {
            GiantAncestryType.CLOUD_GIANT: CombatEffect(
                name="Cloud's Jaunt",
                notes=(
                    "You teleport up to 30 feet to an unoccupied space you can"
                    " see: nothing happens to the targets.",
                ),
            ),
            GiantAncestryType.FIRE_GIANT: CombatEffect(
                name="Fire's Burn",
                damage=(CombatDamage("1d10", DamageType.FIRE),),
                trigger=on_hit,
            ),
            GiantAncestryType.FROST_GIANT: CombatEffect(
                name="Frost's Chill",
                damage=(CombatDamage("1d6", DamageType.COLD),),
                conditions=(
                    CombatCondition(
                        "Frost's Chill", until=(TurnEdge.START, TurnOf.SOURCE)
                    ),
                ),
                notes=("Its Speed is 10 feet less while it has the badge.",),
                trigger=on_hit,
            ),
            GiantAncestryType.HILL_GIANT: CombatEffect(
                name="Hill's Tumble",
                conditions=(CombatCondition(Condition.PRONE),),
                trigger=CombatTrigger(
                    TriggerEvent.HIT,
                    needs_damage=True,
                    largest_target=CreatureSize.LARGE,
                ),
            ),
            GiantAncestryType.STONE_GIANT: CombatEffect(
                name="Stone's Endurance",
                notes=(
                    "When you take damage: take 1d12"
                    f" {'+' if character.get_constitution_modifier() >= 0 else '-'}"
                    f" {abs(character.get_constitution_modifier())} off it before"
                    " you apply it. Nothing happens to the targets.",
                ),
            ),
            GiantAncestryType.STORM_GIANT: CombatEffect(
                name="Storm's Thunder",
                damage=(CombatDamage("1d8", DamageType.THUNDER),),
                notes=("To a creature within 60 feet that just damaged you.",),
            ),
        }[self.giant_ancestry_type]
        return [effect]
