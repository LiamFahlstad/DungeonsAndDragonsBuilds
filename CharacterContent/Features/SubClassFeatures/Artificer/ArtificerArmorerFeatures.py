from Core.Definitions import ARTIFICER_HIT_DIE, Ability, CharacterClass
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
    RegainedOn,
    FeatureDice,
)
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, dc_formula


class ToolsOfTheTrade(Feature):
    def __init__(self):
        super().__init__(
            name="Tools of the Trade",
            origin="Armorer Artificer Level 3",
            usage_tags=["utility"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain the following benefits.\n"
            "Armor Training. You gain training with Heavy armor.\n"
            "Tool Proficiency. You gain proficiency with Smith's Tools. If you already have this tool proficiency, you gain proficiency with one other type of Artisan's Tools of your choice.\n"
            "Armor Crafting. When you craft nonmagical or magic armor, the amount of time required to craft it is halved."
        )
        return description


class Spells(Feature):
    def __init__(self):
        super().__init__(name="Armorer Spells", origin="Armorer Artificer Level 3")

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you reach an Artificer level specified in the Armorer Spells table, you thereafter always have the listed spells prepared.\n"
            "Armorer Spells\n"
            "Artificer Level	Spells\n"
            "3	Magic Missile, Thunderwave\n"
            "5	Mirror Image, Shatter\n"
            "9	Hypnotic Pattern, Lightning Bolt\n"
            "13	Fire Shield, Greater Invisibility\n"
            "17	Passwall, Wall of Force"
        )
        return description


class ArcaneArmor(Feature):
    def __init__(self):
        super().__init__(
            name="Arcane Armor",
            origin="Armorer Artificer Level 3",
            activation=FeatureActivation(action_type=ActionType.ACTION),
            usage_tags=["buff"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Magic action while you have Smith's Tools in hand, you can turn a suit of armor you are wearing into Arcane Armor. The armor continues to be Arcane Armor until you don another suit of armor or you die.\n"
            "You gain the following benefits while wearing your Arcane Armor.\n"
            "No Strength Requirement. If the armor normally has a Strength requirement, the Arcane Armor lacks this requirement for you.\n"
            "Quick Don and Doff. You can don or doff the armor as a Utilize action. The armor can't be removed against your will.\n"
            "Spellcasting Focus. You can use the Arcane Armor as a Spellcasting Focus for your Artificer spells."
        )
        return description

    def get_table_description(self, character: CharacterView) -> list[tuple[str, str]]:
        return [
            ("No Strength Requirement", "Arcane Armor has no Strength requirement"),
            (
                "Quick Don and Doff",
                "Don or doff as a Utilize action; can't be removed against your will",
            ),
            (
                "Spellcasting Focus",
                "Use Arcane Armor as Spellcasting Focus for your Artificer spells",
            ),
        ]

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


FORCE_DEMOLISHER_DICE = FeatureDice(
    "Force Demolisher (Dreadnaught)",
    (
        (3, "1d10"),
        (15, "2d6"),
    ),
    CharacterClass.ARTIFICER,
    note="+ Intelligence modifier, +1 more from level 9",
)
THUNDER_PULSE_DICE = FeatureDice(
    "Thunder Pulse (Guardian)",
    (
        (3, "1d8"),
        (15, "1d10"),
    ),
    CharacterClass.ARTIFICER,
    note="+ Intelligence modifier, +1 more from level 9",
)
LIGHTNING_LAUNCHER_DICE = FeatureDice(
    "Lightning Launcher (Infiltrator)",
    (
        (3, "1d6"),
        (15, "2d6"),
    ),
    CharacterClass.ARTIFICER,
    note="+ Intelligence modifier, +1 more from level 9; +1d6 once per turn",
)


class ArmorModel(Feature):
    def __init__(self):
        super().__init__(
            name="Armor Model",
            origin="Armorer Artificer Level 3",
            usage_tags=["damage", "buff", "control", "utility"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Giant Stature (Dreadnaught): equal to your Intelligence modifier.",
            ),
            dice=[FORCE_DEMOLISHER_DICE, THUNDER_PULSE_DICE, LIGHTNING_LAUNCHER_DICE],
        )

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_intelligence_modifier())

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Weapon dice and Giant Stature's uses are in the panel below.
        return [
            Paragraph(
                "Customize your Arcane Armor as one of three models. Each has a special weapon."
            ),
            Facts(
                (
                    (
                        "Special weapon",
                        "Use your Intelligence modifier, instead of Strength or Dexterity, for its attack and damage rolls",
                    ),
                    (
                        "Change model",
                        "When you finish a Short or Long Rest with Smith's Tools in hand",
                    ),
                )
            ),
            Option(
                "Dreadnaught",
                (
                    Facts(
                        (
                            (
                                "Force Demolisher",
                                "Simple Melee weapon with Reach; Force damage. On a hit against a creature at least one size smaller than you, push it up to 10 feet away or pull it up to 10 feet toward you.",
                            ),
                            (
                                "Giant Stature",
                                "Bonus Action: for 1 minute your reach increases by 5 feet, and you become Large if you're smaller (if there's room)",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Guardian",
                (
                    Facts(
                        (
                            (
                                "Thunder Pulse",
                                "Simple Melee weapon; Thunder damage. A creature hit has Disadvantage on attack rolls against targets other than you until the start of your next turn.",
                            ),
                            (
                                "Defensive Field",
                                "While Bloodied, Bonus Action: gain Temporary Hit Points equal to your Artificer level; you lose them if you doff the armor",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Infiltrator",
                (
                    Facts(
                        (
                            (
                                "Lightning Launcher",
                                "Simple Ranged weapon, range 90/300 feet; Lightning damage. Once on each of your turns when you hit, +1d6 Lightning damage.",
                            ),
                            ("Powered Steps", "Speed +5 feet"),
                            (
                                "Dampening Field",
                                "Advantage on Dexterity (Stealth) checks; it cancels the armor's Disadvantage, if any",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can customize your Arcane Armor. When you do so, choose one of the following armor models: Dreadnaught, Guardian, or Infiltrator. The model you choose gives you special benefits while you wear it.\n"
            "Each model includes a special weapon. When you attack with that weapon, you can add your Intelligence modifier, instead of your Strength or Dexterity modifier, to the attack and damage rolls.\n"
            "You can change the armor's model whenever you finish a Short or Long Rest if you have Smith's Tools in hand.\n"
            "Dreadnaught.\n"
            "You design your armor to become a towering juggernaut in battle. It has the following features:\n"
            "Force Demolisher. An arcane wrecking ball or sledgehammer projects from your armor. The demolisher counts as a Simple Melee weapon with the Reach property, and it deals 1d10 Force damage on a hit. If you hit a creature that is at least one size smaller than you with the demolisher, you can push the creature up to 10 feet straight away from yourself or pull the creature up to 10 feet toward yourself.\n"
            "Giant Stature. As a Bonus Action, you transform and enlarge your armor for 1 minute. For the duration, your reach increases by 5 feet, and if you are smaller than Large, you become Large, along with anything you are wearing. If there isn't enough room for you to increase your size, your size doesn't change. You can use this Bonus Action a number of times equal to your Intelligence modifier (minimum of once). You regain all expended uses when you finish a Long Rest.\n"
            "Guardian.\n"
            "You design your armor to be in the front line of conflict. It has the following features:\n"
            "Thunder Pulse. You can discharge concussive blasts with strikes from your armor. The pulse counts as a Simple Melee weapon and deals 1d8 Thunder damage on a hit. A creature hit by the pulse has Disadvantage on attack rolls against targets other than you until the start of your next turn.\n"
            "Defensive Field. While Bloodied, you can take a Bonus Action to gain Temporary Hit Points equal to your Artificer level. You lose these Temporary Hit Points if you doff the armor.\n"
            "Infiltrator.\n"
            "You customize your armor for subtler undertakings. It has the following features:\n"
            "Lightning Launcher. A gemlike node appears on your armor, from which you can shoot bolts of lightning. The launcher counts as a Simple Ranged weapon with a normal range of 90 feet and a long range of 300 feet, and it deals 1d6 Lightning damage on a hit. Once on each of your turns when you hit a creature with the launcher, you can deal an extra 1d6 Lightning damage to that target.\n"
            "Powered Steps. Your Speed increases by 5 feet.\n"
            "Dampening Field. You have Advantage on Dexterity (Stealth) checks. If the armor imposes Disadvantage on such checks, the Advantage and Disadvantage cancel each other, as normal.\n"
            + self._current_values(character)
        )
        return description

    @staticmethod
    def _current_values(character: CharacterView) -> str:
        """The special weapons' numbers at the character's level (Improved
        Armorer adds +1 to attack and damage, Perfected Armor bigger dice)."""
        artificer_level = character.get_class_level(CharacterClass.ARTIFICER)
        improved = 1 if character.has_feature(ImprovedArmorer) else 0
        perfected = character.has_feature(PerfectedArmor)
        attack = (
            character.get_proficiency_bonus()
            + character.get_intelligence_modifier()
            + improved
        )
        damage = character.get_intelligence_modifier() + improved
        uses = max(1, character.get_intelligence_modifier())
        demolisher, pulse, launcher = (
            ("2d6", "1d10", "2d6") if perfected else ("1d10", "1d8", "1d6")
        )
        lines = [
            f"Your special weapons right now: {attack:+} to hit.",
            f"Force Demolisher: {demolisher} + {damage} Force damage, Reach. Giant Stature: {uses} per Long Rest.",
            f"Thunder Pulse: {pulse} + {damage} Thunder damage. Defensive Field: {artificer_level} Temporary Hit Points.",
            f"Lightning Launcher: {launcher} + {damage} Lightning damage (+1d6 once per turn), range 90/300 feet.",
        ]
        if perfected:
            lines.append(
                f"Guardian pull (Reaction): DC {character.calculate_difficulty_class()} Strength save, {uses} per Long Rest. "
                f"Infiltrator flight (Bonus Action): {uses} per Long Rest."
            )
        return "\n".join(lines)

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST


class ExtraAttack(Feature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="Armorer Artificer Level 5")

    def get_description(self, character: CharacterView) -> str:
        description = "You can attack twice instead of once whenever you take the Attack action on your turn."
        return description


class ImprovedArmorer(Feature):
    def __init__(self):
        super().__init__(
            name="Improved Armorer",
            origin="Armorer Artificer Level 9",
            usage_tags=["damage"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain the following benefits.\n"
            "Armor Replication. You learn an additional plan for your Replicate Magic Item feature, and it must be in the Armor category. If you replace that plan, you must replace it with another Armor plan.\n"
            "In addition, you can create an additional item with that feature, and the item must also be in the Armor category.\n"
            "Improved Arsenal. You gain a +1 bonus to attack and damage rolls made with the special weapon of your Arcane Armor model."
        )
        return description

    def get_table_description(self, character: CharacterView) -> list[tuple[str, str]]:
        return [
            (
                "Armor Replication",
                "Learn additional Replicate Magic Item plan in Armor category; create additional item in Armor category",
            ),
            (
                "Improved Arsenal",
                "+1 bonus to attack and damage rolls with Arcane Armor model's special weapon",
            ),
        ]


class PerfectedArmor(Feature):
    def __init__(self):
        super().__init__(
            name="Perfected Armor",
            origin="Armorer Artificer Level 15",
            usage_tags=["damage", "control", "buff", "utility"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Guardian's pull or Infiltrator's flight, whichever model you wear: equal to your Intelligence modifier.",
            ),
        )

    def calculate_dc(self, character: CharacterView) -> int:
        return character.calculate_difficulty_class()

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_intelligence_modifier())

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The weapon dice are on the Armor Model card; uses are below.
        return [
            Paragraph("Each armor model gains more benefits."),
            Option(
                "Dreadnaught",
                (
                    Facts(
                        (
                            ("Force Demolisher", "Damage becomes 2d6 Force"),
                            (
                                "Giant Stature",
                                "Your reach increases by 10 feet instead, you can become Large or Huge, and you have Advantage on Strength checks and Strength saving throws for the duration",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Guardian",
                (
                    Facts(
                        (
                            ("Thunder Pulse", "Damage becomes 1d10 Thunder"),
                            (
                                "Pull",
                                "Reaction when a Huge or smaller creature you can see ends its turn within 30 feet of you",
                            ),
                            (
                                "Save",
                                f"Strength save against your spell save DC ({dc_formula(Ability.INTELLIGENCE)})",
                            ),
                            (
                                "Failed",
                                "Pulled up to 25 feet straight toward you. If it ends within 5 feet of you, make a melee weapon attack against it as part of the Reaction.",
                            ),
                            (
                                "Uses",
                                "Intelligence modifier (minimum once) per Long Rest",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Infiltrator",
                (
                    Facts(
                        (
                            (
                                "Lightning Launcher",
                                "Damage becomes 2d6 Lightning. A creature it damages sheds Dim Light in a 5-foot radius and has Disadvantage on attack rolls against you until the start of your next turn.",
                            ),
                            (
                                "Flight",
                                "Bonus Action: Fly Speed equal to twice your Speed until the end of the turn. Intelligence modifier (minimum once) uses per Long Rest.",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your Arcane Armor gains additional benefits based on its model, as detailed below.\n"
            "Dreadnaught. The damage die of your Force Demolisher increases to 2d6 Force damage.\n"
            "In addition, when you use your Giant Stature, your reach increases by 10 feet, your size can increase to Large or Huge (your choice), and you have Advantage on Strength checks and Strength saving throws for the duration.\n"
            "Guardian. The damage die of your Thunder Pulse increases to 1d10 Thunder damage.\n"
            "In addition, when a Huge or smaller creature you can see ends its turn within 30 feet of you, you can take a Reaction to magically force that creature to make a Strength saving throw against your spell save DC. On a failed save, you pull the creature up to 25 feet directly toward you to an unoccupied space. If you pull the target to a space within 5 feet of yourself, you can make a melee weapon attack against it as part of this Reaction.\n"
            "You can take this Reaction a number of times equal to your Intelligence modifier (minimum of once), and you regain all expended uses when you finish a Long Rest.\n"
            "Infiltrator. The damage die of your Lightning Launcher increases to 2d6 Lightning damage. Any creature that takes Lightning damage from your Lightning Launcher glimmers with magical light until the start of your next turn. The glimmering creature sheds Dim Light in a 5-foot radius, and it has Disadvantage on attack rolls against you, as the light jolts it if it attacks you.\n"
            "Additionally, as a Bonus Action, you can gain a Fly Speed equal to twice your Speed until the end of the current turn. You can take this Bonus Action a number of times equal to your Intelligence modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return description
