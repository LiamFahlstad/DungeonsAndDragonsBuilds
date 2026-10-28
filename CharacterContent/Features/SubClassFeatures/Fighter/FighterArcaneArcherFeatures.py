from CharacterContent.Features.ClassFeatures.ClassProficiencies import (
    CLASS_SKILL_CHOICES,
)
from CharacterContent.Spells.SpellLists import TransmutationLevel0Spells
from Core.Definitions import Ability, CharacterClass, Skill
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureDice,
    FeatureTarget,
    FeatureUses,
    RegainedOn,
)
from Model.Content.Improvements import SkillProficiencyChoice
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.CharacterSources import SpellSource
from Model.Spells import FeatureSpell
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table, dc_formula

ARCANE_SHOT_DIE = FeatureDice(
    "Arcane Shot Die",
    (
        (3, "d6"),
        (10, "d8"),
        (15, "d10"),
        (18, "d12"),
    ),
    CharacterClass.FIGHTER,
)

ARCANE_ARCHER_LORE_CANTRIPS = (
    TransmutationLevel0Spells.DRUIDCRAFT,
    TransmutationLevel0Spells.PRESTIDIGITATION,
)


class ArcaneArcherLore(Feature):
    SKILL_POOL = [Skill.ARCANA, Skill.NATURE] + [
        skill
        for skill in CLASS_SKILL_CHOICES[CharacterClass.FIGHTER][0]
        if skill not in (Skill.ARCANA, Skill.NATURE)
    ]

    def __init__(
        self,
        cantrip: TransmutationLevel0Spells,
        skill_1: Skill,
        skill_2: Skill,
    ):
        super().__init__(
            name="Arcane Archer Lore",
            origin="Arcane Archer Fighter Level 3",
            passive=True,
        )
        self._cantrip = cantrip
        self._skills = [skill_1, skill_2]
        self._proficiency_choice = SkillProficiencyChoice(
            self._skills,
            self.SKILL_POOL,
            count=2,
            error_prefix="Arcane Archer Lore",
        )

    def granted_spells(self) -> list[FeatureSpell]:
        return [
            FeatureSpell(self._cantrip, Ability.INTELLIGENCE, source=SpellSource.CHOSEN)
        ]

    def apply(self, ledger_writer: LedgerWriter):
        self._proficiency_choice.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        skills = f"Proficiency in {self._skills[0].value} and {self._skills[1].value}"
        if set(self._skills) != {Skill.ARCANA, Skill.NATURE}:
            skills += " (a Fighter skill in place of Arcana or Nature you already had)"
        return [
            Paragraph("You learn magical theory and secrets of nature."),
            Facts(
                (
                    (
                        "Cantrip",
                        f"{self._cantrip.value}, with Intelligence as your spellcasting ability",
                    ),
                    ("Skills", skills),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You learn magical theory and secrets of nature, granting you the following benefits.\n"
            f"    * Cantrip: You know either the Druidcraft or the Prestidigitation cantrip. Intelligence is your spellcasting ability for it. You chose {self._cantrip.value}.\n"
            "    * Skills: You gain proficiency in the Arcana and Nature skills. If you already have one of these proficiencies, you instead gain proficiency in a different skill of your choice from the skills available to Fighters at level 1 (or in two skills available to Fighters at level 1 if you have both). "
            f"You gained {self._skills[0].value} and {self._skills[1].value}."
        )
        return description


class ArcaneShot(Feature):
    def __init__(self):
        super().__init__(
            name="Arcane Shot",
            origin="Arcane Archer Fighter Level 3",
            usage_tags=["damage", "control"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="short or long rest",
                current_formula="Current amount: equal to your Intelligence modifier (minimum of once).",
            ),
            dice=ARCANE_SHOT_DIE,
        )

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_intelligence_modifier())

    def calculate_dc(self, character: CharacterView) -> int:
        return character.calculate_difficulty_class_for_ability(Ability.INTELLIGENCE)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses and the Arcane Shot Die are in the panel below; the options
        # you know follow as their own blocks.
        return [
            Paragraph("Unleash special magical effects with your shots."),
            Facts(
                (
                    (
                        "When",
                        "Once per turn, on a ranged attack with a weapon that has the Ammunition property",
                    ),
                    (
                        "Decide",
                        "After you hit a creature and deal damage to it; before the attack if the option makes no attack roll",
                    ),
                    (
                        "Options known",
                        "2; one more at Fighter levels 7, 10, 15 and 18, when you can also replace one",
                    ),
                    ("Save DC", dc_formula(Ability.INTELLIGENCE)),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You learn to unleash special magical effects with your shots.\n"
            'Arcane Shot Options. You learn two Arcane Shot options of your choice from the "Arcane Shot Options" section later in this subclass\'s description.\n'
            "You learn an additional Arcane Shot option of your choice when you reach Fighter levels 7, 10, 15, and 18. Each time you learn a new Arcane Shot option, you can also replace one option you know with a different one.\n"
            "Using Arcane Shot. Once per turn when you make a ranged attack using a weapon with the Ammunition property, you can apply one of your Arcane Shot options to that attack. You decide to use the option when you hit a creature and deal damage to it unless the option doesn't involve an attack roll.\n"
            "You can use this feature a number of times equal to your Intelligence modifier (minimum of once). You regain all expended uses when you finish a Short or Long Rest.\n"
            "Arcane Shot Die. Arcane Shot options refer to your Arcane Shot Die. Your Arcane Shot Die is a d6.\n"
            "Saving Throws. If an Arcane Shot option requires a saving throw, the DC equals 8 plus your Intelligence modifier and Proficiency Bonus.\n"
            "At Higher Levels. Your Arcane Shot Die changes when you reach certain Fighter levels. The die becomes a d8 at level 10, a d10 at level 15, and a d12 at level 18."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.SHORT_OR_LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


# ── Arcane Shot options ─────────────────────────────────────────────────────


class ArcaneShotOption(Feature):
    """One Arcane Shot option, granted as an extension of ArcaneShot."""

    def __init__(
        self,
        name: str,
        activation: "FeatureActivation | None" = None,
        usage_tags: list | None = None,
    ):
        super().__init__(
            name=name,
            origin="Arcane Shot Option",
            activation=activation,
            usage_tags=usage_tags,
        )

    def calculate_dc(self, character: CharacterView) -> int:
        return character.calculate_difficulty_class_for_ability(Ability.INTELLIGENCE)

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class BanishingShot(ArcaneShotOption):
    def __init__(self):
        super().__init__(
            name="Banishing Shot",
            activation=FeatureActivation(duration="Until End of Its Next Turn"),
            usage_tags=["damage", "control"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Damage", "+1 Arcane Shot Die of Psychic damage"),
                    ("Save", "Charisma"),
                    (
                        "Failed",
                        "Banished to a harmless demiplane until the end of its next turn, with the Incapacitated condition and a Speed of 0",
                    ),
                    (
                        "Return",
                        "In the space it left, or the nearest unoccupied space if that one is occupied",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return "Your ammunition temporarily sequesters your target in a harmless demiplane. The creature you hit takes extra Psychic damage equal to one roll of your Arcane Shot Die and must succeed on a Charisma saving throw or be banished. While banished, the creature has the Incapacitated condition and a Speed of 0. At the end of its next turn, the target reappears in the space it left or, if that space is occupied, in the nearest unoccupied space."


class BeguilingShot(ArcaneShotOption):
    def __init__(self):
        super().__init__(
            name="Beguiling Shot",
            activation=FeatureActivation(duration="Until Start of Next Turn"),
            usage_tags=["damage", "control"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Damage", "+2 Arcane Shot Dice of Psychic damage"),
                    ("Save", "Wisdom"),
                    (
                        "Failed",
                        "Charmed until the start of your next turn by you or an ally within 30 feet of the target (your choice)",
                    ),
                    (
                        "Ends early",
                        "The charmer attacks the target, deals damage to it or forces it to make a saving throw",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return "Your ammunition beguiles your target. The creature you hit takes extra Psychic damage equal to two rolls of your Arcane Shot Die and must succeed on a Wisdom saving throw or have the Charmed condition until the start of your next turn, treating either you or one of your allies within 30 feet of the target (your choice) as the charmer. The Charmed condition ends early if the charmer attacks the target, deals damage to it, or forces it to make a saving throw."


class BurstingShot(ArcaneShotOption):
    def __init__(self):
        super().__init__(
            name="Bursting Shot",
            activation=FeatureActivation(range="10-Foot Emanation"),
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "Immediately after you deal damage to the target"),
                    (
                        "Area",
                        "The target and each creature in a 10-foot Emanation from it",
                    ),
                    ("Damage", "2 Arcane Shot Dice of Force damage to each"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return "You imbue your ammunition with explosive magical energy. Immediately after you deal damage to the creature, your target and each creature within a 10-foot Emanation originating from the target take Force damage equal to two rolls of your Arcane Shot Die."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.AREA


class EnfeeblingShot(ArcaneShotOption):
    def __init__(self):
        super().__init__(
            name="Enfeebling Shot",
            activation=FeatureActivation(duration="Until End of Its Next Turn"),
            usage_tags=["damage", "control"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Damage", "+2 Arcane Shot Dice of Necrotic damage"),
                    ("Save", "Constitution"),
                    (
                        "Failed",
                        "Poisoned until the end of its next turn; whenever it hits with an attack roll, it subtracts one Arcane Shot Die from that attack's total damage",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return "Your ammunition saps your target's strength. The creature you hit takes extra Necrotic damage equal to two rolls of your Arcane Shot Die. The target must also succeed on a Constitution saving throw or have the Poisoned condition until the end of its next turn. Whenever a target Poisoned in this way hits with an attack roll, it subtracts an amount equal to one roll of your Arcane Shot Die from the total damage of that attack."


class GraspingShot(ArcaneShotOption):
    def __init__(self):
        super().__init__(
            name="Grasping Shot",
            activation=FeatureActivation(duration="1 Minute"),
            usage_tags=["damage", "control"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Damage", "+1 Arcane Shot Die of Slashing damage"),
                    ("Save", "Strength"),
                    (
                        "Failed",
                        "Restrained by brambles for 1 minute or until you use this option again",
                    ),
                    (
                        "Escape",
                        "The target or a creature within its reach takes an action to make a Strength (Athletics) check against your Arcane Shot save DC, ending the Restrained condition on a success",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return "Your ammunition creates clutching brambles around your target. The creature you hit takes extra Slashing damage equal to one roll of your Arcane Shot Die and must succeed on a Strength saving throw or have the Restrained condition for 1 minute or until you use this option again. The target or a creature within reach of it can take an action to make a Strength (Athletics) check against your Arcane Shot saving throw DC, removing the brambles and ending the Restrained condition on the target on a successful check."


class PiercingShot(ArcaneShotOption):
    def __init__(self):
        super().__init__(
            name="Piercing Shot",
            activation=FeatureActivation(range="30-Foot Line"),
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Attack roll", "None"),
                    (
                        "Area",
                        "A 30-foot-long, 1-foot-wide Line from you that ignores cover, as the ammunition phases through solid objects",
                    ),
                    ("Save", "Each creature in the Line makes a Dexterity save"),
                )
            ),
            Table(
                ("Save", "Result"),
                (
                    (
                        "Failed",
                        "Damage as if hit, plus 2 Arcane Shot Dice of Piercing damage",
                    ),
                    ("Succeeded", "Half as much damage"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return "You give your ammunition an ethereal quality. When you use this option, you don't make an attack roll for the attack. Instead, the ammunition shoots forward in a 30-foot-long, 1-foot-wide Line originating from you, then vanishes. The Line ignores cover, as the ammunition phases through solid objects. Each creature in the Line makes a Dexterity saving throw. On a failed save, a creature takes damage as if it were hit plus extra Piercing damage equal to two rolls of your Arcane Shot Die. On a successful save, a creature takes half as much damage."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.AREA


class SeekingShot(ArcaneShotOption):
    def __init__(self):
        super().__init__(
            name="Seeking Shot",
            usage_tags=["damage", "utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Attack roll", "None"),
                    ("Target", "One creature you have seen in the last minute"),
                    (
                        "Path",
                        "Moves around corners, ignoring Half Cover and Three-Quarters Cover",
                    ),
                    (
                        "Save",
                        "Dexterity, if the target is within your weapon's long range",
                    ),
                    (
                        "Out of range",
                        "The ammunition disappears after traveling as far as it can",
                    ),
                )
            ),
            Table(
                ("Save", "Result"),
                (
                    (
                        "Failed",
                        "Damage as if hit, plus 2 Arcane Shot Dice of Force damage, and you learn its current location",
                    ),
                    ("Succeeded", "Half as much damage only"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return "Your ammunition can seek out a target. When you use this option, you don't make an attack roll for the attack. Instead, choose one creature you have seen in the last minute. The ammunition flies toward that creature, moving around corners if necessary and ignoring Half Cover and Three-Quarters Cover. If the target is within your weapon's long range, the target makes a Dexterity saving throw. On a failed save, the target takes damage as if it were hit plus extra Force damage equal to two rolls of your Arcane Shot Die, and you learn the target's current location. On a successful save, the target takes half as much damage only. If the target is beyond your weapon's long range, the ammunition disappears after traveling as far as it can."


class ShadowShot(ArcaneShotOption):
    def __init__(self):
        super().__init__(
            name="Shadow Shot",
            activation=FeatureActivation(duration="Until End of Its Next Turn"),
            usage_tags=["damage", "control"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Damage", "+1 Arcane Shot Die of Psychic damage"),
                    ("Save", "Wisdom"),
                    ("Failed", "Blinded until the end of its next turn"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return "Your ammunition occludes your foe's vision with shadows. The creature you hit takes extra Psychic damage equal to one roll of your Arcane Shot Die, and it must succeed on a Wisdom saving throw or have the Blinded condition until the end of its next turn."


# ── Later subclass features ─────────────────────────────────────────────────


class CurvingShot(Feature):
    def __init__(self):
        super().__init__(
            name="Curving Shot",
            origin="Arcane Archer Fighter Level 7",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, range="60 Feet"
            ),
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Action", "Bonus Action"),
                    (
                        "Trigger",
                        "Immediately after you miss a ranged attack roll with a weapon with the Ammunition property",
                    ),
                    (
                        "Target",
                        "A creature you can see within the weapon's range and within 60 feet of the original target",
                    ),
                    ("Effect", "Make an attack roll against the new target"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You learn how to direct an errant shot toward a new target. If you make a ranged attack roll with a weapon with the Ammunition property and miss, you can cause the shot to ricochet toward a new target as a Bonus Action immediately after the attack misses. The new target must be a creature you can see within the weapon's range and within 60 feet of the attack's original target. Make an attack roll against the new target."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class MagicalAmmunition(Feature):
    def __init__(self):
        super().__init__(
            name="Magical Ammunition",
            origin="Arcane Archer Fighter Level 7",
            activation=FeatureActivation(action_type=ActionType.ACTION),
            usage_tags=["control", "utility"],
            uses=FeatureUses(max_uses=1, regain_all_on="short or long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-rest box is in the panel below.
        return [
            Paragraph(
                "Imbue a piece of nonmagical ammunition with a magical property and fire it at a solid surface you can see within the weapon's range."
            ),
            Facts(
                (
                    ("Action", "Magic action"),
                    (
                        "On impact",
                        "The effect activates and the ammunition attaches to the surface for the effect's duration; it's destroyed when the effect ends",
                    ),
                    (
                        "End early",
                        "Remove the attached ammunition as a Magic action",
                    ),
                    (
                        "Restore",
                        "Expend a use of Second Wind (no action required)",
                    ),
                )
            ),
            Option(
                "Darkening Ammunition",
                (
                    Facts(
                        (
                            ("Area", "15-foot Emanation from the ammunition"),
                            ("Duration", "1 minute"),
                            (
                                "Effect",
                                "Magical shadows fill it. Nonmagical flames in it are extinguished, and creatures in it have a -5 penalty to Wisdom (Perception) checks and Passive Perception.",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Unlocking Ammunition",
                (
                    Facts(
                        (
                            ("Area", "15-foot Emanation from the ammunition"),
                            (
                                "Effect",
                                "Each object in it that's held shut by a nonmagical lock, or stuck or barred, becomes unlocked, unstuck or unbarred. An object with several locks has only one unlocked.",
                            ),
                            ("Noise", "A loud knocking, audible up to 300 feet away"),
                        )
                    ),
                ),
            ),
            Option(
                "Vine Ammunition",
                (
                    Facts(
                        (
                            ("Duration", "10 minutes, then the vine withers away"),
                            (
                                "Effect",
                                "A 120-foot-long vine grows from the ammunition; you and other creatures can climb it",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You learn to imbue your ammunition with magical properties. As a Magic action, you can imbue a piece of nonmagical ammunition with one of the following magical properties and fire it at a solid surface you can see within the weapon's range. When the ammunition hits the surface, the ammunition's effect activates, and the ammunition attaches to the surface it hit for the duration of the effect; you can remove an attached piece of ammunition as a Magic action, ending the effect early. When the effect ends, the ammunition is destroyed.\n"
            "Once you use this feature, you can't do so again until you finish a Short or Long Rest. You can also restore your use of this feature by expending a use of your Second Wind (no action required).\n"
            "    * Darkening Ammunition: Magical shadows fill a 15-foot Emanation originating from the ammunition for 1 minute. Nonmagical flames in the Emanation are extinguished, and creatures in the Emanation have a -5 penalty to Wisdom (Perception) checks and Passive Perception.\n"
            "    * Unlocking Ammunition: A burst of magic fills a 15-foot Emanation originating from the ammunition. The ammunition also emits a loud knocking sound, audible up to 300 feet away. Any object in the Emanation that is held shut by a nonmagical lock or that is stuck or barred becomes unlocked, unstuck, or unbarred. If such an object has multiple locks, only one of them is unlocked.\n"
            "    * Vine Ammunition: A 120-foot-long vine grows from the ammunition. You and other creatures can then climb it. The vine withers away after 10 minutes."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.SHORT_OR_LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.AREA


class EverReadyShot(Feature):
    def __init__(self):
        super().__init__(
            name="Ever-Ready Shot", origin="Arcane Archer Fighter Level 10"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "When you roll Initiative, you can regain one expended use of Arcane Shot."
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you roll Initiative, you can regain one expended use of Arcane Shot."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.INITIATIVE_ROLL


class IndomitableTeleport(Feature):
    def __init__(self):
        super().__init__(
            name="Indomitable Teleport",
            origin="Arcane Archer Fighter Level 15",
            activation=FeatureActivation(range="60 Feet"),
            usage_tags=["utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "You use Indomitable and succeed on the saving throw",
                    ),
                    (
                        "Effect",
                        "Teleport up to 60 feet to an unoccupied space you can see",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Your magical mastery lets you escape dire situations. When you use your Indomitable feature and succeed on the saving throw, you can teleport up to 60 feet to an unoccupied space you can see."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class MasterfulShots(Feature):
    def __init__(self):
        super().__init__(
            name="Masterful Shots",
            origin="Arcane Archer Fighter Level 18",
            activation=FeatureActivation(action_type=ActionType.REACTION),
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Action", "Reaction"),
                    (
                        "Trigger",
                        "A creature you can see misses you with an attack roll",
                    ),
                    (
                        "Move",
                        "Up to half your Speed away from the attacker, without provoking Opportunity Attacks",
                    ),
                    (
                        "Attack",
                        "Then make a ranged attack roll against the attacker, if it's within the weapon's range",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You employ agility in your sharpshooting. When a creature you can see misses you with an attack roll, you can take a Reaction to move up to half your Speed away from the attacker without provoking Opportunity Attacks. You can then make a ranged attack roll against the attacker as part of this Reaction if the attacker is within the weapon's range."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY
