from CharacterContent.Spells.SpellLists import (
    AbjurationLevel1Spells,
    AbjurationLevel2Spells,
    AbjurationLevel3Spells,
    AbjurationLevel4Spells,
    AbjurationLevel5Spells,
    ConjurationLevel0Spells,
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
    NecromancyLevel0Spells,
    NecromancyLevel1Spells,
    NecromancyLevel2Spells,
    NecromancyLevel3Spells,
    NecromancyLevel4Spells,
    NecromancyLevel5Spells,
    DruidLevel1Spells,
    DruidLevel2Spells,
    SorcererLevel0Spells,
    WizardLevel0Spells,
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
from Model.CharacterSources import SpellSource
from Model.Grants import Grants
from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
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
    MultiAbilityArmorClass,
    SkillExpertise,
    SkillProficiency,
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
    ALL_LEVELS,
    PROFICIENCY_BONUS_GAINED_AT,
    MAX_ABILITY_MODIFIER,
    MAX_ABILITY_SCORE,
    MAX_PROFICIENCY_BONUS,
)
from Model.View import CharacterView
from Utils import StringUtils
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

    def get_spells(self) -> list[str]:
        return []

    def get_spell_casting_ability(self) -> "Ability | None":
        return None

    def get_spell_source(self) -> "str | None":
        return None

    def grant_to(self, data: "Grants") -> None:
        feat = data.for_general_feat(self)
        feat.add_feature(self)
        for spell in self.get_spells():
            feat.add_spell(
                spell, self.get_spell_casting_ability(), source=self.get_spell_source()
            )


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

    def __init__(
        self, character_level: int, ability: Ability, spell: "str | None" = None
    ):
        if spell is not None and spell not in list(DivinationLevel1Spells) + list(
            EnchantmentLevel1Spells
        ):
            raise ValueError(
                f"Fey Touched spell must be a level 1 Divination or Enchantment spell."
            )
        self.spell = spell
        super().__init__(character_level, ability)

    def grant_to(self, data: Grants) -> None:
        feat = data.for_general_feat(self)
        feat.add_feature(self)
        feat.add_spell(ConjurationLevel2Spells.MISTY_STEP, self.ability)
        if self.spell is not None:
            feat.add_spell(self.spell, self.ability, source=SpellSource.CHOSEN)

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
                        "Once per turn, when an Unarmed Strike hits as part of the Attack action on your turn, can use both its Damage and Grapple options",
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

    def __init__(
        self, character_level: int, ability: Ability, spells: "list[str] | None" = None
    ):
        if character_level < self._MIN_LEVEL:
            raise ValueError(
                f"{self._NAME} requires character level {self._MIN_LEVEL} or higher."
            )
        if ability not in self._ABILITIES:
            allowed = " or ".join(a.value for a in self._ABILITIES)
            raise ValueError(f"{self._NAME} ability increase must be {allowed}.")
        self.ability = ability
        self.spells = spells if spells is not None else []
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

    def get_spells(self) -> list[str]:
        return self.spells

    def get_spell_casting_ability(self) -> Ability:
        return self.ability

    def get_spell_source(self) -> str:
        return SpellSource.CHOSEN

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

    def __init__(
        self, character_level: int, ability: Ability, spell: "str | None" = None
    ):
        if spell is not None and spell not in list(IllusionLevel1Spells) + list(
            NecromancyLevel1Spells
        ):
            raise ValueError(
                f"Shadow Touched spell must be a level 1 Illusion or Necromancy spell."
            )
        self.spell = spell
        super().__init__(character_level, ability)

    def grant_to(self, data: Grants) -> None:
        feat = data.for_general_feat(self)
        feat.add_feature(self)
        feat.add_spell(IllusionLevel2Spells.INVISIBILITY, self.ability)
        if self.spell is not None:
            feat.add_spell(self.spell, self.ability, source=SpellSource.CHOSEN)

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

    def get_spells(self) -> list[str]:
        return [ConjurationLevel0Spells.MAGE_HAND]

    def get_spell_casting_ability(self) -> Ability:
        return self.ability

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

    def get_spells(self) -> list[str]:
        return [DivinationLevel2Spells.DETECT_THOUGHTS]

    def get_spell_casting_ability(self) -> Ability:
        return self.ability

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

    def get_spells(self) -> list[str]:
        return [SorcererLevel0Spells.RAY_OF_FROST]

    def get_spell_casting_ability(self) -> Ability:
        return self.ability

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

    def get_spells(self) -> list[str]:
        return [DruidLevel2Spells.BEAST_SENSE]

    def get_spell_casting_ability(self) -> Ability:
        return self.ability

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


class AberrantAnatomy(GeneralFeat):

    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Aberrant Anatomy requires character level 1 or higher.")
        super().__init__(
            name="Aberrant Anatomy",
            origin="General Feat Ravenloft Campaign",
        )

    def apply(self, ledger_writer: LedgerWriter):
        SkillProficiency([Skill.PERCEPTION]).apply(ledger_writer)
        SkillExpertise([Skill.PERCEPTION]).apply(ledger_writer)
        GrantSense(Sense.BLINDSIGHT, 15).apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Exposure to alien horrors like those of the Far Realm has warped your body."
            ),
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
                "Warping Flesh: right after you roll a 1 on the d20 for a D20 Test",
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
            "Exposure to alien horrors like those of the Far Realm has warped your physical form in supernatural ways. You gain the following features.\n"
            " * Breathless. You can hold your breath for 1 hour.\n"
            " * Extrasensory Perception. You have proficiency in the Perception skill, if you lack it. You also gain Expertise in that skill. In addition, you have Blindsight with a range of 15 feet.\n"
            " * Warping Flesh. Immediately after you make a D20 Test and roll a 1 on the d20, the aberrant influence infecting your form flares, wrenching control of your flesh. Make a Constitution saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you have the Stunned condition until the end of your next turn."
        )

    def calculate_dc(self, character: CharacterView) -> int:
        return 13 + character.get_proficiency_bonus()

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

    def __init__(self, character_level: int, spell_casting_ability: Ability):
        if character_level < 1:
            raise ValueError("Gathered Whispers requires character level 1 or higher.")
        self.spell_casting_ability = spell_casting_ability
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

    def grant_to(self, data: Grants) -> None:
        feat = data.for_general_feat(self)
        feat.add_feature(self)
        feat.add_spell(WizardLevel0Spells.MESSAGE, self.spell_casting_ability)
        feat.add_spell(DivinationLevel2Spells.AUGURY, self.spell_casting_ability)

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

    def __init__(self, character_level: int, spell_casting_ability: Ability):
        if character_level < 1:
            raise ValueError("Living Shadow requires character level 1 or higher.")
        self.spell_casting_ability = spell_casting_ability
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

    def get_spells(self) -> list[str]:
        return [ConjurationLevel0Spells.MAGE_HAND]

    def get_spell_casting_ability(self) -> Ability:
        return self.spell_casting_ability

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

    def __init__(self, character_level: int, spell_casting_ability: Ability):
        if character_level < 1:
            raise ValueError("Touch of Death requires character level 1 or higher.")
        self.spell_casting_ability = spell_casting_ability
        super().__init__(
            name="Touch of Death",
            origin="General Feat Ravenloft Campaign",
        )

    def get_spells(self) -> list[str]:
        return [NecromancyLevel0Spells.CHILL_TOUCH]

    def get_spell_casting_ability(self) -> Ability:
        return self.spell_casting_ability

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

    def __init__(self, character_level: int, spell_casting_ability: Ability):
        if character_level < 1:
            raise ValueError("Watchers requires character level 1 or higher.")
        self.spell_casting_ability = spell_casting_ability
        super().__init__(
            name="Watchers",
            origin="General Feat Ravenloft Campaign",
        )

    def grant_to(self, data: Grants) -> None:
        feat = data.for_general_feat(self)
        feat.add_feature(self)
        feat.add_spell(DruidLevel2Spells.BEAST_SENSE, self.spell_casting_ability)
        feat.add_spell(DruidLevel1Spells.SPEAK_WITH_ANIMALS, self.spell_casting_ability)

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
        _SPELLS         – the always-prepared spell for spell slot levels 1-5, in order;
                          each is of that slot's level or lower (Enchantment Adept
                          puts the 2nd-level Hold Person in its 3rd-level row)
        _SCHOOL_EFFECT  – the school-specific benefit text
    and implement _school_facts(), that benefit as label/value rows for the
    improved description.
    """

    _ABILITIES = _MENTAL_ABILITIES

    _SPELLS: tuple[
        Level1Spells,
        Level1Spells | Level2Spells,
        Level1Spells | Level2Spells | Level3Spells,
        Level1Spells | Level2Spells | Level3Spells | Level4Spells,
        Level1Spells | Level2Spells | Level3Spells | Level4Spells | Level5Spells,
    ]
    _SCHOOL_EFFECT: str

    def _school_facts(self) -> tuple[tuple[str, str], ...]:
        """The school benefit as label/value rows."""
        raise NotImplementedError

    def get_spells(self) -> list[str]:
        return list(self._SPELLS)

    def get_spell_casting_ability(self) -> Ability:
        return self.ability

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
        spell_casting_ability: Ability,
    ):
        self.level_1_spell = level_1_spell
        self.level_2_spell = level_2_spell
        self.spell_casting_ability = spell_casting_ability
        super().__init__(character_level, ability)

    def get_spells(self) -> list[str]:
        return [self.level_1_spell, self.level_2_spell]

    def get_spell_casting_ability(self) -> Ability:
        return self.spell_casting_ability

    def get_spell_source(self) -> str:
        return SpellSource.CHOSEN

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


# ---------------------------------------------------------------------------
# Dragonmark General Feats
# ---------------------------------------------------------------------------


class _GreaterDragonmarkFeat(_AbilityScoreFeat):
    """Base class for the Greater Dragonmark feats (Eberron: Forge of the
    Artificer): +1 to one ability score, the base mark's 1d4 intuition die
    becomes a 1d6, and a mark-specific upgrade.

    Subclasses declare:
        _NAME        - feat name
        _BASE_MARK   - the Dragonmark feat it requires, e.g. "Mark of Healing"
        _INTUITION   - that feat's intuition benefit, e.g. "Medical Intuition"
        _ABILITIES   - allowed abilities for the +1 (default: any)
        _USES        - optional FeatureUses for a limited-use benefit

    pass their own usage_tags (and activation) to __init__, list their
    other benefits in _benefit_facts(), and write get_description() from the
    feat's own text.

    The "requires the Mark of X feat" prerequisite is shown, not enforced:
    no feat checks another feat's presence.
    """

    _BASE_MARK: str
    _INTUITION: str
    _ABILITIES = tuple(Ability)

    def __init__(
        self,
        character_level: int,
        ability: Ability,
        usage_tags=None,
        activation: FeatureActivation | None = None,
    ):
        super().__init__(character_level, ability)
        self.usage_tags = usage_tags
        if activation is not None:
            self.activation = activation

    def _prerequisite(self) -> str:
        return f"General Feat (Prerequisite: Level 4+, {self._BASE_MARK} Feat)\n"

    def _benefit_facts(self) -> tuple:
        """(label, text) rows for this feat's own benefits."""
        return ()

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Improved Intuition",
                        f"{self._INTUITION} from your {self._BASE_MARK} feat rolls 1d6 instead of 1d4",
                    ),
                )
                + self._benefit_facts()
            ),
        ]


class GreaterAberrantMark(_GreaterDragonmarkFeat):
    _NAME = "Greater Aberrant Mark"
    _BASE_MARK = "Aberrant Dragonmark"
    _INTUITION = "Aberrant Fortitude"
    _ABILITIES = (Ability.CONSTITUTION,)
    _USES = FeatureUses(
        max_uses=MAX_PROFICIENCY_BONUS,
        regain_all_on="long rest",
        current_formula="Current amount: equal to your proficiency bonus.",
        gained_at=PROFICIENCY_BONUS_GAINED_AT,
    )

    def __init__(self, character_level: int, ability: Ability):
        super().__init__(
            character_level, ability, usage_tags=["buff", "heal", "damage"]
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Mark of Inspiration's uses are in the panel below.
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Improved Fortitude",
                        "Aberrant Fortitude from your Aberrant Dragonmark feat rolls 1d6 instead of 1d4, and you regain its use on a Short or Long Rest",
                    ),
                    (
                        "Mark of Inspiration",
                        "When you cast a cantrip, roll one or two unexpended Hit Point Dice, then expend them. You gain Temporary Hit Points equal to the roll + your Constitution modifier, and one creature of your choice within 30 feet of you (not you) takes Force damage equal to the roll. Proficiency Bonus times per Long Rest.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            self._prerequisite() + "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Constitution score by 1, to a maximum of 20.\n"
            "Improved Fortitude. When you use the Aberrant Fortitude benefit of your Aberrant Dragonmark feat, you can roll 1d6 instead of 1d4. You also now regain your use of Aberrant Fortitude whenever you finish a Short or Long Rest.\n"
            "Mark of Inspiration. When you cast a cantrip, you can roll one or two of your unexpended Hit Point Dice. You gain a number of Temporary Hit Points equal to the number rolled plus your Constitution modifier, and one creature of your choice within 30 feet of you (not including you) takes Force damage equal to the number rolled. Those dice are then expended.\n"
            "You can use this benefit a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest."
        )

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()


class GreaterMarkOfDetection(_GreaterDragonmarkFeat):
    _NAME = "Greater Mark of Detection"
    _BASE_MARK = "Mark of Detection"
    _INTUITION = "Deductive Intuition"

    def __init__(self, character_level: int, ability: Ability):
        super().__init__(character_level, ability, usage_tags=["buff"])

    def _benefit_facts(self) -> tuple:
        return (
            (
                "Shared Detection",
                "When Magical Detection casts See Invisibility without a spell slot, one creature you can see within 30 feet of you also gains its benefits for the duration",
            ),
        )

    def get_description(self, character: CharacterView) -> str:
        return (
            self._prerequisite() + "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 20.\n"
            "Improved Intuition. When you use the Deductive Intuition benefit of your Mark of Detection feat, you can roll 1d6 instead of 1d4.\n"
            "Shared Detection. When you use the Magical Detection benefit of your Mark of Detection feat to cast See Invisibility without a spell slot, you can choose one creature you can see within 30 feet of yourself. That creature also gains the benefits of the spell for its duration."
        )


class GreaterMarkOfFinding(_GreaterDragonmarkFeat):
    _NAME = "Greater Mark of Finding"
    _BASE_MARK = "Mark of Finding"
    _INTUITION = "Hunter's Intuition"

    def __init__(self, character_level: int, ability: Ability):
        super().__init__(character_level, ability, usage_tags=["buff", "control"])

    def _benefit_facts(self) -> tuple:
        return (
            (
                "Improved Finding",
                "When Finder's Magic casts Hunter's Mark without a spell slot, its range is doubled, and you can make the target unable to benefit from the Invisible condition for the duration",
            ),
        )

    def get_description(self, character: CharacterView) -> str:
        return (
            self._prerequisite() + "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 20.\n"
            "Improved Intuition. When you use the Hunter's Intuition benefit of your Mark of Finding feat, you can roll 1d6 instead of 1d4.\n"
            "Improved Finding. When you use the Finder's Magic benefit of your Mark of Finding to cast Hunter's Mark without a spell slot, the range of the spell is doubled, and you can modify the spell so that the target can't benefit from the Invisible condition for the duration."
        )


class GreaterMarkOfHandling(_GreaterDragonmarkFeat):
    _NAME = "Greater Mark of Handling"
    _BASE_MARK = "Mark of Handling"
    _INTUITION = "Wild Intuition"
    _USES = FeatureUses(
        max_uses=MAX_PROFICIENCY_BONUS,
        regain_all_on="long rest",
        current_formula="Current amount: equal to your proficiency bonus.",
        gained_at=PROFICIENCY_BONUS_GAINED_AT,
    )

    def __init__(self, character_level: int, ability: Ability):
        super().__init__(
            character_level,
            ability,
            usage_tags=["buff", "control"],
            activation=FeatureActivation(
                action_type=ActionType.ACTION,
                duration="Until the start of your next turn",
                range="30 Feet",
            ),
        )

    def _benefit_facts(self) -> tuple:
        # Subdue Animal's uses are in the panel below.
        return (
            (
                "Improved Handling",
                "While mounted, right after you hit a target within 5 feet of your mount with a melee attack roll, your mount can take a Reaction to move up to its Speed or to make one attack with the Attack action (your choice)",
            ),
            (
                "Subdue Animal",
                "Magic action: one Beast or Monstrosity you can see within 30 feet makes a Wisdom saving throw or has the Frightened condition until the start of your next turn. Proficiency Bonus times per Long Rest.",
            ),
            ("Save DC", dc_formula(Ability.WISDOM)),
        )

    def get_description(self, character: CharacterView) -> str:
        return (
            self._prerequisite() + "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 20.\n"
            "Improved Intuition. When you use the Wild Intuition benefit of your Mark of Handling feat, you can roll 1d6 instead of 1d4.\n"
            "Improved Handling. While you are mounted, immediately after you hit a target within 5 feet of your mount with a melee attack roll, your mount can take a Reaction to move up to its Speed or take the Attack action to make one attack only (your choice).\n"
            "Subdue Animal. As a Magic action, you exert command over one Beast or Monstrosity you can see within 30 feet of yourself. The target must succeed on a Wisdom saving throw (DC 8 plus your Wisdom modifier and Proficiency Bonus) or have the Frightened condition until the start of your next turn. You can use this benefit a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest."
        )

    def calculate_dc(self, character: CharacterView) -> int:
        return 8 + character.get_wisdom_modifier() + character.get_proficiency_bonus()

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE


class GreaterMarkOfHealing(_GreaterDragonmarkFeat):
    _NAME = "Greater Mark of Healing"
    _BASE_MARK = "Mark of Healing"
    _INTUITION = "Medical Intuition"
    _USES = FeatureUses(
        max_uses=MAX_PROFICIENCY_BONUS,
        regain_all_on="long rest",
        current_formula="Current amount: equal to your proficiency bonus.",
        gained_at=PROFICIENCY_BONUS_GAINED_AT,
    )

    def __init__(self, character_level: int, ability: Ability):
        super().__init__(character_level, ability, usage_tags=["buff", "heal"])

    def _benefit_facts(self) -> tuple:
        # The free casts are in the panel below.
        return (
            (
                "Improved Healing",
                "Healing Touch casts Cure Wounds without a spell slot Proficiency Bonus times per Long Rest (instead of once)",
            ),
            (
                "Healing Rolls",
                "When you cast Cure Wounds, treat any 1 or 2 on its healing dice as a 3",
            ),
        )

    def get_description(self, character: CharacterView) -> str:
        return (
            self._prerequisite() + "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 20.\n"
            "Improved Intuition. When you use the Medical Intuition benefit of your Mark of Healing feat, you can roll 1d6 instead of 1d4.\n"
            "Improved Healing. You can now use the Healing Touch benefit of your Mark of Healing feat to cast Cure Wounds without using a spell slot a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest.\n"
            "Additionally, when you cast Cure Wounds and roll dice to determine the number of Hit Points restored, you can treat any 1 or 2 on a roll as a 3."
        )

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()


class GreaterMarkOfHospitality(_GreaterDragonmarkFeat):
    _NAME = "Greater Mark of Hospitality"
    _BASE_MARK = "Mark of Hospitality"
    _INTUITION = "Ever Hospitable"
    _USES = FeatureUses(max_uses=1, regain_all_on="long rest")

    def __init__(
        self, character_level: int, ability: Ability, refresh_ability: Ability
    ):
        if refresh_ability not in _MENTAL_ABILITIES:
            raise ValueError(
                "Greater Mark of Hospitality's Inspired Hospitality ability must be Intelligence, Wisdom, or Charisma."
            )
        self.refresh_ability = refresh_ability
        super().__init__(character_level, ability, usage_tags=["buff", "heal"])

    def _benefit_facts(self) -> tuple:
        # The once-per-Long-Rest use is in the panel below.
        return (
            (
                "Inspired Hospitality",
                f"When you cast Purify Food and Drink, instead of its normal effect each creature of your choice within 30 feet of you reduces its Exhaustion level by 1 and gains Temporary Hit Points equal to your Proficiency Bonus + your {self.refresh_ability.value} modifier. Once per Long Rest.",
            ),
        )

    def get_description(self, character: CharacterView) -> str:
        return (
            self._prerequisite() + "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 20.\n"
            "Improved Intuition. When you use the Ever Hospitable benefit of your Mark of Hospitality feat, you can roll 1d6 instead of 1d4.\n"
            f"Inspired Hospitality. When you cast Purify Food and Drink, you can modify the spell so that instead of its normal effect, each creature of your choice within 30 feet of you is refreshed. Each affected creature's Exhaustion level is reduced by 1, and the creature gains Temporary Hit Points equal to your Proficiency Bonus plus your Intelligence, Wisdom, or Charisma modifier (choose when you select this feat: {self.refresh_ability.value}). Once you modify the spell with this benefit, you can't do so again until you finish a Long Rest."
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class GreaterMarkOfMaking(_GreaterDragonmarkFeat):
    _NAME = "Greater Mark of Making"
    _BASE_MARK = "Mark of Making"
    _INTUITION = "Artisan's Intuition"

    def __init__(self, character_level: int, ability: Ability):
        super().__init__(character_level, ability, usage_tags=["buff"])

    def _benefit_facts(self) -> tuple:
        return (
            (
                "Improved Making",
                "When Spellsmith casts Magic Weapon without a spell slot, you cast its level 3 version",
            ),
        )

    def get_description(self, character: CharacterView) -> str:
        return (
            self._prerequisite() + "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 20.\n"
            "Improved Intuition. When you use the Artisan's Intuition benefit of your Mark of Making feat, you can roll 1d6 instead of 1d4.\n"
            "Improved Making. When you use the Spellsmith benefit of your Mark of Making feat to cast Magic Weapon without a spell slot, you cast the spell as its level 3 version."
        )


class GreaterMarkOfPassage(_GreaterDragonmarkFeat):
    _NAME = "Greater Mark of Passage"
    _BASE_MARK = "Mark of Passage"
    _INTUITION = "Intuitive Motion"

    def __init__(self, character_level: int, ability: Ability):
        super().__init__(character_level, ability, usage_tags=["buff"])

    def _benefit_facts(self) -> tuple:
        return (
            (
                "Inspired Passage",
                "When Magical Passage casts Misty Step without a spell slot, choose up to two willing creatures you can see within 30 feet before you teleport; each can take a Reaction to teleport up to 30 feet to an unoccupied space it can see",
            ),
        )

    def get_description(self, character: CharacterView) -> str:
        return (
            self._prerequisite() + "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 20.\n"
            "Improved Intuition. When you use the Intuitive Motion benefit of your Mark of Passage feat, you can roll 1d6 instead of 1d4.\n"
            "Inspired Passage. When you use the Magical Passage benefit of your Mark of Passage feat to cast Misty Step without a spell slot, you can also choose up to two willing creatures you can see within 30 feet of yourself before you teleport. Each target can then take a Reaction to also teleport up to 30 feet to an unoccupied space it can see."
        )


class GreaterMarkOfScribing(_GreaterDragonmarkFeat):
    _NAME = "Greater Mark of Scribing"
    _BASE_MARK = "Mark of Scribing"
    _INTUITION = "Gifted Scribe"
    _USES = FeatureUses(max_uses=1, regain_all_on="long rest")

    def __init__(self, character_level: int, ability: Ability):
        super().__init__(character_level, ability, usage_tags=["buff", "utility"])

    def _benefit_facts(self) -> tuple:
        # The once-per-Long-Rest use is in the panel below.
        return (
            (
                "Inspired Scribing",
                "When you cast Comprehend Languages, up to three willing creatures you can see within 30 feet also gain its benefits, and you and they can communicate telepathically within 1 mile of each other for its duration. Once per Long Rest.",
            ),
        )

    def get_description(self, character: CharacterView) -> str:
        return (
            self._prerequisite() + "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 20.\n"
            "Improved Intuition. When you use the Gifted Scribe benefit of your Mark of Scribing feat, you can roll 1d6 instead of 1d4.\n"
            "Inspired Scribing. When you cast Comprehend Languages, you can modify the spell to encompass up to three willing creatures you can see within 30 feet of yourself. Each chosen creature also gains the benefits of the spell for the duration. In addition, for the duration of the spell, you and the chosen creatures can communicate telepathically with each other while within 1 mile of each other. Once you modify the spell with this benefit, you can't do so again until you finish a Long Rest."
        )


class GreaterMarkOfSentinel(_GreaterDragonmarkFeat):
    _NAME = "Greater Mark of Sentinel"
    _BASE_MARK = "Mark of Sentinel"
    _INTUITION = "Sentinel's Intuition"

    def __init__(self, character_level: int, ability: Ability):
        super().__init__(character_level, ability, usage_tags=["buff", "damage"])

    def _benefit_facts(self) -> tuple:
        return (
            (
                "Improved Sentinel",
                "When you use Vigilant Guardian, you can also make one attack with a weapon or an Unarmed Strike as part of that Reaction",
            ),
        )

    def get_description(self, character: CharacterView) -> str:
        return (
            self._prerequisite() + "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 20.\n"
            "Improved Intuition. When you use the Sentinel's Intuition benefit of your Mark of Sentinel feat, you can roll 1d6 instead of 1d4.\n"
            "Improved Sentinel. When you use the Vigilant Guardian benefit of your Mark of Sentinel feat, you can also make one attack with a weapon or an Unarmed Strike as part of that same Reaction."
        )


class GreaterMarkOfShadow(_GreaterDragonmarkFeat):
    _NAME = "Greater Mark of Shadow"
    _BASE_MARK = "Mark of Shadow"
    _INTUITION = "Cunning Intuition"

    def __init__(self, character_level: int, ability: Ability):
        super().__init__(character_level, ability, usage_tags=["buff"])

    def _benefit_facts(self) -> tuple:
        return (
            (
                "Improved Shadow",
                "When Shape Shadows casts Invisibility without a spell slot, you cast its level 3 version",
            ),
        )

    def get_description(self, character: CharacterView) -> str:
        return (
            self._prerequisite() + "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 20.\n"
            "Improved Intuition. When you use the Cunning Intuition benefit of your Mark of Shadow feat, you can roll 1d6 instead of 1d4.\n"
            "Improved Shadow. When you use the Shape Shadows benefit of your Mark of Shadow feat to cast Invisibility without a spell slot, you cast the spell as its level 3 version."
        )


class GreaterMarkOfStorm(_GreaterDragonmarkFeat):
    _NAME = "Greater Mark of Storm"
    _BASE_MARK = "Mark of Storm"
    _INTUITION = "Windwright's Intuition"

    def __init__(self, character_level: int, ability: Ability):
        super().__init__(character_level, ability, usage_tags=["buff", "utility"])

    def _benefit_facts(self) -> tuple:
        return (
            (
                "Improved Storm",
                "When Storm Magic casts Gust of Wind without a spell slot, you also gain a Fly Speed of 60 feet for the spell's duration",
            ),
        )

    def get_description(self, character: CharacterView) -> str:
        return (
            self._prerequisite() + "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 20.\n"
            "Improved Intuition. When you use the Windwright's Intuition benefit of your Mark of Storm feat, you can roll 1d6 instead of 1d4.\n"
            "Improved Storm. When you use the Storm Magic benefit of your Mark of Storm feat to cast Gust of Wind without a spell slot, you also gain a Fly Speed of 60 feet for the duration of the spell."
        )


class GreaterMarkOfWarding(_GreaterDragonmarkFeat):
    _NAME = "Greater Mark of Warding"
    _BASE_MARK = "Mark of Warding"
    _INTUITION = "Warder's Intuition"
    _USES = FeatureUses(
        max_uses=MAX_PROFICIENCY_BONUS,
        regain_all_on="long rest",
        current_formula="Current amount: equal to your proficiency bonus.",
        gained_at=PROFICIENCY_BONUS_GAINED_AT,
    )

    def __init__(self, character_level: int, ability: Ability):
        super().__init__(
            character_level,
            ability,
            usage_tags=["buff", "control"],
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="30 Feet"
            ),
        )

    def _benefit_facts(self) -> tuple:
        # Improved Warding's uses are in the panel below.
        return (
            (
                "Improved Warding",
                "Reaction when a creature makes an attack roll against you or a creature you can see within 30 feet of you: impose Disadvantage on that roll. Proficiency Bonus times per Long Rest.",
            ),
        )

    def get_description(self, character: CharacterView) -> str:
        return (
            self._prerequisite() + "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 20.\n"
            "Improved Intuition. When you use the Warder's Intuition benefit of your Mark of Warding feat, you can roll 1d6 instead of 1d4.\n"
            "Improved Warding. When a creature makes an attack roll against you or a creature you can see within 30 feet of yourself, you can take a Reaction to impose Disadvantage on that roll. You can use this benefit a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest."
        )

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class PotentDragonmark(_AbilityScoreFeat):
    """Requires any Dragonmark feat (not enforced). The +1 goes to the
    spellcasting ability your Dragonmark feat uses: Constitution for the
    Aberrant Dragonmark, otherwise the Intelligence, Wisdom or Charisma
    chosen with it. Its extra spell slot is tracked by the use box; the
    engine doesn't add it to the spell slot table."""

    _NAME = "Potent Dragonmark"
    _ABILITIES = (
        Ability.CONSTITUTION,
        Ability.INTELLIGENCE,
        Ability.WISDOM,
        Ability.CHARISMA,
    )
    _USES = FeatureUses(max_uses=1, regain_all_on="short or long rest")
    # The extra slot's level: half your level (round up), up to level 5.
    _MAX_SLOT_LEVEL = 5

    def _slot_level(self, level: int) -> int:
        return min(self._MAX_SLOT_LEVEL, (level + 1) // 2)

    def get_resource_tiles(
        self, character: CharacterView
    ) -> list[tuple[str, list[tuple[str, str]]]]:
        slot_level_by_level = {
            level: str(self._slot_level(level))
            for level in ALL_LEVELS
            if level >= self._MIN_LEVEL
        }
        return [
            (
                "Slot Level",
                [
                    (f"Lv {level_range}", value)
                    for level_range, value in StringUtils.compress_level_progression(
                        slot_level_by_level
                    )
                ],
            )
        ]

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The slot's level by character level, and its use, are shown above and below.
        return [
            Facts(
                (
                    (
                        "Ability Score",
                        f"+1 {self.ability.value} (the spellcasting ability of your Dragonmark feat), to a maximum of 20",
                    ),
                    (
                        "Dragonmark Preparation",
                        "The spells on your Spells of the Mark list (if any) are always prepared",
                    ),
                    (
                        "Dragonmark Spellcasting",
                        "One extra spell slot of half your level (round up), up to level 5. It casts only spells prepared through your Dragonmark feat or Dragonmark Preparation. Regained on a Short or Long Rest.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "General Feat (Prerequisite: Level 4+, Any Dragonmark Feat)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase the spellcasting ability score used by your Dragonmark feat by 1, to a maximum of 20.\n"
            "Dragonmark Preparation. You always have the spells on your Spells of the Mark list (if any) prepared.\n"
            "Dragonmark Spellcasting. You have one extra spell slot to cast the spells granted by your Dragonmark feat. The spell slot's level is half your level (round up), to a maximum of level 5. You regain the expended slot when you finish a Short or Long Rest. You can use this spell slot to cast only a spell you have prepared because of your Dragonmark feat or the Dragonmark Preparation benefit of this feat."
        )


# ---------------------------------------------------------------------------
# Planar Pact General Feats
# ---------------------------------------------------------------------------
# The Greater Planar Pacts, D&D Beyond Drops: Fey Sentinel, Infernal Bulwark
# and Infernal Dragoon (May 2026), Fey Tormentor (August 2026), Shadow Trapper
# and Shadow Weaver (October 2026). Each needs its base Planar Pact feat
# (OriginFeats.FeyPact, InfernalPact, ShadowPact); not enforced, since no feat
# checks another feat as a prerequisite.

_FREE_CAST = "Always prepared. Cast it once without a spell slot per Long Rest, or with your spell slots."


class _GreaterPlanarPact(_AbilityScoreFeat):
    """Base class for the Greater Planar Pact feats: an _AbilityScoreFeat
    whose subclasses pass their own usage_tags, activation and uses, and
    that keeps character_level for the extras gained at character level 5.

    Subclasses declare _NAME, _ABILITIES and _PACT (the required feat's
    name), and pass usage_tags=[...] to super().__init__."""

    _PACT: str

    def __init__(
        self,
        character_level: int,
        ability: Ability,
        usage_tags: list | None = None,
        activation: FeatureActivation | None = None,
    ):
        if character_level < self._MIN_LEVEL:
            raise ValueError(
                f"{self._NAME} requires character level {self._MIN_LEVEL} or higher."
            )
        if ability not in self._ABILITIES:
            allowed = " or ".join(a.value for a in self._ABILITIES)
            raise ValueError(f"{self._NAME} ability increase must be {allowed}.")
        self.character_level = character_level
        self.ability = ability
        self._bonus = AbilityScoreBonus(
            [(ability, 1)],
            total=1,
            error_prefix=self._NAME,
            max_score=MAX_ABILITY_SCORE,
        )
        Feature.__init__(
            self,
            name=self._NAME,
            origin=self._ORIGIN,
            uses=self._USES,
            usage_tags=usage_tags,
            activation=activation,
        )

    def _prerequisite(self) -> str:
        return f"General Feat (Prerequisite: Level 4+, {self._PACT} Feat)\n"

    def _ability_increase(self) -> str:
        names = [a.value for a in self._ABILITIES]
        allowed = (
            f"{', '.join(names[:-1])}, or {names[-1]}"
            if len(names) > 2
            else " or ".join(names)
        )
        return f"Ability Score Increase. Increase your {allowed} score by 1, to a maximum of 20.\n"


class FeySentinel(_GreaterPlanarPact):
    _NAME = "Fey Sentinel"
    _PACT = "Fey Pact"
    _ABILITIES = _MENTAL_ABILITIES
    # Fading Target. The free casts are on the spells' rows.
    _USES = FeatureUses(max_uses=1, regain_all_on="long rest")

    def __init__(self, character_level: int, ability: Ability):
        super().__init__(
            character_level,
            ability,
            usage_tags=["buff", "utility"],
            activation=FeatureActivation(
                action_type=ActionType.REACTION,
                duration="Until the start of your next turn",
                range="Self",
            ),
        )

    def grant_to(self, data: Grants) -> None:
        feat = data.for_general_feat(self)
        feat.add_feature(self)
        feat.add_spell(ConjurationLevel1Spells.ENTANGLE, self.ability, _FREE_CAST)
        if self.character_level >= 5:
            feat.add_spell(
                TransmutationLevel3Spells.PLANT_GROWTH, self.ability, _FREE_CAST
            )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        spells = "Entangle" + (" and Plant Growth" if self.character_level >= 5 else "")
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Fading Target",
                        "Reaction when an enemy misses you with an attack roll: you have the Invisible condition until the start of your next turn, or until right after you make an attack roll, deal damage or cast a spell. Once per Long Rest.",
                    ),
                    (
                        "Fey Shift",
                        "When you take the Dash action, you can forgo the extra movement to teleport up to half your Speed to an unoccupied space you can see",
                    ),
                    (
                        "Nature's Roots",
                        f"{spells} always prepared; each once per Long Rest without a spell slot, or with your spell slots. {self.ability.value} is their spellcasting ability.",
                    ),
                )
                + (
                    ()
                    if self.character_level >= 5
                    else (("Character level 5", "Plant Growth, cast the same way"),)
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            self._prerequisite() + "You gain the following benefits.\n"
            f"{self._ability_increase()}"
            "Fading Target. When an enemy misses you with an attack roll, you can take a Reaction to gain the Invisible condition until the start of your next turn or until immediately after you make an attack roll, deal damage, or cast a spell. Once you use this benefit, you can't do so again until you finish a Long Rest.\n"
            "Fey Shift. When you take the Dash action, you can forgo the extra movement to teleport to an unoccupied space you can see within a distance equal to half your Speed instead.\n"
            "Nature's Roots. You always have the Entangle spell prepared. You can cast it once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. You can also cast it using any spell slots you have. The spell's spellcasting ability is the ability increased by this feat.\n"
            "When you reach character level 5, you also always have the Plant Growth spell prepared and can cast it the same way."
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class FeyTormentor(_GreaterPlanarPact):
    _NAME = "Fey Tormentor"
    _PACT = "Fey Pact"
    _ABILITIES = _MENTAL_ABILITIES
    # Faerie Time Warp. The free casts are on the spells' rows.
    _USES = FeatureUses(max_uses=1, regain_all_on="long rest")

    def __init__(self, character_level: int, ability: Ability):
        super().__init__(
            character_level,
            ability,
            usage_tags=["control"],
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="Until the end of your next turn",
                range="60 Feet",
            ),
        )

    def grant_to(self, data: Grants) -> None:
        feat = data.for_general_feat(self)
        feat.add_feature(self)
        feat.add_spell(EnchantmentLevel1Spells.HEX, self.ability, _FREE_CAST)
        if self.character_level >= 5:
            feat.add_spell(
                NecromancyLevel3Spells.BESTOW_CURSE, self.ability, _FREE_CAST
            )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        spells = "Hex" + (" and Bestow Curse" if self.character_level >= 5 else "")
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Hag's Hex",
                        f"{spells} always prepared; each once per Long Rest without a spell slot, or with your spell slots. {self.ability.value} is their spellcasting ability.",
                    ),
                )
                + (
                    ()
                    if self.character_level >= 5
                    else (("Character level 5", "Bestow Curse, cast the same way"),)
                )
            ),
            Option(
                "Faerie Time Warp",
                (
                    Facts(
                        (
                            ("Action", "Bonus Action"),
                            (
                                "Targets",
                                "Up to three creatures you can see within 60 feet",
                            ),
                            (
                                "Save",
                                f"Wisdom, DC {dc_formula(self.ability)}",
                            ),
                            (
                                "Failed",
                                "Speed reduced by 10 feet and a -2 penalty to AC until the end of your next turn",
                            ),
                            ("Recharge", "When you finish a Long Rest"),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            self._prerequisite() + "You gain the following benefits.\n"
            f"{self._ability_increase()}"
            "Faerie Time Warp. As a Bonus Action, choose up to three creatures you can see within 60 feet of yourself. Each target makes a Wisdom saving throw (DC 8 plus the ability modifier of the score increased by this feat and your Proficiency Bonus). On a failed save, the target's Speed is reduced by 10 feet, and it takes a -2 penalty to AC until the end of your next turn.\n"
            "Once you use this benefit, you can't use it again until you finish a Long Rest.\n"
            "Hag's Hex. You always have the Hex spell prepared. You can cast it once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. You can also cast it using any spell slots you have. The spell's spellcasting ability is the ability increased by this feat.\n"
            "When you reach character level 5, you also have the Bestow Curse spell prepared and can cast it in the same way."
        )

    def calculate_dc(self, character: CharacterView) -> int | None:
        return (
            8
            + character.get_ability_modifier(self.ability)
            + character.get_proficiency_bonus()
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class InfernalBulwark(_GreaterPlanarPact):
    _NAME = "Infernal Bulwark"
    _PACT = "Infernal Pact"
    _ABILITIES = (Ability.CONSTITUTION, Ability.CHARISMA)
    # Vengeful Surge. The free cast is on Armor of Agathys' row.
    _USES = FeatureUses(
        max_uses=MAX_PROFICIENCY_BONUS,
        regain_all_on="long rest",
        current_formula="Current amount: equal to your proficiency bonus.",
        gained_at=PROFICIENCY_BONUS_GAINED_AT,
    )

    def __init__(self, character_level: int, ability: Ability):
        super().__init__(
            character_level,
            ability,
            usage_tags=["buff", "damage"],
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="60 Feet"
            ),
        )
        # Devil's Flesh: an unarmored formula, so worn armor or a Shield
        # replaces it and Unarmored Defense doesn't stack with it.
        self._devils_flesh = MultiAbilityArmorClass(
            10, [Ability.DEXTERITY, ability], allows_shield=False
        )

    def apply(self, ledger_writer: LedgerWriter):
        super().apply(ledger_writer)
        self._devils_flesh.apply(ledger_writer)

    def grant_to(self, data: Grants) -> None:
        feat = data.for_general_feat(self)
        feat.add_feature(self)
        feat.add_spell(
            AbjurationLevel1Spells.ARMOR_OF_AGATHYS,
            Ability.CHARISMA,
            "Always prepared. Cast it once without a spell slot per Long Rest - as its level 2 version, dealing Fire damage instead of Cold - or with your spell slots.",
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Devil's Flesh",
                        f"While you wear no armor and wield no Shield, your base AC is 10 + Dexterity modifier + {self.ability.value} modifier",
                    ),
                    (
                        "Infernal Protection",
                        "Armor of Agathys always prepared; once per Long Rest without a spell slot, cast as its level 2 version dealing Fire damage instead of Cold, or with your spell slots. Charisma is its spellcasting ability.",
                    ),
                )
            ),
            Option(
                "Vengeful Surge",
                (
                    Facts(
                        (
                            (
                                "Trigger",
                                "You succeed on a saving throw a creature you can see within 60 feet forced you to make",
                            ),
                            ("Reaction", "Deal 1d10 Fire damage to that creature"),
                            (
                                "Uses",
                                "Proficiency Bonus times per Long Rest",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            self._prerequisite() + "You gain the following benefits.\n"
            f"{self._ability_increase()}"
            "Devil's Flesh. Your skin thickens and assumes a scaled, leathery texture. While you aren't wearing armor or wielding a Shield, your base Armor Class equals 10 plus your Dexterity modifier plus the modifier of the ability increased by this feat.\n"
            "Infernal Protection. You always have the Armor of Agathys spell prepared. You can cast it once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. When you cast it without a spell slot using this feature, you cast this spell as its level 2 version, and it deals Fire damage instead of Cold damage. You can also cast the spell using any spell slots you have of the appropriate level. Charisma is your spellcasting ability for this spell.\n"
            "Vengeful Surge. Whenever a creature you can see within 60 feet of yourself forces you to make a saving throw and you succeed, you can take a Reaction to deal 1d10 Fire damage to that creature.\n"
            "You can use this benefit a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest."
        )

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class InfernalDragoon(_GreaterPlanarPact):
    _NAME = "Infernal Dragoon"
    _PACT = "Infernal Pact"
    _ABILITIES = (Ability.CONSTITUTION, Ability.CHARISMA)
    # Devil's Favor. Devilish Aura has no use limit; the free cast is on
    # Magic Weapon's row.
    _USES = FeatureUses(max_uses=1, regain_all_on="long rest")

    def __init__(self, character_level: int, ability: Ability):
        super().__init__(
            character_level,
            ability,
            usage_tags=["control", "buff"],
            activation=FeatureActivation(
                action_type=ActionType.ACTION,
                duration="Until the end of its next turn",
                range="30-Foot Emanation",
            ),
        )

    def grant_to(self, data: Grants) -> None:
        feat = data.for_general_feat(self)
        feat.add_feature(self)
        feat.add_spell(
            TransmutationLevel2Spells.MAGIC_WEAPON,
            Ability.CHARISMA,
            "Always prepared. Cast it once without a spell slot per Long Rest - that casting lasts 8 hours - or with your spell slots.",
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Devil's Favor",
                        "When you make a D20 Test, add +2 to the roll. Once per Long Rest.",
                    ),
                    (
                        "Diabolic Empowerment",
                        "Magic Weapon always prepared; once per Long Rest without a spell slot, with a duration of 8 hours for that casting, or with your spell slots. Charisma is its spellcasting ability.",
                    ),
                )
            ),
            Option(
                "Devilish Aura",
                (
                    Facts(
                        (
                            ("Action", "Magic action"),
                            (
                                "Area",
                                "30-foot Emanation; creatures of your choice in it",
                            ),
                            (
                                "Save",
                                f"Charisma, DC {dc_formula(self.ability)}",
                            ),
                            ("Failed", "Frightened until the end of its next turn"),
                            (
                                "Success",
                                "Unaffected, and immune to this aura for 24 hours",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            self._prerequisite() + "You gain the following benefits.\n"
            f"{self._ability_increase()}"
            "Devilish Aura. Your close association with diabolic powers unsettles others. You can take a Magic action to manifest an aura of fear in a 30-foot Emanation originating from yourself. Each creature of your choice in that area makes a Charisma saving throw (DC 8 plus the modifier of the ability increased by this feat plus your Proficiency Bonus). On a failed save, it has the Frightened condition until the end of its next turn. On a successful save, a creature is unaffected, and it is immune to this ability for 24 hours.\n"
            "Devil's Favor. You can call on your infernal patron to aid you. When you make a D20 Test, you can add a +2 bonus to the roll. Once you use this benefit, you can't do so again until you finish a Long Rest.\n"
            "Diabolic Empowerment. You always have the Magic Weapon spell prepared. You can cast it once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. When you cast it without a spell slot using this feature, the spell's duration becomes 8 hours for that casting. You can also cast the spell using any spell slots you have of the appropriate level. Charisma is your spellcasting ability for this spell."
        )

    def calculate_dc(self, character: CharacterView) -> int | None:
        return (
            8
            + character.get_ability_modifier(self.ability)
            + character.get_proficiency_bonus()
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class ShadowTrapper(_GreaterPlanarPact):
    _NAME = "Shadow Trapper"
    _PACT = "Shadow Pact"
    _ABILITIES = (Ability.STRENGTH, Ability.WISDOM)

    def __init__(self, character_level: int, ability: Ability):
        super().__init__(character_level, ability, usage_tags=["buff", "damage"])

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Dangerous Shroud",
                        "Advantage on attack rolls against creatures within the Emanation of your Shroud of Shadows",
                    ),
                )
            ),
            Option(
                "Sorrowful Embrace",
                (
                    Facts(
                        (
                            (
                                "Trigger",
                                "The start of the turn of a creature you have Grappled",
                            ),
                            (
                                "Save",
                                f"Wisdom, DC {dc_formula(self.ability)}",
                            ),
                            (
                                "Failed",
                                f"1d4 + {self.ability.value} modifier Psychic damage",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            self._prerequisite()
            + "Your affinity with the Shadowfell's melancholy grants you the following benefits.\n"
            f"{self._ability_increase()}"
            "Dangerous Shroud. You have Advantage on attack rolls against creatures within the Emanation of your Shroud of Shadows.\n"
            "Sorrowful Embrace. At the start of its turn, a creature Grappled by you must succeed on a Wisdom saving throw (DC equals 8 plus the ability modifier of the score increased by this feat and your Proficiency Bonus) or take Psychic damage equal to 1d4 plus the ability modifier of the score increased by this feat."
        )

    def calculate_dc(self, character: CharacterView) -> int | None:
        return (
            8
            + character.get_ability_modifier(self.ability)
            + character.get_proficiency_bonus()
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class ShadowWeaver(_GreaterPlanarPact):
    _NAME = "Shadow Weaver"
    _PACT = "Shadow Pact"
    _ABILITIES = _MENTAL_ABILITIES
    # Create Shadow's free cast of Darkness.
    _USES = FeatureUses(max_uses=1, regain_all_on="long rest")

    def __init__(self, character_level: int, ability: Ability):
        super().__init__(
            character_level,
            ability,
            usage_tags=["control"],
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, range="60 Feet"
            ),
        )

    def grant_to(self, data: Grants) -> None:
        feat = data.for_general_feat(self)
        feat.add_feature(self)
        feat.add_spell(EvocationLevel2Spells.DARKNESS, self.ability, _FREE_CAST)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 20"),
                    (
                        "Create Shadow",
                        f"Darkness always prepared; cast it once per Long Rest without a spell slot, or with your spell slots. {self.ability.value} is its spellcasting ability.",
                    ),
                    (
                        "Manipulate Shadow",
                        "Bonus Action: grow or shrink the radius of a Darkness spell you cast by 5 feet (5 to 25 feet), or move its area to a space within 60 feet of you",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            self._prerequisite()
            + "Your commitment to your planar pact grants you the following benefits.\n"
            f"{self._ability_increase()}"
            "Create Shadow. You always have the Darkness spell prepared. You can cast it once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. You can also cast the spell using any spell slots you have of the appropriate level. The spell's spellcasting ability is the ability increased by this feat.\n"
            "Manipulate Shadow. You can take a Bonus Action to increase or decrease the radius of a Darkness spell you cast by 5 feet (minimum 5 feet, maximum 25 feet) or move the area of Darkness to a space within 60 feet of you."
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.AREA
