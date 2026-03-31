"""Integration tests for the WebSocket server end-to-end pipeline.

Uses FastAPI TestClient with mock LLM to test the full flow:
register_robot -> robot_event -> receive robot_action
"""
import json
import os
import pytest
from fastapi.testclient import TestClient

# Force mock LLM before importing app
os.environ["USE_MOCK_LLM"] = "true"
from backend.main import app, robot_state_store, event_queue


@pytest.fixture(autouse=True)
def _reset_state():
    """Reset shared server state between tests."""
    robot_state_store._states.clear()
    event_queue._queues.clear()
    event_queue._locks.clear()


def _register_msg(robot_id, health=100, ammo=40, position=None):
    return json.dumps({
        "type": "register_robot",
        "robot_id": robot_id,
        "health": health,
        "ammo": ammo,
        "position": position or [512, 460],
    })


def _event_msg(robot_id, event_type="ENEMY_SPOTTED", enemies=None, allies=None, positions=None):
    return json.dumps({
        "type": "robot_event",
        "robot_id": robot_id,
        "event_type": event_type,
        "event_detail": f"{event_type.lower()} test event",
        "local_context": {
            "nearby_enemies": enemies or [],
            "nearby_allies": allies or [],
            "structures": [],
            "recent_events": [],
            "strategic_positions": positions or [
                {"id": "north_chokepoint", "description": "Narrow gap", "position": [512, 200]},
                {"id": "rear_support", "description": "Safe position", "position": [512, 460]},
            ],
        },
        "player_instructions": "Hold position.",
        "commander_broadcast": None,
    })


def _state_update_msg(robot_id, **kwargs):
    msg = {"type": "state_update", "robot_id": robot_id}
    msg.update(kwargs)
    return json.dumps(msg)


def test_register_and_event_returns_action():
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_text(_register_msg("architect_common_hana"))
            ws.send_text(_event_msg(
                "architect_common_hana",
                enemies=[{"id": 1, "type": "zombie", "position": [512, 200], "health": 50}],
            ))
            response = json.loads(ws.receive_text())
            assert response["type"] == "robot_action"
            assert response["robot_id"] == "architect_common_hana"
            assert "action" in response["action"]


def test_vanguard_attacks():
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_text(_register_msg("vanguard_common_rex", health=200, ammo=60))
            ws.send_text(_event_msg(
                "vanguard_common_rex",
                enemies=[{"id": 1, "type": "zombie", "position": [200, 150], "health": 50}],
            ))
            response = json.loads(ws.receive_text())
            assert response["action"]["action"] == "attack"
            assert response["action"]["target_id"] == 1


def test_architect_builds():
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_text(_register_msg("architect_common_hana"))
            ws.send_text(_event_msg("architect_common_hana"))
            response = json.loads(ws.receive_text())
            assert response["action"]["action"] == "build"
            assert response["action"]["structure"] == "wall"


def test_medic_heals():
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_text(_register_msg("medic_common_lily", health=110, ammo=30))
            ws.send_text(_event_msg(
                "medic_common_lily",
                allies=[{"id": "rex", "health": 50, "position": [512, 420]}],
            ))
            response = json.loads(ws.receive_text())
            assert response["action"]["action"] == "heal"


def test_striker_idles_without_enemies():
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_text(_register_msg("striker_common_aurora", health=90, ammo=80))
            ws.send_text(_event_msg("striker_common_aurora", enemies=[]))
            response = json.loads(ws.receive_text())
            assert response["action"]["action"] == "idle"


def test_state_update_changes_health():
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_text(_register_msg("vanguard_common_rex", health=200, ammo=60))
            ws.send_text(_state_update_msg("vanguard_common_rex", health=50))
            ws.send_text(_event_msg(
                "vanguard_common_rex",
                enemies=[{"id": 1, "type": "zombie", "position": [200, 150], "health": 50}],
            ))
            response = json.loads(ws.receive_text())
            assert response["type"] == "robot_action"
            state = robot_state_store.get("vanguard_common_rex")
            assert state.health == 50


def test_invalid_json_returns_error():
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_text("not valid json{{{")
            response = json.loads(ws.receive_text())
            assert "error" in response


def test_unregistered_robot_state_update_returns_error():
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_text(_state_update_msg("nonexistent_robot", health=50))
            response = json.loads(ws.receive_text())
            assert "error" in response


def test_multiple_robots_on_same_connection():
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_text(_register_msg("vanguard_common_rex", health=200, ammo=60))
            ws.send_text(_register_msg("striker_common_aurora", health=90, ammo=80))

            ws.send_text(_event_msg(
                "vanguard_common_rex",
                enemies=[{"id": 1, "type": "zombie", "position": [200, 150], "health": 50}],
            ))
            ws.send_text(_event_msg(
                "striker_common_aurora",
                enemies=[{"id": 2, "type": "zombie", "position": [300, 200], "health": 50}],
            ))

            responses = {}
            for _ in range(2):
                r = json.loads(ws.receive_text())
                responses[r["robot_id"]] = r

            assert responses["vanguard_common_rex"]["action"]["action"] == "attack"
            assert responses["striker_common_aurora"]["action"]["action"] == "attack"
