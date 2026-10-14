"""
FeatureDice (Model/Content/Feature.py): a feature's dice progression over
levels, shown on its card as the whole track of steps.
"""

import io

import pytest

from CharacterContent.Features.ClassFeatures.Monk import MonkFeatures
from CharacterContent.Features.ClassFeatures.Rogue import RogueFeatures
from Core.Definitions import CharacterClass
from Model.ClassLevels import ClassLevels
from Model.Content.Feature import Feature, FeatureDice
from Presentation.FeatureCards import write_feature_card
from tests._fake_view import FakeView
from tests._snapshot_helpers import ALL_BUILDS


def _view(character_class: CharacterClass, level: int) -> FakeView:
    return FakeView(
        class_levels=ClassLevels(
            base_class=character_class, level_per_class={character_class: level}
        )
    )


MARTIAL_ARTS = FeatureDice(
    "Martial Arts Die",
    ((1, "1d6"), (5, "1d8"), (11, "1d10"), (17, "1d12")),
    CharacterClass.MONK,
)


class TestProgression:
    def test_steps_cover_every_level_to_20(self):
        assert MARTIAL_ARTS.steps() == [
            ("1-4", "1d6"),
            ("5-10", "1d8"),
            ("11-16", "1d10"),
            ("17-20", "1d12"),
        ]

    def test_a_step_gained_at_20_is_a_single_level(self):
        dice = FeatureDice("Sea", ((3, "1d6"), (20, "4d6")))
        assert dice.steps() == [("3-19", "1d6"), ("20", "4d6")]

    @pytest.mark.parametrize(
        "level, expected",
        [(1, "1d6"), (4, "1d6"), (5, "1d8"), (16, "1d10"), (17, "1d12"), (20, "1d12")],
    )
    def test_at_level(self, level, expected):
        assert MARTIAL_ARTS.at_level(level) == expected

    def test_at_reads_the_class_level(self):
        assert MARTIAL_ARTS.at(_view(CharacterClass.MONK, 11)) == "1d10"

    def test_at_reads_character_level_without_a_class(self):
        breath = FeatureDice("Breath", ((1, "1d10"), (5, "2d10")))
        view = FakeView(
            class_levels=ClassLevels(
                base_class=CharacterClass.FIGHTER,
                level_per_class={CharacterClass.FIGHTER: 3, CharacterClass.WIZARD: 2},
            )
        )
        assert breath.at(view) == "2d10"
        assert breath.level_basis == "character level"

    def test_from_function_keeps_only_the_changes(self):
        sneak = FeatureDice.from_function(
            "Sneak Attack", lambda level: f"{(level + 1) // 2}d6"
        )
        assert sneak.progression[:3] == ((1, "1d6"), (3, "2d6"), (5, "3d6"))
        assert sneak.at_level(20) == "10d6"

    @pytest.mark.parametrize(
        "progression",
        [
            (),
            ((5, "1d8"), (1, "1d6")),
            ((1, "1d6"), (1, "1d8")),
            ((0, "1d6"),),
            ((21, "1d6"),),
        ],
    )
    def test_bad_progressions_are_rejected(self, progression):
        with pytest.raises(ValueError):
            FeatureDice("Bad", progression)

    def test_a_feature_takes_one_or_several(self):
        assert Feature(dice=MARTIAL_ARTS).dice == [MARTIAL_ARTS]
        assert Feature(dice=[MARTIAL_ARTS, MARTIAL_ARTS]).dice == [MARTIAL_ARTS] * 2
        assert Feature().dice == []


class TestCard:
    def _card(self, name: str, feature_type: type) -> str:
        character = ALL_BUILDS[name]().build()
        feature = next(f for f in character.features if isinstance(f, feature_type))
        out = io.StringIO()
        write_feature_card(feature, character, out)
        return out.getvalue()

    def test_the_card_shows_the_whole_progression(self):
        name = next(n for n in ALL_BUILDS if "Monk" in n)
        html = self._card(name, MonkFeatures.MartialArts)
        assert "Martial Arts Die" in html
        assert "by Monk level" in html
        for levels, dice in MonkFeatures.MARTIAL_ARTS_DIE.steps():
            assert f"<span class='feature-track-value'>{dice}</span>" in html
            assert f"<span class='feature-track-levels'>Lv {levels}</span>" in html

    def test_uses_and_dice_sit_together_in_one_labelled_panel(self):
        name = next(n for n in ALL_BUILDS if "BattleMaster" in n)
        from CharacterContent.Features.SubClassFeatures.Fighter import (
            FighterBattleMasterFeatures,
        )

        html = self._card(name, FighterBattleMasterFeatures.SuperiorityDice)
        start = html.index("<div class='feature-stats'>")
        panel = html[start : html.index("<div class='feature-upgrade'>", start)]
        uses_at = panel.index("<span class='feature-stat-label'>Uses</span>")
        dice_at = panel.index("<span class='feature-stat-label'>Dice</span>")
        assert uses_at < dice_at
        assert "slot-box" in panel[uses_at:dice_at]
        assert "Superiority Die" in panel[dice_at:]
        # The panel comes after the description text.
        assert html.index("fuel your maneuvers") < html.index("feature-stats")

    def test_resource_tiles_render_as_a_scaling_row(self):
        name = next(n for n in ALL_BUILDS if "Barbarian" in n)
        from CharacterContent.Features.ClassFeatures.Barbarian import (
            BarbarianFeatures,
        )

        html = self._card(name, BarbarianFeatures.Rage)
        assert "<span class='feature-stat-label'>Scaling</span>" in html
        assert "Rage Damage" in html

    def test_sneak_attack_track_has_ten_steps(self):
        name = next(n for n in ALL_BUILDS if "Rogue" in n)
        html = self._card(name, RogueFeatures.SneakAttack)
        assert html.count("class='feature-track-step'") == 10


def test_every_granted_feature_dice_matches_its_class_levels():
    """A FeatureDice keyed on a class should only appear on features that
    class grants - catches a constant pasted with the wrong class."""
    for name, builder in ALL_BUILDS.items():
        character = builder().build()
        for feature in character.iter_features_with_extensions():
            for dice in feature.dice:
                if dice.scales_with is not None:
                    assert character.get_class_level(dice.scales_with) > 0, (
                        f"{name}: {feature.name}'s {dice.label} scales with "
                        f"{dice.scales_with.value} level, which the build lacks"
                    )


class TestHeaderTags:
    """Header tag chips (action, duration, range, save DC, usage roles) are
    opt-in (RunCharacterCreator.py --feature-tags); Passive always shows."""

    def _card(self, show_tags: bool) -> str:
        from CharacterContent.Features.SubClassFeatures.Fighter import (
            FighterBattleMasterFeatures,
        )

        name = next(n for n in ALL_BUILDS if "BattleMaster" in n)
        character = ALL_BUILDS[name]().build()
        feature = next(
            f
            for f in character.features
            if isinstance(f, FighterBattleMasterFeatures.SuperiorityDice)
        )
        out = io.StringIO()
        write_feature_card(feature, character, out, show_tags=show_tags)
        return out.getvalue()

    def test_tags_are_hidden_by_default(self):
        html = self._card(show_tags=False)
        for chip in ("feature-dc-tag", "feature-usage-tag", "feature-duration-tag"):
            assert chip not in html

    def test_tags_show_with_the_flag(self):
        html = self._card(show_tags=True)
        assert "feature-dc-tag" in html
        assert "feature-usage-tag" in html

    def test_passive_tag_is_kept_without_the_flag(self):
        name = next(n for n in ALL_BUILDS if "Rogue" in n)
        character = ALL_BUILDS[name]().build()
        feature = next(f for f in character.features if f.passive)
        out = io.StringIO()
        write_feature_card(feature, character, out)
        assert "feature-passive-tag" in out.getvalue()
