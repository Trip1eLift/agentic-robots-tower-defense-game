import re
import pytest
from backend.prompt_builder import PromptBuilder
from backend.models import EventType, LocalContext, RobotEvent


def _make_event(event_type=EventType.ENEMY_SPOTTED, player_instructions="Hold north.", intelligence=5):
    return RobotEvent(
        robot_id="architect_common_hana",
        event_type=event_type,
        event_detail="zombie spotted at north_chokepoint",
        local_context=LocalContext(
            nearby_enemies=[{"id": 1, "type": "zombie", "position": [512, 200], "health": 50}],
            nearby_allies=[{"id": "vanguard_common_rex", "health": 200, "position": [512, 420]}],
            structures=[],
            recent_events=["ENEMY_SPOTTED: zombie at north"],
            strategic_positions=[
                {"id": "north_chokepoint", "description": "Narrow gap on north path", "position": [512, 200]},
                {"id": "rear_support", "description": "Safe rear position", "position": [512, 460]}
            ]
        ),
        player_instructions=player_instructions,
    )


ROBOT_CONFIG = {
    "name": "Hana",
    "class": "architect",
    "rarity": "common",
    "personality_prompt": "You are Hana, a methodical Architect.",
    "base_stats": {"speed": 4, "damage": 3, "armor": 5, "health": 100, "ammo": 40, "building_skill": 7, "intelligence": 5}
}

ROBOT_RUNTIME_STATS = {"health": 80, "ammo": 35}


def test_prompt_contains_personality():
    builder = PromptBuilder()
    prompt = builder.build(ROBOT_CONFIG, ROBOT_RUNTIME_STATS, _make_event())
    assert "You are Hana, a methodical Architect" in prompt


def test_prompt_contains_event():
    builder = PromptBuilder()
    prompt = builder.build(ROBOT_CONFIG, ROBOT_RUNTIME_STATS, _make_event())
    assert "ENEMY_SPOTTED" in prompt
    assert "zombie spotted at north_chokepoint" in prompt


def test_prompt_contains_strategic_positions():
    builder = PromptBuilder()
    prompt = builder.build(ROBOT_CONFIG, ROBOT_RUNTIME_STATS, _make_event())
    assert "north_chokepoint" in prompt
    assert "rear_support" in prompt


def test_intelligence_truncates_player_instructions():
    long_instructions = "x" * 1000
    builder = PromptBuilder()
    prompt = builder.build(ROBOT_CONFIG, ROBOT_RUNTIME_STATS, _make_event(player_instructions=long_instructions))
    match = re.search(r"\[Player Instructions\]\n(.*?)(\n\n|\n\[)", prompt, re.DOTALL)
    assert match is not None, "Player Instructions section not found in prompt"
    instructions_section = match.group(1).strip()
    assert len(instructions_section) == 500, (
        f"Expected 500 chars but got {len(instructions_section)}"
    )
    assert instructions_section == "x" * 500


def test_prompt_contains_commander_broadcast():
    event = _make_event()
    event.commander_broadcast = "Fall back to base!"
    builder = PromptBuilder()
    prompt = builder.build(ROBOT_CONFIG, ROBOT_RUNTIME_STATS, event)
    assert "Fall back to base!" in prompt


def test_prompt_ends_with_json_instruction():
    builder = PromptBuilder()
    prompt = builder.build(ROBOT_CONFIG, ROBOT_RUNTIME_STATS, _make_event())
    assert "You MUST respond with ONLY a JSON object" in prompt


def test_prompt_includes_build_actions():
    builder = PromptBuilder()
    prompt = builder.build(ROBOT_CONFIG, ROBOT_RUNTIME_STATS, _make_event())
    assert "build" in prompt
    assert "deploy_turret" in prompt
    assert '"structure": "wall"' in prompt


def test_prompt_commander_broadcast_none():
    builder = PromptBuilder()
    prompt = builder.build(ROBOT_CONFIG, ROBOT_RUNTIME_STATS, _make_event())
    assert "Commander broadcast: None" in prompt


def test_prompt_empty_recent_events():
    event = _make_event()
    event.local_context.recent_events = []
    builder = PromptBuilder()
    prompt = builder.build(ROBOT_CONFIG, ROBOT_RUNTIME_STATS, event)
    assert "Recent events:\nNone" in prompt
