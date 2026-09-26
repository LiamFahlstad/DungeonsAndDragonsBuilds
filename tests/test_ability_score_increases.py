"""
Ability score increases: ASI, +1 general feats, 2024 background bonus, and the
level-20 capstones. Limits come from the 2024 PHB rule text:
- ASI: +2 to one score or +1 to two, "can't increase above 20".
- Half-feats: "+1, to a maximum of 20".
- Background: "+2 to one and +1 to another, or +1 to all three"; none above 20.
- Primal Champion / Body and Mind: "+4 ... maximum for those scores is 25".
"""

import pytest

from CharacterContent.Features.CharacterFeats import Backgrounds, GeneralFeats
from CharacterContent.Features.ClassFeatures.Barbarian.BarbarianFeatures import (
    PrimalChampion,
)
from CharacterContent.Features.ClassFeatures.Monk.MonkFeatures import BodyAndMind
from Core.Definitions import Ability

STR, DEX, CON, WIS, CHA = (
    Ability.STRENGTH,
    Ability.DEXTERITY,
    Ability.CONSTITUTION,
    Ability.WISDOM,
    Ability.CHARISMA,
)


class TestAbilityScoreImprovement:
    def test_plus_two_to_one(self, make_character):
        character = make_character(strength=16)
        GeneralFeats.AbilityScoreImprovement([(STR, 2)]).apply(character)
        assert character.get_ability_score(STR) == 18

    def test_plus_one_to_two(self, make_character):
        character = make_character(strength=15, constitution=13)
        GeneralFeats.AbilityScoreImprovement([(STR, 1), (CON, 1)]).apply(character)
        assert character.get_ability_score(STR) == 16
        assert character.get_ability_score(CON) == 14

    def test_capped_at_20(self, make_character):
        character = make_character(strength=19)
        GeneralFeats.AbilityScoreImprovement([(STR, 2)]).apply(character)
        assert character.get_ability_score(STR) == 20

    def test_no_effect_at_20(self, make_character):
        character = make_character(strength=20)
        GeneralFeats.AbilityScoreImprovement([(STR, 2)]).apply(character)
        assert character.get_ability_score(STR) == 20

    def test_does_not_lower_score_already_above_20(self, make_character):
        character = make_character(strength=22)
        GeneralFeats.AbilityScoreImprovement([(STR, 2)]).apply(character)
        assert character.get_ability_score(STR) == 22

    @pytest.mark.parametrize(
        "bonuses",
        [
            [(STR, 3)],
            [(STR, 1)],
            [(STR, 3), (DEX, -1)],
            [(STR, 1), (DEX, 1), (CON, 1)],
        ],
        ids=["plus3", "only1", "negative", "three_abilities"],
    )
    def test_invalid_choices_rejected(self, bonuses):
        with pytest.raises(ValueError):
            GeneralFeats.AbilityScoreImprovement(bonuses)


class TestHalfFeat:
    def test_plus_one(self, make_character):
        character = make_character(charisma=15)
        GeneralFeats.Actor(character_level=4, ability=CHA).apply(character)
        assert character.get_ability_score(CHA) == 16

    def test_capped_at_20(self, make_character):
        character = make_character(charisma=20)
        GeneralFeats.Actor(character_level=4, ability=CHA).apply(character)
        assert character.get_ability_score(CHA) == 20

    def test_level_prerequisite(self):
        with pytest.raises(ValueError):
            GeneralFeats.Actor(character_level=3, ability=CHA)

    def test_wrong_ability_rejected(self):
        with pytest.raises(ValueError):
            GeneralFeats.Actor(character_level=4, ability=STR)


class TestBackgroundBonus:
    @pytest.mark.parametrize(
        "bonuses",
        [[(STR, 2), (CON, 1)], [(STR, 1), (DEX, 1), (CON, 1)]],
        ids=["two_one", "one_one_one"],
    )
    def test_valid_splits(self, make_character, bonuses):
        character = make_character()
        Backgrounds.FreeBackgroundAbilityBonus(bonuses).apply(character)
        assert sum(character.get_ability_score(a) - 10 for a in Ability) == 3

    @pytest.mark.parametrize(
        "bonuses",
        [[(STR, 3)], [(STR, 2), (STR, 1)], [(STR, 2)], [(STR, 4), (DEX, -1)]],
        ids=["plus3", "plus3_split", "total2", "negative"],
    )
    def test_invalid_splits_rejected(self, bonuses):
        with pytest.raises(ValueError):
            Backgrounds.FreeBackgroundAbilityBonus(bonuses)


class TestCapstones:
    def test_primal_champion_plus_four(self, make_character):
        character = make_character(strength=20, constitution=18)
        PrimalChampion().apply(character)
        assert character.get_ability_score(STR) == 24
        assert character.get_ability_score(CON) == 22

    def test_primal_champion_max_25(self, make_character):
        character = make_character(strength=23)
        PrimalChampion().apply(character)
        assert character.get_ability_score(STR) == 25

    def test_body_and_mind_max_25(self, make_character):
        character = make_character(dexterity=22, wisdom=20)
        BodyAndMind().apply(character)
        assert character.get_ability_score(DEX) == 25
        assert character.get_ability_score(WIS) == 24
