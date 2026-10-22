from CharacterContent.Spells.SpellLists import (
    AbjurationLevel1Spells,
    AbjurationLevel2Spells,
    AbjurationLevel3Spells,
    AbjurationLevel4Spells,
    AbjurationLevel5Spells,
    ConjurationLevel1Spells,
    ConjurationLevel2Spells,
    ConjurationLevel3Spells,
    ConjurationLevel4Spells,
    ConjurationLevel5Spells,
    DivinationLevel1Spells,
    DivinationLevel2Spells,
    DivinationLevel3Spells,
    DivinationLevel4Spells,
    DivinationLevel5Spells,
    EnchantmentLevel1Spells,
    EnchantmentLevel2Spells,
    EnchantmentLevel4Spells,
    EnchantmentLevel5Spells,
    EvocationLevel1Spells,
    EvocationLevel2Spells,
    EvocationLevel3Spells,
    EvocationLevel4Spells,
    EvocationLevel5Spells,
    IllusionLevel1Spells,
    IllusionLevel2Spells,
    IllusionLevel3Spells,
    IllusionLevel4Spells,
    IllusionLevel5Spells,
    NecromancyLevel1Spells,
    NecromancyLevel2Spells,
    NecromancyLevel3Spells,
    NecromancyLevel4Spells,
    NecromancyLevel5Spells,
    TransmutationLevel1Spells,
    TransmutationLevel2Spells,
    TransmutationLevel3Spells,
    TransmutationLevel4Spells,
    TransmutationLevel5Spells,
    Level1Spells,
    Level2Spells,
    Level3Spells,
    Level4Spells,
    Level5Spells,
)
from Model.Content.Feature import (
    Feature,
    FeatureTarget,
    FeatureUses,
    RegainedOn,
    regained_on_from_uses,
)
from Model.Content.Improvements import (
    AbilityScoreBonus,
    DamageResistance,
    ElementalResistance,
    GrantSense,
    SkillExpertiseChoice,
    SkillProficiencyChoice,
    SavingThrowProficiency,
    SpeedBonus,
    GrantWeaponProficiency,
)
from Core.Definitions import Ability, DamageType, Sense, Skill
from CharacterContent.Items.Weapons import WeaponProficiency
from Model.Ledger.LedgerWriter import LedgerWriter
from Core.Rules import (
    PROFICIENCY_BONUS_GAINED_AT,
    MAX_ABILITY_MODIFIER,
    MAX_ABILITY_SCORE,
    MAX_PROFICIENCY_BONUS,
)
from Model.View import CharacterView
from Model.Content.FeatureText import (
    Block,
    Facts,
    Option,
    Paragraph,
    Table,
    dc_formula,
)


class GeneralFeat(Feature):
    # A feat can be taken once, unless it says it's Repeatable (see
    # Character._validate_feats_taken_once).
    repeatable = False

    labeled_by_class_level = True

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return regained_on_from_uses(self.uses)


class _AbilityScoreFeat(GeneralFeat):
    """Base class for the common Level 4+ general feats that grant +1 to one ability.

    Subclasses declare:
        _NAME       – feat display name
        _ORIGIN     – origin string (defaults to "General Feat Level 4+")
        _ABILITIES  – tuple of allowed Ability values for the +1 bonus
        _MIN_LEVEL  – minimum character level (defaults to 4)

    They only need to implement ``get_description``.
    """

    _NAME: str
    _ORIGIN: str = "General Feat Level 4+"
    _ABILITIES: tuple
    _MIN_LEVEL: int = 4
    # Optional limited-use tracking for subclasses whose benefit has a per-rest
    # use count (e.g. equal to Proficiency Bonus). None for passive feats.
    _USES: FeatureUses | None = None

    def __init__(self, character_level: int, ability: Ability):
        if character_level < self._MIN_LEVEL:
            raise ValueError(
                f"{self._NAME} requires character level {self._MIN_LEVEL} or higher."
            )
        if ability not in self._ABILITIES:
            allowed = " or ".join(a.value for a in self._ABILITIES)
            raise ValueError(f"{self._NAME} ability increase must be {allowed}.")
        self.ability = ability
        self._bonus = AbilityScoreBonus(
            [(ability, 1)],
            total=1,
            error_prefix=self._NAME,
            max_score=MAX_ABILITY_SCORE,
        )
        super().__init__(name=self._NAME, origin=self._ORIGIN, uses=self._USES)

    def apply(self, ledger_writer: LedgerWriter):
        self._bonus.apply(ledger_writer)


class AbilityScoreImprovement(GeneralFeat):
    """Also add either [+1, +1] OR [+2] to any abilities."""

    # 2024 PHB: Repeatable.
    repeatable = True

    def __init__(self, bonuses: list[tuple[Ability, int]]):
        self._bonus = AbilityScoreBonus(
            bonuses,
            total=2,
            error_prefix="Ability Score Improvement",
            max_per_ability=2,
            max_score=MAX_ABILITY_SCORE,
        )
        super().__init__(
            name="Ability Score Improvement",
            origin="General Feat Level 4+",
            passive=True,
        )

    def apply(self, ledger_writer: LedgerWriter):
        self._bonus.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Increase one ability score by 2, or two ability scores by 1 each, to a maximum of 20."
            ),
            Facts(
                tuple(
                    (ability.value, f"+{bonus}")
                    for ability, bonus in self._bonus.bonuses
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        choices = ", ".join(
            f"{ability.value} +{bonus}" for ability, bonus in self._bonus.bonuses
        )
        return (
            "You can increase one ability score of your choice by 2, or you can increase two ability scores of your choice by 1 each. "
            "You can't increase an ability score above 20 using this feature.\n"
            f"Choices: {choices}"
        )


class Actor(_AbilityScoreFeat):
    _NAME = "Actor"
    _ABILITIES = (Ability.CHARISMA,)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Impersonation",
                        "While disguised as a real or fictional person, Advantage on Charisma (Deception or Performance) checks to convince others you're that person",
                    ),
                    (
                        "Mimicry",
                        "Mimic the sounds of other creatures, including speech. A listener sees through it with a Wisdom (Insight) check against DC 8 + Charisma modifier + Proficiency Bonus.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Charisma 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Charisma score by 1, to a maximum of 20.\n"
            "Impersonation. While you're disguised as a real or fictional person, you have Advantage on Charisma (Deception or Performance) checks to convince others that you are that person.\n"
            "Mimicry. You can mimic the sounds of other creatures, including speech. A creature that hears the mimicry must succeed on a Wisdom (Insight) check to determine the effect is faked (DC 8 plus your Charisma modifier and Proficiency Bonus).\n"
        )

    def calculate_dc(self, character: CharacterView) -> int:
        charisma_modifier = character.get_charisma_modifier()
        proficiency_bonus = character.get_proficiency_bonus()
        return 8 + charisma_modifier + proficiency_bonus


class Athlete(_AbilityScoreFeat):
    _NAME = "Athlete"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def __init__(self, character_level: int, ability: Ability):
        if character_level < self._MIN_LEVEL:
            raise ValueError(
                f"{self._NAME} requires character level {self._MIN_LEVEL} or higher."
            )
        if ability not in self._ABILITIES:
            allowed = " or ".join(a.value for a in self._ABILITIES)
            raise ValueError(f"{self._NAME} ability increase must be {allowed}.")
        self.ability = ability
        self._bonus = AbilityScoreBonus(
            [(ability, 1)],
            total=1,
            error_prefix=self._NAME,
            max_score=MAX_ABILITY_SCORE,
        )
        Feature.__init__(
            self, name=self._NAME, origin=self._ORIGIN, usage_tags=["utility"]
        )

    def apply(self, ledger_writer: LedgerWriter):
        self._bonus.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    ("Climb Speed", "Equal to your Speed"),
                    (
                        "Hop Up",
                        "Right yourself from Prone with only 5 feet of movement",
                    ),
                    (
                        "Jumping",
                        "Make a running Long or High Jump after moving only 5 feet",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Strength or Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Climb Speed. You gain a Climb Speed equal to your Speed.\n"
            "Hop Up. When you have the Prone condition, you can right yourself with only 5 feet of movement.\n"
            "Jumping. You can make a running Long or High Jump after moving only 5 feet.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class Charger(_AbilityScoreFeat):
    _NAME = "Charger"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    ("Improved Dash", "The Dash action gives you 10 feet more Speed"),
                    (
                        "Charge Attack",
                        "Once on each of your turns: move 10+ feet straight toward a target right before hitting it with a melee attack roll as part of the Attack action, then add 1d8 to the damage, or push it up to 10 feet (if no more than one size larger than you)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Strength or Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Improved Dash. When you take the Dash action, your Speed increases by 10 feet for that action.\n"
            "Charge Attack. If you move at least 10 feet in a straight line toward a target immediately before hitting it with a melee attack roll as part of the Attack action, choose one of the following effects: gain a 1d8 bonus to the attack's damage roll, or push the target up to 10 feet away if it is no more than one size larger than you. You can use this benefit only once on each of your turns.\n"
        )


class Chef(_AbilityScoreFeat):
    _NAME = "Chef"
    _ABILITIES = (Ability.WISDOM, Ability.CONSTITUTION)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    ("Cook's Utensils", "Proficiency"),
                    (
                        "Replenishing Meal",
                        "During a Short Rest, with ingredients and Cook's Utensils, cook for 4 + Proficiency Bonus creatures. At the end of the rest, each who eats and spends Hit Dice regains an extra 1d8 Hit Points.",
                    ),
                    (
                        "Bolstering Treats",
                        "With 1 hour of work or after a Long Rest, with ingredients and Cook's Utensils, make Proficiency Bonus treats (they last 8 hours). A creature can eat one as a Bonus Action to gain Proficiency Bonus Temporary Hit Points.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Constitution or Wisdom score by 1, to a maximum of 20.\n"
            "Cook's Utensils. You gain proficiency with Cook's Utensils if you don't already have it.\n"
            "Replenishing Meal. As part of a Short Rest, you can cook special food if you have ingredients and Cook's Utensils on hand. You can prepare enough of this food for a number of creatures equal to 4 plus your Proficiency Bonus. At the end of the Short Rest, any creature who eats the food and spends one or more Hit Dice to regain Hit Points regains an extra 1d8 Hit Points.\n"
            "Bolstering Treats. With 1 hour of work or when you finish a Long Rest, you can cook a number of treats equal to your Proficiency Bonus if you have ingredients and Cook's Utensils on hand. These special treats last 8 hours after being made. A creature can use a Bonus Action to eat one of those treats to gain a number of Temporary Hit Points equal to your Proficiency Bonus.\n"
        )


class CrossbowExpert(_AbilityScoreFeat):
    _NAME = "Crossbow Expert"
    _ABILITIES = (Ability.DEXTERITY,)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Ignore Loading",
                        "Hand, Light and Heavy Crossbows lose the Loading property for you, and you can load one without a free hand",
                    ),
                    (
                        "Firing in Melee",
                        "No Disadvantage on crossbow attacks for being within 5 feet of an enemy",
                    ),
                    (
                        "Dual Wielding",
                        "The Light property's extra attack with a Light crossbow adds your ability modifier to its damage, if you aren't already",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Dexterity score by 1, to a maximum of 20.\n"
            "Ignore Loading. You ignore the Loading property of the Hand Crossbow, Heavy Crossbow, and Light Crossbow. If you're holding one of them, you can load a piece of ammunition into it even if you lack a free hand.\n"
            "Firing in Melee. Being within 5 feet of an enemy doesn't impose Disadvantage on your attack rolls with crossbows.\n"
            "Dual Wielding. When you make the extra attack of the Light property, you can add your ability modifier to the damage of the extra attack if that attack is with a crossbow that has the Light property and you aren't already adding that modifier to the damage.\n"
        )


class Crusher(_AbilityScoreFeat):
    _NAME = "Crusher"
    _ABILITIES = (Ability.STRENGTH, Ability.CONSTITUTION)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Push",
                        "Once per turn, when you hit a creature with an attack that deals Bludgeoning damage, move it 5 feet to an unoccupied space, if it's no more than one size larger than you",
                    ),
                    (
                        "Enhanced Critical",
                        "When you score a Critical Hit that deals Bludgeoning damage, attack rolls against the creature have Advantage until the start of your next turn",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Constitution score by 1, to a maximum of 20.\n"
            "Push. Once per turn, when you hit a creature with an attack that deals Bludgeoning damage, you can move it 5 feet to an unoccupied space if the target is no more than one size larger than you.\n"
            "Enhanced Critical. When you score a Critical Hit that deals Bludgeoning damage to a creature, attack rolls against that creature have Advantage until the start of your next turn.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class DefensiveDuelist(_AbilityScoreFeat):
    _NAME = "Defensive Duelist"
    _ABILITIES = (Ability.DEXTERITY,)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Parry",
                        "Reaction, while holding a Finesse weapon, when another creature hits you with a melee attack: add your Proficiency Bonus to your AC against melee attacks until the start of your next turn, potentially causing the attack to miss",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Dexterity score by 1, to a maximum of 20.\n"
            "Parry. If you're holding a Finesse weapon and another creature hits you with a melee attack, you can take a Reaction to add your Proficiency Bonus to your Armor Class, potentially causing the attack to miss you. You gain this bonus to your AC against melee attacks until the start of your next turn.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class DualWielder(_AbilityScoreFeat):
    _NAME = "Dual Wielder"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Ability Score",
                        f"+1 {self.ability.value}, to a maximum of 20",
                    ),
                    (
                        "Enhanced Dual Wielding",
                        "When you take the Attack action and attack with a Light weapon, make one extra attack as a Bonus Action later that turn with a different Melee weapon that isn't Two-Handed. Don't add your ability modifier to its damage unless it's negative.",
                    ),
                    (
                        "Quick Draw",
                        "Draw or stow two weapons that aren't Two-Handed when you could normally draw or stow one",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Strength or Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Enhanced Dual Wielding. When you take the Attack action on your turn and attack with a weapon that has the Light property, you can make one extra attack as a Bonus Action later on the same turn with a different weapon, which must be a Melee weapon that lacks the Two-Handed property. You don't add your ability modifier to the extra attack's damage unless that modifier is negative.\n"
            "Quick Draw. You can draw or stow two weapons that lack the Two-Handed property when you would normally be able to draw or stow only one.\n"
        )


class Durable(_AbilityScoreFeat):
    _NAME = "Durable"
    _ABILITIES = (Ability.CONSTITUTION,)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    ("Defy Death", "Advantage on Death Saving Throws"),
                    (
                        "Speedy Recovery",
                        "Bonus Action: expend and roll one Hit Point Die and regain that many Hit Points",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Constitution score by 1, to a maximum of 20.\n"
            "Defy Death. You have Advantage on Death Saving Throws.\n"
            "Speedy Recovery. As a Bonus Action, you can expend one of your Hit Point Dice, roll the die, and regain a number of Hit Points equal to the roll.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class ElementalAdept(_AbilityScoreFeat):
    # 2024 PHB: Repeatable.
    repeatable = True

    _NAME = "Elemental Adept"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Energy Mastery",
                        "Choose Acid, Cold, Fire, Lightning or Thunder. Your spells ignore Resistance to that type, and you treat any 1 on their damage dice of that type as a 2.",
                    ),
                    ("Repeatable", "Take it again with a different damage type"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Spellcasting or Pact Magic Feature\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Energy Mastery. Choose one of the following damage types: Acid, Cold, Fire, Lightning, or Thunder. Spells you cast ignore Resistance to damage of the chosen type. In addition, when you roll damage for a spell you cast that deals damage of that type, you can treat any 1 on a damage die as a 2.\n"
            "Repeatable. You can take this feat more than once, but you must choose a different damage type each time for Energy Mastery.\n"
        )


class FeyTouched(_AbilityScoreFeat):
    _NAME = "Fey Touched"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Spells",
                        "Misty Step and one level 1 Divination or Enchantment spell, always prepared",
                    ),
                    (
                        "Casting",
                        f"Each once per Long Rest without a spell slot, or with your spell slots. {self.ability.value} is their spellcasting ability.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "Your exposure to the Feywild's magic grants you the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Fey Magic. Choose one level 1 spell from the Divination or Enchantment school of magic. You always have that spell and the Misty Step spell prepared. You can cast each of these spells without expending a spell slot. Once you cast either spell in this way, you can't cast that spell in this way again until you finish a Long Rest. You can also cast these spells using spell slots you have of the appropriate level. The spells' spellcasting ability is the ability increased by this feat.\n"
        )


class Grappler(_AbilityScoreFeat):
    _NAME = "Grappler"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Punch and Grab",
                        "Once per turn, when an Unarmed Strike hits as part of the Attack action on your turn, use both its Damage and Grapple options",
                    ),
                    (
                        "Attack Advantage",
                        "Advantage on attack rolls against a creature you're Grappling",
                    ),
                    (
                        "Fast Wrestler",
                        "Moving a Grappled creature your size or smaller costs no extra movement",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Strength or Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Punch and Grab. When you hit a creature with an Unarmed Strike as part of the Attack action on your turn, you can use both the Damage and the Grapple option. You can use this benefit only once per turn.\n"
            "Attack Advantage. You have Advantage on attack rolls against a creature Grappled by you.\n"
            "Fast Wrestler. You don't have to spend extra movement to move a creature Grappled by you if the creature is your size or smaller.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class GreatWeaponMaster(_AbilityScoreFeat):
    _NAME = "Great Weapon Master"
    _ABILITIES = (Ability.STRENGTH,)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Heavy Weapon Mastery",
                        "When a Heavy weapon hits a creature as part of the Attack action on your turn, deal extra damage equal to your Proficiency Bonus",
                    ),
                    (
                        "Hew",
                        "Right after a Critical Hit with a Melee weapon, or reducing a creature to 0 Hit Points with one, make one attack with it as a Bonus Action",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Strength 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength score by 1, to a maximum of 20.\n"
            "Heavy Weapon Mastery. When you hit a creature with a weapon that has the Heavy property as part of the Attack action on your turn, you can cause the weapon to deal extra damage to the target. The extra damage equals your Proficiency Bonus.\n"
            "Hew. Immediately after you score a Critical Hit with a Melee weapon or reduce a creature to 0 Hit Points with one, you can make one attack with the same weapon as a Bonus Action.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class HeavilyArmored(_AbilityScoreFeat):
    _NAME = "Heavily Armored"
    _ABILITIES = (Ability.CONSTITUTION, Ability.STRENGTH)

    def __init__(self, character_level: int, ability: Ability):
        super().__init__(character_level, ability)
        self.passive = True

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    ("Armor Training", "Heavy armor"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Medium Armor Training\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Constitution or Strength score by 1, to a maximum of 20.\n"
            "Armor Training. You gain training with Heavy armor.\n"
        )


class HeavyArmorMaster(_AbilityScoreFeat):
    _NAME = "Heavy Armor Master"
    _ABILITIES = (Ability.CONSTITUTION, Ability.STRENGTH)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Damage Reduction",
                        "While wearing Heavy armor, Bludgeoning, Piercing and Slashing damage from an attack that hits you is reduced by your Proficiency Bonus",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Heavy Armor Training\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Constitution or Strength score by 1, to a maximum of 20.\n"
            "Damage Reduction. When you're hit by an attack while you're wearing Heavy armor, any Bludgeoning, Piercing, and Slashing damage dealt to you by that attack is reduced by an amount equal to your Proficiency Bonus.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class InspiringLeader(_AbilityScoreFeat):
    _NAME = "Inspiring Leader"
    _ABILITIES = (Ability.WISDOM, Ability.CHARISMA)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Bolstering Performance",
                        f"When you finish a Short or Long Rest, give a speech, song or dance: up to six allies (you included) within 30 feet who witness it gain character level + {self.ability.value} modifier Temporary Hit Points",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Wisdom or Charisma 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Wisdom or Charisma score by 1, to a maximum of 20.\n"
            "Bolstering Performance. When you finish a Short or Long Rest, you can give an inspiring performance: a speech, song, or dance. When you do so, choose up to six allies (which can include yourself) within 30 feet of yourself who witness the performance. The chosen creatures each gain Temporary Hit Points equal to your character level plus the modifier of the ability you increased with this feat.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class KeenMind(_AbilityScoreFeat):
    _NAME = "Keen Mind"
    _ABILITIES = (Ability.INTELLIGENCE,)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Lore Knowledge",
                        "Choose Arcana, History, Investigation, Nature or Religion: proficiency in it, or Expertise if you're already proficient",
                    ),
                    ("Quick Study", "Take the Study action as a Bonus Action"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Intelligence 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence score by 1, to a maximum of 20.\n"
            "Lore Knowledge. Choose one of the following skills: Arcana, History, Investigation, Nature, or Religion. If you lack proficiency in the chosen skill, you gain proficiency in it, and if you already have proficiency in it, you gain Expertise in it.\n"
            "Quick Study. You can take the Study action as a Bonus Action.\n"
        )


class LightlyArmored(_AbilityScoreFeat):
    _NAME = "Lightly Armored"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def __init__(self, character_level: int, ability: Ability):
        super().__init__(character_level, ability)
        self.passive = True

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    ("Armor Training", "Light armor and Shields"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Armor Training. You gain training with Light armor and Shields.\n"
        )


class MageSlayer(_AbilityScoreFeat):
    _NAME = "Mage Slayer"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)
    _USES = FeatureUses(
        max_uses=1,
        regain_all_on="short or long rest",
        current_formula="Used by Guarded Mind.",
    )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Concentration Breaker",
                        "A concentrating creature you damage has Disadvantage on its save to keep Concentration",
                    ),
                    (
                        "Guarded Mind",
                        "When you fail an Intelligence, Wisdom or Charisma save, succeed instead; once per Short or Long Rest",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Concentration Breaker. When you damage a creature that is concentrating, it has Disadvantage on the saving throw it makes to maintain Concentration.\n"
            "Guarded Mind. If you fail an Intelligence, a Wisdom, or a Charisma saving throw, you can cause yourself to succeed instead. Once you use this benefit, you can't use it again until you finish a Short or Long Rest.\n"
        )


class MartialWeaponTraining(_AbilityScoreFeat):
    _NAME = "Martial Weapon Training"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def __init__(self, character_level: int, ability: Ability):
        super().__init__(character_level, ability)
        self.passive = True

    def apply(self, ledger_writer: LedgerWriter):
        super().apply(ledger_writer)
        # "Weapon Proficiency. You gain proficiency with Martial weapons."
        GrantWeaponProficiency([WeaponProficiency.MARTIAL]).apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    ("Weapon Proficiency", "Martial weapons"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Weapon Proficiency. You gain proficiency with Martial weapons.\n"
        )


class MediumArmorMaster(_AbilityScoreFeat):
    _NAME = "Medium Armor Master"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Dexterous Wearer",
                        "While wearing Medium armor with a Dexterity score of 16 or higher, add 3 instead of 2 to your AC",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Medium Armor Training\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Dexterous Wearer. While you're wearing Medium armor, you can add 3, rather than 2, to your AC if you have a Dexterity score of 16 or higher.\n"
        )


class ModeratelyArmored(_AbilityScoreFeat):
    _NAME = "Moderately Armored"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def __init__(self, character_level: int, ability: Ability):
        super().__init__(character_level, ability)
        self.passive = True

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    ("Armor Training", "Medium armor"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Light Armor Training\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Armor Training. You gain training with Medium armor.\n"
        )


class MountedCombatant(_AbilityScoreFeat):
    _NAME = "Mounted Combatant"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY, Ability.WISDOM)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Ability Score",
                        f"+1 {self.ability.value}, to a maximum of 20",
                    ),
                    (
                        "Mounted Strike",
                        "While mounted, Advantage on attack rolls against an unmounted creature within 5 feet of your mount that is at least one size smaller than the mount",
                    ),
                    (
                        "Leap Aside",
                        "While you ride it and neither of you is Incapacitated, your mount takes no damage on a successful Dexterity save against a half-damage effect, and half on a failed one",
                    ),
                    (
                        "Veer",
                        "While mounted and not Incapacitated, make an attack that hits your mount hit you instead",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength, Dexterity, or Wisdom score by 1, to a maximum of 20.\n"
            "Mounted Strike. While mounted, you have Advantage on attack rolls against any unmounted creature within 5 feet of your mount that is at least one size smaller than the mount.\n"
            "Leap Aside. If your mount is subjected to an effect that allows it to make a Dexterity saving throw to take only half damage, it instead takes no damage if it succeeds on the saving throw and only half damage if it fails. For your mount to gain this benefit, you must be riding it, and neither of you can have the Incapacitated condition.\n"
            "Veer. While mounted, you can force an attack that hits your mount to hit you instead if you don't have the Incapacitated condition.\n"
        )


class Observant(_AbilityScoreFeat):
    _NAME = "Observant"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Keen Observer",
                        "Choose Insight, Investigation or Perception: proficiency in it, or Expertise if you're already proficient",
                    ),
                    ("Quick Search", "Take the Search action as a Bonus Action"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Intelligence or Wisdom 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence or Wisdom score by 1, to a maximum of 20.\n"
            "Keen Observer. Choose one of the following skills: Insight, Investigation, or Perception. If you lack proficiency with the chosen skill, you gain proficiency in it, and if you already have proficiency in it, you gain Expertise in it.\n"
            "Quick Search. You can take the Search action as a Bonus Action.\n"
        )


class Piercer(_AbilityScoreFeat):
    _NAME = "Piercer"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Puncture",
                        "Once per turn, when you hit a creature with an attack that deals Piercing damage, reroll one of its damage dice; you must use the new roll",
                    ),
                    (
                        "Enhanced Critical",
                        "When you score a Critical Hit that deals Piercing damage, roll one more damage die for the extra Piercing damage",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity by 1, to a maximum of 20.\n"
            "Puncture. Once per turn, when you hit a creature with an attack that deals Piercing damage, you can reroll one of the attack's damage dice, and you must use the new roll.\n"
            "Enhanced Critical. When you score a Critical Hit that deals Piercing damage to a creature, you can roll one additional damage die when determining the extra Piercing damage the target takes.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class Poisoner(_AbilityScoreFeat):
    _NAME = "Poisoner"
    _ABILITIES = (Ability.DEXTERITY, Ability.INTELLIGENCE)

    def __init__(self, character_level: int, ability: Ability):
        if character_level < self._MIN_LEVEL:
            raise ValueError(
                f"{self._NAME} requires character level {self._MIN_LEVEL} or higher."
            )
        if ability not in self._ABILITIES:
            allowed = " or ".join(a.value for a in self._ABILITIES)
            raise ValueError(f"{self._NAME} ability increase must be {allowed}.")
        self.ability = ability
        self._bonus = AbilityScoreBonus(
            [(ability, 1)],
            total=1,
            error_prefix=self._NAME,
            max_score=MAX_ABILITY_SCORE,
        )
        Feature.__init__(
            self, name=self._NAME, origin=self._ORIGIN, usage_tags=["utility"]
        )

    def apply(self, ledger_writer: LedgerWriter):
        self._bonus.apply(ledger_writer)

    def calculate_dc(self, character: CharacterView) -> int:
        modifier = character.get_ability_modifier(self.ability)
        proficiency_bonus = character.get_proficiency_bonus()
        return 8 + modifier + proficiency_bonus

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Potent Poison",
                        "Your Poison damage ignores Resistance to Poison damage",
                    ),
                    ("Poisoner's Kit", "Proficiency"),
                )
            ),
            Option(
                "Brew Poison",
                (
                    Facts(
                        (
                            (
                                "Brew",
                                "1 hour with a Poisoner's Kit and 50 GP of materials: Proficiency Bonus doses",
                            ),
                            (
                                "Apply",
                                "Bonus Action: coat a weapon or piece of ammunition. It lasts 1 minute or until it deals damage.",
                            ),
                            (
                                "Save",
                                f"A creature damaged by it makes a Constitution save, DC {dc_formula(self.ability)}",
                            ),
                            (
                                "Failed",
                                "2d8 Poison damage and Poisoned until the end of your next turn",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Dexterity or Intelligence score by 1, to a maximum of 20.\n"
            "Potent Poison. When you make a damage roll that deals Poison damage, it ignores Resistance to Poison damage.\n"
            "Brew Poison. You gain proficiency with the Poisoner's Kit. With 1 hour of work using such a kit and expending 50 GP worth of materials, you can create a number of poison doses equal to your Proficiency Bonus. As a Bonus Action, you can apply a poison dose to a weapon or piece of ammunition. Once applied, the poison retains its potency for 1 minute or until you deal damage with the poisoned item, whichever is shorter. When a creature takes damage from the poisoned item, that creature must succeed on a Constitution saving throw (DC 8 plus the modifier of the ability increased by this feat and your Proficiency Bonus) or take 2d8 Poison damage and have the Poisoned condition until the end of your next turn.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class PolearmMaster(_AbilityScoreFeat):
    _NAME = "Polearm Master"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Weapons",
                        "Quarterstaff, Spear, or a weapon with both Heavy and Reach",
                    ),
                    (
                        "Pole Strike",
                        "Right after the Attack action with one: Bonus Action melee attack with the other end, d4 Bludgeoning damage",
                    ),
                    (
                        "Reactive Strike",
                        "While holding one: Reaction to make a melee attack against a creature that enters your reach with it",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Strength or Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Dexterity or Strength score by 1, to a maximum of 20.\n"
            "Pole Strike. Immediately after you take the Attack action and attack with a Quarterstaff, a Spear, or a weapon that has the Heavy and Reach properties, you can use a Bonus Action to make a melee attack with the opposite end of the weapon. The weapon deals Bludgeoning damage, and the weapon's damage die for this attack is a d4.\n"
            "Reactive Strike. While you're holding a Quarterstaff, a Spear, or a weapon that has the Heavy and Reach properties, you can take a Reaction to make one melee attack against a creature that enters the reach you have with that weapon.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class Resilient(_AbilityScoreFeat):
    _NAME = "Resilient"
    _ABILITIES = tuple(Ability)  # any ability is valid

    def __init__(self, character_level: int, ability: Ability):
        super().__init__(character_level, ability)
        self.passive = True

    def apply(self, ledger_writer: LedgerWriter):
        super().apply(ledger_writer)
        SavingThrowProficiency([self.ability]).apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    ("Saving Throw Proficiency", f"{self.ability.value} saving throws"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Choose one ability in which you lack saving throw proficiency. Increase the chosen ability score by 1, to a maximum of 20.\n"
            "Saving Throw Proficiency. You gain saving throw proficiency with the chosen ability.\n"
        )


class RitualCaster(_AbilityScoreFeat):
    _NAME = "Ritual Caster"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)

    def __init__(self, character_level: int, ability: Ability):
        if character_level < self._MIN_LEVEL:
            raise ValueError(
                f"{self._NAME} requires character level {self._MIN_LEVEL} or higher."
            )
        if ability not in self._ABILITIES:
            allowed = " or ".join(a.value for a in self._ABILITIES)
            raise ValueError(f"{self._NAME} ability increase must be {allowed}.")
        self.ability = ability
        self._bonus = AbilityScoreBonus(
            [(ability, 1)],
            total=1,
            error_prefix=self._NAME,
            max_score=MAX_ABILITY_SCORE,
        )
        Feature.__init__(
            self, name=self._NAME, origin=self._ORIGIN, usage_tags=["utility"]
        )

    def apply(self, ledger_writer: LedgerWriter):
        self._bonus.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Ritual Spells",
                        f"Proficiency Bonus level 1 Ritual spells, always prepared and castable with your spell slots; one more each time your Proficiency Bonus increases. {self.ability.value} is their spellcasting ability.",
                    ),
                    (
                        "Quick Ritual",
                        "Cast a prepared Ritual spell in its normal casting time, without a spell slot; once per Long Rest",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Intelligence, Wisdom, or Charisma 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Ritual Spells. Choose a number of level 1 spells equal to your Proficiency Bonus that have the Ritual tag. You always have those spells prepared, and you can cast them with any spell slots you have. The spells' spellcasting ability is the ability increased by this feat. Whenever your Proficiency Bonus increases thereafter, you can add an additional level 1 spell with the Ritual tag to the spells always prepared with this feature.\n"
            "Quick Ritual. With this benefit, you can cast a Ritual spell that you have prepared using its regular casting time rather than the extended time for a Ritual. Doing so doesn't require a spell slot. Once you cast the spell in this way, you can't use this benefit again until you finish a Long Rest.\n"
        )


class Sentinel(_AbilityScoreFeat):
    _NAME = "Sentinel"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Guardian",
                        "Immediately after a creature within 5 feet of you takes the Disengage action or hits a target other than you, make an Opportunity Attack against it",
                    ),
                    (
                        "Halt",
                        "A creature hit by your Opportunity Attack has Speed 0 for the rest of the turn",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Strength or Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Guardian. Immediately after a creature within 5 feet of you takes the Disengage action or hits a target other than you with an attack, you can make an Opportunity Attack against that creature.\n"
            "Halt. When you hit a creature with an Opportunity Attack, the creature's Speed becomes 0 for the rest of the current turn.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class ShadowTouched(_AbilityScoreFeat):
    _NAME = "Shadow Touched"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Spells",
                        "Invisibility and one level 1 Illusion or Necromancy spell, always prepared",
                    ),
                    (
                        "Casting",
                        f"Each once per Long Rest without a spell slot, or with your spell slots. {self.ability.value} is their spellcasting ability.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "Your exposure to the Shadowfell's magic grants you the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Shadow Magic. Choose one level 1 spell from the Illusion or Necromancy school of magic. You always have that spell and the Invisibility spell prepared. You can cast each of these spells without expending a spell slot. Once you cast either spell in this way, you can't cast that spell in this way again until you finish a Long Rest. You can also cast these spells using spell slots you have of the appropriate level. The spells' spellcasting ability is the ability increased by this feat.\n"
        )


class Sharpshooter(_AbilityScoreFeat):
    _NAME = "Sharpshooter"
    _ABILITIES = (Ability.DEXTERITY,)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Bypass Cover",
                        "Your ranged weapon attacks ignore Half Cover and Three-Quarters Cover",
                    ),
                    (
                        "Firing in Melee",
                        "No Disadvantage on Ranged weapon attacks for being within 5 feet of an enemy",
                    ),
                    (
                        "Long Shots",
                        "No Disadvantage on Ranged weapon attacks at long range",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Dexterity score by 1, to a maximum of 20.\n"
            "Bypass Cover. Your ranged attacks with weapons ignore Half Cover and Three-Quarters Cover.\n"
            "Firing in Melee. Being within 5 feet of an enemy doesn't impose Disadvantage on your attack rolls with Ranged weapons.\n"
            "Long Shots. Attacking at long range doesn't impose Disadvantage on your attack rolls with Ranged weapons.\n"
        )


class ShieldMaster(_AbilityScoreFeat):
    _NAME = "Shield Master"
    _ABILITIES = (Ability.STRENGTH,)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts((("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),)),
            Option(
                "Shield Bash",
                (
                    Facts(
                        (
                            (
                                "Trigger",
                                "Once on each of your turns, you hit a creature within 5 feet with a Melee weapon as part of the Attack action, with a Shield equipped",
                            ),
                            ("Save", f"Strength, DC {dc_formula(Ability.STRENGTH)}"),
                            (
                                "Failed",
                                "Push it 5 feet away, or knock it Prone (your choice)",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Interpose Shield",
                (
                    Facts(
                        (
                            ("Action", "Reaction, while holding a Shield"),
                            (
                                "Trigger",
                                "An effect lets you make a Dexterity save for half damage",
                            ),
                            ("Effect", "Take no damage if you succeed"),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Shield Training\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength score by 1, to a maximum of 20.\n"
            "Shield Bash. If you attack a creature within 5 feet of you as part of the Attack action and hit with a Melee weapon, you can immediately bash the target with your Shield if it's equipped, forcing the target to make a Strength saving throw (DC 8 plus your Strength modifier and Proficiency Bonus). On a failed save, you either push the target 5 feet from you or cause it to have the Prone condition (your choice). You can use this benefit only once on each of your turns.\n"
            "Interpose Shield. If you're subjected to an effect that allows you to make a Dexterity saving throw to take only half damage, you can take a Reaction to take no damage if you succeed on the saving throw and are holding a Shield.\n"
        )

    def calculate_dc(self, character: CharacterView) -> int:
        strength_modifier = character.get_strength_modifier()
        proficiency_bonus = character.get_proficiency_bonus()
        return 8 + strength_modifier + proficiency_bonus

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class SkillExpert(_AbilityScoreFeat):
    _NAME = "Skill Expert"
    _ABILITIES = tuple(Ability)  # any ability is valid

    def __init__(self, character_level: int, ability: Ability, skill: Skill):
        self._proficiency = SkillProficiencyChoice(
            [skill], list(Skill), count=1, error_prefix="Skill Expert"
        )
        self._expertise = SkillExpertiseChoice(
            [skill], list(Skill), count=1, error_prefix="Skill Expert"
        )
        super().__init__(character_level, ability)
        self.passive = True

    def apply(self, ledger_writer: LedgerWriter):
        # Both grants are idempotent flags, and expertise's proficiency
        # requirement is validated once everything has applied - so there's
        # nothing to check against what was granted before this feat.
        super().apply(ledger_writer)
        self._proficiency.apply(ledger_writer)
        self._expertise.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    ("Skill Proficiency", self._proficiency.skills[0].value),
                    ("Expertise", self._expertise.skills[0].value),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 20.\n"
            "Skill Proficiency. You gain proficiency in one skill of your choice.\n"
            "Expertise. Choose one skill in which you have proficiency but lack Expertise. You gain Expertise with that skill.\n"
        )


class Skulker(_AbilityScoreFeat):
    _NAME = "Skulker"
    _ABILITIES = (Ability.DEXTERITY,)

    def __init__(self, character_level: int, ability: Ability):
        super().__init__(character_level, ability)
        self._sense = GrantSense(Sense.BLINDSIGHT, 10)

    def apply(self, ledger_writer: LedgerWriter):
        super().apply(ledger_writer)
        self._sense.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    ("Blindsight", "10 feet"),
                    (
                        "Fog of War",
                        "Advantage on Dexterity (Stealth) checks made as part of the Hide action during combat",
                    ),
                    (
                        "Sniper",
                        "If you attack while hidden and miss, the attack roll doesn't reveal your location",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Dexterity score by 1, to a maximum of 20.\n"
            "Blindsight. You have Blindsight with a range of 10 feet.\n"
            "Fog of War. You exploit the distractions of battle, gaining Advantage on any Dexterity (Stealth) check you make as part of the Hide action during combat.\n"
            "Sniper. If you make an attack roll while hidden and the roll misses, making the attack roll doesn't reveal your location.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class Slasher(_AbilityScoreFeat):
    _NAME = "Slasher"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Hamstring",
                        "Once per turn, when you hit a creature with an attack that deals Slashing damage, reduce its Speed by 10 feet until the start of your next turn",
                    ),
                    (
                        "Enhanced Critical",
                        "When you score a Critical Hit that deals Slashing damage, the creature has Disadvantage on attack rolls until the start of your next turn",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Hamstring. Once per turn when you hit a creature with an attack that deals Slashing damage, you can reduce the Speed of that creature by 10 feet until the start of your next turn.\n"
            "Enhanced Critical. When you score a Critical Hit that deals Slashing damage to a creature, it has Disadvantage on attack rolls until the start of your next turn.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class Speedy(_AbilityScoreFeat):
    _NAME = "Speedy"
    _ABILITIES = (Ability.DEXTERITY, Ability.CONSTITUTION)

    def apply(self, ledger_writer: LedgerWriter):
        super().apply(ledger_writer)
        # "Speed Increase. Your Speed increases by 10 feet."
        SpeedBonus(10).apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    ("Speed Increase", "+10 feet"),
                    (
                        "Dash over Difficult Terrain",
                        "When you Dash on your turn, Difficult Terrain costs no extra movement for the rest of that turn",
                    ),
                    (
                        "Agile Movement",
                        "Opportunity Attacks have Disadvantage against you",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Dexterity or Constitution 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Dexterity or Constitution score by 1, to a maximum of 20.\n"
            "Speed Increase. Your Speed increases by 10 feet.\n"
            "Dash over Difficult Terrain. When you take the Dash action on your turn, Difficult Terrain doesn't cost you extra movement for the rest of that turn.\n"
            "Agile Movement. Opportunity Attacks have Disadvantage against you.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class SpellSniper(_AbilityScoreFeat):
    _NAME = "Spell Sniper"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Bypass Cover",
                        "Your spell attack rolls ignore Half Cover and Three-Quarters Cover",
                    ),
                    (
                        "Casting in Melee",
                        "No Disadvantage on spell attack rolls for being within 5 feet of an enemy",
                    ),
                    (
                        "Increased Range",
                        "A spell with a range of 10+ feet that makes an attack roll gains 60 feet of range",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Spellcasting or Pact Magic Feature\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Bypass Cover. Your attack rolls for spells ignore Half Cover and Three-Quarters Cover.\n"
            "Casting in Melee. Being within 5 feet of an enemy doesn't impose Disadvantage on your attack rolls with spells.\n"
            "Increased Range. When you cast a spell that has a range of at least 10 feet and requires you to make an attack roll, you can increase the spell's range by 60 feet.\n"
        )


class Telekinetic(_AbilityScoreFeat):
    _NAME = "Telekinetic"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Minor Telekinesis",
                        f"You learn Mage Hand: no Verbal or Somatic components, the hand can be Invisible, and its range and leash are 30 feet longer. {self.ability.value} is its spellcasting ability.",
                    ),
                )
            ),
            Option(
                "Telekinetic Shove",
                (
                    Facts(
                        (
                            ("Action", "Bonus Action"),
                            ("Range", "30 feet"),
                            ("Target", "One creature you can see"),
                            ("Save", f"Strength, DC {dc_formula(self.ability)}"),
                            ("Failed", "Moved 5 feet toward or away from you"),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Minor Telekinesis. You learn the Mage Hand spell. You can cast it without Verbal or Somatic components, you can make the spectral hand Invisible, and its range and the distance it can be away from you both increase by 30 feet when you cast it. The spell's spellcasting ability is the ability increased by this feat.\n"
            "Telekinetic Shove. As a Bonus Action, you can telekinetically shove one creature you can see within 30 feet of yourself. When you do so, the target must succeed on a Strength saving throw (DC 8 plus the ability modifier of the score increased by this feat and your Proficiency Bonus) or be moved 5 feet toward or away from you.\n"
        )

    def calculate_dc(self, character: CharacterView) -> int:
        modifier = character.get_ability_modifier(self.ability)
        proficiency_bonus = character.get_proficiency_bonus()
        return 8 + modifier + proficiency_bonus

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE


class Telepathic(_AbilityScoreFeat):
    _NAME = "Telepathic"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)

    def __init__(self, character_level: int, ability: Ability):
        if character_level < self._MIN_LEVEL:
            raise ValueError(
                f"{self._NAME} requires character level {self._MIN_LEVEL} or higher."
            )
        if ability not in self._ABILITIES:
            allowed = " or ".join(a.value for a in self._ABILITIES)
            raise ValueError(f"{self._NAME} ability increase must be {allowed}.")
        self.ability = ability
        self._bonus = AbilityScoreBonus(
            [(ability, 1)],
            total=1,
            error_prefix=self._NAME,
            max_score=MAX_ABILITY_SCORE,
        )
        Feature.__init__(
            self, name=self._NAME, origin=self._ORIGIN, usage_tags=["utility"]
        )

    def apply(self, ledger_writer: LedgerWriter):
        self._bonus.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Telepathic Utterance",
                        "Speak telepathically to a creature you can see within 60 feet, in a language you know; it understands only if it knows that language and can't reply this way",
                    ),
                    (
                        "Detect Thoughts",
                        f"Always prepared; cast it once per Long Rest without a slot or components, or with your spell slots. {self.ability.value} is its spellcasting ability.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Telepathic Utterance. You can speak telepathically to any creature you can see within 60 feet of yourself. Your telepathic utterances are in a language you know, and the creature understands you only if it knows that language. Your communication doesn't give the creature the ability to respond to you telepathically.\n"
            "Detect Thoughts. You always have the Detect Thoughts spell prepared. You can cast it without a spell slot or spell components, and you must finish a Long Rest before you can cast it in this way again. You can also cast it using spell slots you have of the appropriate level. Your spellcasting ability for the spell is the ability increased by this feat.\n"
        )


class WarCaster(_AbilityScoreFeat):
    _NAME = "War Caster"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Ability Score",
                        f"+1 {self.ability.value}, to a maximum of 20",
                    ),
                    (
                        "Concentration",
                        "Advantage on Constitution saves to maintain Concentration",
                    ),
                    (
                        "Reactive Spell",
                        "When a creature provokes an Opportunity Attack by leaving your reach, take a Reaction to cast a spell at it instead. The spell must have a casting time of an action and target only that creature.",
                    ),
                    (
                        "Somatic Components",
                        "Perform them even with weapons or a Shield in one or both hands",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Spellcasting or Pact Magic Feature\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Concentration. You have Advantage on Constitution saving throws that you make to maintain Concentration.\n"
            "Reactive Spell. When a creature provokes an Opportunity Attack from you by leaving your reach, you can take a Reaction to cast a spell at the creature rather than making an Opportunity Attack. The spell must have a casting time of one action and must target only that creature.\n"
            "Somatic Components. You can perform the Somatic components of spells even when you have weapons or a Shield in one or both hands.\n"
        )


class WeaponMaster(_AbilityScoreFeat):
    _NAME = "Weapon Master"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Mastery Property",
                        "Use the mastery property of one kind of Simple or Martial weapon you're proficient with; change the kind when you finish a Long Rest",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Mastery Property. Your training with weapons allows you to use the mastery property of one kind of Simple or Martial weapon of your choice, provided you have proficiency with it. Whenever you finish a Long Rest, you can change the kind of weapon to another eligible kind.\n"
        )


class ColdCaster(_AbilityScoreFeat):
    _NAME = "Cold Caster"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Cantrip",
                        f"Ray of Frost (or another Wizard cantrip if you know it); {self.ability.value} is its spellcasting ability",
                    ),
                    (
                        "Frostbite",
                        "Once per turn, when an attack roll hits a creature and deals Cold damage, it subtracts 1d4 from its next save before the end of your next turn",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "General Feat (Prerequisite: Level 4+)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Cantrip. You learn the Ray of Frost cantrip. If you already know it, you learn a different Wizard cantrip of your choice. The spell's spellcasting ability is the ability increased by this feat.\n"
            "Frostbite. Once per turn when you hit a creature with an attack roll and deal Cold damage, you can temporarily negate the creature's defenses. The creature subtracts 1d4 from the next saving throw it makes before the end of your next turn.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class Dragonscarred(_AbilityScoreFeat):
    _NAME = "Dragonscarred"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.CONSTITUTION, Ability.CHARISMA)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Damage Resistance",
                        "One of Acid, Cold, Fire, Lightning or Poison, chosen when you take the feat",
                    ),
                    (
                        "Fearsome Power",
                        "When you deal damage to a creature as part of the Attack or Magic action on your turn, use Dragon's Terror (Cult of the Dragon Initiate) as a Bonus Action this turn",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "General Feat (Prerequisite: Level 4+, Cult of the Dragon Initiate Feat)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Constitution or Charisma score by 1, to a maximum of 20.\n"
            "Damage Resistance. When you gain this feat, choose Acid, Cold, Fire, Lightning, or Poison. You have Resistance to the chosen damage type.\n"
            "Fearsome Power. When you deal damage to a creature as part of the Attack or Magic action on your turn, you can use the Dragon's Terror benefit of the Cult of the Dragon Initiate feat as a Bonus Action this turn.\n"
        )


class EnclaveMAGIC(_AbilityScoreFeat):
    _NAME = "Enclave Magic"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Friend to Animals",
                        "Advantage on checks for the Influence action with Beasts",
                    ),
                    (
                        "Two Hearts, One Mind",
                        f"Beast Sense is always prepared; cast it once per Long Rest without a slot (then it needs no Concentration), or with your spell slots. {self.ability.value} is its spellcasting ability.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "General Feat (Prerequisite: Level 4+, Emerald Enclave Fledgling Feat)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Friend to Animals. You have Advantage on ability checks when taking the Influence action with Beasts.\n"
            "Two Hearts, One Mind. You always have the Beast Sense spell prepared. You can cast it once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. When you cast it without a spell slot using this feature, it doesn't require Concentration. You can also cast the spell using any spell slots you have of the appropriate level. The spell's spellcasting ability is the ability increased by this feat.\n"
        )

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST


class FairyTrickster(_AbilityScoreFeat):
    _NAME = "Fairy Trickster"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.DEXTERITY, Ability.CHARISMA)
    _USES = FeatureUses(
        max_uses=MAX_PROFICIENCY_BONUS,
        regain_all_on="long rest",
        current_formula="Current amount: equal to your proficiency bonus.",
        gained_at=PROFICIENCY_BONUS_GAINED_AT,
    )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Flustering Strike's uses are in the panel below.
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Faerie Trod Trotter",
                        "When you take the Disengage action on your turn, Difficult Terrain costs no extra movement for the rest of the turn",
                    ),
                )
            ),
            Option(
                "Flustering Strike",
                (
                    Facts(
                        (
                            ("Trigger", "You hit a creature with an attack roll"),
                            ("Save", f"Wisdom, DC {dc_formula(self.ability)}"),
                            (
                                "Failed",
                                "Disadvantage on saving throws until the end of your next turn",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "General Feat (Prerequisite: Level 4+)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Dexterity or Charisma ability score by 1, to a maximum of 20.\n"
            "Faerie Trod Trotter. When you take the Disengage action on your turn, Difficult Terrain doesn't cost you extra movement for the rest of that turn.\n"
            "Flustering Strike. When you hit a creature with an attack roll, you can attempt to fluster the target. The target must succeed on a Wisdom saving throw (DC 8 plus the ability modifier of the score increased by this feat and your Proficiency Bonus) or have Disadvantage on saving throws until the end of your next turn.\n"
            "You can use this benefit a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest."
        )
        return description

    def calculate_dc(self, character: CharacterView) -> int:
        modifier = character.get_ability_modifier(self.ability)
        proficiency_bonus = character.get_proficiency_bonus()
        return 8 + modifier + proficiency_bonus

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class GenieMagic(_AbilityScoreFeat):
    _NAME = "Genie Magic"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)
    _USES = FeatureUses(max_uses=1, regain_all_on="long rest")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Wish Magic",
                        f"Magic action: cast a level 1 Sorcerer spell with a casting time of an action, once per Long Rest. {self.ability.value} is its spellcasting ability.",
                    ),
                    (
                        "Slot level",
                        "As a level 1 slot; level 2 from character level 11, level 3 from 17",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "General Feat (Prerequisite: Level 4+)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Wish Magic. As a Magic action, you can cast a level 1 spell of your choice from the Sorcerer spell list that has a casting time of an action. Once you use this benefit, you can't do so again until you finish a Long Rest. The spell's spellcasting ability is the ability increased by this feat.\n"
            "When you reach level 11, the spell you cast with this feat is cast as though using a level 2 spell slot. When you reach level 17, the spell is cast as though using a level 3 spell slot.\n"
        )


class HarperTeamwork(_AbilityScoreFeat):
    _NAME = "Harper Teamwork"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.DEXTERITY, Ability.CHARISMA)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Withering Wordplay",
                        "When you Help an ally's attack roll against an enemy, that enemy also has Disadvantage on its first saving throw before the start of your next turn",
                    ),
                    (
                        "Inspiring Willpower",
                        "When you succeed on a save to end the Frightened or Paralyzed condition on yourself, end the same condition on one ally you can see within 30 feet",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "General Feat (Prerequisite: Level 4+, Harper Agent Feat)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Dexterity or Charisma score by 1, to a maximum of 20.\n"
            "Withering Wordplay. When you take the Help action to assist an ally's attack roll against an enemy, that enemy also has Disadvantage on the first saving throw it makes before the start of your next turn.\n"
            "Inspiring Willpower. If you succeed on a saving throw to end the Frightened or Paralyzed condition on yourself, you can choose one ally you can see within 30 feet of yourself that has the same condition. That condition immediately ends for that ally.\n"
        )


class LordlyResolve(_AbilityScoreFeat):
    _NAME = "Lordly Resolve"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.STRENGTH, Ability.CHARISMA)
    _USES = FeatureUses(max_uses=1, regain_all_on="long rest")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Facts((("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),)),
            Option(
                "Standard Bearer",
                (
                    Facts(
                        (
                            ("Action", "Bonus Action"),
                            ("Range", "60 feet"),
                            ("Target", "Up to three creatures that can see you"),
                            (
                                "Rally",
                                "Each can use its Reaction to stand up from Prone, if its Speed isn't 0",
                            ),
                            (
                                "Resolve",
                                "For 1 minute, or until you're Incapacitated, they can't be possessed, Charmed or Frightened; if already, they have Advantage on new saves against it",
                            ),
                            ("Limit", "Once per Long Rest"),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "General Feat (Prerequisite: Level 4+, Lords' Alliance Agent Feat)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Charisma score by 1, to a maximum of 20.\n"
            "Standard Bearer. As a Bonus Action, choose up to three creatures within 60 feet of yourself that can see you. Each target can immediately take a Reaction to right itself and end the Prone condition, provided its Speed isn't 0.\n"
            "Additionally, you bolster the targets' resolve, which lasts for 1 minute or until you have the Incapacitated condition. While bolstered, a target can't be possessed or gain the Charmed or Frightened condition; if a target is already possessed, Charmed, or Frightened, the target has Advantage on any new saving throw against the relevant effect.\n"
            "Once you use this benefit, you can't do so again until you finish a Long Rest.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class MythalTouched(_AbilityScoreFeat):
    _NAME = "Mythal Touched"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)
    _USES = FeatureUses(
        max_uses=MAX_PROFICIENCY_BONUS,
        regain_all_on="long rest",
        current_formula="Current amount: equal to your proficiency bonus.",
        gained_at=PROFICIENCY_BONUS_GAINED_AT,
    )

    def calculate_dc(self, character: CharacterView) -> int:
        modifier = character.get_ability_modifier(self.ability)
        proficiency_bonus = character.get_proficiency_bonus()
        return 8 + modifier + proficiency_bonus

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Mythal Ward's uses are in the panel below.
        return [
            Facts(
                (
                    (
                        "Ability Score",
                        f"+1 {self.ability.value}, to a maximum of 20",
                    ),
                )
            ),
            Option(
                "Mythal Ward",
                (
                    Facts(
                        (
                            ("Action", "Reaction"),
                            (
                                "Trigger",
                                "A spell attack hits you, or you fail a saving throw against a spell",
                            ),
                            ("Effect", "Roll a d20 on the table below"),
                            (
                                "Save DC",
                                f"8 + {self.ability.value} modifier + Proficiency Bonus",
                            ),
                        )
                    ),
                    Table(
                        ("d20", "Effect"),
                        (
                            (
                                "1-2",
                                "You and each creature within 15 feet of you make a Dexterity save: Force damage equal to 1d8 x the triggering spell's level, or half on a success.",
                            ),
                            (
                                "3-7",
                                "You and the triggering spell's caster form a telepathic link for 1 hour.",
                            ),
                            (
                                "8-10",
                                "Gravity reverses in a 15-foot-radius, 60-foot-tall Cylinder centered on you for 1 minute, as Reverse Gravity.",
                            ),
                            (
                                "11-13",
                                "You and the triggering spell's caster each make a Constitution save. Failed: Stunned until the end of its next turn.",
                            ),
                            (
                                "14-17",
                                "+2 bonus to AC for 1 minute, which can turn the triggering spell attack into a miss.",
                            ),
                            (
                                "18-19",
                                "Each flammable, nonmagical object within 10 feet of the triggering spell's caster bursts into flame, takes 1d4 Fire damage and is burning.",
                            ),
                            (
                                "20",
                                "The triggering spell dissipates with no effect and the action used to cast it is wasted; a spell slot used for it isn't expended.",
                            ),
                        ),
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "General Feat (Prerequisite: Level 4+)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Mythal Ward. If a spell attack hits you or you fail a saving throw against a spell, you can take a Reaction to roll on the Mythal-Touched Magic table to create a magical effect. If an effect requires a saving throw, the DC equals 8 plus the modifier of the ability increased by this feat and your Proficiency Bonus.\n"
            "You can use this benefit a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest.\n"
            "Mythal-Touched Magic (roll 1d20):\n"
            "1-2: You and each creature within 15 feet of you make a Dexterity saving throw, taking Force damage equal to 1d8 times the level of the triggering spell on a failed save or half as much on a success.\n"
            "3-7: You and the triggering spell's caster form a telepathic link for 1 hour.\n"
            "8-10: Gravity is reversed in a 15-foot-radius, 60-foot-tall Cylinder centered on you for 1 minute, per the Reverse Gravity spell.\n"
            "11-13: You and the triggering spell's caster each make a Constitution saving throw. On a failed save, the creature has the Stunned condition until the end of its next turn.\n"
            "14-17: You gain a +2 bonus to AC for 1 minute, potentially turning the triggering spell into a miss if it was a spell attack.\n"
            "18-19: Any flammable, nonmagical object within 10 feet of the triggering spell's caster bursts into flame, takes 1d4 Fire damage, and is burning.\n"
            "20: The triggering spell dissipates with no effect, and the action used to cast it is wasted. If cast with a spell slot, the slot isn't expended."
        )
        return description


class OrdersResilience(_AbilityScoreFeat):
    _NAME = "Order's Resilience"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.STRENGTH, Ability.WISDOM, Ability.CHARISMA)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Resurge",
                        "Right yourself from Prone with only 5 feet of movement",
                    ),
                    (
                        "Stronger Together",
                        "While within 5 feet of an ally that isn't Incapacitated, you and that ally have Advantage on Strength saving throws (not while you're Incapacitated)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "General Feat (Prerequisite: Level 4+, Tyro of the Gauntlet Feat)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Resurge. When you have the Prone condition, you can right yourself with only 5 feet of movement.\n"
            "Stronger Together. If you are within 5 feet of an ally that doesn't have the Incapacitated condition, you and that ally have Advantage on Strength saving throws. You can't use this benefit while you have the Incapacitated condition.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class PurpleDragonCommandant(_AbilityScoreFeat):
    _NAME = "Purple Dragon Commandant"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)
    _USES = FeatureUses(
        max_uses=MAX_PROFICIENCY_BONUS,
        regain_all_on="long rest",
        current_formula="Current amount: equal to your proficiency bonus.",
        gained_at=PROFICIENCY_BONUS_GAINED_AT,
    )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Encourage Ally",
                        f"Bonus Action: one ally you can see within 30 feet gains 2d6 + {self.ability.value} modifier Temporary Hit Points. Proficiency Bonus times per Long Rest.",
                    ),
                    ("Last Stand", "Advantage on attack rolls while Bloodied"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "General Feat (Prerequisite: Level 4+, Purple Dragon Rook Feat or Martial Weapon Proficiency)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Encourage Ally. As a Bonus Action, you bolster one ally you can see within 30 feet. The ally gains Temporary Hit Points equal to 2d6 plus the modifier of the ability score increased by this feat. You can take this Bonus Action a number of times equal to your Proficiency Bonus, and you regain all uses when you finish a Long Rest.\n"
            "Last Stand. You have Advantage on attack rolls while Bloodied.\n"
            f"Right now: Encourage Ally grants 2d6 + {character.get_ability_modifier(self.ability)} Temporary Hit Points."
        )
        return description

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class SpellfireAdept(_AbilityScoreFeat):
    _NAME = "Spellfire Adept"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Fueled Spellfire",
                        "Once per turn, when a spell you cast deals Radiant damage, expend and roll up to two Hit Point Dice and add the total to one damage roll",
                    ),
                    (
                        "Searing Spellfire",
                        "Your Radiant damage rolls ignore Resistance to Radiant damage",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "General Feat (Prerequisite: Level 4+, Spellfire Spark Feat or the Spellcasting or Pact Magic Feature)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Fueled Spellfire. Once per turn, when a spell you cast deals Radiant damage, you can expend up to two Hit Point Dice, roll them, and add the total rolled to one damage roll of the spell.\n"
            "Searing Spellfire. When you make a damage roll that deals Radiant damage, it ignores Resistance to Radiant damage.\n"
        )


class StreetJustice(_AbilityScoreFeat):
    _NAME = "Street Justice"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Headlock",
                        "Your allies have Advantage on attack rolls against a creature you're grappling",
                    ),
                    (
                        "Sturdy Knot",
                        "When you bind a creature with Chain, Manacles or Rope, add your Proficiency Bonus to the DC to escape or burst it",
                    ),
                    (
                        "Tough Talk",
                        "A Hostile attitude doesn't impose Disadvantage on your Charisma (Intimidation) checks to influence a creature",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "General Feat (Prerequisite: Level 4+)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Headlock. Your allies have Advantage on attack rolls against a creature Grappled by you.\n"
            "Sturdy Knot. When you use Chain, Manacles, or Rope to bind a creature, add your Proficiency Bonus to the DC to escape or burst the Chain, Manacles, or Rope.\n"
            "Tough Talk. A creature's Hostile attitude doesn't impose Disadvantage on your Charisma (Intimidation) checks to influence that creature.\n"
        )


class ZhentarimTactics(_AbilityScoreFeat):
    _NAME = "Zhentarim Tactics"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.DEXTERITY, Ability.CHARISMA)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Retaliate",
                        "Immediately after a creature within 5 feet hits you with a melee attack, make an Opportunity Attack against it",
                    ),
                    (
                        "Versatile Merc",
                        "When you finish a Long Rest, choose a skill you're proficient in: you have Expertise in it until you finish your next Long Rest",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "General Feat (Prerequisite: Level 4+, Zhentarim Ruffian Feat)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Dexterity or Charisma score by 1, to a maximum of 20.\n"
            "Retaliate. Immediately after a creature within 5 feet of you hits you with a melee attack, you can make an Opportunity Attack against that creature.\n"
            "Versatile Merc. When you finish a Long Rest, choose a skill in which you have proficiency. You have Expertise in that skill until you finish your next Long Rest.\n"
        )


# ---------------------------------------------------------------------------
# Ravenloft Campaign General Feats
# ---------------------------------------------------------------------------


class DarkGift(GeneralFeat):

    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Dark Gift requires character level 1 or higher.")
        super().__init__(
            name="Dark Gift",
            origin="General Feat Ravenloft Campaign",
        )
        self._sense = GrantSense(Sense.BLINDSIGHT, 15)

    def apply(self, ledger_writer: LedgerWriter):
        self._sense.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Alien horrors have warped your body."),
            Facts(
                (
                    ("Breathless", "Hold your breath for 1 hour"),
                    (
                        "Extrasensory Perception",
                        "Proficiency and Expertise in Perception",
                    ),
                    ("Blindsight", "15 feet"),
                )
            ),
            Option(
                "Drawback: right after you roll a 1 on the d20 for a D20 Test",
                (
                    Facts(
                        (
                            ("Save", "Constitution, DC 13 + Proficiency Bonus"),
                            ("Failed", "Stunned until the end of your next turn"),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Exposure to alien horrors like those of the Far Realm has warmed your physical form in supernatural ways. You gain the following features.\n"
            " * Breathless. You can hold your breath for 1 hour.\n"
            " * Extrasensory Perception. You have proficiency in the Perception skill, if you lack it. You also gain Expertise in that skill.\n"
            " * Blindsight. In addition, you have Blindsight with a range of 15 feet.\n"
            " * Warping Flesh. Immediately after you make a D20 Test and roll a 1 on the d20, the aberrant influence infecting your form flares, wrenching control of your flesh. Make a Constitution saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you have the Stunned condition until the end of your next turn."
        )

    def calculate_dc(self, character: CharacterView) -> int:
        proficiency_bonus = character.get_proficiency_bonus()
        return 13 + proficiency_bonus

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class EchoingSoul(GeneralFeat):

    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Echoing Soul requires character level 1 or higher.")
        super().__init__(
            name="Echoing Soul",
            origin="General Feat Ravenloft Campaign",
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("You feel echoes of a past or alternate life."),
            Facts(
                (
                    (
                        "Channelled Prowess",
                        "Proficiency in two skills of your choice, and Expertise in one skill you're proficient in; change that choice after any Long Rest",
                    ),
                    ("Inherent Tongues", "One extra language"),
                )
            ),
            Option(
                "Drawback: right after you roll a 1 on the d20 for a D20 Test",
                (
                    Facts(
                        (
                            ("Save", "Constitution, DC 13 + Proficiency Bonus"),
                            (
                                "Failed",
                                "Incapacitated until the end of your next turn, with your Speed halved",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "You experience echoes from a past or alternate life. You gain the following features.\n"
            " * Channelled Prowess. You have proficiency in two skills of your choice. In addition, choose one skill you have proficiency in. You gain Expertise in that skill. Whenever you finish a Long Rest you can change your choice of for this benefit.\n"
            " * Inherent Tongues. You know one additional language of your choice, which you choose from the language tables in the Player's Handbook.\n"
            " * Intrusive Echoes. Immediately after you make a D20 Test and roll a 1 on the d20, memories and sensations from your soul's other life threaten to overtake you. Make a Constitution saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you have the Incapacitated condition until the end of your next turn. While you are Incapacitated in this way, your Speed is halved."
        )

    def calculate_dc(self, character: CharacterView) -> int:
        proficiency_bonus = character.get_proficiency_bonus()
        return 13 + proficiency_bonus

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class GatheredWhispers(GeneralFeat):

    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Gathered Whispers requires character level 1 or higher.")
        super().__init__(
            name="Gathered Whispers",
            origin="General Feat Ravenloft Campaign",
            uses=FeatureUses(
                max_uses=MAX_PROFICIENCY_BONUS,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your proficiency bonus.",
                gained_at=PROFICIENCY_BONUS_GAINED_AT,
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Whispering spirits only you can hear haunt you."),
            Facts(
                (
                    (
                        "Spirit Whispers",
                        "You learn Message (no Material components) and always have Augury prepared: cast it once per Long Rest without a slot or components, or with your spell slots. Intelligence, Wisdom or Charisma is the spellcasting ability (chosen with the feat).",
                    ),
                    (
                        "Unearthly Scream",
                        "Reaction when an attack roll hits you: add your Proficiency Bonus to your AC against it. Proficiency Bonus times per Long Rest.",
                    ),
                )
            ),
            Option(
                "Drawback: right after you roll a 1 on the d20 for a D20 Test",
                (
                    Facts(
                        (
                            ("Save", "Wisdom, DC 13 + Proficiency Bonus"),
                            (
                                "Failed",
                                "Deafened until the end of your next turn, with Disadvantage on ability checks and attack rolls while Deafened",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You are haunted by a cacophony of whispering spirits only you can hear. You gain the following features.\n"
            " * Spirit Whispers. You learn the Message spell and can cast it without Material components. Additionally, you always have the Augury spell prepared. You can cast it without a spell slot or spell components, and you must finish a Long Rest before you can cast it in this way again. You can also cast the spell using any spell slots you have.\n"
            " * Intelligence, Wisdom, or Charisma is your spellcasting ability for this benefit (choose when you select this feat).\n"
            " * Unearthly Scream. When you are hit by an attack roll, you can take a Reaction to channel your haunting spirits into a protective, otherworldly scream. You can add your Proficiency Bonus to your AC against that attack, potentially causing it to miss. You can use this benefit a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest.\n"
            " * Voices from Beyond. Immediately after you make a D20 Test and roll a 1 on the d20, the haunting whispers rise to a ghastly volume. Make a Wisdom saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you have the Deafened condition until the end of your next turn. While Deafened, you have Disadvantage on ability checks and attack rolls."
        )
        return description

    def calculate_dc(self, character: CharacterView) -> int:
        proficiency_bonus = character.get_proficiency_bonus()
        return 13 + proficiency_bonus

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class LivingShadow(GeneralFeat):

    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Living Shadow requires character level 1 or higher.")
        super().__init__(
            name="Living Shadow",
            origin="General Feat Ravenloft Campaign",
            uses=FeatureUses(
                max_uses=MAX_PROFICIENCY_BONUS,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your proficiency bonus.",
                gained_at=PROFICIENCY_BONUS_GAINED_AT,
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Your shadow is animate, and sometimes acts on its own will."),
            Facts(
                (
                    (
                        "Grasping Shadow",
                        "You learn Mage Hand and cast it without components; Intelligence, Wisdom or Charisma is its spellcasting ability (chosen with the feat)",
                    ),
                    (
                        "Lengthened Strike",
                        "When you make a melee attack roll as part of the Attack or Magic action on your turn, your reach for it is 10 feet longer. Proficiency Bonus times per Long Rest.",
                    ),
                )
            ),
            Option(
                "Drawback: right after you roll a 1 on the d20 for a D20 Test",
                (
                    Facts(
                        (
                            ("Save", "Wisdom, DC 13 + Proficiency Bonus"),
                            (
                                "Failed",
                                "Incapacitated until the start of your next turn, then roll a d8 on Shadow's Will for what you do that turn",
                            ),
                        )
                    ),
                    Table(
                        ("d8", "Shadow's Will"),
                        (
                            (
                                "1",
                                "No action or Bonus Action; use all your movement in a random direction (d4: 1 north, 2 east, 3 south, 4 west)",
                            ),
                            (
                                "2-6",
                                "No movement or Bonus Action; Attack action with one melee attack against a random creature in reach (no action if none)",
                            ),
                            ("7-8", "You fall Prone and your turn ends"),
                        ),
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "The shadow you cast is animate and ever-present - sometimes it even acts according to its own will. You gain the following features.\n"
            " * Grasping Shadow. You learn the Mage Hand spell and can cast it without spell components. Intelligence, Wisdom or Charisma is your spellcasting ability for this spell (choose when you select this feat).\n"
            " * Lengthened Strike. When you make a melee attack roll as part of the Attack or Magic action on your turn, you can increase your reach for that attack by 10 feet, as your shadow stretches to aid you. You can use this feature a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest.\n"
            " * Ominous Will. Immediately after you make a D20 Test and roll a 1 on the d20, your shadow attempts to exert its will. Make a Wisdom saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you have the Incapacitated condition until the start of your next turn, at which point you must roll on the Shadow's Will table to determine what you do during that turn.\n"
            "Shadow's Will\n"
            "1d8\tBehaviour\n"
            "1\tYou don't take any action or a Bonus Action, and you use all your movement to move. Roll 1d4 for the direction 1, north: 2, east; 3, south; 4, west.\n"
            "2-6\tYou don't move or take a Bonus Action, and you take the Attack action to make one melee attack against a random creature within reach. If none are within reach, you take no action.\n"
            "7-8\tYou have the Prone condition, and your turn ends."
        )
        return description

    def calculate_dc(self, character: CharacterView) -> int:
        proficiency_bonus = character.get_proficiency_bonus()
        return 13 + proficiency_bonus

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class MistWalker(GeneralFeat):

    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Mist Walker requires character level 1 or higher.")
        super().__init__(
            name="Mist Walker",
            origin="General Feat Ravenloft Campaign",
            uses=FeatureUses(
                max_uses=MAX_PROFICIENCY_BONUS,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your proficiency bonus.",
                gained_at=PROFICIENCY_BONUS_GAINED_AT,
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "You slip through the Mists' grasp, but linger too long and they drain your life."
            ),
            Facts(
                (
                    (
                        "Domain Traveler",
                        "Entering the Mists to reach a domain you know by name, you count as holding a Mist talisman keyed to it. Borders a Darklord has closed still stop you.",
                    ),
                    (
                        "Mist Walk",
                        "Reaction when you take damage or fail a save to avoid or end Grappled or Restrained: teleport up to 15 feet to an unoccupied space you can see. Proficiency Bonus times per Long Rest.",
                    ),
                    (
                        "Poisoned Roots",
                        "After a Long Rest, the area within 10 miles drains you: each Short Rest you finish there, make a Constitution save (DC 13 + Proficiency Bonus) or get no benefit from it",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You know how to slip through the Mists' grasp, but this freedom comes at a price: If you remain in one area for too long, the Mists find you and drain your life force. You gain the following features.\n"
            "Domain Traveler. When you enter the Mists intent on reaching a specific domain, you are treated as if you possess a Mist talisman keyed to that domain. To use this feature, you must know the name of the domain you have chosen as your destination, but you don't need to have previously visited that land. This trait doesn't allow you to bypass domain borders closed by a Darklord's will.\n"
            "Mist Walk. When you take damage or fail a saving throw to avoid or end the Grappled or Restrained condition, you can take a Reaction and teleport up to 15 feet to an unoccupied space you can see. You can use this feature a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest.\n"
            "Poisoned Roots. When you finish a Long Rest, the world around you in a 10-mile radius becomes a siphon that leeches away at your vitality. Whenever you finish a Short Rest in that area, make a Constitution saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you get no benefits from finishing that rest."
        )
        return description

    def calculate_dc(self, character: CharacterView) -> int:
        proficiency_bonus = character.get_proficiency_bonus()
        return 13 + proficiency_bonus

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class SecondSkin(GeneralFeat):

    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Second Skin requires character level 1 or higher.")
        super().__init__(
            name="Second Skin",
            origin="General Feat Ravenloft Campaign",
            uses=FeatureUses(
                max_uses=MAX_PROFICIENCY_BONUS,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your proficiency bonus.",
                gained_at=PROFICIENCY_BONUS_GAINED_AT,
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("The Mists have toughened your skin."),
            Facts(
                (
                    (
                        "Hardened Skin",
                        "Your base AC is 13 + Dexterity modifier, and you can still use a Shield",
                    ),
                    (
                        "Resilient Form",
                        "Reaction when you take damage: reduce it by your Proficiency Bonus. Proficiency Bonus times per Long Rest.",
                    ),
                )
            ),
            Option(
                "Drawback: right after you roll a 1 on the d20 for a D20 Test",
                (
                    Facts(
                        (
                            ("Save", "Constitution, DC 13 + Proficiency Bonus"),
                            (
                                "Failed",
                                "You have the Vulnerable condition until the end of your next turn",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your skin is toughened and hardened by the Mists, granting you unnatural resilience. You gain the following features.\n"
            " * Hardened Skin. Your base AC becomes 13 + your Dexterity modifier. You can use a shield and still gain this benefit.\n"
            " * Resilient Form. When you take damage, you can take a Reaction to reduce that damage by an amount equal to your Proficiency Bonus. You can use this feature a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest.\n"
            " * Vulnerable Weakness. Immediately after you make a D20 Test and roll a 1 on the d20, your toughened skin becomes brittle and vulnerable. Make a Constitution saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you have the Vulnerable condition until the end of your next turn."
        )
        return description

    def calculate_dc(self, character: CharacterView) -> int:
        proficiency_bonus = character.get_proficiency_bonus()
        return 13 + proficiency_bonus

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class SymbioticBeing(GeneralFeat):

    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Symbiotic Being requires character level 1 or higher.")
        super().__init__(
            name="Symbiotic Being",
            origin="General Feat Ravenloft Campaign",
            uses=FeatureUses(
                max_uses=MAX_PROFICIENCY_BONUS,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your proficiency bonus.",
                gained_at=PROFICIENCY_BONUS_GAINED_AT,
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "A second being lives in your body, helping you while furthering its own agenda."
            ),
            Facts(
                (
                    (
                        "Entwined Existence",
                        "The symbiote can't be targeted. It dies when you die and revives when you're returned to life.",
                    ),
                    (
                        "Second Mind",
                        "Proficiency in Arcana, Deception, History, Intimidation, Insight, Investigation, Nature, Religion, Perception or Persuasion, and one extra language",
                    ),
                    (
                        "Sustained Symbiosis",
                        "Reaction when you fail a saving throw: expend a Hit Die, roll it and add it to the save. Proficiency Bonus times per Long Rest.",
                    ),
                )
            ),
            Option(
                "Drawback: right after you roll a 1 on the d20 for a D20 Test",
                (
                    Facts(
                        (
                            (
                                "Save",
                                "Charisma, DC 13 + Proficiency Bonus (the DM may also call for it when you act against the symbiote's agenda)",
                            ),
                            (
                                "Failed",
                                "Charmed for 1d12 hours: you must try to follow the symbiote's commands and goals. Repeat the save whenever you take damage, ending it on a success.",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "A second being resides within your body, offering knowledge and assistance while furthering its own agenda. You gain the following features.\n"
            "Entwined Existence. The symbiote can't be targeted. If you die, so does your symbiote. If you are returned to life, your symbiote also revives.\n"
            "Second Mind. You gain proficiency in one of the following skills: Arcana, Deception, History, Intimidation, Insight, Investigation, Nature, Religion, Perception, or Persuasion. You also know one additional language of your choice, chosen from the language tables in the Player's Handbook.\n"
            "Sustained Symbiosis. When you fail a saving throw, you can take a Reaction and expend one of your Hit Dice. Roll the die and add the number rolled to the saving throw, potentially turning the failure into a success.\n"
            "You can use this feature a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest.\n"
            "Symbiotic Agenda. Immediately after you make a D20 Test and roll a 1 on the d20, your symbiote attempts to assert control. Make a Charisma saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you have the Charmed condition for 1d12 hours. While Charmed, you must try to follow the symbiote's commands and further its goals, as determined by the DM. Whenever you take damage, you can repeat this save, ending the effect on a success.\n"
            "At the DM's discretion, you might make this saving throw whenever you act contrary to the symbiote's agenda."
        )
        return description

    def calculate_dc(self, character: CharacterView) -> int:
        proficiency_bonus = character.get_proficiency_bonus()
        return 13 + proficiency_bonus

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class TouchOfDeath(GeneralFeat):

    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Touch of Death requires character level 1 or higher.")
        super().__init__(
            name="Touch of Death",
            origin="General Feat Ravenloft Campaign",
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Death Touch",
                        "You learn Chill Touch and can cast it without spell components; its Necrotic damage ignores Resistance",
                    ),
                    (
                        "Spellcasting ability",
                        "Intelligence, Wisdom or Charisma, chosen when you take this feat",
                    ),
                    ("Pull of the Grave", "Disadvantage on Death Saving Throws"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Deathly power resides within you, bursting out at the slightest provocation. You gain the following features.\n"
            "Death Touch. You learn the Chill Touch spell and can cast it without spell components. Necrotic damage you deal with this spell ignores Resistance. Intelligence, Wisdom, or Charisma is your spellcasting ability for this spell (choose when you select this feat).\n"
            "Pull of the Grave. You have Disadvantage on Death Saving Throws."
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class Watchers(GeneralFeat):

    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Watchers requires character level 1 or higher.")
        super().__init__(
            name="Watchers",
            origin="General Feat Ravenloft Campaign",
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Something unnatural always watches you, as vermin and other eerie creatures."
            ),
            Facts(
                (
                    (
                        "Borrowed Eyes",
                        "Beast Sense and Speak with Animals are always prepared; cast each once per Long Rest without a slot, or with your spell slots",
                    ),
                    (
                        "Heightened Suspicion",
                        "When you take the Search action, add 1d4 to its ability checks",
                    ),
                    (
                        "Incessant Watchers",
                        "Disadvantage on saving throws against Scrying",
                    ),
                )
            ),
            Option(
                "Drawback: right after you roll a 1 on the d20 for a D20 Test",
                (
                    Facts(
                        (
                            ("Save", "Wisdom, DC 13 + Proficiency Bonus"),
                            (
                                "Failed",
                                "Disadvantage on D20 Tests for 1 minute; repeat the save at the end of each of your turns, ending it on a success",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Something unnatural is always watching you, taking the form of scurrying vermin and other eerie creatures. You gain the following features.\n"
            "Borrowed Eyes. You always have the Beast Sense and Speak with Animals spells prepared. You can cast each spell without a spell slot, and you must finish a Long Rest before you can cast it in this way again. You can also cast these spells using spell slots you have of the appropriate level.\n"
            "Heightened Suspicion. Whenever you take the Search action, you can roll 1d4 and add the number rolled to any ability check made as part of that action.\n"
            "Incessant Watchers. You have Disadvantage on saving throws made against the Scrying spell.\n"
            "In addition, immediately after you make a D20 Test and roll a 1 on the d20, paranoia threatens to overwhelm you. Make a Wisdom saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you have Disadvantage on D20 Tests for 1 minute. You can repeat the save at the end of each of your turns, ending the effect early on a success."
        )

    def calculate_dc(self, character: CharacterView) -> int:
        proficiency_bonus = character.get_proficiency_bonus()
        return 13 + proficiency_bonus

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


# ---------------------------------------------------------------------------
# Arcana Unleashed 2026 General Feats
# ---------------------------------------------------------------------------


class ElementalFamiliar(_AbilityScoreFeat):
    _NAME = "Elemental Familiar"
    _ABILITIES = tuple(Ability)

    def __init__(self, character_level: int, ability: Ability, damage_type: DamageType):
        valid_types = (
            DamageType.ACID,
            DamageType.COLD,
            DamageType.FIRE,
            DamageType.LIGHTNING,
            DamageType.THUNDER,
        )
        if damage_type not in valid_types:
            valid_str = ", ".join(dt.value for dt in valid_types)
            raise ValueError(
                f"Elemental Familiar damage type must be one of: {valid_str}."
            )
        self.damage_type = damage_type
        self._resistance = ElementalResistance(damage_type)
        super().__init__(character_level, ability)

    def apply(self, ledger_writer: LedgerWriter):
        super().apply(ledger_writer)
        self._resistance.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts((("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),)),
            Option(
                f"Elemental Energy ({self.damage_type.value})",
                (
                    Paragraph(
                        "When you cast Find Familiar, imbue your familiar with Acid, Cold, Fire, Lightning or Thunder energy until you cast it again."
                    ),
                    Facts(
                        (
                            ("Resistance", "Your familiar resists the chosen type"),
                            (
                                "Energy Pulse",
                                "Bonus Action: your familiar, within 120 feet, uses its Reaction to burst",
                            ),
                            ("Area", "5-foot Emanation from the familiar"),
                            (
                                "Save",
                                "Dexterity, DC 8 + your Find Familiar spellcasting ability modifier + Proficiency Bonus",
                            ),
                            (
                                "Failed",
                                "2d4 damage of the chosen type, and Prone if Medium or smaller",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "General Feat (Prerequisite: Level 4+, Familiar Friend Feat)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 20.\n"
            "Elemental Energy. You learn how to imbue your familiar with elemental power. When you cast the Find Familiar spell, choose Acid, Cold, Fire, Lightning, or Thunder damage. Your familiar is imbued with this energy until you cast Find Familiar again, granting it the following benefits:\n"
            "Elemental Resistance. Your familiar has Resistance to the chosen damage type.\n"
            "Energy Pulse. As a Bonus Action, you command your familiar to unleash a burst of elemental energy. Your familiar must be within 120 feet of you and take a Reaction to unleash this burst. Each creature in a 5-foot Emanation originating from your familiar makes a Dexterity saving throw (DC 8 plus your spellcasting ability modifier for the Find Familiar spell and your Proficiency Bonus). On a failed save, a creature takes 2d4 damage of the chosen type, and if the creature is Medium or smaller, it has the Prone condition."
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.AREA


class SpellResistant(_AbilityScoreFeat):
    _NAME = "Spell Resistant"
    _ABILITIES = (Ability.DEXTERITY, Ability.CONSTITUTION)
    _USES = FeatureUses(
        max_uses=MAX_PROFICIENCY_BONUS,
        regain_all_on="long rest",
        current_formula="Current amount: equal to your proficiency bonus.",
        gained_at=PROFICIENCY_BONUS_GAINED_AT,
    )

    def __init__(
        self, character_level: int, ability: Ability, resistance_damage_type: DamageType
    ):
        valid_types = (
            DamageType.NECROTIC,
            DamageType.PSYCHIC,
            DamageType.RADIANT,
            DamageType.THUNDER,
        )
        if resistance_damage_type not in valid_types:
            valid_str = ", ".join(dt.value for dt in valid_types)
            raise ValueError(
                f"Spell Resistant damage type must be one of: {valid_str}."
            )
        self.resistance_damage_type = resistance_damage_type
        self._resistance = DamageResistance(resistance_damage_type)
        super().__init__(character_level, ability)

    def apply(self, ledger_writer: LedgerWriter):
        super().apply(ledger_writer)
        self._resistance.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Magical Resilience",
                        f"Resistance to {self.resistance_damage_type.value} damage",
                    ),
                    (
                        "Magic Resistant",
                        "When you would fail a save against a spell or magical effect, add 1d6 to it. Proficiency Bonus times per Long Rest.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "General Feat (Prerequisite: Level 4+)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Dexterity or Constitution score by 1, to a maximum of 20.\n"
            "Magical Resilience. You have Resistance to one of the following damage types (choose when you gain this feat): Necrotic, Psychic, Radiant, or Thunder.\n"
            "Magic Resistant. When you would fail a saving throw against a spell or magical effect, you can roll 1d6 and add the number rolled to the save's total, potentially turning the failure into a success. You can use this benefit a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest."
        )
        return description

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


# ---------------------------------------------------------------------------
# Arcana Unleashed 2026: School Adepts
# ---------------------------------------------------------------------------

_MENTAL_ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)
_STRENGTH_OR_DEXTERITY = (Ability.STRENGTH, Ability.DEXTERITY)


class _SchoolAdept(_AbilityScoreFeat):
    """Base class for the 8 school Adept feats, which differ only in their
    name, spell table and school benefit.

    Subclasses declare:
        _NAME           – feat name, e.g. "Abjuration Adept"
        _SPELLS         – the always-prepared spell for spell slot levels 1-5, in order
        _SCHOOL_EFFECT  – the school-specific benefit text
    and implement _school_facts(), that benefit as label/value rows for the
    improved description.
    """

    _ABILITIES = _MENTAL_ABILITIES

    _SPELLS: tuple[Level1Spells, Level2Spells, Level3Spells, Level4Spells, Level5Spells]
    _SCHOOL_EFFECT: str

    def _school_facts(self) -> tuple[tuple[str, str], ...]:
        """The school benefit as label/value rows."""
        raise NotImplementedError

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        effect_name = self._SCHOOL_EFFECT.split(". ", 1)[0]
        return [
            Facts((("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),)),
            Option(effect_name, (Facts(self._school_facts()),)),
            Option(
                f"{self._NAME} Spells",
                (
                    Paragraph(
                        "Always prepared once you have spell slots of that level"
                    ),
                    Table(
                        ("Spell slot level", "Spell"),
                        tuple(
                            (str(level), spell.value)
                            for level, spell in enumerate(self._SPELLS, start=1)
                        ),
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        spell_table = "\n".join(
            f"{slot_level} | {spell.value}"
            for slot_level, spell in enumerate(self._SPELLS, start=1)
        )
        return (
            "Prerequisite: Level 4+, Spellcasting or Pact Magic Feature\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            f"Additional Spells. Your prowess allows you to always have certain spells at the ready. When you have spell slots of a level specified in the {self._NAME} Spells table, you thereafter always have the spells listed for that level and lower prepared.\n"
            f"{self._SCHOOL_EFFECT}\n"
            f"{self._NAME} Spells:\n"
            "Spell Slot Level | Spell\n"
            f"{spell_table}"
        )


class AbjurationAdept(_SchoolAdept):
    _NAME = "Abjuration Adept"
    _SPELLS = (
        AbjurationLevel1Spells.SHIELD,
        AbjurationLevel2Spells.LESSER_RESTORATION,
        AbjurationLevel3Spells.PROTECTION_FROM_ENERGY,
        AbjurationLevel4Spells.BANISHMENT,
        AbjurationLevel5Spells.MASS_CURE_WOUNDS,
    )
    _SCHOOL_EFFECT = "Protective Ward. When you cast a spell from the Abjuration school using a spell slot, you or one creature you can see within 30 feet of yourself gains Temporary Hit Points equal to twice the level of spell slot expended."

    def _school_facts(self) -> tuple[tuple[str, str], ...]:
        return (
            ("Trigger", "You cast an Abjuration spell using a spell slot"),
            ("Target", "You or one creature you can see within 30 feet"),
            ("Effect", "Temporary Hit Points equal to twice the slot's level"),
        )


class ConjurationAdept(_SchoolAdept):
    _NAME = "Conjuration Adept"
    _SPELLS = (
        ConjurationLevel1Spells.ENTANGLE,
        ConjurationLevel2Spells.MISTY_STEP,
        ConjurationLevel3Spells.CONJURE_ANIMALS,
        ConjurationLevel4Spells.DIMENSION_DOOR,
        ConjurationLevel5Spells.CONJURE_ELEMENTAL,
    )
    _SCHOOL_EFFECT = "Persistent Conjuration. While maintaining Concentration on a spell from the Conjuration school, you gain a bonus to Constitution saving throws to maintain this Concentration. This bonus is equal to the ability modifier of the score increased by this feat."

    def _school_facts(self) -> tuple[tuple[str, str], ...]:
        return (
            ("While", "You're concentrating on a Conjuration spell"),
            (
                "Effect",
                f"Add your {self.ability.value} modifier to Constitution saves to keep that Concentration",
            ),
        )


class DivinationAdept(_SchoolAdept):
    _NAME = "Divination Adept"
    _SPELLS = (
        DivinationLevel1Spells.DETECT_EVIL_AND_GOOD,
        DivinationLevel2Spells.MIND_SPIKE,
        DivinationLevel3Spells.CLAIRVOYANCE,
        DivinationLevel4Spells.DIVINATION,
        DivinationLevel5Spells.SCRYING,
    )
    _SCHOOL_EFFECT = "Prescient Intervention. When a creature you can see within 60 feet of yourself makes a D20 Test, you can take a Reaction to give that creature Advantage or Disadvantage (your choice) on that roll. Once you use this benefit, you can't do so again until you finish a Long Rest. You can also regain use of this feature when you cast a spell from the Divination school using a spell slot."
    _USES = FeatureUses(max_uses=1, regain_all_on="long rest")

    def _school_facts(self) -> tuple[tuple[str, str], ...]:
        return (
            ("Action", "Reaction"),
            ("Trigger", "A creature you can see within 60 feet makes a D20 Test"),
            ("Effect", "Give it Advantage or Disadvantage on the roll (your choice)"),
            (
                "Recharge",
                "Once per Long Rest; casting a Divination spell with a spell slot also restores it",
            ),
        )


class EnchantmentAdept(_SchoolAdept):
    _NAME = "Enchantment Adept"
    _SPELLS = (
        EnchantmentLevel1Spells.DISSONANT_WHISPERS,
        EnchantmentLevel2Spells.ENTHRALL,
        EnchantmentLevel2Spells.HOLD_PERSON,
        EnchantmentLevel4Spells.DOMINATE_BEAST,
        EnchantmentLevel5Spells.MODIFY_MEMORY,
    )
    _SCHOOL_EFFECT = "Subtle Enchantments. When you cast a spell from the Enchantment school using a spell slot, you can cast it without any Verbal, Somatic, or Material components, except Material components that are consumed by the spell or that have a cost specified in the spell."

    def _school_facts(self) -> tuple[tuple[str, str], ...]:
        return (
            ("Trigger", "You cast an Enchantment spell using a spell slot"),
            (
                "Effect",
                "Cast it without Verbal, Somatic or Material components, except costly or consumed Materials",
            ),
        )


class EvocationAdept(_SchoolAdept):
    _NAME = "Evocation Adept"
    _SPELLS = (
        EvocationLevel1Spells.CHROMATIC_ORB,
        EvocationLevel2Spells.SHATTER,
        EvocationLevel3Spells.FIREBALL,
        EvocationLevel4Spells.VITRIOLIC_SPHERE,
        EvocationLevel5Spells.WALL_OF_FORCE,
    )
    _SCHOOL_EFFECT = "Fueled Evocation. Once per turn when you cast an Evocation spell and deal damage, you can roll up to two of your unexpended Hit Point Dice and add the total rolled to one of the spell's damage rolls. Those Hit Point Dice are then expended."

    def _school_facts(self) -> tuple[tuple[str, str], ...]:
        return (
            ("Trigger", "Once per turn, an Evocation spell you cast deals damage"),
            (
                "Effect",
                "Roll up to two unexpended Hit Point Dice and add the total to one of its damage rolls",
            ),
            ("Cost", "Those Hit Point Dice are expended"),
        )


class IllusionAdept(_SchoolAdept):
    _NAME = "Illusion Adept"
    _SPELLS = (
        IllusionLevel1Spells.SILENT_IMAGE,
        IllusionLevel2Spells.PHANTASMAL_FORCE,
        IllusionLevel3Spells.MAJOR_IMAGE,
        IllusionLevel4Spells.HALLUCINATORY_TERRAIN,
        IllusionLevel5Spells.SEEMING,
    )
    _SCHOOL_EFFECT = "Masterful Illusions. When you cast a spell from the Illusion school using a spell slot, you can cast it without any Verbal, Somatic, or Material components, except Material components that are consumed by the spell or that have a cost specified in the spell. Additionally, creatures have Disadvantage on Intelligence (Investigation) checks made to discern the true nature of illusions created by your spells."

    def _school_facts(self) -> tuple[tuple[str, str], ...]:
        return (
            (
                "Components",
                "Cast Illusion spells with a spell slot without Verbal, Somatic or Material components, except costly or consumed Materials",
            ),
            (
                "Convincing",
                "Creatures have Disadvantage on Intelligence (Investigation) checks to discern your spells' illusions",
            ),
        )


class NecromancyAdept(_SchoolAdept):
    _NAME = "Necromancy Adept"
    _SPELLS = (
        NecromancyLevel1Spells.INFLICT_WOUNDS,
        NecromancyLevel2Spells.RAY_OF_ENFEEBLEMENT,
        NecromancyLevel3Spells.VAMPIRIC_TOUCH,
        NecromancyLevel4Spells.BLIGHT,
        NecromancyLevel5Spells.RAISE_DEAD,
    )
    _SCHOOL_EFFECT = "Life Manipulation. When you cast a spell from the Necromancy school using a spell slot, you can immediately roll up to two of your unexpended Hit Point Dice. You regain Hit Points equal to the total rolled plus the level of spell slot expended. Those Hit Point Dice are then expended."

    def _school_facts(self) -> tuple[tuple[str, str], ...]:
        return (
            ("Trigger", "You cast a Necromancy spell using a spell slot"),
            (
                "Effect",
                "Immediately roll up to two unexpended Hit Point Dice: regain the total + the slot's level in Hit Points",
            ),
            ("Cost", "Those Hit Point Dice are expended"),
        )


class TransmutationAdept(_SchoolAdept):
    _NAME = "Transmutation Adept"
    _SPELLS = (
        TransmutationLevel1Spells.JUMP,
        TransmutationLevel2Spells.SPIDER_CLIMB,
        TransmutationLevel3Spells.SLOW,
        TransmutationLevel4Spells.POLYMORPH,
        TransmutationLevel5Spells.ANIMATE_OBJECTS,
    )
    _SCHOOL_EFFECT = "Magical Augmentation. On your turn when you cast a spell from the Transmutation school using a spell slot, your Speed increases by a number of feet equal to five times the level of spell slot expended. This increase lasts until the end of the turn."

    def _school_facts(self) -> tuple[tuple[str, str], ...]:
        return (
            (
                "Trigger",
                "On your turn, you cast a Transmutation spell using a spell slot",
            ),
            ("Effect", "Speed + 5 x the slot's level feet until the end of the turn"),
        )


# ---------------------------------------------------------------------------
# Arcana Unleashed 2026: other general feats
# ---------------------------------------------------------------------------


class MagicConnoisseur(_AbilityScoreFeat):
    _NAME = "Magic Connoisseur"
    _ABILITIES = _MENTAL_ABILITIES
    # One free cast of each of the two chosen spells per Long Rest.
    _USES = FeatureUses(max_uses=2, regain_all_on="long rest")

    def __init__(
        self,
        character_level: int,
        ability: Ability,
        level_1_spell: str,
        level_2_spell: str,
    ):
        self.level_1_spell = level_1_spell
        self.level_2_spell = level_2_spell
        super().__init__(character_level, ability)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Spells",
                        f"{self.level_1_spell} (level 1) and {self.level_2_spell} (level 2), from your Magic Initiate list, always prepared",
                    ),
                    (
                        "Casting",
                        "Each once per Long Rest without a slot, or with your spell slots; your Magic Initiate spellcasting ability",
                    ),
                    (
                        "Spell Change",
                        "Whenever you gain a level, replace one with another of the same level from that list",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Magic Initiate Feat\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Additional Spells. Choose a level 1 and a level 2 spell from the same list you selected for the Magic Initiate feat's cantrips. You always have those spells prepared. "
            "You can cast each spell once without a spell slot, and you regain the ability to cast it in this way when you finish a Long Rest. "
            "You can also cast those spells using any spell slots you have of the appropriate level. The spellcasting ability for these spells is the same as the spellcasting ability chosen for your Magic Initiate feat's spells.\n"
            f"Chosen spells: {self.level_1_spell} (level 1) and {self.level_2_spell} (level 2).\n"
            "Spell Change. Whenever you gain a new level, you can replace one of the spells you chose for this feat with a different spell of the same level from the chosen spell list."
        )


class OtherworldlyFamiliar(_AbilityScoreFeat):
    _NAME = "Otherworldly Familiar"
    _ABILITIES = tuple(Ability)
    VALID_DAMAGE_TYPES = (
        DamageType.NECROTIC,
        DamageType.POISON,
        DamageType.PSYCHIC,
        DamageType.RADIANT,
        DamageType.THUNDER,
    )

    def __init__(self, character_level: int, ability: Ability, damage_type: DamageType):
        if damage_type not in self.VALID_DAMAGE_TYPES:
            allowed = ", ".join(dt.value for dt in self.VALID_DAMAGE_TYPES)
            raise ValueError(f"{self._NAME} damage type must be one of: {allowed}.")
        # The familiar gains this resistance, not the character - so it is
        # only described, never applied to the stat block.
        self.damage_type = damage_type
        super().__init__(character_level, ability)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts((("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),)),
            Option(
                "Otherworldly Power",
                (
                    Paragraph(
                        "When you cast Find Familiar, you can imbue your familiar until you cast the spell again:"
                    ),
                    Facts(
                        (
                            (
                                "Energy Resistance",
                                f"Resistance to {self.damage_type.value} damage",
                            ),
                            (
                                "Phase Walk",
                                "It moves through creatures and objects as Difficult Terrain; ending its turn in an object shunts it to its last unoccupied space",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Familiar Friend Feat\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 20.\n"
            "Otherworldly Power. When you cast the Find Familiar spell, you can imbue your familiar with otherworldly might, which lasts until you cast Find Familiar again. While imbued, your familiar gains the following benefits:\n"
            f"Energy Resistance. Your familiar has Resistance to {self.damage_type.value} damage.\n"
            "Phase Walk. Your familiar can move through other creatures and objects as if they were Difficult Terrain. If your familiar ends its turn inside an object, it is shunted to the last unoccupied space it was in."
        )


class SoothingFamiliar(_AbilityScoreFeat):
    _NAME = "Soothing Familiar"
    _ABILITIES = tuple(Ability)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Healing Beacon",
                        "While your familiar is within 120 feet of you, an ally in a 5-foot Emanation from it treats a 1 or 2 as a 3 on dice that restore Hit Points",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Familiar Friend Feat\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 20.\n"
            "Healing Beacon. Positive energy fills a 5-foot Emanation originating from your familiar as long as it is within 120 feet of you. Whenever an ally in that Emanation rolls a die to determine the number of Hit Points restored to a creature, that ally can treat a roll of 1 or 2 on the die as a 3."
        )


class SpellSubterfuge(_AbilityScoreFeat):
    _NAME = "Spell Subterfuge"
    _ABILITIES = _MENTAL_ABILITIES
    _USES = FeatureUses(
        max_uses=MAX_ABILITY_MODIFIER,
        regain_all_on="long rest",
        current_formula="Current amount: equal to the ability modifier of the score increased by this feat.",
    )

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_ability_modifier(self.ability))

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Shrouding Spells",
                        "After you cast a spell with a casting time of an action using a spell slot, take both the Dash and Hide actions as a Bonus Action. Uses: your "
                        + self.ability.value
                        + " modifier (minimum 1) per Long Rest.",
                    ),
                    (
                        "Sneaky Casting",
                        "While Invisible from Hide, a Verbal component or a spell attack doesn't end it if you end the turn behind Three-Quarters or Total Cover",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Spellcasting or Pact Magic Feature\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Shrouding Spells. After you cast a spell that has a casting time of an action using a spell slot, you can take both the Dash and Hide actions as a Bonus Action. "
            "You can use this benefit a number of times equal to the ability modifier of the score increased by this feat, and you regain all expended uses when you finish a Long Rest.\n"
            "Sneaky Casting. If you have the Hide action's Invisible condition, casting a spell with a Verbal component or making a spell attack doesn't end that condition on you if you end the turn behind Three-Quarters Cover or Total Cover."
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class WarlikeFamiliar(_AbilityScoreFeat):
    _NAME = "Warlike Familiar"
    _ABILITIES = tuple(Ability)
    # One free cast of Battle Familiar per Long Rest.
    _USES = FeatureUses(max_uses=1, regain_all_on="long rest")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Battle Familiar",
                        "Always prepared; cast it once per Long Rest without a slot, or with your spell slots. Spellcasting ability: the one from Familiar Friend.",
                    ),
                    (
                        "Intercept Attack",
                        "When a creature within 5 feet of your familiar is hit by an attack roll, the familiar can use its Reaction to add your Proficiency Bonus to that creature's AC against it",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Familiar Friend Feat\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 20.\n"
            "Battle Familiar. You always have the Battle Familiar spell prepared. You can cast it once without a spell slot, and you regain the ability to cast it in this way when you finish a Long Rest. "
            "You can also cast the spell using any spell slots you have of the appropriate level. Your spellcasting ability for this spell is the one chosen for the Faithful Companion benefit of your Familiar Friend feat.\n"
            "Intercept Attack. When a creature within 5 feet of your familiar is hit by an attack roll, your familiar can take a Reaction to add a bonus to the creature's Armor Class against that attack, potentially causing the attack to miss. The bonus is equal to your Proficiency Bonus."
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


# ---------------------------------------------------------------------------
# D&D Beyond Drops July 2026
# ---------------------------------------------------------------------------


class ShiftingCombatant(_AbilityScoreFeat):
    _NAME = "Shifting Combatant"
    _ABILITIES = _STRENGTH_OR_DEXTERITY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Fearless Leap",
                        "After a Long Jump with a 10-foot run-up, if you land within 5 feet of two or more enemies, attack rolls against you have Disadvantage until the start of your next turn",
                    ),
                )
            ),
            Option(
                "Domino Strike",
                (
                    Facts(
                        (
                            (
                                "Trigger",
                                "You hit with a weapon and use its Push mastery to push the creature into a Large or smaller creature's space",
                            ),
                            (
                                "Save",
                                f"Both make a Dexterity save, DC {dc_formula(self.ability)}",
                            ),
                            ("Failed", "1d10 Bludgeoning damage"),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+, Weapon Mastery Feature\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Domino Strike. When you hit a creature with a weapon and activate the Push mastery property to push that creature into a space occupied by a Large or smaller creature, you can force the creatures to collide. "
            "Each creature makes a Dexterity saving throw (DC 8 plus the ability modifier of the score increased by this feat and your Proficiency Bonus), taking 1d10 Bludgeoning damage on a failed save.\n"
            "Fearless Leap. When you make a Long Jump, moving at least 10 feet immediately before the jump, and land in a space within 5 feet of two or more enemies, attack rolls made against you have Disadvantage until the start of your next turn."
        )

    def calculate_dc(self, character: CharacterView) -> int:
        return (
            8
            + character.get_ability_modifier(self.ability)
            + character.get_proficiency_bonus()
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class TacticalCombatant(_AbilityScoreFeat):
    _NAME = "Tactical Combatant"
    _ABILITIES = _STRENGTH_OR_DEXTERITY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Buffering Strike",
                        "When you hit with a weapon, gain Temporary Hit Points equal to the total rolled on its damage dice",
                    ),
                    (
                        "Honed Instincts",
                        "When you fail an ability check, add 1d6 to it",
                    ),
                    (
                        "Recharge",
                        "Each benefit once; regain it when you roll Initiative or finish a Short or Long Rest",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 4+ and Strength or Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Buffering Strike. When you hit a creature with a weapon, you can gain Temporary Hit Points equal to the total number rolled on the weapon's damage dice. Once you use this benefit, you can't use it again until you roll Initiative or finish a Short or Long Rest.\n"
            "Honed Instincts. When you fail an ability check, you can roll 1d6 and add the number rolled to the ability check, potentially turning it into a success. Once you use this benefit, you can't use it again until you roll Initiative or finish a Short or Long Rest."
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF
