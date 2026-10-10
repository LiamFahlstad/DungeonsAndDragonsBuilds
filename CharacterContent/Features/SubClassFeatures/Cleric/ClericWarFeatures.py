from Core.Definitions import CLERIC_HIT_DIE, DamageType
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    FeatureTarget,
    RegainedOn,
)
from Model.Content.Improvements import DamageResistance
from Model.Ledger.LedgerWriter import LedgerWriter
from Utils import StringUtils
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.View import CharacterView


class GuidedStrike(Feature):
    def __init__(self):
        super().__init__(
            name="Guided Strike",
            origin="War Domain Cleric Level 3",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="30 Feet"
            ),
            usage_tags=["buff"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = "When you or a creature within 30 feet of you misses with an attack roll, you can expend one use of your Channel Divinity and give that roll a +10 bonus, potentially causing it to hit. When you use this feature to benefit another creature's attack roll, you must take a Reaction to do so."
        return description

    def get_table_description(self, character: CharacterView) -> list[tuple[str, str]]:
        return [
            ("What", "Add +10 to a missed attack roll"),
            ("Trigger", "Reaction (for others) or no action (for self)"),
            ("Cost", "Channel Divinity"),
            ("Range", "30 feet for other creatures"),
            ("Effect", "Attack may hit after bonus applied"),
        ]

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class WarDomainSpells(Feature):
    def __init__(self):
        super().__init__(name="War Domain Spells", origin="War Domain Cleric Level 3")

    def get_description(self, character: CharacterView) -> str:
        description = "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the War Domain Spells table, you thereafter always have the listed spells prepared."
        return description


class WarPriest(Feature):
    def __init__(self):
        super().__init__(
            name="War Priest",
            origin="War Domain Cleric Level 3",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION),
            usage_tags=["damage"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="short or long rest",
                current_formula="Current amount: equal to your Wisdom modifier.",
            ),
        )

    def get_description(self, character: CharacterView) -> str:
        description = "As a Bonus Action, you can make one attack with a weapon or an Unarmed Strike. You regain all expended uses when you finish a Short or Long Rest."
        return description

    def get_table_description(self, character: CharacterView) -> list[tuple[str, str]]:
        uses = self.number_of_uses(character)
        return [
            ("What", "Make one extra attack"),
            ("Trigger", "Bonus Action"),
            ("Attack Type", "Weapon or Unarmed Strike"),
            ("Uses", f"{uses} (Wisdom modifier, minimum 1)"),
            ("Recharge", "Short or Long Rest"),
        ]

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.SHORT_OR_LONG_REST

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_wisdom_modifier())


class WarGodsBlessing(Feature):
    def __init__(self):
        super().__init__(
            name="War God's Blessing",
            origin="War Domain Cleric Level 6",
            activation=FeatureActivation(duration="1 Minute"),
            usage_tags=["buff", "damage"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = "You can expend a use of your Channel Divinity to cast Shield of Faith or Spiritual Weapon rather than expending a spell slot. When you cast either spell in this way, the spell doesn't require Concentration. Instead the spell lasts for 1 minute, but it ends early if you cast that spell again, have the Incapacitated condition, or die."
        return description

    def get_table_description(self, character: CharacterView) -> list[tuple[str, str]]:
        return [
            ("What", "Cast Shield of Faith or Spiritual Weapon"),
            ("Cost", "Channel Divinity (instead of spell slot)"),
            ("Concentration", "Not required"),
            ("Duration", "1 minute"),
            ("Ending", "Ends early if cast again, Incapacitated, or die"),
        ]


class AvatarOfBattle(Feature):
    def __init__(self):
        super().__init__(
            name="Avatar of Battle",
            origin="War Domain Cleric Level 17",
            skippable_in_concise=True,
            usage_tags=["buff"],
        )
        self._resistances = [
            DamageResistance(DamageType.BLUDGEONING),
            DamageResistance(DamageType.PIERCING),
            DamageResistance(DamageType.SLASHING),
        ]

    def apply(self, effects: LedgerWriter):
        for resistance in self._resistances:
            resistance.apply(effects)

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain Resistance to Bludgeoning, Piercing, and Slashing damage."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF
