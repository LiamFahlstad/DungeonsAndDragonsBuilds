from Core.Definitions import (
    FIGHTER_HIT_DIE,
    Ability,
)
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
    Option,
    dc_formula,
)
from CharacterContent.Features.SubClassFeatures.ThirdCasterSpellcasting import (
    spellcasting_table,
)


class EldritchKnightSpellcasting(Feature):
    def __init__(self):
        super().__init__(name="Spellcasting", origin="Eldritch Knight Fighter Level 3")

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
                        "Two Wizard cantrips (Ray of Frost and Shocking Grasp recommended); a third at Fighter level 10. Whenever you gain a Fighter level, replace one.",
                    ),
                    (
                        "Prepared spells",
                        "As many as the table shows, of levels you have slots for, from the Wizard list. Start with three level 1 spells (Burning Hands, Jump and Shield recommended). Whenever you gain a Fighter level, replace one.",
                    ),
                    (
                        "Spell slots",
                        "As the table below; regain all when you finish a Long Rest",
                    ),
                )
            ),
            Option("Eldritch Knight Spellcasting", (spellcasting_table("Fighter"),)),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You have learned to cast spells. See chapter 7 for the rules on spellcasting. The information below details how you use those rules as an Eldritch Knight.\n"
            "Cantrips. You know two cantrips of your choice from the Wizard spell list. Ray of Frost and Shocking Grasp are recommended. Whenever you gain a Fighter level, you can replace one of these cantrips with another cantrip of your choice from the Wizard spell list.\n"
            "When you reach Fighter level 10, you learn another Wizard cantrip of your choice.\n"
            "Spell Slots. You regain all expended spell slots when you finish a Long Rest.\n"
            "Prepared Spells of Level 1+. You prepare the list of level 1+ spells that are available for you to cast with this feature. To start, choose three level 1 spells from the Wizard spell list. Burning Hands, Jump, and Shield are recommended.\n"
            "The number of spells on your list increases as you gain Fighter levels, as shown in the Prepared Spells column of the Eldritch Knight Spellcasting table. Whenever that number increases, choose additional spells from the Wizard spell list until the number of spells on your list matches the number on the table. The chosen spells must be of a level for which you have spell slots. For example, if you're a level 7 Fighter, your list of prepared spells can include five Wizard spells of levels 1 and 2 in any combination.\n"
            "Changing Your Prepared Spells. Whenever you gain a Fighter level, you can replace one spell on your list with another Wizard spell for which you have spell slots.\n"
            "Spellcasting Ability. Intelligence is your spellcasting ability for your Wizard spells.\n"
            "Spellcasting Focus. You can use an Arcane Focus as a Spellcasting Focus for your Wizard spells"
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST


class WarBond(Feature):
    def __init__(self):
        super().__init__(
            name="War Bond",
            origin="Eldritch Knight Fighter Level 3",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION),
            usage_tags=["utility"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.OBJECT

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Bond with up to two weapons."),
            Facts(
                (
                    (
                        "Ritual",
                        "1 hour (can be during a Short Rest), with the weapon in reach, then touch it. Fails if another Fighter is bonded to it or someone else is attuned to it.",
                    ),
                    (
                        "Can't be disarmed",
                        "Of a bonded weapon, unless you're Incapacitated",
                    ),
                    (
                        "Summon",
                        "Bonus Action: a bonded weapon on the same plane teleports to your hand (one at a time)",
                    ),
                    (
                        "Limit",
                        "Two bonded weapons; bonding a third breaks one of the others",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You learn a ritual that creates a magical bond between yourself and one weapon. You perform the ritual over the course of 1 hour, which can be done during a Short Rest. The weapon must be within your reach throughout the ritual, at the conclusion of which you touch the weapon and forge the bond. The bond fails if another Fighter is bonded to the weapon or if the weapon is a magic item to which someone else is attuned.\n"
            "Once you have bonded a weapon to yourself, you can't be disarmed of that weapon unless you have the Incapacitated condition. If it is on the same plane of existence, you can summon that weapon as a Bonus Action, causing it to teleport instantly to your hand.\n"
            "You can have up to two bonded weapons, but you can summon only one at a time with a Bonus Action. If you attempt to bond with a third weapon, you must break the bond with one of the other two."
        )
        return description


class WarMagic(Feature):
    def __init__(self):
        super().__init__(name="War Magic", origin="Eldritch Knight Fighter Level 7")

    def get_description(self, character: CharacterView) -> str:
        description = "When you take the Attack action on your turn, you can replace one of the attacks with a casting of one of your Wizard cantrips that has a casting time of an action."
        return description


class EldritchStrike(Feature):
    def __init__(self):
        super().__init__(
            name="Eldritch Strike",
            origin="Eldritch Knight Fighter Level 10",
            usage_tags=["control"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def get_description(self, character: CharacterView) -> str:
        description = "You learn how to make your weapon strikes undercut a creature's ability to withstand your spells. When you hit a creature with an attack using a weapon, that creature has Disadvantage on the next saving throw it makes against a spell you cast before the end of your next turn."
        return description


class ArcaneCharge(Feature):
    def __init__(self):
        super().__init__(
            name="Arcane Charge",
            origin="Eldritch Knight Fighter Level 15",
            activation=FeatureActivation(range="30 Feet"),
            usage_tags=["utility"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_description(self, character: CharacterView) -> str:
        description = "When you use your Action Surge, you can teleport up to 30 feet to an unoccupied space you can see. You can teleport before or after the additional action."
        return description


class ImprovedWarMagic(Feature):
    def __init__(self):
        super().__init__(
            name="Improved War Magic", origin="Eldritch Knight Fighter Level 18"
        )

    def get_description(self, character: CharacterView) -> str:
        description = "When you take the Attack action on your turn, you can replace two of the attacks with a casting of one of your level 1 or level 2 Wizard spells that has a casting time of an action."
        return description
