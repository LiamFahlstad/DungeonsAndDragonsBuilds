from enum import StrEnum

from CharacterContent.Spells.SpellFactory.Enums import School
from CharacterContent.Spells.SpellLists import (
    BardLevel6Spells,
    SorcererLevel0Spells,
    SorcererLevel1Spells,
    SorcererLevel2Spells,
    SorcererLevel3Spells,
    SorcererLevel4Spells,
    SorcererLevel5Spells,
    SorcererLevel6Spells,
    SorcererLevel7Spells,
    SorcererLevel8Spells,
)
from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureUses,
    RegainedOn,
    regained_on_from_uses,
)
from Model.Content.Improvements import (
    AbilityScoreBonus,
    ConditionImmunity,
    DamageImmunity,
    DamageResistance,
    GrantSense,
    HitPointsBonus,
    SkillExpertise,
    SkillExpertiseChoice,
    SkillProficiency,
    SpeedBonus,
)
from Core.Definitions import Ability, Condition, DamageType, Sense, Skill
from Core.Rules import ABSOLUTE_MAX_ABILITY_SCORE
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.Spells import FeatureSpell
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Table, dc_formula


class EpicBoon(Feature):
    # A feat can be taken once, unless it says it's Repeatable (see
    # Character._validate_feats_taken_once).
    repeatable = False

    labeled_by_class_level = True

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return regained_on_from_uses(self.uses)


class DummyEpicBoon(EpicBoon):
    def __init__(self):
        super().__init__(name="Epic Boon", origin="Epic Boon Feature")

    def get_description(self, character: CharacterView) -> str:
        return "This is a dummy epic boon for testing purposes."


_ANY_ABILITY = tuple(Ability)
_MENTAL_ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)


class _AbilityScoreEpicBoon(EpicBoon):
    """Base class for epic boons that grant +1 to one ability (to a maximum of 30).

    Subclasses declare:
        _NAME       – boon display name
        _ABILITIES  – tuple of allowed Ability values for the +1 bonus
        _USES       – optional FeatureUses for per-rest effects (None for passive)

    A subclass passes usage_tags=[...] (as a literal list, so the usage-tags
    skill's tag_report.py can find it) and activation to super().__init__.
    They only need to implement get_description().
    """

    _NAME: str
    _ABILITIES: tuple[Ability, ...]
    _USES: FeatureUses | None = None

    def __init__(
        self,
        ability: Ability,
        usage_tags: list | None = None,
        activation: FeatureActivation | None = None,
    ):
        if ability not in self._ABILITIES:
            allowed = " or ".join(a.value for a in self._ABILITIES)
            raise ValueError(f"{self._NAME} ability increase must be {allowed}.")
        self.ability = ability
        self._bonus = AbilityScoreBonus(
            [(ability, 1)],
            total=1,
            error_prefix=self._NAME,
            max_score=ABSOLUTE_MAX_ABILITY_SCORE,
        )
        super().__init__(
            name=self._NAME,
            origin="Epic Boon Feat Level 19+",
            uses=self._USES,
            usage_tags=usage_tags,
            activation=activation,
        )

    def apply(self, ledger_writer: LedgerWriter):
        self._bonus.apply(ledger_writer)


class BoonOfCombatProwess(_AbilityScoreEpicBoon):
    _NAME = "Boon of Combat Prowess"
    _ABILITIES = _ANY_ABILITY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    (
                        "Peerless Aim",
                        "When you miss with an attack roll, you can hit instead",
                    ),
                    ("Limit", "Then not again until the start of your next turn"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 30.\n"
            "Peerless Aim. When you miss with an attack roll, you can hit instead. Once you use this benefit, you can't use it again until the start of your next turn."
        )


class BoonOfDimensionalTravel(_AbilityScoreEpicBoon):
    _NAME = "Boon of Dimensional Travel"
    _ABILITIES = _ANY_ABILITY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    (
                        "Blink Steps",
                        "Immediately after you take the Attack or Magic action, teleport up to 30 feet to an unoccupied space you can see",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 30.\n"
            "Blink Steps. Immediately after you take the Attack action or the Magic action, you can teleport up to 30 feet to an unoccupied space you can see."
        )


class BoonOfEnergyResistance(_AbilityScoreEpicBoon):
    _NAME = "Boon of Energy Resistance"
    _ABILITIES = _ANY_ABILITY
    VALID_DAMAGE_TYPES = (
        DamageType.ACID,
        DamageType.COLD,
        DamageType.FIRE,
        DamageType.LIGHTNING,
        DamageType.NECROTIC,
        DamageType.POISON,
        DamageType.PSYCHIC,
        DamageType.RADIANT,
        DamageType.THUNDER,
    )

    def __init__(self, ability: Ability, damage_types: list[DamageType]):
        if len(damage_types) != 2 or damage_types[0] == damage_types[1]:
            raise ValueError(f"{self._NAME} requires exactly 2 different damage types.")
        invalid = [dt for dt in damage_types if dt not in self.VALID_DAMAGE_TYPES]
        if invalid:
            allowed = ", ".join(dt.value for dt in self.VALID_DAMAGE_TYPES)
            raise ValueError(f"{self._NAME} damage types must be among: {allowed}.")
        super().__init__(ability)
        self.damage_types = damage_types
        self._resistances = [DamageResistance(dt) for dt in damage_types]

    def apply(self, ledger_writer: LedgerWriter):
        super().apply(ledger_writer)
        for resistance in self._resistances:
            resistance.apply(ledger_writer)

    def calculate_dc(self, character: CharacterView) -> int:
        return (
            8
            + character.get_constitution_modifier()
            + character.get_proficiency_bonus()
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    (
                        "Energy Resistances",
                        "Two of Acid, Cold, Fire, Lightning, Necrotic, Poison, Psychic, Radiant or Thunder; change them when you finish a Long Rest",
                    ),
                    (
                        "Current choices",
                        " and ".join(dt.value for dt in self.damage_types),
                    ),
                )
            ),
            Option(
                "Energy Redirection",
                (
                    Facts(
                        (
                            ("Action", "Reaction"),
                            ("Trigger", "You take damage of one of your chosen types"),
                            (
                                "Target",
                                "Another creature you can see within 60 feet that isn't behind Total Cover",
                            ),
                            (
                                "Save",
                                "Dexterity save, DC 8 + Constitution modifier + Proficiency Bonus",
                            ),
                            (
                                "Failed",
                                "2d12 + Constitution modifier damage of the same type",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        chosen = " and ".join(dt.value for dt in self.damage_types)
        return (
            "Prerequisite: Level 19+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 30.\n"
            "Energy Resistances. You gain Resistance to two of the following damage types of your choice: Acid, Cold, Fire, Lightning, Necrotic, Poison, Psychic, Radiant, or Thunder. Whenever you finish a Long Rest, you can change your choices.\n"
            f"Current choices: {chosen}.\n"
            "Energy Redirection. When you take damage of one of the types chosen for the Energy Resistances benefit, you can take a Reaction to direct damage of the same type toward another creature you can see within 60 feet of yourself that isn't behind Total Cover. "
            f"If you do so, that creature must succeed on a Dexterity saving throw (DC {self.calculate_dc(character)}) or take damage equal to 2d12 plus your Constitution modifier."
        )


class BoonOfEruptingSpellpower(_AbilityScoreEpicBoon):
    _NAME = "Boon of Erupting Spellpower"
    _ABILITIES = _MENTAL_ABILITIES
    # Also regained when you roll Initiative (see the description).
    _USES = FeatureUses(max_uses=1, regain_all_on="short or long rest")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    (
                        "Spell Overload",
                        "When you cast a damaging spell with a spell slot, treat any 1 or 2 on its damage dice as a 3, and creatures it damages have the Prone condition",
                    ),
                    (
                        "Recharge",
                        "When you roll Initiative or finish a Short or Long Rest",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+, Spellcasting or Pact Magic Feature\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 30.\n"
            "Spell Overload. When you cast a spell that deals damage using a spell slot, you can cause its magical energy to surge. You can treat any 1 or 2 on a damage die rolled for the spell as a 3, and creatures that took damage from the spell also have the Prone condition. Once you use this benefit, you can't do so again until you roll Initiative or finish a Short or Long Rest."
        )


class BoonOfFate(_AbilityScoreEpicBoon):
    _NAME = "Boon of Fate"
    _ABILITIES = _ANY_ABILITY
    # Also regained when you roll Initiative (see the description).
    _USES = FeatureUses(max_uses=1, regain_all_on="short or long rest")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    (
                        "Improve Fate",
                        "When you or a creature within 60 feet succeeds on or fails a D20 Test, roll 2d4 and add or subtract it from the d20 roll",
                    ),
                    (
                        "Recharge",
                        "When you roll Initiative or finish a Short or Long Rest",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 30.\n"
            "Improve Fate. When you or another creature within 60 feet of you succeeds on or fails a D20 Test, you can roll 2d4 and apply the total rolled as a bonus or penalty to the d20 roll. Once you use this benefit, you can't use it again until you roll Initiative or finish a Short or Long Rest."
        )


class BoonOfFortitude(_AbilityScoreEpicBoon):
    _NAME = "Boon of Fortitude"
    _ABILITIES = _ANY_ABILITY

    def __init__(self, ability: Ability):
        super().__init__(ability)
        self._hit_points = HitPointsBonus(40)

    def apply(self, ledger_writer: LedgerWriter):
        super().apply(ledger_writer)
        self._hit_points.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    ("Hit Point maximum", "+40"),
                    (
                        "Fortified Health",
                        "When you regain Hit Points, regain extra Hit Points equal to your Constitution modifier; then not again until the start of your next turn",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 30.\n"
            "Fortified Health. Your Hit Point maximum increases by 40. In addition, whenever you regain Hit Points, you can regain additional Hit Points equal to your Constitution modifier. Once you've regained these additional Hit Points, you can't do so again until the start of your next turn."
        )


class BoonOfIrresistibleOffense(_AbilityScoreEpicBoon):
    _NAME = "Boon of Irresistible Offense"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    (
                        "Overcome Defenses",
                        "Your Bludgeoning, Piercing and Slashing damage always ignores Resistance",
                    ),
                    (
                        "Overwhelming Strike",
                        f"On a 20 on the d20 for an attack roll, deal extra damage of the attack's type equal to your {self.ability.value} score",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 30.\n"
            "Overcome Defenses. The Bludgeoning, Piercing, and Slashing damage you deal always ignores Resistance.\n"
            "Overwhelming Strike. When you roll a 20 on the d20 for an attack roll, you can deal extra damage to the target equal to the ability score increased by this feat. The extra damage's type is the same as the attack's type."
        )


class BoonOfMagicSchoolMastery(_AbilityScoreEpicBoon):
    _NAME = "Boon of Magic School Mastery"
    _ABILITIES = _MENTAL_ABILITIES
    # Repeatable, with a different school each time.
    repeatable = True
    # One free cast of the Signature Arcanum spell per Long Rest.
    _USES = FeatureUses(max_uses=1, regain_all_on="long rest")

    def __init__(
        self,
        ability: Ability,
        school: School,
        rote_spell: str,
        signature_spell: str,
    ):
        super().__init__(ability)
        self.school = school
        self.rote_spell = rote_spell
        self.signature_spell = signature_spell

    def granted_spells(self) -> list[FeatureSpell]:
        return [
            FeatureSpell(
                self.rote_spell,
                ruling="Always prepared. Cast it without a spell slot or spell components, or with your spell slots.",
                source=self.name,
            ),
            FeatureSpell(
                self.signature_spell,
                ruling="Always prepared. Cast it once without a spell slot (regained on a Long Rest), or with your spell slots.",
                source=self.name,
            ),
        ]

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    ("Mastered school", self.school.value),
                    (
                        "Rote Casting",
                        f"{self.rote_spell} (level 1) is always prepared; cast it without a spell slot or components",
                    ),
                    (
                        "Signature Arcanum",
                        f"{self.signature_spell} (level 7 or lower) is always prepared; cast it once without a spell slot, regained when you finish a Long Rest",
                    ),
                    (
                        "Spell slots",
                        "You can also cast both with spell slots of the right level",
                    ),
                    ("Repeatable", "Take it again with a different school"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+, Spellcasting or Pact Magic Feature\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 30.\n"
            f"Mastered School: {self.school.value}. Your choice grants you the following features:\n"
            f"Rote Casting. You always have {self.rote_spell} (a level 1 {self.school.value} spell from your class's spell list) prepared and can cast it without a spell slot or spell components.\n"
            f"Signature Arcanum. You always have {self.signature_spell} (a level 7 or lower {self.school.value} spell) prepared. You can cast it once without a spell slot, and you regain the ability to cast it in this way when you finish a Long Rest.\n"
            "You can also cast these prepared spells using any spell slots you have of the appropriate level.\n"
            "Repeatable. You can take this feat more than once, but you must choose a different school of magic each time."
        )


class BoonOfRecovery(_AbilityScoreEpicBoon):
    _NAME = "Boon of Recovery"
    _ABILITIES = _ANY_ABILITY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    (
                        "Last Stand",
                        "When you'd drop to 0 Hit Points, drop to 1 instead and regain half your Hit Point maximum; once per Long Rest",
                    ),
                    (
                        "Recover Vitality",
                        "A pool of ten d10s. Bonus Action: expend and roll any number, regaining Hit Points equal to the total. The pool refills when you finish a Long Rest.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 30.\n"
            "Last Stand. When you would be reduced to 0 Hit Points, you can drop to 1 Hit Point instead and regain a number of Hit Points equal to half your Hit Point maximum. Once you use this benefit, you can't use it again until you finish a Long Rest.\n"
            "Recover Vitality. You have a pool of ten d10s. As a Bonus Action, you can expend dice from the pool, roll those dice, and regain a number of Hit Points equal to the roll's total. You regain all the expended dice when you finish a Long Rest."
        )


class BoonOfSkill(_AbilityScoreEpicBoon):
    _NAME = "Boon of Skill"
    _ABILITIES = _ANY_ABILITY

    def __init__(self, ability: Ability, expertise_skill: Skill):
        super().__init__(ability)
        self.expertise_skill = expertise_skill
        self._all_skills = SkillProficiency(list(Skill))
        self._expertise = SkillExpertiseChoice(
            [expertise_skill], list(Skill), count=1, error_prefix=self._NAME
        )

    def apply(self, ledger_writer: LedgerWriter):
        super().apply(ledger_writer)
        self._all_skills.apply(ledger_writer)
        self._expertise.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    ("All-Around Adept", "Proficiency in all skills"),
                    ("Expertise", self.expertise_skill.value),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 30.\n"
            "All-Around Adept. You gain proficiency in all skills.\n"
            f"Expertise. You gain Expertise in {self.expertise_skill.value}."
        )


class BoonOfSpeed(_AbilityScoreEpicBoon):
    _NAME = "Boon of Speed"
    _ABILITIES = _ANY_ABILITY

    def __init__(self, ability: Ability):
        super().__init__(ability)
        self._speed = SpeedBonus(30)

    def apply(self, ledger_writer: LedgerWriter):
        super().apply(ledger_writer)
        self._speed.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    (
                        "Escape Artist",
                        "Bonus Action: take the Disengage action, which also ends the Grappled condition on you",
                    ),
                    ("Quickness", "+30 feet Speed"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 30.\n"
            "Escape Artist. As a Bonus Action, you can take the Disengage action, which also ends the Grappled condition on you.\n"
            "Quickness. Your Speed increases by 30 feet."
        )


class BoonOfSpellRecall(_AbilityScoreEpicBoon):
    _NAME = "Boon of Spell Recall"
    _ABILITIES = _MENTAL_ABILITIES

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    (
                        "Free Casting",
                        "When you cast a spell with a level 1-4 slot, roll 1d4: if it matches the slot's level, the slot isn't expended",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+, Spellcasting or Pact Magic Feature\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 30.\n"
            "Free Casting. Whenever you cast a spell with a level 1-4 spell slot, roll 1d4. If the number you roll is the same as the slot's level, the slot isn't expended."
        )


class BoonOfTheIronMind(_AbilityScoreEpicBoon):
    _NAME = "Boon of the Iron Mind"
    _ABILITIES = _ANY_ABILITY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    (
                        "Unshakable Focus",
                        "You lose Concentration only if you cast or activate another Concentration effect, have the Petrified or Unconscious condition, or die",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 30.\n"
            "Unshakable Focus. When you are maintaining Concentration on an effect, you lose Concentration only if you cast a spell or activate another effect that requires Concentration, if you have the Petrified or Unconscious condition, or if you die."
        )


class BoonOfTheNightSpirit(_AbilityScoreEpicBoon):
    _NAME = "Boon of the Night Spirit"
    _ABILITIES = _ANY_ABILITY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    (
                        "Merge with Shadows",
                        "In Dim Light or Darkness, give yourself the Invisible condition as a Bonus Action; it ends right after you take an action, Bonus Action or Reaction",
                    ),
                    (
                        "Shadowy Form",
                        "In Dim Light or Darkness, Resistance to all damage except Psychic and Radiant",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 30.\n"
            "Merge with Shadows. While within Dim Light or Darkness, you can give yourself the Invisible condition as a Bonus Action. The condition ends on you immediately after you take an action, a Bonus Action, or a Reaction.\n"
            "Shadowy Form. While within Dim Light or Darkness, you have Resistance to all damage except Psychic and Radiant."
        )


class BoonOfTruesight(_AbilityScoreEpicBoon):
    _NAME = "Boon of Truesight"
    _ABILITIES = _ANY_ABILITY

    def __init__(self, ability: Ability):
        super().__init__(ability)
        self._truesight = GrantSense(Sense.TRUESIGHT, 60)

    def apply(self, ledger_writer: LedgerWriter):
        super().apply(ledger_writer)
        self._truesight.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    ("Truesight", "60 feet"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 30.\n"
            "Truesight. You have Truesight with a range of 60 feet."
        )


_STR_OR_CON = (Ability.STRENGTH, Ability.CONSTITUTION)
_CON_WIS_CHA = (Ability.CONSTITUTION, Ability.WISDOM, Ability.CHARISMA)


class BoonOfBloodshed(_AbilityScoreEpicBoon):
    _NAME = "Boon of Bloodshed"
    _ABILITIES = _ANY_ABILITY

    def __init__(self, ability: Ability):
        super().__init__(ability, usage_tags=["buff", "damage"])

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    (
                        "Killer's Fortune",
                        "When an enemy you can see drops to 0 Hit Points, Advantage on your next attack roll before the end of your next turn",
                    ),
                    (
                        "Power from Pain",
                        f"Once per turn, when you make an attack roll while Bloodied, deal extra damage of the attack's type equal to your Proficiency Bonus (+{character.get_proficiency_bonus()})",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 30.\n"
            "Killer's Fortune. When an enemy you can see is reduced to 0 Hit Points, you gain Advantage on the next attack roll you make before the end of your next turn.\n"
            "Power from Pain. Once per turn, when you make an attack roll while Bloodied, you can deal extra damage to the target equal to your Proficiency Bonus. The extra damage's type is the same as the attack's type."
        )


class BoonOfBountifulHealth(_AbilityScoreEpicBoon):
    _NAME = "Boon of Bountiful Health"
    _ABILITIES = _ANY_ABILITY

    def __init__(self, ability: Ability):
        super().__init__(ability, usage_tags=["heal"])

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    (
                        "Augmented Health",
                        "Whenever you gain Temporary Hit Points, gain 5 more",
                    ),
                    (
                        "Superior Recuperation",
                        "When you spend Hit Point Dice to regain Hit Points, you can use the highest number possible for each die",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 30.\n"
            "Augmented Health. When you gain Temporary Hit Points, increase the number of Temporary Hit Points you gain by 5.\n"
            "Superior Recuperation. When you spend one or more Hit Point Dice to regain Hit Points, you can instead use the highest number possible for each die."
        )


class BoonOfCommunication(_AbilityScoreEpicBoon):
    _NAME = "Boon of Communication"
    _ABILITIES = _MENTAL_ABILITIES

    def __init__(self, ability: Ability):
        super().__init__(ability, usage_tags=["buff", "utility"])

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    (
                        "Cunning Speaker",
                        "No Disadvantage on ability checks to influence Hostile creatures",
                    ),
                    (
                        "Gifted Interpreter",
                        "You understand the literal meaning of any spoken, signed or written language you hear or see",
                    ),
                    ("Mental Communication", "Telepathy, 120 feet"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 30.\n"
            "Cunning Speaker. You don't have Disadvantage on ability checks to influence Hostile creatures.\n"
            "Gifted Interpreter. You understand the literal meaning of any language you hear or see signed, and you can understand the literal meaning of any written language you see.\n"
            "Mental Communication. You gain telepathy with a range of 120 feet."
        )


class BoonOfDesperateResilience(_AbilityScoreEpicBoon):
    _NAME = "Boon of Desperate Resilience"
    _ABILITIES = _STR_OR_CON

    def __init__(self, ability: Ability):
        super().__init__(ability, usage_tags=["buff"])

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    (
                        "Defense of Body and Mind",
                        "While Bloodied, Resistance to every damage type except Force",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Constitution score by 1, to a maximum of 30.\n"
            "Defense of Body and Mind. While you are Bloodied, you have Resistance to every damage type except Force."
        )


class BoonOfExquisiteRadiance(_AbilityScoreEpicBoon):
    _NAME = "Boon of Exquisite Radiance"
    _ABILITIES = _ANY_ABILITY
    # Powerful Radiance.
    _USES = FeatureUses(max_uses=1, regain_all_on="long rest")

    def __init__(self, ability: Ability):
        super().__init__(ability, usage_tags=["damage"])

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    (
                        "Eternal Rest",
                        "Creatures you reduce to 0 Hit Points can't become Undead",
                    ),
                    (
                        "Powerful Radiance",
                        "When you make a damage roll that deals Radiant damage, use the highest number possible for each damage die",
                    ),
                    ("Recharge", "When you finish a Long Rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 30.\n"
            "Eternal Rest. Creatures you reduce to 0 Hit Points can't become Undead.\n"
            "Powerful Radiance. When you make a damage roll that deals Radiant damage, you can instead use the highest number possible for each damage die. Once you use this benefit, you can't do so again until you finish a Long Rest."
        )


class BoonOfFluidForms(_AbilityScoreEpicBoon):
    _NAME = "Boon of Fluid Forms"
    _ABILITIES = _MENTAL_ABILITIES
    # Shapechanger.
    _USES = FeatureUses(max_uses=1, regain_all_on="long rest")

    def __init__(self, ability: Ability):
        super().__init__(
            ability,
            usage_tags=["buff", "heal"],
            activation=FeatureActivation(
                action_type=ActionType.ACTION, duration="1 Hour", range="Self"
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    (
                        "Shapechanger",
                        "Magic action: shape-shift into a Beast, Humanoid or Monstrosity of Challenge Rating 10 or lower for 1 hour",
                    ),
                    (
                        "Temporary Hit Points",
                        "Equal to the form's Hit Points, +20 (Hardy Transformation); the form ends early when they run out",
                    ),
                    (
                        "You keep",
                        "Creature type, alignment, personality, Intelligence, Wisdom and Charisma, Hit Points, Hit Point Dice, proficiencies, ability to communicate, and Spellcasting or Pact Magic",
                    ),
                    ("End early", "Take a Magic action to return to your true form"),
                    ("Recharge", "When you finish a Long Rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 30.\n"
            "Shapechanger. You can take a Magic action to shape-shift into a Beast, Humanoid, or Monstrosity with a Challenge Rating no higher than 10. When you shape-shift, you gain a number of Temporary Hit Points equal to the Hit Points of the form. The shape-shifting effect lasts for 1 hour, and it ends early if you have no Temporary Hit Points left or if you take a Magic action to return to your true form.\n"
            "Your game statistics are replaced by the stat block of the chosen form, but you retain your creature type; alignment; personality; Intelligence, Wisdom, and Charisma scores; Hit Points; Hit Point Dice; proficiencies; and ability to communicate. If you have the Spellcasting or Pact Magic feature, you retain it too. Upon shape-shifting, you determine whether your equipment drops to the ground or changes in size and shape to fit the new form while you're in it.\n"
            "Once you use this benefit, you can't do so again until you finish a Long Rest.\n"
            "Hardy Transformation. When you gain Temporary Hit Points when you shape-shift, increase that number of Temporary Hit Points by 20."
        )


class BoonOfFortunesFavor(_AbilityScoreEpicBoon):
    _NAME = "Boon of Fortune's Favor"
    _ABILITIES = _ANY_ABILITY

    def __init__(self, ability: Ability):
        super().__init__(ability, usage_tags=["buff"])

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    (
                        "Saving Throw Reroll",
                        "When you fail a saving throw, reroll it and use the new roll",
                    ),
                    ("Limit", "Then not again until the start of your next turn"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 30.\n"
            "Saving Throw Reroll. When you fail a saving throw, you can reroll it and must use the new roll. Once you use this benefit, you can't do so again until the start of your next turn."
        )


class BoonOfPoisonMastery(_AbilityScoreEpicBoon):
    _NAME = "Boon of Poison Mastery"
    _ABILITIES = _ANY_ABILITY

    def __init__(self, ability: Ability):
        super().__init__(ability, usage_tags=["buff", "damage"])
        self._poison_immunity = DamageImmunity(DamageType.POISON)
        self._poisoned_immunity = ConditionImmunity(Condition.POISONED)

    def apply(self, ledger_writer: LedgerWriter):
        super().apply(ledger_writer)
        self._poison_immunity.apply(ledger_writer)
        self._poisoned_immunity.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    (
                        "Antitoxic",
                        "Immunity to Poison damage and the Poisoned condition",
                    ),
                    (
                        "Perfect Poisoner",
                        "Once per turn, when you roll Poison damage a creature takes from your attack, spell or feature, use the highest number possible for each die",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 30.\n"
            "Antitoxic. You have Immunity to Poison damage and the Poisoned condition.\n"
            "Perfect Poisoner. Once per turn, when you roll dice to determine Poison damage a creature takes from your attack, spell, or feature, you can instead use the highest number possible for each die."
        )


class BoonOfRevelry(_AbilityScoreEpicBoon):
    _NAME = "Boon of Revelry"
    _ABILITIES = _MENTAL_ABILITIES
    # One free cast of Otto's Irresistible Dance per Long Rest.
    _USES = FeatureUses(max_uses=1, regain_all_on="long rest")
    SPELL = BardLevel6Spells.OTTOS_IRRESISTIBLE_DANCE

    def __init__(self, ability: Ability):
        super().__init__(ability, usage_tags=["control"])

    def granted_spells(self) -> list[FeatureSpell]:
        return [
            FeatureSpell(
                self.SPELL,
                ruling="Always prepared. Cast it once without a spell slot (regained on a Long Rest), or with your spell slots. No spell components, and taking damage doesn't break your Concentration on it.",
                source=self.name,
            )
        ]

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    (
                        "Inspire Dance",
                        f"{self.SPELL.value} is always prepared; cast it once without a spell slot, regained when you finish a Long Rest, or with spell slots of the right level",
                    ),
                    (
                        "When you cast it",
                        "No spell components, and taking damage doesn't break your Concentration on it",
                    ),
                    (
                        "Sing Out",
                        "A creature that failed its save and is Charmed by the spell can't cast spells with Verbal components, and sings delightful nonsense if it can sing",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 30.\n"
            "Inspire Dance. You always have the Otto's Irresistible Dance spell prepared. You can cast it once without a spell slot, and you regain the ability to cast it that way when you finish a Long Rest. You can also cast the spell using any spell slots you have of the appropriate level.\n"
            "When you cast the spell, it requires no spell components, and taking damage doesn't break your Concentration on it.\n"
            "Sing Out. While a creature that failed its saving throw against your Otto's Irresistible Dance has the Charmed condition from that spell, it can't cast spells with Verbal components, and it sings delightful nonsense if it can sing."
        )


class BoonOfTerror(_AbilityScoreEpicBoon):
    _NAME = "Boon of Terror"
    _ABILITIES = (Ability.CHARISMA,)
    # Flee, Fools!
    _USES = FeatureUses(max_uses=1, regain_all_on="short or long rest")

    def __init__(self, ability: Ability = Ability.CHARISMA):
        super().__init__(
            ability,
            usage_tags=["buff", "control"],
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="60 Feet"
            ),
        )
        self._fearless = ConditionImmunity(Condition.FRIGHTENED)
        # "Proficiency ... if you don't already have it": granting it again is harmless.
        self._intimidation = SkillProficiency([Skill.INTIMIDATION])
        self._intimidation_expertise = SkillExpertise([Skill.INTIMIDATION])

    def apply(self, ledger_writer: LedgerWriter):
        super().apply(ledger_writer)
        self._fearless.apply(ledger_writer)
        self._intimidation.apply(ledger_writer)
        self._intimidation_expertise.apply(ledger_writer)

    def calculate_dc(self, character: CharacterView) -> int:
        return 8 + character.get_charisma_modifier() + character.get_proficiency_bonus()

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", "+1 Charisma, to a maximum of 30"),
                    ("Fearless", "Immunity to the Frightened condition"),
                    ("Intimidating", "Proficiency and Expertise in Intimidation"),
                )
            ),
            Option(
                "Flee, Fools!",
                (
                    Facts(
                        (
                            ("Action", "Reaction"),
                            (
                                "Trigger",
                                "A Frightened creature starts its turn within 60 feet of you",
                            ),
                            (
                                "Target",
                                "That creature, if you can see it and it isn't behind Total Cover",
                            ),
                            (
                                "Save",
                                f"Wisdom save, DC {self.calculate_dc(character)} ({dc_formula(Ability.CHARISMA)})",
                            ),
                            (
                                "Failed",
                                "It spends its turn moving away from you by the fastest available means",
                            ),
                            ("Recharge", "When you finish a Short or Long Rest"),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Charisma score by 1, to a maximum of 30.\n"
            "Fearless. You have Immunity to the Frightened condition.\n"
            "Flee, Fools! When a creature with the Frightened condition starts its turn within 60 feet of you, you can take a Reaction to stoke its terror, provided you can see the creature and it isn't behind Total Cover. "
            f"If you do so, the creature must succeed on a Wisdom saving throw (DC {self.calculate_dc(character)}) or spend its turn moving away from you by the fastest available means. Once you use this benefit, you can't use it again until you finish a Short or Long Rest.\n"
            "Intimidating. You gain Proficiency in the Intimidation skill if you don't already have it. You also gain Expertise in Intimidation."
        )


class BoonOfTheBrightSun(_AbilityScoreEpicBoon):
    _NAME = "Boon of the Bright Sun"
    _ABILITIES = _CON_WIS_CHA

    def __init__(self, ability: Ability):
        super().__init__(
            ability,
            usage_tags=["heal", "utility"],
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="Until Dismissed",
                range="30-Foot Emanation",
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    (
                        "Daylight Presence",
                        "Bonus Action: radiate a 30-foot Emanation of Bright Light that is sunlight; a spell's Darkness it overlaps is dispelled",
                    ),
                    (
                        "Ends",
                        "When you dismiss it (no action required), die or have the Incapacitated condition",
                    ),
                    (
                        "Fortifying Light",
                        "While it's active, at the start of each of your turns, you and allies you can see in it gain 10 Temporary Hit Points",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Constitution, Wisdom, or Charisma score by 1, to a maximum of 30.\n"
            "Daylight Presence. As a Bonus Action, you radiate a 30-foot Emanation of Bright Light that is sunlight. If any of the Emanation's area overlaps with an area of Darkness created by a spell, that spell is dispelled. The Emanation lasts until you dismiss it (no action required), die, or have the Incapacitated condition.\n"
            "Fortifying Light. When your Daylight Presence is active, at the start of each of your turns, you and allies you can see in your Daylight Presence gain 10 Temporary Hit Points."
        )


class BoonOfTheFuriousStorm(_AbilityScoreEpicBoon):
    _NAME = "Boon of the Furious Storm"
    _ABILITIES = _MENTAL_ABILITIES

    def __init__(self, ability: Ability):
        super().__init__(ability, usage_tags=["buff", "control"])
        # The Immunity while Bloodied is conditional, so it stays in the text.
        self._resistances = [
            DamageResistance(DamageType.LIGHTNING),
            DamageResistance(DamageType.THUNDER),
        ]

    def apply(self, ledger_writer: LedgerWriter):
        super().apply(ledger_writer)
        for resistance in self._resistances:
            resistance.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    (
                        "Eye of the Storm",
                        "Resistance to Lightning and Thunder damage; Immunity to them while Bloodied",
                    ),
                    (
                        "Storm's Strength",
                        "Creatures have Disadvantage on saving throws against your spells that deal Lightning or Thunder damage",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+, Spellcasting or Pact Magic Feature\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 30.\n"
            "Eye of the Storm. You have Resistance to Lightning and Thunder damage. While you are Bloodied, you have Immunity to Lightning and Thunder damage.\n"
            "Storm's Strength. Creatures have Disadvantage on saving throws against your spells that deal Lightning or Thunder damage."
        )


class BoonOfTheSoulDrinker(_AbilityScoreEpicBoon):
    _NAME = "Boon of the Soul Drinker"
    _ABILITIES = _ANY_ABILITY
    # Siphon Life.
    _USES = FeatureUses(max_uses=1, regain_all_on="short or long rest")

    def __init__(self, ability: Ability):
        super().__init__(
            ability,
            usage_tags=["buff", "heal"],
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="120 Feet"
            ),
        )
        self._resistances = [
            DamageResistance(DamageType.COLD),
            DamageResistance(DamageType.NECROTIC),
        ]

    def apply(self, ledger_writer: LedgerWriter):
        super().apply(ledger_writer)
        for resistance in self._resistances:
            resistance.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    ("Grave Resistance", "Resistance to Cold and Necrotic damage"),
                )
            ),
            Option(
                "Siphon Life",
                (
                    Facts(
                        (
                            ("Action", "Reaction"),
                            (
                                "Trigger",
                                "An enemy within 120 feet of you is reduced to 0 Hit Points",
                            ),
                            ("Effect", "You regain 50 Hit Points"),
                            ("Recharge", "When you finish a Short or Long Rest"),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Prerequisite: Level 19+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 30.\n"
            "Grave Resistance. You have Resistance to Cold damage and Necrotic damage.\n"
            "Siphon Life. When an enemy within 120 feet of you is reduced to 0 Hit Points, you can take a Reaction to regain 50 Hit Points. Once you use this benefit, you can't use it again until you finish a Short or Long Rest."
        )


class SiberysDragonmarkSpell(StrEnum):
    """The Siberys Dragonmark Spells table."""

    ANIMAL_SHAPES = "Animal Shapes"
    CONTROL_WEATHER = "Control Weather"
    DEMIPLANE = "Demiplane"
    HEROES_FEAST = "Heroes' Feast"
    MAZE = "Maze"
    MIND_BLANK = "Mind Blank"
    PLANE_SHIFT = "Plane Shift"
    PROJECT_IMAGE = "Project Image"
    REGENERATE = "Regenerate"
    SYMBOL = "Symbol"
    TELEPORT = "Teleport"
    TRUE_SEEING = "True Seeing"


# The table's Suggested Dragonmark column.
SIBERYS_SUGGESTED_DRAGONMARKS = {
    SiberysDragonmarkSpell.ANIMAL_SHAPES: "Handling",
    SiberysDragonmarkSpell.CONTROL_WEATHER: "Storm",
    SiberysDragonmarkSpell.DEMIPLANE: "Making",
    SiberysDragonmarkSpell.HEROES_FEAST: "Hospitality",
    SiberysDragonmarkSpell.MAZE: "Warding",
    SiberysDragonmarkSpell.MIND_BLANK: "Sentinel",
    SiberysDragonmarkSpell.PLANE_SHIFT: "Passage",
    SiberysDragonmarkSpell.PROJECT_IMAGE: "Shadow",
    SiberysDragonmarkSpell.REGENERATE: "Healing",
    SiberysDragonmarkSpell.SYMBOL: "Scribing",
    SiberysDragonmarkSpell.TELEPORT: "Finding",
    SiberysDragonmarkSpell.TRUE_SEEING: "Detection",
}

_SORCERER_SPELLS_LEVEL_8_OR_LOWER = frozenset(
    spell.value
    for spell_list in (
        SorcererLevel0Spells,
        SorcererLevel1Spells,
        SorcererLevel2Spells,
        SorcererLevel3Spells,
        SorcererLevel4Spells,
        SorcererLevel5Spells,
        SorcererLevel6Spells,
        SorcererLevel7Spells,
        SorcererLevel8Spells,
    )
    for spell in spell_list
)


class BoonOfSiberys(_AbilityScoreEpicBoon):
    _NAME = "Boon of Siberys"
    _ABILITIES = _ANY_ABILITY
    # One free cast of the chosen spell per Short or Long Rest.
    _USES = FeatureUses(max_uses=1, regain_all_on="short or long rest")

    def __init__(
        self,
        ability: Ability,
        spell: SiberysDragonmarkSpell | str,
        spellcasting_ability: Ability,
    ):
        """`spell` is a SiberysDragonmarkSpell, or the name of a level 8 or
        lower Sorcerer spell (e.g. SorcererLevel3Spells.FIREBALL)."""
        table_spells = {str(table_spell) for table_spell in SiberysDragonmarkSpell}
        if (
            str(spell) not in table_spells
            and str(spell) not in _SORCERER_SPELLS_LEVEL_8_OR_LOWER
        ):
            raise ValueError(
                f"{self._NAME} spell must be a level 8 or lower Sorcerer spell or "
                "a spell from the Siberys Dragonmark Spells table."
            )
        if spellcasting_ability not in _MENTAL_ABILITIES:
            raise ValueError(
                f"{self._NAME} spellcasting ability must be Intelligence, Wisdom, or Charisma."
            )
        super().__init__(ability)
        self.spell = str(spell)
        self.spellcasting_ability = spellcasting_ability

    def granted_spells(self) -> list[FeatureSpell]:
        return [
            FeatureSpell(
                self.spell,
                self.spellcasting_ability,
                "Always prepared. Cast it once without a spell slot or spell components (regained on a Short or Long Rest), or with your spell slots.",
                source=self.name,
            )
        ]

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Ability Score", f"+1 {self.ability.value}, to a maximum of 30"),
                    (
                        "Aberrant Magic",
                        f"{self.spell} is always prepared; cast it once without a spell slot or components, regained when you finish a Short or Long Rest, or with spell slots of the right level",
                    ),
                    ("Spellcasting ability", self.spellcasting_ability.value),
                )
            ),
            Table(
                ("Siberys Dragonmark Spells", "Suggested Dragonmark"),
                tuple(
                    (str(table_spell), mark)
                    for table_spell, mark in SIBERYS_SUGGESTED_DRAGONMARKS.items()
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        table = "\n".join(
            f"- {table_spell} (suggested dragonmark: {mark})"
            for table_spell, mark in SIBERYS_SUGGESTED_DRAGONMARKS.items()
        )
        return (
            "Prerequisite: Level 19+, Eberron Campaign\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 30.\n"
            "Aberrant Magic. Choose a level 8 or lower spell from the Sorcerer spell list or a spell from the Siberys Dragonmark Spells table (the table includes dragonmark suggestions if you'd like to associate a spell with one of the marks). You always have that spell prepared. You can cast it once without a spell slot or spell components, and you regain the ability to cast it in that way when you finish a Short or Long Rest. You can also cast this spell using any spell slots you have of the appropriate level. Intelligence, Wisdom, or Charisma is your spellcasting ability for this spell (choose when you gain this feat).\n"
            f"Chosen spell: {self.spell} ({self.spellcasting_ability.value}).\n"
            "Siberys Dragonmark Spells:\n"
            f"{table}"
        )
