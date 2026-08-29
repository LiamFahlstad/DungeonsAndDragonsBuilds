import Core.Definitions as Definitions
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureUses, FeatureActivation
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class Spellcasting(Feature):
    def __init__(self):
        super().__init__(name="Spellcasting", origin="Sorcerer Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Spellcasting\n"
            "    * Replacing Cantrips: Change one when you gain a Sorcerer level.\n"
            "    * Replacing Spells: Change one whenever you gain a Sorcerer level.\n"
            "    * Regaining Spell Slots: You regain all expended spell slots when you finish a Long Rest.\n"
            "    * Spellcasting Ability: Charisma"
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Replacing Cantrips", "Change one when you gain a Sorcerer level"),
            ("Replacing Spells", "Change one when you gain a Sorcerer level"),
            ("Regaining Spell Slots", "All expended slots return on Long Rest"),
            ("Spellcasting Ability", "Charisma"),
        ]


class InnateSorcery(Feature):
    def __init__(self):
        super().__init__(
            name="Innate Sorcery",
            origin="Sorcerer Level 1",
            activation=FeatureActivation(action_type="bonus_action", duration="1 Minute"),
            usage_tags=["buff"],
            uses=FeatureUses(max_uses=2, regain_all_on="long rest"),
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "An event in your past left an indelible mark on you, infusing you with simmering magic. As a Bonus Action, you can unleash that magic for 1 minute, during which you gain the following benefits:\n"
            "The spell save DC of your Sorcerer spells increases by 1.\n"
            "You have Advantage on the attack rolls of Sorcerer spells you cast.\n"
            "You can use this feature twice, and you regain all expended uses of it when you finish a Long Rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Activation", "Bonus Action"),
            ("Duration", "1 minute"),
            ("Uses", "2 (regain on Long Rest)"),
            ("Effect", "Spell save DC +1; Advantage on Sorcerer spell attack rolls"),
        ]


class FontOfMagic(Feature):
    def __init__(self):
        super().__init__(
            name="Font of Magic",
            origin="Sorcerer Level 2",
            uses=FeatureUses(
                max_uses=20,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Sorcerer level.",
            ),
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Rules for Sorcery Points:\n"
            "    * You regain all expended Sorcery Points when you finish a Long Rest.\n"
            "    * Using Sorcery Points: You can use your Sorcery Points to fuel the options below, along with other features, such as Metamagic, that use those points.\n"
            "    * Converting Spell Slots to Sorcery Points: You can expend a spell slot to gain a number of Sorcery Points equal to the slot's level (no action required).\n"
            "    * Creating Spell Slots: As a Bonus Action, you can transform unexpended Sorcery Points into one spell slot. The Creating Spell Slots table shows the cost of creating a spell slot of a given level, and it lists the minimum Sorcerer level you must be to create a slot. Any spell slot you create with this feature vanishes when you finish a Long Rest.\n"
            "   Spell Slot Level | Sorcery Point Cost | Minimum Sorcerer Level\n"
            "   -----------------|--------------------|-----------------------\n"
            "           1        |         2          |           2           \n"
            "           2        |         3          |           3           \n"
            "           3        |         5          |           5           \n"
            "           4        |         6          |           7           \n"
            "           5        |         7          |           9           "
        )
        return description

    def get_resource_tiles(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, list[tuple[str, str]]]]:
        points_by_level = {level: str(level) for level in range(2, 21)}
        steps = [
            (f"Lv {level_range}", value)
            for level_range, value in StringUtils.compress_level_progression(
                points_by_level
            )
        ]
        return [("Sorcery Points", steps)]


class Metamagic(Feature):
    def __init__(self):
        super().__init__(name="Metamagic", origin="Sorcerer Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        sorcerer_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.SORCERER
        )
        if sorcerer_level < 10:
            metamaagic_options = 2
        elif sorcerer_level < 17:
            metamaagic_options = 4
        else:
            metamaagic_options = 6
        description = (
            f"Because your magic flows from within, you can alter your spells to suit your needs; You have {metamaagic_options} options to temporarily modify spells you cast. To use an option, you must spend the number of Sorcery Points that it costs.\n"
            "You can use only one Metamagic option on a spell when you cast it unless otherwise noted in one of those options.\n"
            "Whenever you gain a Sorcerer level, you can replace one of your Metamagic options with one you don't know. You gain two more options at Sorcerer level 10 and two more at Sorcerer level 17."
        )
        return description

    def get_resource_tiles(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, list[tuple[str, str]]]]:
        options_by_level = {}
        for level in range(2, 21):
            if level < 10:
                options_by_level[level] = 2
            elif level < 17:
                options_by_level[level] = 4
            else:
                options_by_level[level] = 6
        steps = [
            (f"Lv {level_range}", str(value))
            for level_range, value in StringUtils.compress_level_progression(
                options_by_level
            )
        ]
        return [("Metamagic Options Known", steps)]

    def get_concise_description(self, character_stat_block: CharacterStatBlock) -> str:
        sorcerer_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.SORCERER
        )
        if sorcerer_level < 10:
            metamagic_options = 2
        elif sorcerer_level < 17:
            metamagic_options = 4
        else:
            metamagic_options = 6
        return (
            f"You know {metamagic_options} Metamagic options to modify spells by spending Sorcery Points. "
            f"Use only one per spell cast (unless noted otherwise). Replace one option at each level up; "
            f"gain 2 more at level 10 and 2 more at level 17."
        )


class SorcerousRestoration(Feature):
    def __init__(self):
        super().__init__(name="Sorcerous Restoration", origin="Sorcerer Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you finish a Short Rest, you can regain expended Sorcery Points, but no more than a number equal to half your Sorcerer level (round down). Once you use this feature, you can't do so again until you finish a Long Rest."
        return description


class SorceryIncarnate(Feature):
    def __init__(self):
        super().__init__(
            name="Sorcery Incarnate", origin="Sorcerer Level 7", usage_tags=["buff"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "If you have no uses of Innate Sorcery left, you can use it if you spend 2 Sorcery Points when you take the Bonus Action to activate it.\n"
            "In addition, while your Innate Sorcery feature is active, you can use up to two of your Metamagic options on each spell you cast."
        )
        return description


class ArcaneApotheosis(Feature):
    def __init__(self):
        super().__init__(
            name="Arcane Apotheosis", origin="Sorcerer Level 20", usage_tags=["buff"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "While your Innate Sorcery feature is active, you can use one Metamagic option on each of your turns without spending Sorcery Points on it."
        return description
