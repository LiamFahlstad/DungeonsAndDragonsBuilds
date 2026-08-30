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
    DamageImmunity,
    DamageResistance,
    GrantLanguage,
)
from Core.Definitions import DamageType, Language
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class WindSpeaker(Feature):
    def __init__(self):
        super().__init__(
            name="Wind Speaker",
            origin="Storm Sorcery Sorcerer Level 3",
            skippable_in_concise=True,
        )
        self._language = GrantLanguage(Language.PRIMORDIAL, self.name)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._language.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The arcane magic you command is infused with elemental air. You can speak, read, and write Primordial. Knowing this language allows you to understand and be understood by those who speak its dialects: Aquan, Auran, Ignan, and Terran."
        return description


class TempestuousMagic(Feature):
    def __init__(self):
        super().__init__(
            name="Tempestuous Magic",
            origin="Storm Sorcery Sorcerer Level 3",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION),
            usage_tags=["utility"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can use a bonus action on your turn to cause whirling gusts of elemental air to briefly surround you, immediately before or after you cast a spell of 1st level or higher. Doing so allows you to fly up to 10 feet without provoking opportunity attacks."
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class HeartOfTheStorm(Feature):
    def __init__(self):
        super().__init__(
            name="Heart of the Storm",
            origin="Storm Sorcery Sorcerer Level 6",
            activation=FeatureActivation(range="10 Feet"),
            usage_tags=["damage", "buff"],
        )
        self._resistances = [
            DamageResistance(DamageType.LIGHTNING, self.name),
            DamageResistance(DamageType.THUNDER, self.name),
        ]

    def apply(self, character_stat_block: CharacterStatBlock):
        for resistance in self._resistances:
            resistance.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain resistance to lightning and thunder damage. In addition, whenever you start casting a spell of 1st level or higher that deals lightning or thunder damage, stormy magic erupts from you. This eruption causes creatures of your choice that you can see within 10 feet of you to take lightning or thunder damage (choose each time this ability activates) equal to half your sorcerer level."
        return description


class StormGuide(Feature):
    def __init__(self):
        super().__init__(
            name="Storm Guide",
            origin="Storm Sorcery Sorcerer Level 6",
            activation=FeatureActivation(action_type=ActionType.ACTION, range="100-Foot Radius"),
            usage_tags=["utility"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to subtly control the weather around you.\n"
            "If it is raining, you can use an action to cause the rain to stop falling in a 20-foot-radius sphere centered on you. You can end this effect as a bonus action.\n"
            "If it is windy, you can use a bonus action each round to choose the direction that the wind blows in a 100-foot-radius sphere centered on you. The wind blows in that direction until the end of your next turn. This feature doesn't alter the speed of the wind."
        )
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.AREA


class StormsFury(Feature):
    def __init__(self):
        super().__init__(
            name="Storm's Fury",
            origin="Storm Sorcery Sorcerer Level 14",
            activation=FeatureActivation(action_type=ActionType.REACTION, range="20 Feet"),
            usage_tags=["damage", "control"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you are hit by a melee attack, you can use your reaction to deal lightning damage to the attacker. The damage equals your sorcerer level. The attacker must also make a Strength saving throw against your sorcerer spell save DC. On a failed save, the attacker is pushed in a straight line up to 20 feet away from you."
        return description

    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        sorcerer_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.SORCERER
        )
        return [
            ("Trigger", "Hit by melee attack"),
            ("Action", "Reaction"),
            ("Damage", f"{sorcerer_level} lightning damage"),
            ("Save", "Strength saving throw vs spell save DC"),
            ("On Failed Save", "Pushed up to 20 feet away"),
        ]


class WindSoul(Feature):
    def __init__(self):
        super().__init__(
            name="Wind Soul",
            origin="Storm Sorcery Sorcerer Level 18",
            activation=FeatureActivation(action_type=ActionType.ACTION, duration="1 Hour", range="30 Feet"),
            usage_tags=["utility", "buff"],
        )
        self._immunities = [
            DamageImmunity(DamageType.LIGHTNING, self.name),
            DamageImmunity(DamageType.THUNDER, self.name),
        ]

    def apply(self, character_stat_block: CharacterStatBlock):
        for immunity in self._immunities:
            immunity.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain immunity to lightning and thunder damage.\n"
            "You also gain a magical flying speed of 60 feet. As an action, you can reduce your flying speed to 30 feet for 1 hour and choose a number of creatures within 30 feet of you equal to 3 + your Charisma modifier. The chosen creatures gain a magical flying speed of 30 feet for 1 hour. Once you reduce your flying speed in this way, you can't do so again until you finish a short or long rest."
        )
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.ALLY
