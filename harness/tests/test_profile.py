"""Tests for the per-turn context-composition profiler.

The properties worth testing are the ones the list itself cares about: a turn is
one checkpoint, deltas are between checkpoints, a profiler that breaks on an
unknown field measures nothing, and the flags name the failure the entry
describes rather than a generic warning.
"""

from __future__ import annotations

import json

from token_harness import profile as profiler


def _checkpoint(prompt, cache_read, cache_write, tool_tokens, tool_calls, segments):
    return {
        "type": "session.usage_checkpoint",
        "data": {
            "promptCacheBreakState": [
                {
                    "models": {
                        "mai-code-1.1-flash": {
                            "prompt_tokens": prompt,
                            "cache_read": cache_read,
                            "cache_write": cache_write,
                            "tool_tokens": tool_tokens,
                            "tool_count": tool_calls,
                            "system_segments": [
                                {"segment": name, "tokens": tokens}
                                for name, tokens in segments.items()
                            ],
                        }
                    }
                }
            ]
        },
    }


SESSION = "\n".join(
    [
        json.dumps({"type": "assistant.message", "data": {"content": "hi"}}),
        json.dumps(
            _checkpoint(
                17_549,
                8_704,
                1_200,
                8_521,
                23,
                {"tool_instructions": 7_101, "identity": 503, "custom_instructions": 797},
            )
        ),
        json.dumps(
            _checkpoint(
                21_000,
                17_000,
                1_300,
                8_521,
                23,
                {"tool_instructions": 7_101, "identity": 503, "custom_instructions": 797},
            )
        ),
        # A turn with a field the reader has never seen. Must not be fatal.
        json.dumps(
            {
                "type": "session.usage_checkpoint",
                "data": {
                    "promptCacheBreakState": [
                        {"models": {"gpt-next": {"prompt_tokens": 22_000, "brand_new_field": 7}}}
                    ]
                },
            }
        ),
        json.dumps({"type": "result", "exitCode": 0}),
    ]
)


def test_each_checkpoint_is_a_turn():
    profile = profiler.parse_events(SESSION, source="fixture")
    assert len(profile.turns) == 3
    assert [t.prompt_tokens for t in profile.turns] == [17_549, 21_000, 22_000]


def test_deltas_are_between_checkpoints():
    profile = profiler.parse_events(SESSION, source="fixture")
    assert profile.growth == [17_549, 3_451, 1_000]


def test_segments_and_shares_come_from_the_final_turn():
    profile = profiler.parse_events(SESSION, source="fixture")
    final = profile.final
    assert final.segments == {}
    assert final.tool_share == 0.0  # unknown fields default to zero, not to a guess


def test_fixed_overhead_sums_segments():
    profile = profiler.parse_events(SESSION, source="fixture")
    assert profile.turns[0].fixed_overhead == 7_101 + 503 + 797


def test_unknown_fields_are_tolerated():
    """A profiler that dies on a CLI bump measures nothing."""
    profile = profiler.parse_events(SESSION, source="fixture")
    assert "no session.usage_checkpoint events found" not in profile.warnings
    assert profile.turns[-1].prompt_tokens == 22_000


def test_empty_and_malformed_input():
    empty = profiler.parse_events("", source="empty")
    assert empty.turns == []
    assert empty.warnings == ["empty input"]

    junk = profiler.parse_events("not json\n{still not}", source="junk")
    assert junk.turns == []
    assert any("no session.usage_checkpoint" in w for w in junk.warnings)


def test_flags_name_what_is_actually_wrong():
    lines = [
        json.dumps(
            _checkpoint(10_000, 0, 100, 9_000, 0, {"identity": 100})
        )
    ]
    profile = profiler.parse_events("\n".join(lines))
    flags = profile.flags()
    joined = " ".join(flags)
    assert "schemas_loaded_unused" in joined
    assert "tool_share_high" in joined
    assert "cache_cold" in joined


def test_no_growth_turn_is_flagged_as_rebilling():
    lines = [
        json.dumps(_checkpoint(5_000, 4_000, 100, 1_000, 2, {"identity": 50})),
        json.dumps(_checkpoint(5_000, 4_000, 100, 1_000, 2, {"identity": 50})),
    ]
    profile = profiler.parse_events("\n".join(lines))
    assert any("no_growth_turns" in f for f in profile.flags())


def test_provenance_is_stamped():
    profile = profiler.parse_events(SESSION, source="fixture")
    prov = profile.provenance()
    assert prov["n_turns"] == 3
    assert prov["model"] == "gpt-next"
    assert prov["date"]
    assert prov["harness"] == "token-harness profile"


def test_json_and_table_formats_render():
    profile = profiler.parse_events(SESSION, source="fixture")
    payload = json.loads(profiler.format_json(profile))
    assert payload["final_turn"]["prompt_tokens"] == 22_000
    table = profiler.format_table(profile)
    assert "Context composition" in table
    assert "turn" in table
