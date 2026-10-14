from Model.Content.Feature import (
    Feature,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from Model.View import CharacterView
from Model.Content.FeatureText import (
    Block,
    Facts,
    Paragraph,
    dc_formula,
    Option,
)
from Core.Definitions import Ability
from CharacterContent.Features.SubClassFeatures.ThirdCasterSpellcasting import (
    spellcasting_table,
)


class Spellcasting(Feature):
    def __init__(self):
        super().__init__(name="Spellcasting", origin="Arcane Trickster Rogue Level 3")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "You cast Wizard spells, with Intelligence as your spellcasting ability."
            ),
            Facts(
                (
                    ("Save DC", dc_formula(Ability.INTELLIGENCE)),
                    ("Spell attack", "Intelligence modifier + Proficiency Bonus"),
                    ("Focus", "An Arcane Focus"),
                    (
                        "Cantrips",
                        "Mage Hand and two other Wizard cantrips (Mind Sliver and Minor Illusion recommended); another at Rogue level 10. Whenever you gain a Rogue level, replace one other than Mage Hand.",
                    ),
                    (
                        "Prepared spells",
                        "As many as the table shows, of levels you have slots for, from the Wizard list. Start with three level 1 spells (Charm Person, Disguise Self and Fog Cloud recommended). Whenever you gain a Rogue level, replace one.",
                    ),
                    (
                        "Spell slots",
                        "As the table below; regain all when you finish a Long Rest",
                    ),
                )
            ),
            Option("Arcane Trickster Spellcasting", (spellcasting_table("Rogue"),)),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You have learned to cast spells. See chapter 7 for the rules on spellcasting. The information below details how you use those rules as an Arcane Trickster.\n"
            "Cantrips. You know three cantrips: Mage Hand and two other cantrips of your choice from the Wizard spell list (see that class's section for its list). Mind Sliver and Minor Illusion are recommended.\n"
            "Whenever you gain a Rogue level, you can replace one of your cantrips, except Mage Hand, with another Wizard cantrip of your choice.\n"
            "When you reach Rogue level 10, you learn another Wizard cantrip of your choice.\n"
            "Spell Slots. The Arcane Trickster Spellcasting table shows how many spell slots you have to cast your level 1+ spells. You regain all expended spell slots when you finish a Long Rest.\n"
            "Prepared Spells of Level 1+. You prepare a list of the level 1+ spells that are available for you to cast with this feature. To start, choose three level 1 Wizard spells. Charm Person, Disguise Self and Fog Cloud are recommended.\n"
            "The number of spells on your list increases as you gain Rogue levels, as shown in the Prepared Spells column of the Arcane Trickster Spellcasting table. Whenever that number increases, choose additional Wizard spells until the number of spells on your list matches the number in the Arcane Trickster Spellcasting table. The chosen spells must be of a level for which you have spell slots. For example, if you're a level 7 Rogue, your list of prepared spells can include five Wizard spells of level 1 or 2 in any combination.\n"
            "Changing Your Prepared Spells. Whenever you gain a Rogue level, you can replace one spell on your list with another Wizard spell for which you have spell slots.\n"
            "Spellcasting Ability. Intelligence is your Spellcasting ability for your Wizard Spells.\n"
            "Spellcasting Focus. You can use an Arcane Focus as a Spellcasting Focus for your Wizard Spells."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST


class MageHandLegerdemain(Feature):
    def __init__(self):
        super().__init__(
            name="Mage Hand Legerdemain",
            origin="Arcane Trickster Rogue Level 3",
            usage_tags=["utility"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = "When you cast Mage Hand, you can cast it as a Bonus Action, and you can make the spectral hand Invisible. You can control the hand as a Bonus Action, and through it, you can make Dexterity (Sleight of Hand) checks."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.OBJECT


class MagicalAmbush(Feature):
    def __init__(self):
        super().__init__(
            name="Magical Ambush",
            origin="Arcane Trickster Rogue Level 9",
            usage_tags=["buff"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = "If you have the Invisible condition when you cast a spell on a creature, it has Disadvantage on any saving throw it makes against the spell on the same turn."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE


class VersatileTrickster(Feature):
    def __init__(self):
        super().__init__(
            name="Versatile Trickster",
            origin="Arcane Trickster Rogue Level 13",
            activation=FeatureActivation(range="5 Feet"),
            usage_tags=["control"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = "You gain the ability to distract targets with your Mage Hand. When you use the Trip option of your Cunning Strike on a creature, you can also use that option on another creature within 5 feet of the spectral hand."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class SpellThief(Feature):
    def __init__(self):
        super().__init__(
            name="Spell Thief",
            origin="Arcane Trickster Rogue Level 17",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, duration="8 Hours"
            ),
            usage_tags=["buff", "control"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Steal the knowledge of a spell from another spellcaster."),
            Facts(
                (
                    ("Action", "Reaction"),
                    (
                        "Trigger",
                        "Immediately after a creature casts a spell that targets you or includes you in its area",
                    ),
                    (
                        "Save",
                        f"Intelligence save against your spell save DC ({dc_formula(Ability.INTELLIGENCE)})",
                    ),
                    (
                        "Failed",
                        "The spell's effect on you is negated. If it's level 1+ and a level you can cast, you have it prepared for 8 hours and the caster can't cast it for 8 hours.",
                    ),
                    ("Limit", "Once per Long Rest (after you steal a spell)"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain the ability to magically steal the knowledge of how to cast a spell from another spellcaster.\n"
            "Immediately after a creature casts a spell that targets you or includes you in its area of effect, you can take a Reaction to force the creature to make an Intelligence saving throw. The DC equals your spell save DC. On a failed save, you negate the spell's effect against you, and you steal the knowledge of the spell if it is at least level 1 and of a level you can cast (it doesn't need to be a Wizard spell). For the next 8 hours, you have the spell prepared. The creature can't cast it until 8 hours have passed.\n"
            "Once you steal a spell with this feature, you can't use this feature again until you finish a Long Rest."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY
