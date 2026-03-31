import pytest
from pydantic import ValidationError
from backend.models import (
    EventType, RobotEvent, MoveAction, AttackAction,
    BuildAction, RetreatAction, SupportAction, parse_robot_action,
    WsIncoming, WsOutgoing,
)


def test_robot_event_valid():
    event = RobotEvent(
        robot_id="architect_common_hana",
        event_type=EventType.ENEMY_SPOTTED,
        event_detail="zombie at position (200, 150)",
        local_context={
            "nearby_enemies": [{"id": 1, "type": "zombie", "position": [200, 150], "health": 50}],
            "nearby_allies": [],
            "structures": [],
            "recent_events": [],
            "strategic_positions": [
                {"id": "north_chokepoint", "description": "Narrow gap on north path", "position": [512, 200]}
            ]
        },
        player_instructions="Build a wall at the north chokepoint first, then hold.",
        commander_broadcast=None
    )
    assert event.robot_id == "architect_common_hana"
    assert event.event_type == EventType.ENEMY_SPOTTED


def test_robot_event_commander_broadcast_defaults_to_none():
    event = RobotEvent(
        robot_id="vanguard_common_rex",
        event_type=EventType.ENEMY_SPOTTED,
        event_detail="zombie spotted",
        local_context={
            "nearby_enemies": [], "nearby_allies": [],
            "structures": [], "recent_events": [], "strategic_positions": []
        },
        player_instructions="Hold position.",
    )
    assert event.commander_broadcast is None


def test_move_action_valid():
    action = MoveAction(action="move", destination="north_chokepoint", reason="Blocking north approach")
    assert action.action == "move"
    assert action.destination == "north_chokepoint"


def test_move_action_rejects_empty_destination():
    with pytest.raises(ValidationError):
        MoveAction(action="move", destination="", reason="Bad")


def test_attack_action_valid():
    action = AttackAction(action="attack", target_id=1, approach="maintain_range", reason="Engaging zombie")
    assert action.target_id == 1


def test_build_action_valid():
    action = BuildAction(action="build", structure="wall", destination="north_chokepoint", reason="Creating chokepoint")
    assert action.structure == "wall"


def test_build_action_turret():
    action = BuildAction(action="deploy_turret", structure="turret", destination="west_flank", reason="Cover flank")
    assert action.structure == "turret"


def test_build_action_rejects_invalid_structure():
    with pytest.raises(ValidationError):
        BuildAction(action="build", structure="laser_cannon", destination="north_chokepoint", reason="Bad")


def test_retreat_action_valid():
    action = RetreatAction(action="retreat", destination="rear_support", reason="Low health")
    assert action.destination == "rear_support"


def test_support_action_heal():
    action = SupportAction(action="heal", target_id=2, reason="Ally at 30% health")
    assert action.target_id == 2


def test_support_action_idle():
    action = SupportAction(action="idle", target_id=None, reason="No threats")
    assert action.action == "idle"


def test_parse_robot_action_move():
    data = {"action": "move", "destination": "west_flank", "reason": "Better position"}
    action = parse_robot_action(data)
    assert isinstance(action, MoveAction)


def test_parse_robot_action_attack():
    data = {"action": "attack", "target_id": 3, "approach": "close_in", "reason": "Enemy in range"}
    action = parse_robot_action(data)
    assert isinstance(action, AttackAction)


def test_parse_robot_action_unknown_type():
    with pytest.raises(ValueError, match="Unknown action type: explode"):
        parse_robot_action({"action": "explode"})


def test_parse_robot_action_missing_key():
    with pytest.raises(ValueError, match="Unknown action type: None"):
        parse_robot_action({})


def test_parse_robot_action_missing_required_fields():
    with pytest.raises(ValidationError):
        parse_robot_action({"action": "attack"})


def test_ws_incoming_valid():
    msg = WsIncoming(
        type="robot_event",
        robot_id="vanguard_common_rex",
        event_type=EventType.TAKING_DAMAGE,
        event_detail="hit for 8 damage",
        local_context={
            "nearby_enemies": [], "nearby_allies": [],
            "structures": [], "recent_events": [], "strategic_positions": []
        },
        player_instructions="Hold the north chokepoint.",
        commander_broadcast=None
    )
    assert msg.robot_id == "vanguard_common_rex"


def test_ws_incoming_rejects_wrong_type():
    with pytest.raises(ValidationError):
        WsIncoming(
            type="wrong",
            robot_id="vanguard_common_rex",
            event_type=EventType.TAKING_DAMAGE,
            event_detail="hit",
            local_context={
                "nearby_enemies": [], "nearby_allies": [],
                "structures": [], "recent_events": [], "strategic_positions": []
            },
            player_instructions="Hold.",
        )


def test_ws_incoming_to_robot_event():
    msg = WsIncoming(
        type="robot_event",
        robot_id="vanguard_common_rex",
        event_type=EventType.TAKING_DAMAGE,
        event_detail="hit for 8 damage",
        local_context={
            "nearby_enemies": [{"id": 1, "type": "zombie", "position": [200, 150], "health": 50}],
            "nearby_allies": [],
            "structures": [], "recent_events": [], "strategic_positions": []
        },
        player_instructions="Hold the north chokepoint.",
        commander_broadcast="Fall back!"
    )
    event = msg.to_robot_event()
    assert isinstance(event, RobotEvent)
    assert event.robot_id == "vanguard_common_rex"
    assert event.event_type == EventType.TAKING_DAMAGE
    assert event.event_detail == "hit for 8 damage"
    assert event.player_instructions == "Hold the north chokepoint."
    assert event.commander_broadcast == "Fall back!"


def test_ws_outgoing_valid():
    action = MoveAction(action="move", destination="north_chokepoint", reason="Moving to hold")
    msg = WsOutgoing(robot_id="vanguard_common_rex", action=action)
    assert msg.robot_id == "vanguard_common_rex"


def test_ws_outgoing_serialization_roundtrip():
    action = AttackAction(action="attack", target_id=1, approach="maintain_range", reason="Engage")
    msg = WsOutgoing(robot_id="striker_common_aurora", action=action)
    data = msg.model_dump()
    assert data["robot_id"] == "striker_common_aurora"
    assert data["action"]["action"] == "attack"
    assert data["action"]["target_id"] == 1
