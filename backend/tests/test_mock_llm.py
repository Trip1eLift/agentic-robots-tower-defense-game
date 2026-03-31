import pytest
import json
from backend.mock_llm import MockLLM


def _make_prompt(robot_class: str, enemies=None, allies=None):
    """Build a minimal prompt string that MockLLM can parse."""
    enemies = enemies or []
    allies = allies or []
    enemies_text = json.dumps(enemies)
    allies_text = json.dumps(allies)
    return f"""[System]
You are TestBot, a common {robot_class} robot. You are brave.
Your stats: speed=5, damage=6, armor=8, health=200/200, ammo=60, building_skill=2

[Player Instructions]
Hold position.

[Environment]
Nearby enemies: {enemies_text}
Nearby allies: {allies_text}
Structures: []
Recent events:
None
Strategic positions:
- north_chokepoint: Narrow gap on north path
- base_entrance: Last defensive line

[Global]
Commander broadcast: None

[Event]
ENEMY_SPOTTED: zombie at north

[Instruction]
You MUST respond with ONLY a JSON object. No other text.
"""


@pytest.mark.asyncio
async def test_vanguard_attacks_nearest_enemy():
    mock = MockLLM()
    prompt = _make_prompt("vanguard", enemies=[{"id": 1, "type": "zombie", "position": [200, 150], "health": 50}])
    result = json.loads(await mock.think(prompt))
    assert result["action"] == "attack"
    assert result["target_id"] == 1


@pytest.mark.asyncio
async def test_vanguard_moves_to_base_entrance_when_no_enemies():
    mock = MockLLM()
    prompt = _make_prompt("vanguard", enemies=[])
    result = json.loads(await mock.think(prompt))
    assert result["action"] == "move"
    assert result["destination"] == "base_entrance"


@pytest.mark.asyncio
async def test_striker_attacks_nearest_enemy_in_range():
    mock = MockLLM()
    prompt = _make_prompt("striker", enemies=[{"id": 2, "type": "zombie", "position": [300, 200], "health": 50}])
    result = json.loads(await mock.think(prompt))
    assert result["action"] == "attack"
    assert result["target_id"] == 2


@pytest.mark.asyncio
async def test_striker_holds_position_when_no_enemies():
    mock = MockLLM()
    prompt = _make_prompt("striker", enemies=[])
    result = json.loads(await mock.think(prompt))
    assert result["action"] == "idle"


@pytest.mark.asyncio
async def test_architect_builds_when_multiple_positions():
    mock = MockLLM()
    prompt = _make_prompt("architect", enemies=[])
    result = json.loads(await mock.think(prompt))
    # With 2 strategic positions in the prompt, architect builds
    assert result["action"] == "build"
    assert result["structure"] == "wall"


@pytest.mark.asyncio
async def test_medic_heals_lowest_health_ally():
    mock = MockLLM()
    allies = [
        {"id": "rex", "health": 50, "position": [512, 420]},
        {"id": "hana", "health": 100, "position": [512, 460]},
    ]
    prompt = _make_prompt("medic", allies=allies)
    result = json.loads(await mock.think(prompt))
    assert result["action"] == "heal"


@pytest.mark.asyncio
async def test_medic_idles_when_no_allies():
    mock = MockLLM()
    prompt = _make_prompt("medic", allies=[])
    result = json.loads(await mock.think(prompt))
    assert result["action"] == "idle"


# Round-trip integration tests: MockLLM -> ActionParser
from backend.action_parser import ActionParser
from backend.models import AttackAction, BuildAction, MoveAction, SupportAction


@pytest.mark.asyncio
async def test_roundtrip_vanguard():
    mock = MockLLM()
    parser = ActionParser()
    prompt = _make_prompt("vanguard", enemies=[{"id": 1, "type": "zombie", "position": [200, 150], "health": 50}])
    raw = await mock.think(prompt)
    action = parser.parse(raw)
    assert isinstance(action, AttackAction)


@pytest.mark.asyncio
async def test_roundtrip_striker():
    mock = MockLLM()
    parser = ActionParser()
    prompt = _make_prompt("striker", enemies=[{"id": 2, "type": "zombie", "position": [300, 200], "health": 50}])
    raw = await mock.think(prompt)
    action = parser.parse(raw)
    assert isinstance(action, AttackAction)


@pytest.mark.asyncio
async def test_roundtrip_architect():
    mock = MockLLM()
    parser = ActionParser()
    prompt = _make_prompt("architect", enemies=[])
    raw = await mock.think(prompt)
    action = parser.parse(raw)
    assert isinstance(action, BuildAction)


@pytest.mark.asyncio
async def test_roundtrip_medic():
    mock = MockLLM()
    parser = ActionParser()
    allies = [{"id": "rex", "health": 50, "position": [512, 420]}]
    prompt = _make_prompt("medic", allies=allies)
    raw = await mock.think(prompt)
    action = parser.parse(raw)
    assert isinstance(action, SupportAction)
    assert action.action == "heal"
