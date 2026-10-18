from enum import Enum

from CharacterContent.Features.ClassFeatures.Druid.WildShapeForms import (
    format_wild_shape_form,
    wild_shape_temp_hp_formula,
)
from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
    RegainedOn,
)
from Model.Content.Improvements import (
    GrantLanguage,
    SkillBonus,
    GrantArmorTraining,
    GrantWeaponProficiency,
)
from Model.Creatures.Combatants import CreatureForm
from Core.Definitions import Ability, CharacterClass, Language, Skill, ArmorType
from CharacterContent.Items.Weapons import WeaponProficiency
from Model.View import CharacterView
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.Content.FeatureText import (
    Block,
    Facts,
    Option,
    Paragraph,
    StatBlock,
    dc_formula,
)


class PrimalOrderType(str, Enum):
    MAGICIAN = "Magician"
    WARDEN = "Warden"


class Spellcasting(Feature):
    def __init__(self):
        super().__init__(name="Spellcasting", origin="Druid Level 1")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Spellcasting ability", "Wisdom"),
                    ("Save DC", dc_formula(Ability.WISDOM)),
                    ("Spell attack", "Wisdom modifier + Proficiency Bonus"),
                    ("Cantrips", "Replace one whenever you gain a Druid level"),
                    (
                        "Prepared spells",
                        "Replace one whenever you finish a Long Rest",
                    ),
                    ("Spell slots", "Regain all when you finish a Long Rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Spellcasting\n"
            "    * Replacing Cantrips: Change one when you gain a Druid level.\n"
            "    * Replacing Spells: Change one when you finish a Long Rest.\n"
            "    * Regaining Spell Slots: You regain all expended spell slots when you finish a Long Rest.\n"
            "    * Spellcasting Ability: Wisdom"
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST


class Druidic(Feature):
    def __init__(self):
        super().__init__(name="Druidic", origin="Druid Level 1")
        self._language = GrantLanguage(Language.DRUIDIC)

    def apply(self, ledger_writer: LedgerWriter):
        self._language.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Language", "Druidic, the secret language of Druids"),
                    ("Always prepared", "Speak with Animals"),
                    (
                        "Hidden messages",
                        "You and others who know Druidic spot them automatically. Others spot one with a successful DC 15 Intelligence (Investigation) check, but can't decipher it without magic.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You know Druidic, the secret language of Druids. While learning this ancient tongue, you also unlocked the magic of communicating with animals; you always have the Speak with Animals spell prepared.\n"
            "You can use Druidic to leave hidden messages. You and others who know Druidic automatically spot such a message. Others spot the message's presence with a successful DC 15 Intelligence (Investigation) check but can't decipher it without magic."
        )
        return description


class PrimalOrder(Feature):
    def __init__(self, order: PrimalOrderType = PrimalOrderType.MAGICIAN):
        super().__init__(
            name="Primal Order", origin="Druid Level 1", usage_tags=["buff"]
        )
        self.order = order

    def apply(self, ledger_writer: LedgerWriter):
        # Warden: "...proficiency with Martial weapons and training with Medium armor."
        if self.order == PrimalOrderType.WARDEN:
            GrantWeaponProficiency([WeaponProficiency.MARTIAL]).apply(ledger_writer)
            GrantArmorTraining([ArmorType.MEDIUM]).apply(ledger_writer)
        if self.order != PrimalOrderType.MAGICIAN:
            return

        def bonus(cs: CharacterView) -> int:
            return max(1, cs.get_wisdom_modifier())

        SkillBonus(Skill.ARCANA, bonus).apply(ledger_writer)
        SkillBonus(Skill.NATURE, bonus).apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        if self.order == PrimalOrderType.WARDEN:
            return [
                Paragraph("Warden: trained for battle."),
                Facts(
                    (
                        ("Weapons", "Proficiency with Martial weapons"),
                        ("Armor", "Training with Medium armor"),
                    )
                ),
            ]
        return [
            Paragraph("Magician: a mystical connection to nature."),
            Facts(
                (
                    ("Extra cantrip", "One more cantrip from the Druid spell list"),
                    (
                        "Arcana and Nature",
                        "+ Wisdom modifier (minimum +1) to Intelligence (Arcana or Nature) checks",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        if self.order == PrimalOrderType.WARDEN:
            return (
                "Warden. Trained for battle, you gain proficiency with Martial weapons "
                "and training with Medium armor."
            )
        return (
            "Magician. You know one extra cantrip from the Druid spell list. In addition, "
            "your mystical connection to nature gives you a bonus to your Intelligence "
            "(Arcana or Nature) checks. The bonus equals your Wisdom modifier (minimum bonus of +1)."
        )


class WildShape(Feature):
    def __init__(self, known_forms: list[CreatureForm]):
        super().__init__(
            name="Wild Shape",
            origin="Druid Level 2",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="Until You Leave Form or are Incapacitated",
            ),
            usage_tags=["heal"],
            uses=FeatureUses(
                max_uses=4,
                regain_x_on=(1, "short rest"),
                regain_all_on="long rest",
                current_formula="Current amount: determined by your Druid level — 2 uses at levels 2-5, 3 at 6-16, 4 at 17+.",
                gained_at=[2, 2, 6, 17],
            ),
        )
        self.known_forms = known_forms

    def _rules(self, character: CharacterView) -> dict[str, str]:
        """Wild Shape rules as formulas, so the sheet holds at every Druid level."""
        from CharacterContent.Features.SubClassFeatures.Druid.DruidMoonFeatures import (
            CircleForms,
        )

        if character.has_feature(CircleForms):
            max_cr = "Druid level ÷ 3, rounded down (Circle Forms)"
        else:
            max_cr = "1/4, rising to 1/2 at Druid level 4 and 1 at Druid level 8"
        return {
            "Action": "Bonus Action to transform; Bonus Action to leave the form early",
            "Duration": (
                "Hours equal to half your Druid level; ends early if you use "
                "Wild Shape again, have the Incapacitated condition, or die"
            ),
            "Uses": (
                "2 at Druid level 2, 3 at Druid level 6, 4 at Druid level 17; "
                "regain one on a Short Rest and all on a Long Rest"
            ),
            "Known Forms": (
                "4 Beasts, rising to 6 at Druid level 4 and 8 at Druid level 8; "
                "replace one when you finish a Long Rest"
            ),
            "Max Challenge Rating": max_cr,
            "Fly Speed": "Forms with a Fly Speed allowed from Druid level 8",
            "Temporary Hit Points": (
                f"{wild_shape_temp_hp_formula(character)}, gained when you assume a form"
            ),
            "You Keep": (
                "Your personality, memories, and speech; creature type; Hit Points "
                "and Hit Dice; Intelligence, Wisdom, and Charisma scores; class "
                "features, languages, and feats"
            ),
            "Skills and Saves": (
                "Keep your proficiencies (with your Proficiency Bonus) and gain the "
                "Beast's; use whichever modifier is higher"
            ),
            "Spellcasting": (
                "You can't cast spells, but transforming doesn't break Concentration "
                "or end spells you've already cast"
            ),
            "Objects": (
                "The form's limbs decide what you can handle; your equipment falls, "
                "merges into the form (no effect), or is worn if the DM agrees it fits"
            ),
        }

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses and their recharge are in the panel below. The base rules,
        # so the card reads the same for every Druid: Circle Forms' own card
        # gives its Challenge Rating and Temporary Hit Points, and the stat
        # blocks below already apply them.
        rules = {
            label: text
            for label, text in self._rules(character).items()
            if label != "Uses"
        }
        rules["Max Challenge Rating"] = (
            "1/4, rising to 1/2 at Druid level 4 and 1 at Druid level 8"
        )
        rules["Temporary Hit Points"] = (
            "Equal to your Druid level, gained when you assume a form"
        )
        groups = {
            "Transforming": ("Action", "Duration", "Temporary Hit Points"),
            "Forms": ("Known Forms", "Max Challenge Rating", "Fly Speed"),
            "While shape-shifted": (
                "You Keep",
                "Skills and Saves",
                "Spellcasting",
                "Objects",
            ),
        }
        return [
            Paragraph("Shape-shift into a Beast form you have learned."),
            *(
                Option(name, (Facts(tuple((label, rules[label]) for label in labels)),))
                for name, labels in groups.items()
            ),
            Paragraph("Your known forms:"),
            *(
                StatBlock(format_wild_shape_form(form, character))
                for form in self.known_forms
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        known_forms_lines = "\n".join(
            format_wild_shape_form(form, character) for form in self.known_forms
        )
        rules = "\n".join(
            f"{label}. {text}" for label, text in self._rules(character).items()
        )
        return rules + "\n\nKnown Forms:\n" + known_forms_lines

    def get_original_description(self) -> str:
        """Official 2024 rules text, kept for reference only (not rendered)."""
        return (
            "The power of nature allows you to assume the form of an animal. As a Bonus Action, you shape-shift into a Beast form that you have learned for this feature (see “Known Forms” below). You stay in that form for a number of hours equal to half your Druid level or until you use Wild Shape again, have the Incapacitated condition, or die. You can also leave the form early as a Bonus Action.\n"
            "Number of Uses. You can use Wild Shape. You regain one expended use when you finish a Short Rest, and you regain all expended uses when you finish a Long Rest.\n"
            "You gain additional uses when you reach certain Druid levels, as shown in the Wild Shape column of the Druid Features table.\n"
            "Known Forms. You know four Beast forms for this feature, chosen from among Beast stat blocks that have a maximum Challenge Rating of 1/4 and that lack a Fly Speed (see appendix B for stat block options). The Rat, Riding Horse, Spider, and Wolf are recommended. Whenever you finish a Long Rest, you can replace one of your known forms with another eligible form.\n"
            "When you reach certain Druid levels, your number of known forms and the maximum Challenge Rating for those forms increases, as shown in the Beast Shapes table. In addition, starting at level 8, you can adopt a form that has a Fly Speed.\n"
            "When choosing known forms, you may look in the Monster Manual or elsewhere for eligible Beasts if the Dungeon Master permits you to do so.\n"
            "Rules While Shape-Shifted. While in a form, you retain your personality, memories, and ability to speak, and the following rules apply:\n"
            "Temporary Hit Points. When you assume a Wild Shape form, you gain a number of Temporary Hit Points equal to your Druid level.\n"
            "Game Statistics. Your game statistics are replaced by the Beast's stat block, but you retain your creature type; Hit Points; Hit Point Dice; Intelligence, Wisdom, and Charisma scores; class features; languages; and feats. You also retain your skill and saving throw proficiencies and use your Proficiency Bonus for them, in addition to gaining the proficiencies of the creature. If a skill or saving throw modifier in the Beast's stat block is higher than yours, use the one in the stat block.\n"
            "No Spellcasting. You can't cast spells, but shape-shifting doesn't break your Concentration or otherwise interfere with a spell you've already cast.\n"
            "Objects. Your ability to handle objects is determined by the form's limbs rather than your own. In addition, you choose whether your equipment falls in your space, merges into your new form, or is worn by it. Worn equipment functions as normal, but the DM decides whether it's practical for the new form to wear a piece of equipment based on the creature's size and shape. Your equipment doesn't change size or shape to match the new form, and any equipment that the new form can't wear must either fall to the ground or merge with the form. Equipment that merges with the form has no effect while you're in that form.\n"
        )

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.SHORT_OR_LONG_REST

    def number_of_uses(self, character: CharacterView) -> int:
        druid_level = character.get_class_level(CharacterClass.DRUID)
        if druid_level >= 17:
            return 4
        elif druid_level >= 6:
            return 3
        else:
            return 2

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class AdditionalWildShapeForms(Feature):
    def __init__(self, known_forms: list[CreatureForm], origin: str):
        super().__init__(name="Additional Known Forms", origin=origin)
        self.known_forms = known_forms

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            StatBlock(format_wild_shape_form(form, character))
            for form in self.known_forms
        ]

    def get_description(self, character: CharacterView) -> str:
        return "\n".join(
            format_wild_shape_form(form, character) for form in self.known_forms
        )


class WildCompanion(Feature):
    def __init__(self):
        super().__init__(
            name="Wild Companion",
            origin="Druid Level 2",
            activation=FeatureActivation(
                action_type=ActionType.ACTION, duration="Until Long Rest"
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Summon a nature spirit in an animal form to aid you."),
            Facts(
                (
                    ("Action", "Magic action"),
                    ("Cost", "A spell slot or a use of Wild Shape"),
                    ("Effect", "Cast Find Familiar without Material components"),
                    (
                        "Familiar",
                        "It's Fey, and disappears when you finish a Long Rest",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can summon a nature spirit that assumes an animal form to aid you. As a Magic action, you can expend a spell slot or a use of Wild Shape to cast the Find Familiar spell without Material components.\n"
            "When you cast the spell in this way, the familiar is Fey and disappears when you finish a Long Rest."
        )
        return description


class WildResurgence(Feature):
    def __init__(self):
        super().__init__(name="Wild Resurgence", origin="Druid Level 5")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Trade spell slots and uses of Wild Shape."),
            Option(
                "Spell slot into Wild Shape",
                (
                    Facts(
                        (
                            ("Action", "No action required"),
                            (
                                "Requirement",
                                "You have no uses of Wild Shape left",
                            ),
                            (
                                "Effect",
                                "Expend a spell slot to gain one use of Wild Shape",
                            ),
                            ("Limit", "Once on each of your turns"),
                        )
                    ),
                ),
            ),
            Option(
                "Wild Shape into spell slot",
                (
                    Facts(
                        (
                            ("Action", "No action required"),
                            (
                                "Effect",
                                "Expend one use of Wild Shape to gain a level 1 spell slot",
                            ),
                            ("Limit", "Once per Long Rest"),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Once on each of your turns, if you have no uses of Wild Shape left, you can give yourself one use by expending a spell slot (no action required).\n"
            "In addition, you can expend one use of Wild Shape (no action required) to give yourself a level 1 spell slot, but you can't do so again until you finish a Long Rest."
        )
        return description


class PotentSpellcasting(Feature):
    def __init__(self):
        super().__init__(
            name="Potent Spellcasting", origin="Druid Level 7", usage_tags=["damage"]
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Add your Wisdom modifier to the damage you deal with any Druid cantrip."
        )
        return description


class PrimalStrike(Feature):
    def __init__(self):
        super().__init__(
            name="Primal Strike", origin="Druid Level 7", usage_tags=["damage"]
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "Once on each of your turns, you hit a creature with an attack roll using a weapon or a Beast form's attack in Wild Shape",
                    ),
                    (
                        "Damage",
                        "Extra 1d8 Cold, Fire, Lightning or Thunder damage (choose when you hit)",
                    ),
                    ("From Druid level 15", "2d8 instead (Improved Primal Strike)"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Once on each of your turns when you hit a creature with an attack roll using a weapon or a Beast "
            "form's attack in Wild Shape, you can cause the target to take an extra 1d8 Cold, Fire, Lightning, "
            "or Thunder damage (choose when you hit)."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class ImprovedPotentSpellcasting(Feature):
    def __init__(self):
        super().__init__(name="Improved Potent Spellcasting", origin="Druid Level 15")

    def get_description(self, character: CharacterView) -> str:
        description = "When you cast a Druid cantrip with a range of 10 feet or greater, the spell's range increases by 300 feet."
        return description


class ImprovedPrimalStrike(Feature):
    def __init__(self):
        super().__init__(
            name="Improved Primal Strike",
            origin="Druid Level 15",
            usage_tags=["damage"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = "The extra damage of your Primal Strike increases to 2d8."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class BeastSpells(Feature):
    def __init__(self):
        super().__init__(name="Beast Spells", origin="Druid Level 18")

    def get_description(self, character: CharacterView) -> str:
        description = "While using Wild Shape, you can cast spells in Beast form, except for any spell that has a Material component with a cost specified or that consumes its Material component."
        return description


class Archdruid(Feature):
    def __init__(self):
        super().__init__(
            name="Archdruid",
            origin="Druid Level 20",
            uses=FeatureUses(
                max_uses=1,
                regain_all_on="long rest",
                current_formula="Used by Nature Magician.",
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("The vitality of nature constantly blooms within you."),
            Option(
                "Evergreen Wild Shape",
                (
                    Facts(
                        (
                            (
                                "Trigger",
                                "You roll Initiative and have no uses of Wild Shape left",
                            ),
                            ("Effect", "Regain one expended use of Wild Shape"),
                        )
                    ),
                ),
            ),
            Option(
                "Nature Magician",
                (
                    Facts(
                        (
                            ("Action", "No action required"),
                            (
                                "Convert",
                                "Any number of unexpended Wild Shape uses into one spell slot, each use giving 2 spell levels (two uses make a level 4 slot)",
                            ),
                            ("Limit", "Once per Long Rest (box below)"),
                        )
                    ),
                ),
            ),
            Option(
                "Longevity",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "For every ten years that pass, your body ages only one year",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "The vitality of nature constantly blooms within you, granting you the following benefits.\n"
            "Evergreen Wild Shape. Whenever you roll Initiative and have no uses of Wild Shape left, you regain one expended use of it.\n"
            "Nature Magician. You can convert uses of Wild Shape into a spell slot (no action required). Choose a number of your unexpended uses of Wild Shape and convert them into a single spell slot, with each use contributing 2 spell levels. For example, if you convert two uses of Wild Shape, you produce a level 4 spell slot. Once you use this benefit, you can't do so again until you finish a Long Rest.\n"
            "Longevity. The primal magic that you wield causes you to age more slowly. For every ten years that pass, your body ages only one year."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.INITIATIVE_ROLL
