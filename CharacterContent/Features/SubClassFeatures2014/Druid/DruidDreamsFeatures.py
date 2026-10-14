import Core.Definitions as Definitions
from Core.Definitions import CharacterClass
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from Core.Rules import MAX_ABILITY_MODIFIER, levels_gained
from Model.View import CharacterView


class BalmOfTheSummerCourt(Feature):
    def __init__(self):
        super().__init__(
            name="Balm of the Summer Court",
            origin="Circle of Dreams Druid Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, range="120 Feet"
            ),
            usage_tags=["heal"],
            uses=FeatureUses(
                max_uses=20,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Druid level.",
                gained_at=levels_gained(lambda level: level, from_level=3),
            ),
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "At 2nd level, you become imbued with the blessings of the Summer Court. You are a font of energy that offers respite from injuries. You have a pool of fey energy represented by a number of d6s equal to your druid level.\n"
            "\n"
            "As a bonus action, you can choose an ally you can see within 120 feet of you and spend a number of those dice equal to half your druid level or less. Roll the spent dice and add them together. The target regains a number of hit points equal to the total. The target also gains 1 temporary hit point per die spent.\n"
            "\n"
            "You regain the expended dice when you finish a long rest."
        )
        level = character.get_class_level(CharacterClass.DRUID)
        description += f"\nRight now: {level}d6 in the pool, up to {max(1, level // 2)} dice at a time."
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_class_level(Definitions.CharacterClass.DRUID)


class HearthOfMoonlightAndShadow(Feature):
    def __init__(self):
        super().__init__(
            name="Hearth of Moonlight and Shadow",
            origin="Circle of Dreams Druid Level 6",
            usage_tags=["buff"],
            activation=FeatureActivation(
                duration="Until End of Rest", range="30-Foot Radius"
            ),
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "At 6th level, home can be wherever you are. During a short or long rest, you can invoke the shadowy power of the Gloaming Court to help guard your respite. At the start of the rest, you touch a point in space, and an invisible, 30-foot-radius sphere of magic appears, centered on that point. Total cover blocks the sphere.\n"
            "\n"
            "While within the sphere, you and your allies gain a +5 bonus to Dexterity (Stealth) and Wisdom (Perception) checks, and any light from open flames in the sphere (a campfire, torches, or the like) isn't visible outside it.\n"
            "\n"
            "The sphere vanishes at the end of the rest or when you leave the sphere."
        )
        return description


class HiddenPaths(Feature):
    def __init__(self):
        super().__init__(
            name="Hidden Paths",
            origin="Circle of Dreams Druid Level 10",
            usage_tags=["utility"],
            activation=FeatureActivation(action_type="bonus_action"),
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Wisdom modifier.",
            ),
        )

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_wisdom_modifier())

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Starting at 10th level, you can use the hidden, magical pathways that some fey use to traverse space in a blink of an eye. As a bonus action on your turn, you can teleport up to 60 feet to an unoccupied space you can see. Alternatively, you can use your action to teleport one willing creature you touch up to 30 feet to an unoccupied space you can see.\n"
            "\n"
            "You can use this feature a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses of it when you finish a long rest."
        )
        return description


class WalkerInDreams(Feature):
    def __init__(self):
        super().__init__(
            name="Walker in Dreams",
            origin="Circle of Dreams Druid Level 14",
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "At 14th level, the magic of the Feywild grants you the ability to travel mentally or physically through dreamlands.\n"
            "\n"
            "When you finish a short rest, you can cast one of the following spells, without expending a spell slot or requiring material components: Dream (with you as the messenger), Scrying, or Teleportation Circle.\n"
            "\n"
            "This use of Teleportation Circle is special. Rather than opening a portal to a permanent teleportation circle, it opens a portal to the last location where you finished a long rest on your current plane of existence. If you haven't taken a long rest on your current plane, the spell fails but isn't wasted.\n"
            "\n"
            "Once you use this feature, you can't use it again until you finish a long rest."
        )
        return description
