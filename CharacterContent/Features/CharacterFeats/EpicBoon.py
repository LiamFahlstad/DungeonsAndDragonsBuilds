from CharacterContent.Spells.SpellFactory.Enums import School
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    RegainedOn,
    regained_on_from_uses,
)
from Model.Content.Improvements import (
    AbilityScoreBonus,
    DamageResistance,
    GrantSense,
    HitPointsBonus,
    SkillExpertiseChoice,
    SkillProficiency,
    SpeedBonus,
)
from Core.Definitions import Ability, DamageType, Sense, Skill
from Core.Rules import ABSOLUTE_MAX_ABILITY_SCORE
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option


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

    They only need to implement get_description().
    """

    _NAME: str
    _ABILITIES: tuple[Ability, ...]
    _USES: FeatureUses | None = None

    def __init__(self, ability: Ability):
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
            name=self._NAME, origin="Epic Boon Feat Level 19+", uses=self._USES
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
