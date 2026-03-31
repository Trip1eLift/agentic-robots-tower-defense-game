import pytest
from backend.action_parser import ActionParser
from backend.models import MoveAction, AttackAction, BuildAction, RetreatAction, SupportAction


def test_parse_clean_json_move():
    parser = ActionParser()
    raw = '{"action": "move", "destination": "north_chokepoint", "reason": "Blocking"}'
    action = parser.parse(raw)
    assert isinstance(action, MoveAction)
    assert action.destination == "north_chokepoint"


def test_parse_clean_json_attack():
    parser = ActionParser()
    raw = '{"action": "attack", "target_id": 2, "approach": "close_in", "reason": "Enemy close"}'
    action = parser.parse(raw)
    assert isinstance(action, AttackAction)
    assert action.target_id == 2


def test_parse_json_embedded_in_prose():
    parser = ActionParser()
    raw = 'I should move to the chokepoint. {"action": "move", "destination": "west_flank", "reason": "Better angle"} That seems right.'
    action = parser.parse(raw)
    assert isinstance(action, MoveAction)
    assert action.destination == "west_flank"


def test_parse_invalid_json_returns_idle():
    parser = ActionParser()
    raw = "I cannot decide what to do right now."
    action = parser.parse(raw)
    assert isinstance(action, SupportAction)
    assert action.action == "idle"


def test_parse_unknown_action_returns_idle():
    parser = ActionParser()
    raw = '{"action": "dance", "destination": "north"}'
    action = parser.parse(raw)
    assert isinstance(action, SupportAction)
    assert action.action == "idle"


def test_parse_build_action():
    parser = ActionParser()
    raw = '{"action": "build", "structure": "wall", "destination": "north_chokepoint", "reason": "Creating barrier"}'
    action = parser.parse(raw)
    assert isinstance(action, BuildAction)
    assert action.structure == "wall"


def test_parse_retreat_action():
    parser = ActionParser()
    raw = '{"action": "retreat", "destination": "rear_support", "reason": "Low health"}'
    action = parser.parse(raw)
    assert isinstance(action, RetreatAction)
