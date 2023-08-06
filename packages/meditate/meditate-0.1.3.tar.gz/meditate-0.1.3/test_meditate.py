"""Test meditate."""

from hypothesis import given, reject
from hypothesis.strategies import integers, none, one_of
import hypothesis.strategies

import meditate


def maybe_integers():
    return one_of(none(), integers())


@given(
    maybe_integers(),
    maybe_integers(),
    maybe_integers(),
)
def test_parse_duration_input(
        hours,
        minutes,
        seconds,
):
    """Assert time input parsing is correct."""
    wanted_seconds = 0
    input_str = ""
    if hours is None:
        hours = 0
    if minutes is None:
        minutes = 0
    if seconds is None:
        seconds = 0

    input_str += f"{hours}h"
    input_str += f"{minutes}m"
    input_str += f"{seconds}s"

    total_seconds = (
        60.0 * 60 * hours +
        60 * minutes +
        seconds
    )

    try:
        assert meditate.parse_duration_input(
            input_str=input_str,
        ) == total_seconds
    except meditate.DurationConfigurationException as e:
        reject()
