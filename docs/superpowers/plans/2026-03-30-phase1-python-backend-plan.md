# Phase 1 — Python AI Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Python WebSocket backend that receives robot state-change events from Godot, builds LLM prompts, queries Ollama (Dolphin-Mistral 7B), parses structured robot actions, and sends them back to Godot.

**Architecture:** FastAPI WebSocket server accepts a single persistent connection from Godot. Per-robot async event queues feed a prompt builder that merges robot state + player instructions + environment context. An async Ollama client processes queued think requests and returns typed Pydantic actions.

**Tech Stack:** Python 3.11+, FastAPI, uvicorn, pydantic v2, ollama (official Python client), pytest, pytest-asyncio

---

## Branch

All work on this plan goes on branch: `feat/phase1-python-backend`

```bash
git checkout -b feat/phase1-python-backend
```

---

## File Structure

```
backend/
├── __init__.py          # Package marker (empty file)
├── main.py              # FastAPI app + WebSocket endpoint
├── models.py            # Pydantic models: events, actions, WS messages
├── config_loader.py     # Load + validate JSON data files from data/
├── robot_state.py       # In-memory robot state store
├── event_queue.py       # Per-robot async event queue + dispatcher
├── prompt_builder.py    # Build LLM prompts from state + context
├── ollama_client.py     # Async Ollama wrapper
├── action_parser.py     # Parse LLM JSON response → RobotAction
├── requirements.txt
└── tests/
    ├── conftest.py
    ├── test_models.py
    ├── test_config_loader.py
    ├── test_robot_state.py
    ├── test_prompt_builder.py
    ├── test_action_parser.py
    └── test_event_queue.py

data/
├── robots/archetypes/
│   ├── architect_common_hana.json
│   ├── vanguard_common_rex.json
│   ├── striker_common_aurora.json
│   └── medic_common_lily.json
├── enemies/
│   └── zombie.json
├── maps/
│   └── ch01_mission_01_map.json
└── campaign/
    └── chapter_01/
        ├── chapter.json
        ├── mission_01.json
        ├── mission_02.json
        └── mission_03.json
```

---

## Task 1: Project Setup

**Files:**
- Create: `backend/__init__.py`
- Create: `backend/requirements.txt`
- Create: `backend/tests/conftest.py`

- [ ] **Step 1: Create branch**

```bash
git checkout -b feat/phase1-python-backend
```

Expected: `Switched to a new branch 'feat/phase1-python-backend'`

- [ ] **Step 2: Create `backend/__init__.py`**

Create an empty file at `backend/__init__.py` so that `backend` is a proper Python package.

- [ ] **Step 3: Create `backend/requirements.txt`**

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic==2.9.2
ollama==0.3.3
pytest==8.3.3
pytest-asyncio==0.24.0
httpx==0.27.2
websockets==13.1
```

- [ ] **Step 4: Install dependencies**

```bash
cd backend
pip install -r requirements.txt
```

Expected: All packages install without errors.

- [ ] **Step 5: Create `backend/tests/conftest.py`**

```python
import pytest

pytest_plugins = ['pytest_asyncio']
```

- [ ] **Step 6: Verify pytest works**

```bash
cd backend
pytest tests/ -v
```

Expected: `no tests ran` (no test files yet, but no errors)

- [ ] **Step 7: Commit**

```bash
git add backend/__init__.py backend/requirements.txt backend/tests/conftest.py
git commit -m "feat: bootstrap python backend project"
```

---

## Task 2: Data Config Files

**Files:**
- Create: `data/robots/archetypes/architect_common_hana.json`
- Create: `data/robots/archetypes/vanguard_common_rex.json`
- Create: `data/robots/archetypes/striker_common_aurora.json`
- Create: `data/robots/archetypes/medic_common_lily.json`
- Create: `data/enemies/zombie.json`
- Create: `data/maps/ch01_mission_01_map.json`
- Create: `data/campaign/chapter_01/chapter.json`
- Create: `data/campaign/chapter_01/mission_01.json`
- Create: `data/campaign/chapter_01/mission_02.json`
- Create: `data/campaign/chapter_01/mission_03.json`

- [ ] **Step 1: Create robot configs**

`data/robots/archetypes/architect_common_hana.json`:
```json
{
  "id": "architect_common_hana",
  "name": "Hana",
  "class": "architect",
  "rarity": "common",
  "base_stats": {
    "speed": 4,
    "damage": 3,
    "armor": 5,
    "health": 100,
    "ammo": 40,
    "building_skill": 7,
    "intelligence": 5
  },
  "personality_prompt": "You are Hana, a methodical Architect. You prioritize building fortifications before engaging enemies. You think several steps ahead and position structures to create chokepoints.",
  "portrait": "res://assets/robots/hana/portrait.png",
  "sprite": "res://assets/robots/hana/sprite.png"
}
```

`data/robots/archetypes/vanguard_common_rex.json`:
```json
{
  "id": "vanguard_common_rex",
  "name": "Rex",
  "class": "vanguard",
  "rarity": "common",
  "base_stats": {
    "speed": 5,
    "damage": 6,
    "armor": 8,
    "health": 200,
    "ammo": 60,
    "building_skill": 2,
    "intelligence": 3
  },
  "personality_prompt": "You are Rex, a fearless Vanguard. You charge enemies to protect your allies. You position yourself between threats and the base.",
  "portrait": "res://assets/robots/rex/portrait.png",
  "sprite": "res://assets/robots/rex/sprite.png"
}
```

`data/robots/archetypes/striker_common_aurora.json`:
```json
{
  "id": "striker_common_aurora",
  "name": "Aurora",
  "class": "striker",
  "rarity": "common",
  "base_stats": {
    "speed": 7,
    "damage": 9,
    "armor": 3,
    "health": 90,
    "ammo": 80,
    "building_skill": 1,
    "intelligence": 4
  },
  "personality_prompt": "You are Aurora, a precise Striker. You pick off high-value targets from optimal range. You avoid close combat and conserve ammo.",
  "portrait": "res://assets/robots/aurora/portrait.png",
  "sprite": "res://assets/robots/aurora/sprite.png"
}
```

`data/robots/archetypes/medic_common_lily.json`:
```json
{
  "id": "medic_common_lily",
  "name": "Lily",
  "class": "medic",
  "rarity": "common",
  "base_stats": {
    "speed": 5,
    "damage": 2,
    "armor": 4,
    "health": 110,
    "ammo": 30,
    "building_skill": 3,
    "intelligence": 6
  },
  "personality_prompt": "You are Lily, a caring Medic. You monitor your allies' health and heal those in danger. You stay behind the front line and support the team.",
  "portrait": "res://assets/robots/lily/portrait.png",
  "sprite": "res://assets/robots/lily/sprite.png"
}
```

- [ ] **Step 2: Create enemy config**

`data/enemies/zombie.json`:
```json
{
  "id": "zombie",
  "name": "Zombie",
  "stats": {
    "speed": 2,
    "damage": 8,
    "health": 50,
    "armor": 1,
    "attack_range": 40,
    "attack_rate": 1.0
  },
  "sprite": "res://assets/enemies/zombie/sprite.png",
  "xp_reward": 10,
  "behavior": "move_to_base"
}
```

- [ ] **Step 3: Create map config**

`data/maps/ch01_mission_01_map.json`:
```json
{
  "id": "ch01_mission_01_map",
  "name": "Collapsed Road",
  "tilemap": "res://maps/ch01_mission_01.tscn",
  "base_position": [512, 500],
  "robot_spawn_zones": [
    {"id": "zone_main", "rect": [350, 400, 320, 120]}
  ],
  "enemy_spawn_points": [
    {"id": "spawn_north", "position": [512, 50]},
    {"id": "spawn_west",  "position": [50,  300]}
  ],
  "buildable_zones": [
    {"rect": [200, 150, 600, 350], "max_structures": 8}
  ],
  "strategic_positions": [
    {
      "id": "north_chokepoint",
      "description": "Narrow gap in rubble on north path, good for Vanguard to hold the line",
      "position": [512, 200],
      "suitable_for": ["vanguard", "architect"]
    },
    {
      "id": "west_flank",
      "description": "Open ground on west approach, good for Striker to pick off enemies at range",
      "position": [200, 300],
      "suitable_for": ["striker"]
    },
    {
      "id": "base_entrance",
      "description": "Last defensive line directly in front of the base",
      "position": [512, 420],
      "suitable_for": ["vanguard", "medic"]
    },
    {
      "id": "rear_support",
      "description": "Safe position behind the front line, ideal for Medic and Architect",
      "position": [512, 460],
      "suitable_for": ["medic", "architect"]
    }
  ]
}
```

- [ ] **Step 4: Create campaign configs**

`data/campaign/chapter_01/chapter.json`:
```json
{
  "id": "chapter_01",
  "title": "The Outskirts",
  "missions": ["mission_01", "mission_02", "mission_03"]
}
```

`data/campaign/chapter_01/mission_01.json`:
```json
{
  "id": "ch01_mission_01",
  "title": "First Contact",
  "type": "normal",
  "map_id": "ch01_mission_01_map",
  "max_robots": 4,
  "reward_currency": 300,
  "objectives": [
    {"type": "SURVIVE", "required": true}
  ],
  "waves": [
    {
      "wave_number": 1,
      "enemies": [{"type": "zombie", "count": 8}]
    },
    {
      "wave_number": 2,
      "enemies": [{"type": "zombie", "count": 12}]
    },
    {
      "wave_number": 3,
      "enemies": [{"type": "zombie", "count": 16}]
    }
  ]
}
```

`data/campaign/chapter_01/mission_02.json`:
```json
{
  "id": "ch01_mission_02",
  "title": "Hold the Line",
  "type": "normal",
  "map_id": "ch01_mission_01_map",
  "max_robots": 4,
  "reward_currency": 400,
  "objectives": [
    {"type": "SURVIVE", "required": true},
    {"type": "ELIMINATE", "required": false, "target_count": 30}
  ],
  "waves": [
    {
      "wave_number": 1,
      "enemies": [{"type": "zombie", "count": 10}]
    },
    {
      "wave_number": 2,
      "enemies": [{"type": "zombie", "count": 15}]
    },
    {
      "wave_number": 3,
      "enemies": [{"type": "zombie", "count": 20}]
    }
  ]
}
```

`data/campaign/chapter_01/mission_03.json`:
```json
{
  "id": "ch01_mission_03",
  "title": "The Swarm",
  "type": "normal",
  "map_id": "ch01_mission_01_map",
  "max_robots": 4,
  "reward_currency": 500,
  "objectives": [
    {"type": "SURVIVE", "required": true},
    {"type": "ELIMINATE", "required": true, "target_count": 40}
  ],
  "waves": [
    {
      "wave_number": 1,
      "enemies": [{"type": "zombie", "count": 12}]
    },
    {
      "wave_number": 2,
      "enemies": [{"type": "zombie", "count": 18}]
    },
    {
      "wave_number": 3,
      "enemies": [{"type": "zombie", "count": 25}]
    }
  ]
}
```

- [ ] **Step 5: Commit**

```bash
git add data/
git commit -m "feat: add phase 1 data config files"
```

---

## Task 3: Pydantic Models

**Files:**
- Create: `backend/models.py`
- Create: `backend/tests/test_models.py`

- [ ] **Step 1: Write failing tests**

`backend/tests/test_models.py`:
```python
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


def test_move_action_valid():
    action = MoveAction(action="move", destination="north_chokepoint", reason="Blocking north approach")
    assert action.action == "move"
    assert action.destination == "north_chokepoint"


def test_attack_action_valid():
    action = AttackAction(action="attack", target_id=1, approach="maintain_range", reason="Engaging zombie")
    assert action.target_id == 1


def test_build_action_valid():
    action = BuildAction(action="build", structure="wall", destination="north_chokepoint", reason="Creating chokepoint")
    assert action.structure == "wall"


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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend
pytest tests/test_models.py -v
```

Expected: `ImportError` — `backend.models` does not exist yet.

- [ ] **Step 3: Create `backend/models.py`**

```python
from __future__ import annotations
from enum import Enum
from typing import Any, Literal, Optional, Union
from pydantic import BaseModel


class EventType(str, Enum):
    ENEMY_SPOTTED = "ENEMY_SPOTTED"
    ENEMY_IN_RANGE = "ENEMY_IN_RANGE"
    TAKING_DAMAGE = "TAKING_DAMAGE"
    AMMO_LOW = "AMMO_LOW"
    ATTACK_MISSED = "ATTACK_MISSED"
    ENEMY_ELIMINATED = "ENEMY_ELIMINATED"
    BUILD_COMPLETE = "BUILD_COMPLETE"
    ALLY_DIED = "ALLY_DIED"
    ALLY_NEEDS_HEAL = "ALLY_NEEDS_HEAL"
    BASE_UNDER_ATTACK = "BASE_UNDER_ATTACK"
    OBJECTIVE_UPDATE = "OBJECTIVE_UPDATE"
    COMMANDER_BROADCAST = "COMMANDER_BROADCAST"


class LocalContext(BaseModel):
    nearby_enemies: list[dict[str, Any]]  # Each enemy has "id" (small sequential int, e.g. 1, 2, 3)
    nearby_allies: list[dict[str, Any]]
    structures: list[dict[str, Any]]
    recent_events: list[str]
    strategic_positions: list[dict[str, Any]]


class RobotEvent(BaseModel):
    robot_id: str
    event_type: EventType
    event_detail: str
    local_context: LocalContext
    player_instructions: str
    commander_broadcast: Optional[str]


class MoveAction(BaseModel):
    action: Literal["move"]
    destination: str
    reason: Optional[str] = None


class AttackAction(BaseModel):
    action: Literal["attack", "snipe"]
    target_id: int  # Small sequential ID (1, 2, 3...) assigned by game manager, NOT Godot instance IDs
    approach: Literal["close_in", "maintain_range", "stay_back"]
    reason: Optional[str] = None


class BuildAction(BaseModel):
    action: Literal["build", "deploy_turret"]
    structure: Literal["wall", "barricade", "watchtower", "ammo_depot", "medic_station"]
    destination: str
    reason: Optional[str] = None


class RetreatAction(BaseModel):
    action: Literal["retreat"]
    destination: str
    reason: Optional[str] = None


class SupportAction(BaseModel):
    action: Literal["heal", "idle"]
    target_id: Optional[int] = None  # Small sequential ID (1, 2, 3...) or None for idle
    reason: Optional[str] = None


RobotAction = Union[MoveAction, AttackAction, BuildAction, RetreatAction, SupportAction]

_ACTION_MAP = {
    "move": MoveAction,
    "attack": AttackAction,
    "snipe": AttackAction,
    "build": BuildAction,
    "deploy_turret": BuildAction,
    "retreat": RetreatAction,
    "heal": SupportAction,
    "idle": SupportAction,
}


def parse_robot_action(data: dict[str, Any]) -> RobotAction:
    action_type = data.get("action")
    model = _ACTION_MAP.get(action_type)
    if model is None:
        raise ValueError(f"Unknown action type: {action_type}")
    return model(**data)


class WsIncoming(BaseModel):
    type: Literal["robot_event"]
    robot_id: str
    event_type: EventType
    event_detail: str
    local_context: LocalContext
    player_instructions: str
    commander_broadcast: Optional[str]

    def to_robot_event(self) -> RobotEvent:
        """Convert WsIncoming to RobotEvent for the event queue."""
        return RobotEvent(
            robot_id=self.robot_id,
            event_type=self.event_type,
            event_detail=self.event_detail,
            local_context=self.local_context,
            player_instructions=self.player_instructions,
            commander_broadcast=self.commander_broadcast,
        )


class WsOutgoing(BaseModel):
    robot_id: str
    action: RobotAction
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_models.py -v
```

Expected: All 13 tests `PASSED`.

- [ ] **Step 5: Commit**

```bash
git add backend/models.py backend/tests/test_models.py
git commit -m "feat: add pydantic models for events and robot actions"
```

---

## Task 4: Config Loader

**Files:**
- Create: `backend/config_loader.py`
- Create: `backend/tests/test_config_loader.py`

- [ ] **Step 1: Write failing tests**

`backend/tests/test_config_loader.py`:
```python
import pytest
from pathlib import Path
from backend.config_loader import ConfigLoader

DATA_DIR = Path(__file__).parent.parent.parent / "data"


def test_load_robot_config():
    loader = ConfigLoader(DATA_DIR)
    robot = loader.get_robot("architect_common_hana")
    assert robot["name"] == "Hana"
    assert robot["class"] == "architect"
    assert robot["base_stats"]["intelligence"] == 5


def test_load_all_robots():
    loader = ConfigLoader(DATA_DIR)
    robots = loader.get_all_robots()
    assert len(robots) == 4
    classes = {r["class"] for r in robots}
    assert classes == {"architect", "vanguard", "striker", "medic"}


def test_load_map_config():
    loader = ConfigLoader(DATA_DIR)
    map_cfg = loader.get_map("ch01_mission_01_map")
    assert map_cfg["name"] == "Collapsed Road"
    assert len(map_cfg["strategic_positions"]) == 4


def test_load_mission_config():
    loader = ConfigLoader(DATA_DIR)
    mission = loader.get_mission("ch01_mission_01")
    assert mission["title"] == "First Contact"
    assert len(mission["waves"]) == 3


def test_load_enemy_config():
    loader = ConfigLoader(DATA_DIR)
    enemy = loader.get_enemy("zombie")
    assert enemy["stats"]["health"] == 50


def test_missing_robot_raises():
    loader = ConfigLoader(DATA_DIR)
    with pytest.raises(KeyError):
        loader.get_robot("nonexistent_robot")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_config_loader.py -v
```

Expected: `ImportError` — `backend.config_loader` does not exist yet.

- [ ] **Step 3: Create `backend/config_loader.py`**

```python
from __future__ import annotations
import json
from pathlib import Path


class ConfigLoader:
    def __init__(self, data_dir: Path):
        self._data_dir = data_dir
        self._robots: dict = {}
        self._maps: dict = {}
        self._missions: dict = {}
        self._enemies: dict = {}
        self._load_all()

    def _load_all(self) -> None:
        for path in (self._data_dir / "robots" / "archetypes").glob("*.json"):
            cfg = json.loads(path.read_text(encoding="utf-8"))
            self._robots[cfg["id"]] = cfg

        for path in (self._data_dir / "maps").glob("*.json"):
            cfg = json.loads(path.read_text(encoding="utf-8"))
            self._maps[cfg["id"]] = cfg

        for path in (self._data_dir / "enemies").glob("*.json"):
            cfg = json.loads(path.read_text(encoding="utf-8"))
            self._enemies[cfg["id"]] = cfg

        for path in (self._data_dir / "campaign").rglob("mission_*.json"):
            cfg = json.loads(path.read_text(encoding="utf-8"))
            self._missions[cfg["id"]] = cfg

    def get_robot(self, robot_id: str) -> dict:
        if robot_id not in self._robots:
            raise KeyError(f"Robot not found: {robot_id}")
        return self._robots[robot_id]

    def get_all_robots(self) -> list[dict]:
        return list(self._robots.values())

    def get_map(self, map_id: str) -> dict:
        if map_id not in self._maps:
            raise KeyError(f"Map not found: {map_id}")
        return self._maps[map_id]

    def get_mission(self, mission_id: str) -> dict:
        if mission_id not in self._missions:
            raise KeyError(f"Mission not found: {mission_id}")
        return self._missions[mission_id]

    def get_enemy(self, enemy_id: str) -> dict:
        if enemy_id not in self._enemies:
            raise KeyError(f"Enemy not found: {enemy_id}")
        return self._enemies[enemy_id]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_config_loader.py -v
```

Expected: All 6 tests `PASSED`.

- [ ] **Step 5: Commit**

```bash
git add backend/config_loader.py backend/tests/test_config_loader.py
git commit -m "feat: add config loader for JSON data files"
```

---

## Task 5: Robot State Store

**Files:**
- Create: `backend/robot_state.py`
- Create: `backend/tests/test_robot_state.py`

- [ ] **Step 1: Write failing tests**

`backend/tests/test_robot_state.py`:
```python
import pytest
from backend.robot_state import RobotStateStore, RobotState


def test_register_robot():
    store = RobotStateStore()
    store.register("architect_common_hana", health=100, max_health=100, ammo=40, position=(512, 460))
    state = store.get("architect_common_hana")
    assert state.health == 100
    assert state.position == (512, 460)
    assert state.is_alive is True


def test_update_health():
    store = RobotStateStore()
    store.register("vanguard_common_rex", health=200, max_health=200, ammo=60, position=(512, 420))
    store.update_health("vanguard_common_rex", new_health=150)
    assert store.get("vanguard_common_rex").health == 150


def test_robot_dies_at_zero_health():
    store = RobotStateStore()
    store.register("striker_common_aurora", health=90, max_health=90, ammo=80, position=(200, 300))
    store.update_health("striker_common_aurora", new_health=0)
    assert store.get("striker_common_aurora").is_alive is False


def test_update_position():
    store = RobotStateStore()
    store.register("medic_common_lily", health=110, max_health=110, ammo=30, position=(512, 460))
    store.update_position("medic_common_lily", new_position=(300, 400))
    assert store.get("medic_common_lily").position == (300, 400)


def test_set_current_action():
    store = RobotStateStore()
    store.register("architect_common_hana", health=100, max_health=100, ammo=40, position=(512, 460))
    store.set_current_action("architect_common_hana", "build")
    assert store.get("architect_common_hana").current_action == "build"


def test_get_missing_robot_raises():
    store = RobotStateStore()
    with pytest.raises(KeyError):
        store.get("nonexistent")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_robot_state.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Create `backend/robot_state.py`**

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RobotState:
    robot_id: str
    health: int
    max_health: int
    ammo: int
    position: tuple[float, float]
    current_action: Optional[str] = None
    is_alive: bool = True


class RobotStateStore:
    def __init__(self):
        self._states: dict[str, RobotState] = {}

    def register(self, robot_id: str, health: int, max_health: int, ammo: int, position: tuple[float, float]) -> None:
        self._states[robot_id] = RobotState(
            robot_id=robot_id,
            health=health,
            max_health=max_health,
            ammo=ammo,
            position=position,
        )

    def get(self, robot_id: str) -> RobotState:
        if robot_id not in self._states:
            raise KeyError(f"Robot not registered: {robot_id}")
        return self._states[robot_id]

    def update_health(self, robot_id: str, new_health: int) -> None:
        state = self.get(robot_id)
        state.health = max(0, new_health)
        if state.health == 0:
            state.is_alive = False

    def update_position(self, robot_id: str, new_position: tuple[float, float]) -> None:
        self.get(robot_id).position = new_position

    def set_current_action(self, robot_id: str, action: str) -> None:
        self.get(robot_id).current_action = action

    def all_states(self) -> list[RobotState]:
        return list(self._states.values())
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_robot_state.py -v
```

Expected: All 6 tests `PASSED`.

- [ ] **Step 5: Commit**

```bash
git add backend/robot_state.py backend/tests/test_robot_state.py
git commit -m "feat: add in-memory robot state store"
```

---

## Task 6: Prompt Builder

**Files:**
- Create: `backend/prompt_builder.py`
- Create: `backend/tests/test_prompt_builder.py`

- [ ] **Step 1: Write failing tests**

`backend/tests/test_prompt_builder.py`:
```python
import pytest
from backend.prompt_builder import PromptBuilder
from backend.models import EventType, LocalContext, RobotEvent


def _make_event(event_type=EventType.ENEMY_SPOTTED, player_instructions="Hold north.", intelligence=5):
    return RobotEvent(
        robot_id="archer_common_hana",
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
        commander_broadcast=None
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
    # intelligence=5 → max 500 chars (intelligence * 100)
    prompt = builder.build(ROBOT_CONFIG, ROBOT_RUNTIME_STATS, _make_event(player_instructions=long_instructions))
    # Extract the Player Instructions section from the prompt
    import re
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
    assert "Respond with a single JSON action" in prompt
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_prompt_builder.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Create `backend/prompt_builder.py`**

```python
from __future__ import annotations
import json
from backend.models import RobotEvent


class PromptBuilder:
    def build(self, robot_config: dict, runtime_stats: dict, event: RobotEvent) -> str:
        stats = robot_config["base_stats"]
        intelligence = stats["intelligence"]
        # Character limit formula: intelligence * 100 (e.g. intelligence=5 → 500 chars max)
        # Higher-intelligence robots can process longer player instructions
        max_instruction_chars = intelligence * 100

        instructions = event.player_instructions[:max_instruction_chars]

        ctx = event.local_context
        enemies_text = json.dumps(ctx.nearby_enemies, indent=None)
        allies_text = json.dumps(ctx.nearby_allies, indent=None)
        structures_text = json.dumps(ctx.structures, indent=None)
        events_text = "\n".join(ctx.recent_events) if ctx.recent_events else "None"
        positions_text = "\n".join(
            f"- {p['id']}: {p['description']}" for p in ctx.strategic_positions
        )

        broadcast_line = (
            f'Commander broadcast: "{event.commander_broadcast}"'
            if event.commander_broadcast
            else "Commander broadcast: None"
        )

        health = runtime_stats.get("health", stats["health"])
        ammo = runtime_stats.get("ammo", stats["ammo"])

        return f"""[System]
You are {robot_config['name']}, a {robot_config['rarity']} {robot_config['class']} robot. {robot_config['personality_prompt']}
Your stats: speed={stats['speed']}, damage={stats['damage']}, armor={stats['armor']}, health={health}/{stats['health']}, ammo={ammo}, building_skill={stats['building_skill']}

[Player Instructions]
{instructions}

[Environment]
Nearby enemies: {enemies_text}
Nearby allies: {allies_text}
Structures: {structures_text}
Recent events:
{events_text}
Strategic positions:
{positions_text}

[Global]
{broadcast_line}

[Event]
{event.event_type.value}: {event.event_detail}

[Instruction]
Respond with a single JSON action. Valid actions: move, attack, snipe, build, deploy_turret, retreat, heal, idle.
Enemy target_id values are small sequential integers (1, 2, 3...) as shown in the enemy list above.
Example move: {{"action": "move", "destination": "north_chokepoint", "reason": "Blocking advance"}}
Example attack: {{"action": "attack", "target_id": 1, "approach": "maintain_range", "reason": "Enemy in range"}}
"""
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_prompt_builder.py -v
```

Expected: All 6 tests `PASSED`.

- [ ] **Step 5: Commit**

```bash
git add backend/prompt_builder.py backend/tests/test_prompt_builder.py
git commit -m "feat: add prompt builder with intelligence-based truncation"
```

---

## Task 7: Action Parser

**Files:**
- Create: `backend/action_parser.py`
- Create: `backend/tests/test_action_parser.py`

- [ ] **Step 1: Write failing tests**

`backend/tests/test_action_parser.py`:
```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_action_parser.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Create `backend/action_parser.py`**

```python
from __future__ import annotations
import json
import re
from backend.models import RobotAction, SupportAction, parse_robot_action


class ActionParser:
    _JSON_PATTERN = re.compile(r'\{[^{}]*\}', re.DOTALL)

    def parse(self, llm_response: str) -> RobotAction:
        candidates = self._JSON_PATTERN.findall(llm_response)
        for candidate in candidates:
            try:
                data = json.loads(candidate)
                if "action" in data:
                    return parse_robot_action(data)
            except (json.JSONDecodeError, ValueError, TypeError):
                continue
        return SupportAction(action="idle", reason="Could not parse LLM response")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_action_parser.py -v
```

Expected: All 7 tests `PASSED`.

- [ ] **Step 5: Commit**

```bash
git add backend/action_parser.py backend/tests/test_action_parser.py
git commit -m "feat: add action parser with prose extraction fallback"
```

---

## Task 8: Ollama Client

**Files:**
- Create: `backend/ollama_client.py`

Note: This task has no unit tests because it wraps a live external service (Ollama). Integration is tested in Task 10.

- [ ] **Step 1: Verify Ollama is installed and Dolphin-Mistral is available**

```bash
ollama list
```

Expected output includes `dolphin-mistral` in the list. If not, run:

```bash
ollama pull dolphin-mistral
```

Wait for download to complete (~4GB).

- [ ] **Step 2: Create `backend/ollama_client.py`**

```python
from __future__ import annotations
import asyncio
import ollama


class OllamaClient:
    MODEL = "dolphin-mistral"

    def __init__(self):
        self._client = ollama.AsyncClient()

    async def think(self, prompt: str) -> str:
        response = await self._client.chat(
            model=self.MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.3, "num_predict": 200}
        )
        return response.message.content
```

`temperature=0.3` keeps responses consistent and JSON-parseable. `num_predict=200` caps token output — actions don't need to be long.

- [ ] **Step 3: Manual smoke test**

```bash
cd backend
python -c "
import asyncio
from backend.ollama_client import OllamaClient

async def test():
    client = OllamaClient()
    result = await client.think('Reply with exactly: {\"action\": \"idle\", \"reason\": \"test\"}')
    print(result)

asyncio.run(test())
"
```

Expected: Output contains `idle` somewhere in a JSON-like structure.

- [ ] **Step 4: Commit**

```bash
git add backend/ollama_client.py
git commit -m "feat: add async ollama client wrapper"
```

---

## Task 9: Event Queue

**Files:**
- Create: `backend/event_queue.py`
- Create: `backend/tests/test_event_queue.py`

- [ ] **Step 1: Write failing tests**

`backend/tests/test_event_queue.py`:
```python
import asyncio
import pytest
from backend.event_queue import EventQueue
from backend.models import EventType, LocalContext, RobotEvent


def _make_event(robot_id: str, event_type=EventType.ENEMY_SPOTTED) -> RobotEvent:
    return RobotEvent(
        robot_id=robot_id,
        event_type=event_type,
        event_detail="test event",
        local_context=LocalContext(
            nearby_enemies=[], nearby_allies=[], structures=[],
            recent_events=[], strategic_positions=[]
        ),
        player_instructions="Hold position.",
        commander_broadcast=None
    )


@pytest.mark.asyncio
async def test_enqueue_and_dequeue():
    queue = EventQueue()
    event = _make_event("architect_common_hana")
    await queue.enqueue(event)
    dequeued = await queue.dequeue("architect_common_hana")
    assert dequeued.robot_id == "architect_common_hana"


@pytest.mark.asyncio
async def test_queue_is_per_robot():
    queue = EventQueue()
    await queue.enqueue(_make_event("architect_common_hana"))
    await queue.enqueue(_make_event("vanguard_common_rex"))
    hana_event = await queue.dequeue("architect_common_hana")
    assert hana_event.robot_id == "architect_common_hana"


@pytest.mark.asyncio
async def test_dequeue_empty_returns_none():
    queue = EventQueue()
    result = await queue.dequeue_nowait("architect_common_hana")
    assert result is None


@pytest.mark.asyncio
async def test_coalescing_keeps_latest_event():
    """Event coalescing: newer events discard older queued events for the same robot."""
    queue = EventQueue()
    await queue.enqueue(_make_event("architect_common_hana", EventType.ENEMY_SPOTTED))
    await queue.enqueue(_make_event("architect_common_hana", EventType.TAKING_DAMAGE))
    # Coalescing should discard the older ENEMY_SPOTTED, keeping only TAKING_DAMAGE
    assert queue.size("architect_common_hana") == 1
    event = await queue.dequeue("architect_common_hana")
    assert event.event_type == EventType.TAKING_DAMAGE


@pytest.mark.asyncio
async def test_coalescing_does_not_affect_other_robots():
    """Events for different robots are independent - coalescing is per-robot."""
    queue = EventQueue()
    await queue.enqueue(_make_event("architect_common_hana", EventType.ENEMY_SPOTTED))
    await queue.enqueue(_make_event("vanguard_common_rex", EventType.TAKING_DAMAGE))
    assert queue.size("architect_common_hana") == 1
    assert queue.size("vanguard_common_rex") == 1
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_event_queue.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Create `backend/event_queue.py`**

```python
from __future__ import annotations
import asyncio
from typing import Optional
from backend.models import RobotEvent


class EventQueue:
    """Per-robot async event queue with coalescing.

    Event coalescing: when a new event arrives for a robot, any older queued
    events for that robot are discarded. Only the latest event is kept. This
    prevents stale context from backed-up events reaching the LLM.
    """

    def __init__(self):
        self._queues: dict[str, asyncio.Queue[RobotEvent]] = {}

    def _get_queue(self, robot_id: str) -> asyncio.Queue[RobotEvent]:
        if robot_id not in self._queues:
            self._queues[robot_id] = asyncio.Queue()
        return self._queues[robot_id]

    async def enqueue(self, event: RobotEvent) -> None:
        q = self._get_queue(event.robot_id)
        # Coalesce: drain any older events so only the latest remains
        while not q.empty():
            try:
                q.get_nowait()
            except asyncio.QueueEmpty:
                break
        await q.put(event)

    async def dequeue(self, robot_id: str) -> RobotEvent:
        return await self._get_queue(robot_id).get()

    async def dequeue_nowait(self, robot_id: str) -> Optional[RobotEvent]:
        try:
            return self._get_queue(robot_id).get_nowait()
        except asyncio.QueueEmpty:
            return None

    def size(self, robot_id: str) -> int:
        return self._get_queue(robot_id).qsize()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_event_queue.py -v
```

Expected: All 5 tests `PASSED`.

- [ ] **Step 5: Commit**

```bash
git add backend/event_queue.py backend/tests/test_event_queue.py
git commit -m "feat: add per-robot async event queue"
```

---

## Task 10: WebSocket Server

**Files:**
- Create: `backend/main.py`

- [ ] **Step 1: Create `backend/main.py`**

```python
from __future__ import annotations
import asyncio
import json
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from backend.action_parser import ActionParser
from backend.config_loader import ConfigLoader
from backend.event_queue import EventQueue
from backend.models import SupportAction, WsIncoming, WsOutgoing
from backend.ollama_client import OllamaClient
from backend.prompt_builder import PromptBuilder
from backend.robot_state import RobotStateStore

DATA_DIR = Path(__file__).parent.parent / "data"

app = FastAPI()

config_loader = ConfigLoader(DATA_DIR)
robot_state_store = RobotStateStore()
event_queue = EventQueue()
prompt_builder = PromptBuilder()
action_parser = ActionParser()
ollama_client = OllamaClient()


async def process_robot_events(robot_id: str, websocket: WebSocket) -> None:
    import logging
    logger = logging.getLogger(__name__)

    robot_config = config_loader.get_robot(robot_id)
    while True:
        event = await event_queue.dequeue(robot_id)
        try:
            state = robot_state_store.get(robot_id)
        except KeyError:
            continue

        try:
            runtime_stats = {"health": state.health, "ammo": state.ammo}
            prompt = prompt_builder.build(robot_config, runtime_stats, event)
            llm_response = await ollama_client.think(prompt)
            action = action_parser.parse(llm_response)
        except Exception as e:
            logger.error(f"LLM processing failed for {robot_id}: {e}")
            action = SupportAction(action="idle", reason=f"LLM error: {type(e).__name__}")

        robot_state_store.set_current_action(robot_id, action.action)

        outgoing = WsOutgoing(robot_id=robot_id, action=action)
        await websocket.send_text(outgoing.model_dump_json())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    processor_tasks: dict[str, asyncio.Task] = {}

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid JSON received"}))
                continue

            if data.get("type") == "register_robot":
                robot_id = data["robot_id"]
                robot_state_store.register(
                    robot_id=robot_id,
                    health=data["health"],
                    max_health=data["health"],
                    ammo=data["ammo"],
                    position=tuple(data["position"])
                )
                if robot_id not in processor_tasks:
                    processor_tasks[robot_id] = asyncio.create_task(
                        process_robot_events(robot_id, websocket)
                    )
                continue

            if data.get("type") == "state_update":
                robot_id = data["robot_id"]
                if "health" in data:
                    robot_state_store.update_health(robot_id, data["health"])
                if "position" in data:
                    robot_state_store.update_position(robot_id, tuple(data["position"]))
                if "ammo" in data:
                    robot_state_store.get(robot_id).ammo = data["ammo"]
                continue

            msg = WsIncoming(**data)
            await event_queue.enqueue(msg.to_robot_event())

    except WebSocketDisconnect:
        for task in processor_tasks.values():
            task.cancel()
    except ValidationError as e:
        await websocket.send_text(json.dumps({"error": str(e)}))
```

- [ ] **Step 2: Run the server**

```bash
cd backend
uvicorn backend.main:app --host 0.0.0.0 --port 8765 --reload
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8765 (Press CTRL+C to quit)
INFO:     Started reloader process
```

- [ ] **Step 3: Manual WebSocket smoke test**

In a second terminal:
```bash
python -c "
import asyncio
import websockets
import json

async def test():
    async with websockets.connect('ws://localhost:8765/ws') as ws:
        # Register a robot
        await ws.send(json.dumps({
            'type': 'register_robot',
            'robot_id': 'architect_common_hana',
            'health': 100,
            'ammo': 40,
            'position': [512, 460]
        }))

        # Send an event
        await ws.send(json.dumps({
            'type': 'robot_event',
            'robot_id': 'architect_common_hana',
            'event_type': 'ENEMY_SPOTTED',
            'event_detail': 'zombie at north_chokepoint',
            'local_context': {
                'nearby_enemies': [{'id': 1, 'type': 'zombie', 'position': [512, 200], 'health': 50}],
                'nearby_allies': [],
                'structures': [],
                'recent_events': [],
                'strategic_positions': [
                    {'id': 'north_chokepoint', 'description': 'Narrow gap', 'position': [512, 200]}
                ]
            },
            'player_instructions': 'Build a wall at the chokepoint.',
            'commander_broadcast': None
        }))

        response = await asyncio.wait_for(ws.recv(), timeout=30)
        print('Response:', response)

asyncio.run(test())
"
```

Expected: JSON response containing `robot_id` and an `action` (e.g. `move`, `build`, or `idle`). May take 5-15 seconds for Ollama to respond.

- [ ] **Step 4: Run all tests**

```bash
pytest tests/ -v
```

Expected: All tests `PASSED`.

- [ ] **Step 5: Commit**

```bash
git add backend/main.py
git commit -m "feat: add fastapi websocket server tying all backend components together"
```

---

## Task 11: Push and Open PR

- [ ] **Step 1: Push branch**

```bash
git push -u origin feat/phase1-python-backend
```

- [ ] **Step 2: Open PR**

```bash
gh pr create \
  --title "Phase 1: Python AI Backend" \
  --body "$(cat <<'EOF'
## Summary
- FastAPI WebSocket server receives robot events from Godot
- Per-robot async event queue feeds prompt builder
- Prompt builder merges robot config + runtime stats + player instructions + environment context
- Ollama client queries Dolphin-Mistral 7B asynchronously
- Action parser extracts typed Pydantic actions from LLM response
- Config loader reads all JSON data files from data/
- 4 robot configs, 3 mission configs, 1 map config, zombie enemy config

## Test plan
- [ ] `pytest backend/tests/ -v` passes all tests
- [ ] `uvicorn backend.main:app --port 8765` starts without errors
- [ ] Manual WebSocket smoke test returns a valid robot action
- [ ] Ollama Dolphin-Mistral model is available via `ollama list`

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## All Tests Passing Check

```bash
pytest backend/tests/ -v --tb=short
```

Expected final output:
```
tests/test_action_parser.py::test_parse_clean_json_move PASSED
tests/test_action_parser.py::test_parse_clean_json_attack PASSED
tests/test_action_parser.py::test_parse_json_embedded_in_prose PASSED
tests/test_action_parser.py::test_parse_invalid_json_returns_idle PASSED
tests/test_action_parser.py::test_parse_unknown_action_returns_idle PASSED
tests/test_action_parser.py::test_parse_build_action PASSED
tests/test_action_parser.py::test_parse_retreat_action PASSED
tests/test_config_loader.py::test_load_robot_config PASSED
tests/test_config_loader.py::test_load_all_robots PASSED
tests/test_config_loader.py::test_load_map_config PASSED
tests/test_config_loader.py::test_load_mission_config PASSED
tests/test_config_loader.py::test_load_enemy_config PASSED
tests/test_config_loader.py::test_missing_robot_raises PASSED
tests/test_event_queue.py::test_enqueue_and_dequeue PASSED
tests/test_event_queue.py::test_queue_is_per_robot PASSED
tests/test_event_queue.py::test_dequeue_empty_returns_none PASSED
tests/test_event_queue.py::test_coalescing_keeps_latest_event PASSED
tests/test_event_queue.py::test_coalescing_does_not_affect_other_robots PASSED
tests/test_models.py::test_robot_event_valid PASSED
tests/test_models.py::test_move_action_valid PASSED
tests/test_models.py::test_attack_action_valid PASSED
tests/test_models.py::test_build_action_valid PASSED
tests/test_models.py::test_retreat_action_valid PASSED
tests/test_models.py::test_support_action_heal PASSED
tests/test_models.py::test_support_action_idle PASSED
tests/test_models.py::test_parse_robot_action_move PASSED
tests/test_models.py::test_parse_robot_action_attack PASSED
tests/test_models.py::test_ws_incoming_valid PASSED
tests/test_models.py::test_ws_incoming_to_robot_event PASSED
tests/test_models.py::test_ws_outgoing_valid PASSED
tests/test_prompt_builder.py::test_prompt_contains_personality PASSED
tests/test_prompt_builder.py::test_prompt_contains_event PASSED
tests/test_prompt_builder.py::test_prompt_contains_strategic_positions PASSED
tests/test_prompt_builder.py::test_intelligence_truncates_player_instructions PASSED
tests/test_prompt_builder.py::test_prompt_contains_commander_broadcast PASSED
tests/test_prompt_builder.py::test_prompt_ends_with_json_instruction PASSED
tests/test_robot_state.py::test_register_robot PASSED
tests/test_robot_state.py::test_update_health PASSED
tests/test_robot_state.py::test_robot_dies_at_zero_health PASSED
tests/test_robot_state.py::test_update_position PASSED
tests/test_robot_state.py::test_set_current_action PASSED
tests/test_robot_state.py::test_get_missing_robot_raises PASSED

42 passed in X.XXs
```
