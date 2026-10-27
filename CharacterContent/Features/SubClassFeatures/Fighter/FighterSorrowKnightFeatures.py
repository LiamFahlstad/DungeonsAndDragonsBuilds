from Core.Definitions import Ability, CharacterClass, DamageType, Sense
from Core.Rules import MAX_ABILITY_MODIFIER, levels_gained
from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureDice,
    FeatureTarget,
    FeatureUses,
    RegainedOn,
)
from Model.Content.FeatureText import (
    Block,
    Facts,
    Option,
    Paragraph,
    Table,
    dc_formula,
)
from Model.Content.Improvements import DamageResistance, GrantOrExtendSense
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.View import CharacterView

# The Despairing Strike Dice table: (Fighter level, die size, number of dice).
_DESPAIRING_STRIKE_DICE = (
    (3, "d8", 3),
    (10, "d10", 4),
    (15, "d12", 5),
)


def despairing_strike_dice(fighter_level: int) -> tuple[str, int]:
    """(die size, number of dice) at a Sorrow Knight Fighter level."""
    die, count = _DESPAIRING_STRIKE_DICE[0][1], 0
    for from_level, level_die, level_count in _DESPAIRING_STRIKE_DICE:
        if fighter_level >= from_level:
            die, count = level_die, level_count
    return die, count


# The level each Despairing Strike Die box is gained at: [3, 3, 3, 10, 15].
DESPAIRING_STRIKE_DICE_GAINED_AT = levels_gained(
    lambda level: despairing_strike_dice(level)[1], from_level=3
)

DESPAIRING_STRIKE_DIE = FeatureDice(
    "Despairing Strike Die",
    tuple((level, die) for level, die, _ in _DESPAIRING_STRIKE_DICE),
    scales_with=CharacterClass.FIGHTER,
)

_DESPAIRING_STRIKE_DIE_FORMULA = (
    "Despairing Strike Die (d8; d10 from Fighter level 10, d12 from Fighter level 15)"
)


def _sorrow_knight_dc(character: CharacterView) -> int:
    return 8 + character.get_wisdom_modifier() + character.get_proficiency_bonus()


class DespairingStrikes(Feature):
    def __init__(self):
        super().__init__(
            name="Despairing Strikes",
            origin="Sorrow Knight Fighter Level 3",
            usage_tags=["damage", "control"],
            uses=FeatureUses(
                max_uses=len(DESPAIRING_STRIKE_DICE_GAINED_AT),
                regain_all_on="short or long rest",
                gained_at=DESPAIRING_STRIKE_DICE_GAINED_AT,
            ),
            dice=DESPAIRING_STRIKE_DIE,
        )

    def number_of_uses(self, character: CharacterView) -> int:
        return despairing_strike_dice(
            character.get_class_level(CharacterClass.FIGHTER)
        )[1]

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.SHORT_OR_LONG_REST

    def calculate_dc(self, character: CharacterView) -> int:
        return _sorrow_knight_dc(character)

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Dice count, size and recharge are in the panel below.
        return [
            Paragraph(
                "You channel the despair of an emotional wound into your weapon strikes, fueled by Despairing Strike Dice."
            ),
            Facts(
                (
                    (
                        "Trigger",
                        "You hit a creature with an attack roll using a weapon",
                    ),
                    ("Cost", "Expend one Despairing Strike Die"),
                    (
                        "Damage",
                        "Extra Psychic damage equal to the die roll",
                    ),
                    (
                        "Effect",
                        "You can also add one of the effects below",
                    ),
                    ("Limit", "No more than one die per attack"),
                    ("Save DC", dc_formula(Ability.WISDOM)),
                )
            ),
            Option(
                "Abandoned",
                (
                    Facts(
                        (
                            ("Save", "Intelligence saving throw"),
                            (
                                "Failed",
                                "Deafened until the end of your next turn. While Deafened, the target regards all creatures it can see as enemies until the end of your next turn.",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Dread",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "The target has Disadvantage on the next saving throw it makes before the start of your next turn",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Each sorrow knight bears an emotional wound like a deep scar, through which they channel despair against their enemies. This misery is fueled by special dice called Despairing Strike Dice.\n"
            "The Despairing Strike Dice table shows the die size and number of these dice you have when you reach certain Fighter levels. A Despairing Strike Die is expended when you use it. You regain all expended Despairing Strike Dice when you finish a Short or Long Rest.\n"
            "Despairing Strike Dice\n"
            "Fighter Level\tDice Size\tNumber\n"
            "3\tD8\t3\n"
            "10\tD10\t4\n"
            "15\tD12\t5\n"
            "When you hit a creature with an attack roll using a weapon, you can expend a Despairing Strike Die and roll that die. You deal additional Psychic damage equal to the roll and can also add one of the following effects. You can’t expend more than one die per attack.\n"
            "If a Despairing Strike effect requires a saving throw, the DC equals 8 plus your Wisdom modifier and Proficiency Bonus.\n"
            "Abandoned. The target must succeed on an Intelligence saving throw or have the Deafened condition until the end of your next turn. While Deafened, the target regards all creatures it can see as enemies until the end of your next turn.\n"
            "Dread. The target has Disadvantage on the next saving throw it makes before the start of your next turn."
        )
        return description


class SolemnGaze(Feature):
    def __init__(self):
        super().__init__(
            name="Solemn Gaze",
            origin="Sorrow Knight Fighter Level 3",
            activation=FeatureActivation(
                action_type=ActionType.ACTION, range="30 Feet"
            ),
            usage_tags=["utility"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Wisdom modifier (minimum of once).",
            ),
        )
        self._darkvision = GrantOrExtendSense(Sense.DARKVISION, 60)

    def apply(self, ledger_writer: LedgerWriter):
        self._darkvision.apply(ledger_writer)

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_wisdom_modifier())

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def calculate_dc(self, character: CharacterView) -> int:
        return _sorrow_knight_dc(character)

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Empathetic Inquiry's uses are in the panel below.
        return [
            Paragraph(
                "You see through the darkness around you and recognize the darkness in others."
            ),
            Option(
                "Darkvision",
                (
                    Facts(
                        (
                            (
                                "Range",
                                "60 feet, or +60 feet if you already have Darkvision",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Empathetic Inquiry",
                (
                    Facts(
                        (
                            ("Action", "Magic action"),
                            ("Range", "30 feet"),
                            ("Target", "A creature you can see"),
                            (
                                "Save",
                                f"Wisdom saving throw ({dc_formula(Ability.WISDOM)})",
                            ),
                            (
                                "Failed",
                                "You learn an emotion that looms large in its mind, such as a worry, love or hate",
                            ),
                            (
                                "Noticed",
                                "If the target can see you, it knows you have read its emotions",
                            ),
                            (
                                "Uses",
                                "Wisdom modifier (minimum of once) per Long Rest",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can see through the darkness around you and recognize the darkness in others. You gain the following benefits.\n"
            "Darkvision. You gain Darkvision with a range of 60 feet. If you already have Darkvision, its range increases by 60 feet.\n"
            "Empathetic Inquiry. As a Magic action, you can attempt to search the mind of a creature you can see within 30 feet. The target must succeed on a Wisdom saving throw (DC equals 8 plus your Wisdom modifier and Proficiency Bonus) or you learn an emotion that looms large in its mind, such as a worry, love, or hate. If the target can see you, it knows you have read its emotions. You can use this feature a number of times equal to your Wisdom modifier (minimum of once). You regain all expended uses when you finish a Long Rest."
        )
        return description


class DreadedAppearance(Feature):
    def __init__(self):
        super().__init__(
            name="Dreaded Appearance",
            origin="Sorrow Knight Fighter Level 7",
            activation=FeatureActivation(range="10-Foot Emanation"),
            usage_tags=["damage", "control"],
            uses=FeatureUses(max_uses=1, regain_all_on="short or long rest"),
        )

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.SHORT_OR_LONG_REST

    def calculate_dc(self, character: CharacterView) -> int:
        return _sorrow_knight_dc(character)

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-rest box for the appearance is in the panel below.
        return [
            Facts(
                (
                    ("Trigger", "You use Tactical Shift"),
                    (
                        "Teleport",
                        "Instead of moving, teleport to an unoccupied space you can see within 30 feet of yourself",
                    ),
                )
            ),
            Option(
                "Appearance of Fears",
                (
                    Facts(
                        (
                            ("When", "Immediately after you reappear"),
                            (
                                "Target",
                                "Each creature of your choice in a 10-foot Emanation from you; only they see the appearance of their fears",
                            ),
                            (
                                "Save",
                                f"Wisdom saving throw ({dc_formula(Ability.WISDOM)})",
                            ),
                            ("Limit", "Once per Short or Long Rest"),
                        )
                    ),
                    Table(
                        ("Save", "Result"),
                        (
                            (
                                "Failed",
                                f"Psychic damage equal to a roll of your {_DESPAIRING_STRIKE_DIE_FORMULA}, and Frightened until the end of your next turn",
                            ),
                            ("Succeeded", "Half damage only"),
                        ),
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you use Tactical Shift, you can teleport to an unoccupied space you can see within 30 feet of yourself instead of moving.\n"
            "Immediately after you reappear, you can briefly take on the appearance of creatures’ fears, visible only to those creatures. Each creature of your choice within a 10-foot Emanation originating from you makes a Wisdom saving throw (DC equals 8 plus your Wisdom modifier and your Proficiency Bonus). On a failed save, a target takes Psychic damage equal to a roll of your Despairing Strike die and has the Frightened condition until the end of your next turn. On a successful save, it takes half damage only.\n"
            "Once you take on this appearance, you can’t do so again until you finish a Short or Long Rest."
        )
        return description


class UnsettledStrikes(Feature):
    def __init__(self):
        super().__init__(
            name="Unsettled Strikes",
            origin="Sorrow Knight Fighter Level 10",
            usage_tags=["control"],
        )

    def calculate_dc(self, character: CharacterView) -> int:
        return _sorrow_knight_dc(character)

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("These effects are now among your Despairing Strike options."),
            Option(
                "Apathetic",
                (
                    Facts(
                        (
                            ("Save", "Wisdom saving throw"),
                            (
                                "Failed",
                                "Incapacitated until the start of your next turn. While Incapacitated this way, it can give only one-word responses when spoken to.",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Lost",
                (
                    Facts((("Save", "Charisma saving throw"),)),
                    Table(
                        ("Save", "Result"),
                        (
                            (
                                "Failed",
                                "Blinded, and its Speed is reduced to 0, until the end of its next turn",
                            ),
                            (
                                "Succeeded",
                                "Its Speed is halved until the end of its next turn",
                            ),
                        ),
                    ),
                ),
            ),
            Option(
                "Weary",
                (
                    Facts(
                        (
                            ("Save", "Constitution saving throw"),
                            ("Failed", "The target gains 1 Exhaustion level"),
                            (
                                "Limit",
                                "Can't raise the target's Exhaustion level above 2",
                            ),
                            (
                                "Duration",
                                "Exhaustion levels from this effect are removed at the end of your next turn",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You further channel the pathos of the Shadowfell through your fighting abilities. The following effects are now among your Despairing Strike options.\n"
            "Apathetic. The target must succeed on a Wisdom saving throw or have the Incapacitated condition until the start of your next turn. While Incapacitated in this way, the target can give only one-word responses when spoken to.\n"
            "Lost. The target makes a Charisma saving throw. On a failed save, the target has the Blinded condition, and its Speed is reduced to 0 until the end of its next turn. On a successful save, the target’s Speed is halved until the end of its next turn.\n"
            "Weary. The target must succeed on a Constitution saving throw or gain 1 Exhaustion level. This effect can’t increase the target’s Exhaustion level above 2. Exhaustion levels gained from this effect are removed at the end of your next turn."
        )
        return description


class GrimConstitution(Feature):
    def __init__(self):
        super().__init__(
            name="Grim Constitution",
            origin="Sorrow Knight Fighter Level 15",
            usage_tags=["buff"],
        )
        self._resistances = [
            DamageResistance(DamageType.NECROTIC),
            DamageResistance(DamageType.PSYCHIC),
        ]

    def apply(self, ledger_writer: LedgerWriter):
        for resistance in self._resistances:
            resistance.apply(ledger_writer)

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Resistance", "Necrotic and Psychic damage"),
                    (
                        "Trigger",
                        "You are subjected to an effect that reduces your Hit Point maximum",
                    ),
                    (
                        "Save",
                        "Constitution saving throw, DC 15. On a success, your Hit Point maximum isn't decreased.",
                    ),
                    (
                        "Escalation",
                        "The DC increases by 5 each time you make this save after the first, and resets to 15 when you finish a Short or Long Rest",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You have Resistance to Necrotic and Psychic damage.\n"
            "In addition, when you are subjected to an effect that reduces your Hit Point maximum, you can make a DC 15 Constitution saving throw. If you succeed, your Hit Point maximum isn’t decreased. Each time you make this Constitution saving throw after the first, the DC increases by 5. When you finish a Short or Long Rest, the DC resets to 15."
        )
        return description


class GrievingMantle(Feature):
    def __init__(self):
        super().__init__(
            name="Grieving Mantle",
            origin="Sorrow Knight Fighter Level 18",
            activation=FeatureActivation(
                duration="1 Minute or Until Incapacitated",
            ),
            usage_tags=["buff"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "You use Action Surge"),
                    (
                        "Duration",
                        "1 minute, or until you have the Incapacitated condition",
                    ),
                    (
                        "Effect",
                        "You attune yourself to the Shadowfell and gain both benefits below",
                    ),
                )
            ),
            Option(
                "Shade Form",
                (
                    Facts(
                        (
                            ("Action", "Reaction"),
                            ("Trigger", "You are hit by an attack roll"),
                            (
                                "Effect",
                                "You become insubstantial for a moment; the attack's total damage against you is reduced to 0",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Unwavering Resolve",
                (
                    Facts(
                        (
                            (
                                "Immunity",
                                "The Charmed and Frightened conditions",
                            ),
                            (
                                "On activation",
                                "If you're Charmed or Frightened, the condition ends on you",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you use your Action Surge, you attune yourself to the Shadowfell for 1 minute or until you have the Incapacitated condition. For the duration, you gain the following benefits.\n"
            "Shade Form. When you are hit by an attack roll, you can take a Reaction to become insubstantial for a moment and reduce the attack’s total damage against you to 0.\n"
            "Unwavering Resolve. You have Immunity to the Charmed and Frightened conditions. If you’re Charmed or Frightened when you activate your Grieving Mantle, the condition ends on you."
        )
        return description
