# PR 1: Core Combat Fix -- Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix unreliable damage, add body blocking, introduce weapon data system with attack speed, add attack lock state machine, and fix zombie target tracking.

**Architecture:** Extract attack logic from Robot.gd into a new AttackComponent child node with a windup/recovery state machine. Weapon stats move from hardcoded robot configs into separate JSON files loaded by ConfigLoader. Zombies switch from per-frame re-targeting to persistent target tracking. Body blocking uses Godot collision layers. Backend prompt builder updated to render weapon info instead of removed stat fields.

**Tech Stack:** Godot 4 (GDScript), Python 3.11+ (FastAPI), JSON config files

---

## File Map

### New Files
| File | Responsibility |
|------|---------------|
| `data/weapons/broadsword.json` | Rex's melee weapon stats |
| `data/weapons/sniper_rifle.json` | Aurora's ranged weapon stats |
| `data/weapons/smg.json` | Hana's ranged weapon stats |
| `data/weapons/energy_pistol.json` | Lily's ranged weapon stats |
| `godot/scenes/robots/AttackComponent.gd` | Attack lock state machine, weapon handling, clip tracking stub, action buffering |

### Modified Files
| File | Changes |
|------|---------|
| `data/robots/archetypes/vanguard_common_rex.json` | Remove damage/attack_range/ammo from base_stats, add weapon_id |
| `data/robots/archetypes/striker_common_aurora.json` | Same migration |
| `data/robots/archetypes/architect_common_hana.json` | Same migration |
| `data/robots/archetypes/medic_common_lily.json` | Same migration |
| `data/enemies/zombie.json` | No change (attack_rate already present, Zombie.gd will start reading it) |
| `godot/scripts/ConfigLoader.gd` | Add get_weapon(), fix list_dir_end() leaks |
| `godot/scenes/robots/Robot.gd` | Delegate attack to AttackComponent, add heal() public method, weapon loading, MOVEMENT_BLOCKED stuck detection, remove damage*3 |
| `godot/scenes/robots/Robot.tscn` | Change collision shape to CircleShape2D(20), set layers/masks, add AttackComponent node |
| `godot/scenes/enemies/Zombie.gd` | Persistent target tracking, read attack_rate from config, cached re-targeting |
| `godot/scenes/enemies/Zombie.tscn` | Change collision shape to CircleShape2D(16), set layers 2, masks 1+2+3 |
| `godot/scenes/map/Map.tscn` | Base collision layer 3, masks 1+2 (convert Base from Node2D to StaticBody2D) |
| `godot/scenes/map/Map.gd` | No script changes needed |
| `backend/models.py` | Add WEAPON_RELOADING and MOVEMENT_BLOCKED to EventType enum |
| `backend/prompt_builder.py` | Replace stats['damage']/stats['ammo'] with weapon info |
| `backend/robot_state.py` | Replace ammo field with weapon_state dict |
| `backend/main.py` | Update register_robot and state_update to use weapon_state instead of ammo |
| `godot/scripts/WebSocketClient.gd` | Update register_robot/send_state_update signatures (weapon_state replaces ammo) |
| `backend/mock_llm.py` | Fix comment about target_id type |
| `backend/tests/test_config_loader.py` | Add weapon loading tests |
| `backend/tests/test_prompt_builder.py` | Update for new prompt format |

---

## Task 1: Weapon Data Files + ConfigLoader.get_weapon()

**Files:**
- Create: `data/weapons/broadsword.json`, `data/weapons/sniper_rifle.json`, `data/weapons/smg.json`, `data/weapons/energy_pistol.json`
- Modify: `backend/config_loader.py`
- Modify: `godot/scripts/ConfigLoader.gd`
- Test: `backend/tests/test_config_loader.py`

- [ ] **Step 1: Create the data/weapons/ directory and all 4 weapon JSON files**

```bash
mkdir -p data/weapons
```

`data/weapons/broadsword.json`:
```json
{
  "id": "broadsword",
  "name": "Vanguard Broadsword",
  "class": "broadsword",
  "type": "melee",
  "damage": 18,
  "range": 60,
  "attack_speed": 1.5
}
```

`data/weapons/sniper_rifle.json`:
```json
{
  "id": "sniper_rifle",
  "name": "Hawkeye MK-IV",
  "class": "sniper_rifle",
  "type": "ranged",
  "damage": 27,
  "range": 200,
  "attack_speed": 2.0,
  "clip_size": 5,
  "reload_time": 3.0
}
```

`data/weapons/smg.json`:
```json
{
  "id": "smg",
  "name": "Ironworks SMG",
  "class": "smg",
  "type": "ranged",
  "damage": 6,
  "range": 80,
  "attack_speed": 0.3,
  "clip_size": 30,
  "reload_time": 2.0
}
```

`data/weapons/energy_pistol.json`:
```json
{
  "id": "energy_pistol",
  "name": "Medi-Pulse Pistol",
  "class": "energy_pistol",
  "type": "ranged",
  "damage": 8,
  "range": 60,
  "attack_speed": 0.8,
  "clip_size": 12,
  "reload_time": 1.5
}
```

- [ ] **Step 2: Write failing tests for Python ConfigLoader weapon loading**

Add to `backend/tests/test_config_loader.py`:

```python
def test_load_weapon_config():
    loader = ConfigLoader(DATA_DIR)
    weapon = loader.get_weapon("broadsword")
    assert weapon["name"] == "Vanguard Broadsword"
    assert weapon["type"] == "melee"
    assert weapon["damage"] == 18
    assert weapon["range"] == 60
    assert weapon["attack_speed"] == 1.5


def test_load_all_weapons():
    loader = ConfigLoader(DATA_DIR)
    weapons = loader.get_all_weapons()
    assert len(weapons) == 4
    weapon_ids = {w["id"] for w in weapons}
    assert weapon_ids == {"broadsword", "sniper_rifle", "smg", "energy_pistol"}


def test_missing_weapon_raises():
    loader = ConfigLoader(DATA_DIR)
    with pytest.raises(KeyError):
        loader.get_weapon("nonexistent_weapon")


def test_ranged_weapon_has_clip_fields():
    loader = ConfigLoader(DATA_DIR)
    sniper = loader.get_weapon("sniper_rifle")
    assert sniper["clip_size"] == 5
    assert sniper["reload_time"] == 3.0


def test_melee_weapon_has_no_clip_fields():
    loader = ConfigLoader(DATA_DIR)
    sword = loader.get_weapon("broadsword")
    assert "clip_size" not in sword
    assert "reload_time" not in sword
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_config_loader.py -v`
Expected: FAIL -- `ConfigLoader` has no `get_weapon` method

- [ ] **Step 4: Implement get_weapon() and get_all_weapons() in Python ConfigLoader**

Add to `backend/config_loader.py` in `__init__`:
```python
self._weapons: dict = {}
```

Add to `_load_all()`:
```python
weapons_dir = self._data_dir / "weapons"
if weapons_dir.exists():
    for path in weapons_dir.glob("*.json"):
        cfg = self._load_json(path)
        self._weapons[cfg["id"]] = cfg
```

Add methods:
```python
def get_weapon(self, weapon_id: str) -> dict:
    if weapon_id not in self._weapons:
        raise KeyError(f"Weapon not found: {weapon_id}")
    return self._weapons[weapon_id]

def get_all_weapons(self) -> list[dict]:
    return list(self._weapons.values())
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_config_loader.py -v`
Expected: ALL PASS

- [ ] **Step 6: Add get_weapon() to Godot ConfigLoader**

Modify `godot/scripts/ConfigLoader.gd`. Add `var _weapons: Dictionary = {}` to the top variables.

Add `_load_weapons()` call to `_ready()`.

Add the loading function:
```gdscript
func _load_weapons() -> void:
	var dir = DirAccess.open("res://data/weapons")
	if dir == null:
		push_error("ConfigLoader: cannot open data/weapons")
		return
	dir.list_dir_begin()
	var file_name = dir.get_next()
	while file_name != "":
		if file_name.ends_with(".json"):
			var cfg = _load_json("res://data/weapons/" + file_name)
			if cfg:
				_weapons[cfg["id"]] = cfg
		file_name = dir.get_next()
	dir.list_dir_end()

func get_weapon(weapon_id: String) -> Dictionary:
	if not _weapons.has(weapon_id):
		push_error("ConfigLoader: weapon not found: " + weapon_id)
		return {"id": weapon_id, "name": "Fallback", "class": "unknown", "type": "melee", "damage": 1, "range": 50, "attack_speed": 1.0}
	return _weapons[weapon_id]
```

- [ ] **Step 7: Fix list_dir_end() leaks in all existing ConfigLoader functions**

Add `dir.list_dir_end()` after each `while` loop in `_load_robots()`, `_load_maps()`, `_load_enemies()`, and `_load_missions_from_dir()`. Example for `_load_robots()`:

```gdscript
func _load_robots() -> void:
	var dir = DirAccess.open("res://data/robots/archetypes")
	if dir == null:
		push_error("ConfigLoader: cannot open data/robots/archetypes")
		return
	dir.list_dir_begin()
	var file_name = dir.get_next()
	while file_name != "":
		if file_name.ends_with(".json"):
			var cfg = _load_json("res://data/robots/archetypes/" + file_name)
			if cfg:
				_robots[cfg["id"]] = cfg
		file_name = dir.get_next()
	dir.list_dir_end()
```

Same pattern for `_load_maps()`, `_load_enemies()`, `_load_missions_from_dir()`.

- [ ] **Step 8: Symlink/copy weapons directory into godot/data/**

The Godot project uses `res://data/` which maps to `godot/data/`. The repo root `data/` is the source of truth. Check if `godot/data/` is a symlink or copy of `data/`. If it's a symlink, weapons will auto-appear. If it's a copy, copy `data/weapons/` into `godot/data/weapons/`.

```bash
# Check if godot/data is a symlink
ls -la godot/data
# If not a symlink, copy:
cp -r data/weapons godot/data/weapons
```

- [ ] **Step 9: Commit**

```bash
git add data/weapons/ godot/data/weapons/ godot/scripts/ConfigLoader.gd backend/config_loader.py backend/tests/test_config_loader.py
git commit -m "feat: add weapon data system and ConfigLoader.get_weapon()"
```

---

## Task 2: Robot Config Migration + Backend Updates

**Files:**
- Modify: `data/robots/archetypes/vanguard_common_rex.json`
- Modify: `data/robots/archetypes/striker_common_aurora.json`
- Modify: `data/robots/archetypes/architect_common_hana.json`
- Modify: `data/robots/archetypes/medic_common_lily.json`
- Modify: `backend/models.py`
- Modify: `backend/prompt_builder.py`
- Modify: `backend/robot_state.py`
- Modify: `backend/main.py`
- Modify: `backend/mock_llm.py`
- Modify: `godot/scripts/WebSocketClient.gd`
- Test: `backend/tests/test_prompt_builder.py`

- [ ] **Step 1: Migrate all 4 robot JSON configs**

Remove `damage`, `attack_range`, `ammo` from `base_stats`. Add `weapon_id` at the top level.

`data/robots/archetypes/vanguard_common_rex.json`:
```json
{
  "id": "vanguard_common_rex",
  "name": "Rex",
  "class": "vanguard",
  "rarity": "common",
  "description": "A fearless frontline tank who throws himself between enemies and allies. Rex never retreats first.",
  "weapon_id": "broadsword",
  "base_stats": {
    "speed": 5,
    "armor": 8,
    "health": 400,
    "building_skill": 2,
    "intelligence": 3
  },
  "personality_prompt": "You are Rex, a fearless Vanguard. You charge enemies to protect your allies. You position yourself between threats and the base. You never abandon a chokepoint unless critically wounded. You talk tough and encourage teammates. You refuse to sit back when allies are in danger.",
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
  "description": "A precise long-range fighter who picks off targets from a safe distance. Aurora wastes nothing.",
  "weapon_id": "sniper_rifle",
  "base_stats": {
    "speed": 7,
    "armor": 3,
    "health": 180,
    "building_skill": 1,
    "intelligence": 4
  },
  "personality_prompt": "You are Aurora, a precise Striker. You pick off high-value targets from optimal range. You avoid close combat and conserve ammo for critical shots. You reposition constantly to maintain sight lines. You refuse to engage in melee and will retreat before letting enemies close in. You call out priority targets for the team.",
  "portrait": "res://assets/robots/aurora/portrait.png",
  "sprite": "res://assets/robots/aurora/sprite.png"
}
```

`data/robots/archetypes/architect_common_hana.json`:
```json
{
  "id": "architect_common_hana",
  "name": "Hana",
  "class": "architect",
  "rarity": "common",
  "description": "A methodical builder who fortifies positions before the enemy arrives. Hana thinks three steps ahead.",
  "weapon_id": "smg",
  "base_stats": {
    "speed": 4,
    "armor": 5,
    "health": 200,
    "building_skill": 7,
    "intelligence": 5
  },
  "personality_prompt": "You are Hana, a methodical Architect. You prioritize building fortifications before engaging enemies. You think several steps ahead and position structures to create chokepoints. You prefer walls and barricades over direct combat. You refuse to rush into fights without defenses in place. You refer to allies by name and suggest where they should position.",
  "portrait": "res://assets/robots/hana/portrait.png",
  "sprite": "res://assets/robots/hana/sprite.png"
}
```

`data/robots/archetypes/medic_common_lily.json`:
```json
{
  "id": "medic_common_lily",
  "name": "Lily",
  "class": "medic",
  "rarity": "common",
  "description": "A caring support unit who keeps the team alive from behind the front line. Lily prioritizes the most wounded.",
  "weapon_id": "energy_pistol",
  "base_stats": {
    "speed": 5,
    "armor": 4,
    "health": 220,
    "building_skill": 3,
    "intelligence": 6
  },
  "personality_prompt": "You are Lily, a caring Medic. You monitor your allies' health and heal those in danger. You stay behind the front line and support the team. You refuse to move to the front when allies need healing. You announce when teammates are critical and prioritize the most damaged ally. You only attack when no one needs healing.",
  "portrait": "res://assets/robots/lily/portrait.png",
  "sprite": "res://assets/robots/lily/sprite.png"
}
```

Copy updated configs to `godot/data/` if not symlinked.

- [ ] **Step 2: Add WEAPON_RELOADING and MOVEMENT_BLOCKED to EventType enum**

In `backend/models.py`, add to the `EventType` enum:
```python
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
    WEAPON_RELOADING = "WEAPON_RELOADING"
    MOVEMENT_BLOCKED = "MOVEMENT_BLOCKED"
```

- [ ] **Step 3: Update RobotState to replace ammo with weapon_state**

In `backend/robot_state.py`, replace the `ammo` field:
```python
@dataclass
class RobotState:
    robot_id: str
    health: int
    max_health: int
    position: tuple[float, float]
    current_action: Optional[str] = None
    is_alive: bool = True
    weapon_state: Optional[dict] = None
```

Update `register()` signature:
```python
def register(self, robot_id: str, health: int, max_health: int, position: tuple[float, float], weapon_state: Optional[dict] = None) -> None:
    self._states[robot_id] = RobotState(
        robot_id=robot_id,
        health=health,
        max_health=max_health,
        position=position,
        weapon_state=weapon_state,
    )
```

Add:
```python
def update_weapon_state(self, robot_id: str, weapon_state: dict) -> None:
    self.get(robot_id).weapon_state = weapon_state
```

- [ ] **Step 4: Update main.py register_robot and state_update handlers**

In `backend/main.py`, update the `register_robot` handler:
```python
if data.get("type") == "register_robot":
    robot_id = data["robot_id"]
    robot_state_store.register(
        robot_id=robot_id,
        health=data["health"],
        max_health=data["health"],
        position=tuple(data["position"]),
        weapon_state=data.get("weapon_state"),
    )
```

Update the `state_update` handler:
```python
if data.get("type") == "state_update":
    robot_id = data["robot_id"]
    if "health" in data:
        robot_state_store.update_health(robot_id, data["health"])
    if "position" in data:
        robot_state_store.update_position(robot_id, tuple(data["position"]))
    if "weapon_state" in data:
        robot_state_store.update_weapon_state(robot_id, data["weapon_state"])
    continue
```

- [ ] **Step 5: Write failing test for updated prompt builder**

Update `backend/tests/test_prompt_builder.py`. Change ROBOT_CONFIG to match new schema:

```python
ROBOT_CONFIG = {
    "name": "Hana",
    "class": "architect",
    "rarity": "common",
    "personality_prompt": "You are Hana, a methodical Architect.",
    "weapon_id": "smg",
    "base_stats": {"speed": 4, "armor": 5, "health": 100, "building_skill": 7, "intelligence": 5}
}

WEAPON_CONFIG = {
    "id": "smg",
    "name": "Ironworks SMG",
    "class": "smg",
    "type": "ranged",
    "damage": 6,
    "range": 80,
    "attack_speed": 0.3,
    "clip_size": 30,
    "reload_time": 2.0
}

ROBOT_RUNTIME_STATS = {"health": 80, "weapon_state": {"clip": 25, "max_clip": 30, "is_reloading": False}}
```

Update all test calls to pass weapon config:
```python
def test_prompt_contains_weapon_info():
    builder = PromptBuilder()
    prompt = builder.build(ROBOT_CONFIG, WEAPON_CONFIG, ROBOT_RUNTIME_STATS, _make_event())
    assert "Ironworks SMG" in prompt
    assert "damage=6" in prompt
    assert "range=80" in prompt


def test_prompt_contains_weapon_state():
    builder = PromptBuilder()
    prompt = builder.build(ROBOT_CONFIG, WEAPON_CONFIG, ROBOT_RUNTIME_STATS, _make_event())
    assert "25/30" in prompt or "clip" in prompt.lower()
```

- [ ] **Step 6: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_prompt_builder.py -v`
Expected: FAIL -- `build()` signature changed

- [ ] **Step 7: Update prompt_builder.py**

Replace `backend/prompt_builder.py` `build()` method to accept weapon_config:

```python
class PromptBuilder:
    def build(self, robot_config: dict, weapon_config: dict, runtime_stats: dict, event: RobotEvent) -> str:
        stats = robot_config["base_stats"]
        intelligence = stats["intelligence"]
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

        # Weapon info
        weapon_name = weapon_config.get("name", "Unknown")
        weapon_damage = weapon_config.get("damage", 0)
        weapon_range = weapon_config.get("range", 0)
        weapon_type = weapon_config.get("type", "unknown")
        attack_speed = weapon_config.get("attack_speed", 1.0)

        # Weapon state from runtime
        weapon_state = runtime_stats.get("weapon_state", {})
        clip = weapon_state.get("clip", weapon_config.get("clip_size", 0))
        max_clip = weapon_state.get("max_clip", weapon_config.get("clip_size", 0))
        is_reloading = weapon_state.get("is_reloading", False)

        if weapon_type == "melee":
            weapon_line = f"Weapon: {weapon_name} ({weapon_type}, damage={weapon_damage}, range={weapon_range}, speed={attack_speed}s)"
        else:
            reload_status = "reloading" if is_reloading else "ready"
            weapon_line = f"Weapon: {weapon_name} ({weapon_type}, damage={weapon_damage}, range={weapon_range}, speed={attack_speed}s, ammo={clip}/{max_clip}, {reload_status})"

        return f"""[System]
You are {robot_config['name']}, a {robot_config['rarity']} {robot_config['class']} robot. {robot_config['personality_prompt']}
Your stats: speed={stats['speed']}, armor={stats['armor']}, health={health}/{stats['health']}, building_skill={stats['building_skill']}
{weapon_line}

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
You MUST respond with ONLY a JSON object. No other text.
Valid actions: move, attack, snipe, build, deploy_turret, retreat, heal, idle.
Enemy target_id values are small sequential integers (1, 2, 3...) as shown in the enemy list above.

PRIORITY RULES:
1. If enemies are nearby, you MUST attack or snipe. Do NOT move or idle when enemies are present.
2. If you are a medic and an ally has low health, you MUST heal them.
3. Only move if no enemies are nearby and you need to reposition.
4. Only idle if there is truly nothing to do.

Example: {{"action": "attack", "target_id": 1, "approach": "close_in", "reason": "Enemy nearby, engaging"}}
Example: {{"action": "snipe", "target_id": 2, "approach": "maintain_range", "reason": "Picking off target at range"}}
Example: {{"action": "heal", "target_id": 2, "reason": "Ally at low health"}}
Example: {{"action": "move", "destination": "north_chokepoint", "reason": "Repositioning to chokepoint"}}
Example: {{"action": "build", "structure": "wall", "destination": "north_chokepoint", "reason": "Fortifying position"}}
"""
```

- [ ] **Step 8: Update main.py to pass weapon_config to prompt_builder**

In `backend/main.py`, update `process_robot_events()`:

```python
async def process_robot_events(robot_id: str, websocket: WebSocket) -> None:
    robot_config = config_loader.get_robot(robot_id)
    weapon_id = robot_config.get("weapon_id", "broadsword")
    try:
        weapon_config = config_loader.get_weapon(weapon_id)
    except KeyError:
        weapon_config = {"id": weapon_id, "name": "Fallback", "type": "melee", "damage": 1, "range": 50, "attack_speed": 1.0}
    try:
        while True:
            event = await event_queue.dequeue(robot_id)
            try:
                state = robot_state_store.get(robot_id)
            except KeyError:
                continue

            if not state.is_alive:
                continue

            try:
                runtime_stats = {"health": state.health, "weapon_state": state.weapon_state or {}}
                prompt = prompt_builder.build(robot_config, weapon_config, runtime_stats, event)
                async with _ollama_semaphore:
                    llm_response = await ollama_client.think(prompt)
                action = action_parser.parse(llm_response)
            except Exception as e:
                logger.error(f"LLM processing failed for {robot_id}: {e}")
                action = SupportAction(action="idle", reason=f"LLM error: {type(e).__name__}")

            robot_state_store.set_current_action(robot_id, action.action)

            outgoing = WsOutgoing(type="robot_action", robot_id=robot_id, action=action)
            async with _ws_send_lock:
                await websocket.send_text(outgoing.model_dump_json())
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Processor task for {robot_id} died: {e}")
```

- [ ] **Step 9: Fix mock_llm.py target_id comment**

In `backend/mock_llm.py` line 74, change:
```python
# target_id must be int to match SupportAction schema; use index as fallback
```
to:
```python
# target_id can be int or string per SupportAction schema; prefer ally id, fall back to index
```

- [ ] **Step 10: Update all existing prompt_builder tests to new signature**

All calls to `builder.build()` must now pass 4 args: `(ROBOT_CONFIG, WEAPON_CONFIG, ROBOT_RUNTIME_STATS, event)`. Update every existing test function's `build()` call.

- [ ] **Step 11: Run all backend tests**

Run: `cd backend && python -m pytest -v`
Expected: ALL PASS

- [ ] **Step 12: Update WebSocketClient.gd to send weapon_state instead of ammo**

In `godot/scripts/WebSocketClient.gd`, update `register_robot`:
```gdscript
func register_robot(robot_id: String, health: int, position: Vector2, weapon_state: Dictionary = {}) -> void:
	_send({
		"type": "register_robot",
		"robot_id": robot_id,
		"health": health,
		"position": [position.x, position.y],
		"weapon_state": weapon_state
	})
```

Update `send_state_update`:
```gdscript
func send_state_update(robot_id: String, health: int, position: Vector2, weapon_state: Dictionary = {}) -> void:
	_send({
		"type": "state_update",
		"robot_id": robot_id,
		"health": health,
		"position": [position.x, position.y],
		"weapon_state": weapon_state
	})
```

- [ ] **Step 13: Commit**

```bash
git add data/robots/archetypes/ backend/models.py backend/prompt_builder.py backend/robot_state.py backend/main.py backend/mock_llm.py backend/tests/test_prompt_builder.py godot/scripts/WebSocketClient.gd
git commit -m "feat: migrate robot configs to weapon_id, update backend prompt and state for weapon system"
```

---

## Task 3: AttackComponent Extraction

**Files:**
- Create: `godot/scenes/robots/AttackComponent.gd`
- Modify: `godot/scenes/robots/Robot.gd`
- Modify: `godot/scenes/robots/Robot.tscn`

This task extracts attack logic into AttackComponent WITHOUT changing behavior yet. Same 1.0s timer, same damage*3 logic -- just reorganized. The attack lock state machine comes in Task 5.

- [ ] **Step 1: Create AttackComponent.gd**

```gdscript
extends Node

signal attack_damage_applied(target: Node2D, damage: int)
signal attack_started(target: Node2D)
signal windup_finished()

const ATTACK_RANGE_BUFFER = 1.3

var _weapon: Dictionary = {}
var _target: Node2D = null
var _attack_timer: Timer = null
var _is_winding_up: bool = false
var _buffered_action: Dictionary = {}

# State machine: IDLE -> WINDUP -> RECOVERY -> IDLE
enum State { IDLE, WINDUP, RECOVERY }
var _state: int = State.IDLE

func setup(weapon: Dictionary, attack_timer: Timer) -> void:
	_weapon = weapon
	_attack_timer = attack_timer
	_attack_timer.timeout.connect(_on_attack_timer)

func get_weapon() -> Dictionary:
	return _weapon

func get_weapon_range() -> float:
	return float(_weapon.get("range", 50))

func get_weapon_damage() -> int:
	return int(_weapon.get("damage", 1))

func get_attack_speed() -> float:
	return float(_weapon.get("attack_speed", 1.0))

func is_winding_up() -> bool:
	return _is_winding_up

func get_target() -> Node2D:
	return _target

func start_attack(target: Node2D) -> void:
	_target = target
	attack_started.emit(target)
	if _attack_timer.is_stopped():
		_perform_attack()
		_attack_timer.wait_time = get_attack_speed()
		_attack_timer.start()

func stop_attack() -> void:
	_target = null
	_attack_timer.stop()
	_state = State.IDLE
	_is_winding_up = false

func has_target() -> bool:
	return _target != null and is_instance_valid(_target)

func buffer_action(action: Dictionary) -> void:
	_buffered_action = action

func pop_buffered_action() -> Dictionary:
	var action = _buffered_action
	_buffered_action = {}
	return action

func _perform_attack() -> void:
	if _target == null or not is_instance_valid(_target):
		return
	var parent = get_parent()
	if parent == null:
		return
	var dist = parent.global_position.distance_to(_target.global_position)
	var weapon_range = get_weapon_range()
	if dist > weapon_range:
		return
	var damage = get_weapon_damage()
	attack_damage_applied.emit(_target, damage)

func _on_attack_timer() -> void:
	if not has_target():
		stop_attack()
		return
	_perform_attack()
```

- [ ] **Step 2: Add AttackComponent node to Robot.tscn**

Add this node entry to `Robot.tscn` after the AttackTimer node:
```
[ext_resource type="Script" path="res://scenes/robots/AttackComponent.gd" id="3"]

[node name="AttackComponent" type="Node" parent="."]
script = ExtResource("3")
```

- [ ] **Step 3: Refactor Robot.gd to use AttackComponent**

Key changes to Robot.gd:

Add `@onready var attack_component: Node = $AttackComponent` at the top.

In `setup()`, load weapon and pass to AttackComponent:
```gdscript
var weapon_id = config.get("weapon_id", "broadsword")
var weapon = ConfigLoader.get_weapon(weapon_id)
attack_component.setup(weapon, attack_timer)
attack_component.attack_damage_applied.connect(_on_attack_damage_applied)
```

Remove the old `attack_timer.timeout.connect(_on_attack_timer)` line.
Remove the old `attack_timer.wait_time = 1.0` line.

Replace `_perform_attack()` with delegation:
```gdscript
func _on_attack_damage_applied(target: Node2D, damage: int) -> void:
	GameRecorder.log_attack(robot_id, GameManager.get_enemy_id(target), damage)
	if target.has_method("take_damage"):
		target.take_damage(damage)
	_push_recent_event("ENEMY_ATTACKED: " + str(target.name))
	var weapon_state = _build_weapon_state()
	WebSocketClient.send_state_update(robot_id, _health, global_position, weapon_state)
```

Remove `_ammo`, `_ammo_low_fired`, `resupply_ammo()`, and the AMMO_LOW event logic. These will be re-added in PR 2 (Reload System) via the AttackComponent.

Update `_auto_attack_if_idle()` to use `attack_component`:
```gdscript
func _auto_attack_if_idle() -> void:
	if not attack_component.has_target() and not _enemies_in_perception.is_empty():
		var action_name = _current_action.get("action", "idle")
		if action_name in ["idle", "move", "retreat", "", "build", "deploy_turret"]:
			var nearest: Node2D = null
			var nearest_dist := 999999.0
			for e in _enemies_in_perception:
				if is_instance_valid(e):
					var d = global_position.distance_to(e.global_position)
					if d < nearest_dist:
						nearest_dist = d
						nearest = e
			if nearest:
				var weapon_range = attack_component.get_weapon_range()
				if nearest_dist <= weapon_range:
					attack_component.start_attack(nearest)
```

Update `execute_action()` attack case:
```gdscript
"attack", "snipe":
	_target_enemy = _find_enemy_by_id(action.get("target_id", -1))
	if _target_enemy:
		attack_component.start_attack(_target_enemy)
```

Update `_check_enemy_in_range()` to use weapon range:
```gdscript
func _check_enemy_in_range() -> void:
	var weapon_range = attack_component.get_weapon_range()
	for enemy in _enemies_in_perception:
		if is_instance_valid(enemy):
			var dist = global_position.distance_to(enemy.global_position)
			if dist <= weapon_range:
				_fire_event("ENEMY_IN_RANGE",
					str(GameManager.get_enemy_id(enemy)) + " at distance " + str(int(dist)))
				return
```

Remove the old `_on_attack_timer()` and `_perform_attack()` functions.

Update `_die()` to call `attack_component.stop_attack()` instead of `attack_timer.stop()`.

Add `heal()` public method and update `_perform_heal()`:
```gdscript
func heal(amount: int) -> void:
	_health = min(_max_health, _health + amount)
	if _health_bar:
		_health_bar.value = _health

func _perform_heal(action: Dictionary) -> void:
	var target_id = action.get("target_id", null)
	if target_id == null:
		return
	for r in get_tree().get_nodes_in_group("robots"):
		if is_instance_valid(r) and r != self and r.is_alive():
			if r.robot_id == str(target_id) or r.robot_id.ends_with(str(target_id)):
				var heal_amount = _config["base_stats"].get("intelligence", 5) * 5
				r.heal(heal_amount)
				GameRecorder.log_heal(robot_id, r.robot_id, heal_amount)
				_push_recent_event("HEALED: " + r.robot_id + " for " + str(heal_amount))
				var weapon_state = _build_weapon_state()
				WebSocketClient.send_state_update(r.robot_id, r._health, r.global_position, weapon_state)
				return
	_push_recent_event("HEAL_FAILED: target " + str(target_id) + " not found")
```

Add `_build_weapon_state()`:
```gdscript
func _build_weapon_state() -> Dictionary:
	var weapon = attack_component.get_weapon()
	return {
		"weapon_name": weapon.get("name", "Unknown"),
		"clip": weapon.get("clip_size", 0),
		"max_clip": weapon.get("clip_size", 0),
		"is_reloading": false
	}
```

Update `setup()` to register with new WebSocket signature:
```gdscript
WebSocketClient.register_robot(robot_id, _health, global_position, _build_weapon_state())
```

Update `take_damage()` WebSocket call:
```gdscript
WebSocketClient.send_state_update(robot_id, _health, global_position, _build_weapon_state())
```

Remove the `_ammo` variable, `_ammo_low_fired`, and all `_ammo` references. Remove `get_ammo()` -- this will need updating in Game.gd and CampaignManager.

Update `_build_local_context()` to include weapon_state:
```gdscript
# Add weapon_state to local context
return {
	"nearby_enemies": enemies,
	"nearby_allies": allies,
	"structures": [],
	"recent_events": _recent_events.duplicate(),
	"strategic_positions": positions,
}
```

- [ ] **Step 4: Update Game.gd to remove ammo references**

In `godot/scenes/Game.gd`, update lines 38-40 that restore health/ammo:
```gdscript
for robot in get_tree().get_nodes_in_group("robots"):
	if is_instance_valid(robot):
		var rid = robot.robot_id
		var saved_hp = CampaignManager.get_robot_health(rid, robot._max_health)
		robot._health = saved_hp
		if robot._health_bar:
			robot._health_bar.value = saved_hp
```

Update `_save_robot_states()`:
```gdscript
func _save_robot_states() -> void:
	for robot in GameManager._robots:
		if is_instance_valid(robot):
			CampaignManager.save_robot_state(robot.robot_id, robot.get_health(), 0)
```

- [ ] **Step 5: Run the game to verify no crashes**

Run: `bash run_e2e.sh` or manually launch the Godot game.
Expected: Game runs, robots attack enemies, no script errors. Damage values should now come from weapon data (18 for Rex instead of old 6*3=18 -- same net damage, confirming the migration is correct).

- [ ] **Step 6: Commit**

```bash
git add godot/scenes/robots/AttackComponent.gd godot/scenes/robots/Robot.gd godot/scenes/robots/Robot.tscn godot/scenes/Game.gd
git commit -m "refactor: extract AttackComponent from Robot.gd, delegate attack logic to child node"
```

---

## Task 4: Zombie Target Tracking Fix

**Files:**
- Modify: `godot/scenes/enemies/Zombie.gd`

- [ ] **Step 1: Rewrite Zombie.gd with persistent target tracking**

Replace `godot/scenes/enemies/Zombie.gd`:

```gdscript
extends CharacterBody2D

signal died(zombie: Node2D)

@onready var nav_agent: NavigationAgent2D = $NavAgent
@onready var attack_timer: Timer = $AttackTimer

var _health: int = 50
var _max_health: int = 50
var _speed: float = 60.0
var _damage: int = 8
var _attack_range: float = 45.0
var _base_target: Node2D = null
var _base_position: Vector2 = Vector2.ZERO
var _current_target: Node2D = null
var _health_bar: ProgressBar = null
var _target_lost_timer: float = 0.0
const TARGET_LOST_TIMEOUT = 3.0

func setup(config: Dictionary, map: Node2D) -> void:
	var stats = config["stats"]
	_health = stats["health"]
	_max_health = stats["health"]
	_speed = stats["speed"] * 20.0
	_damage = stats["damage"]
	_attack_range = stats["attack_range"]
	_base_target = map
	_base_position = map.get_base_position()
	_current_target = null
	nav_agent.target_position = _base_position
	attack_timer.wait_time = stats.get("attack_rate", 1.0)
	attack_timer.timeout.connect(_on_attack_timer)
	attack_timer.start()
	_setup_health_bar()

func _setup_health_bar() -> void:
	_health_bar = ProgressBar.new()
	_health_bar.max_value = _max_health
	_health_bar.value = _health
	_health_bar.custom_minimum_size = Vector2(30, 3)
	_health_bar.position = Vector2(-15, -25)
	_health_bar.show_percentage = false
	var bg = StyleBoxFlat.new()
	bg.bg_color = Color(0.2, 0.2, 0.2)
	bg.set_content_margin_all(0)
	var fill = StyleBoxFlat.new()
	fill.bg_color = Color(0.8, 0.2, 0.2)
	fill.set_content_margin_all(0)
	_health_bar.add_theme_stylebox_override("background", bg)
	_health_bar.add_theme_stylebox_override("fill", fill)
	add_child(_health_bar)

func _physics_process(delta: float) -> void:
	# Check if current robot target is still valid
	if _current_target != null and _current_target != _base_target:
		if not is_instance_valid(_current_target):
			_current_target = null
			_target_lost_timer = 0.0
		elif _current_target.has_method("is_alive") and not _current_target.is_alive():
			_current_target = null
			_target_lost_timer = 0.0
		else:
			var dist = global_position.distance_to(_current_target.global_position)
			var aggro_range = _attack_range * 3.0
			if dist > aggro_range:
				_target_lost_timer += delta
				if _target_lost_timer >= TARGET_LOST_TIMEOUT:
					_current_target = null
					_target_lost_timer = 0.0
			else:
				_target_lost_timer = 0.0

	# Re-acquire target if needed
	if _current_target == null or _current_target == _base_target:
		var robot = _find_nearest_robot()
		if robot:
			_current_target = robot
			_target_lost_timer = 0.0

	# Move toward current target
	if _current_target != null and _current_target != _base_target and is_instance_valid(_current_target):
		var dist = global_position.distance_to(_current_target.global_position)
		if dist <= _attack_range:
			velocity = Vector2.ZERO
		else:
			nav_agent.target_position = _current_target.global_position
			if not nav_agent.is_navigation_finished():
				var next_pos = nav_agent.get_next_path_position()
				velocity = (next_pos - global_position).normalized() * _speed
	else:
		# Walk toward base
		var dist = global_position.distance_to(_base_position)
		if dist <= _attack_range:
			velocity = Vector2.ZERO
		else:
			nav_agent.target_position = _base_position
			if not nav_agent.is_navigation_finished():
				var next_pos = nav_agent.get_next_path_position()
				velocity = (next_pos - global_position).normalized() * _speed

	move_and_slide()

func _find_nearest_robot() -> Node2D:
	var closest: Node2D = null
	var aggro_range := _attack_range * 3.0
	var closest_dist := aggro_range
	for robot in get_tree().get_nodes_in_group("robots"):
		if not is_instance_valid(robot):
			continue
		if robot.has_method("is_alive") and not robot.is_alive():
			continue
		var dist = global_position.distance_to(robot.global_position)
		if dist < closest_dist:
			closest_dist = dist
			closest = robot
	return closest

func _on_attack_timer() -> void:
	# Attack current target only -- no looping through all robots
	if _current_target != null and _current_target != _base_target and is_instance_valid(_current_target):
		if _current_target.has_method("is_alive") and _current_target.is_alive():
			var dist = global_position.distance_to(_current_target.global_position)
			if dist <= _attack_range and _current_target.has_method("take_damage"):
				_current_target.take_damage(_damage)
				return
	# No robot target in range -- attack base if close enough
	if _base_target and is_instance_valid(_base_target):
		var dist = global_position.distance_to(_base_position)
		if dist <= _attack_range and _base_target.has_method("take_base_damage"):
			_base_target.take_base_damage(_damage)

func take_damage(amount: int) -> void:
	_health = max(0, _health - amount)
	if _health_bar:
		_health_bar.value = _health
	if _health == 0:
		died.emit(self)
		queue_free()

func get_health() -> int:
	return _health
```

Key changes from original:
- `_current_target` starts as `null` (not `map`)
- `_find_nearest_robot()` only called on re-target, NOT every frame
- `_on_attack_timer()` attacks `_current_target` only, no loop
- `attack_timer.wait_time` set from `stats["attack_rate"]` (was hardcoded in .tscn)
- `_target_lost_timer` tracks 3s timeout before dropping target beyond aggro range
- Health bar setup extracted to `_setup_health_bar()` for clarity

- [ ] **Step 2: Run E2E to verify zombie damage consistency**

Run: `bash run_e2e.sh`
Then: `python analyze_recording.py`

Expected: E2E log shows consistent zombie damage events against the same target ID until that target dies. No gaps in damage events. Verify with:
```bash
grep "ATTACK\|DAMAGE_TAKEN" e2e_recording.log | head -50
```

- [ ] **Step 3: Commit**

```bash
git add godot/scenes/enemies/Zombie.gd
git commit -m "fix: zombie persistent target tracking, read attack_rate from config"
```

---

## Task 5: Attack Lock State Machine

**Files:**
- Modify: `godot/scenes/robots/AttackComponent.gd`
- Modify: `godot/scenes/robots/Robot.gd`

- [ ] **Step 1: Implement windup/recovery state machine in AttackComponent**

Replace the contents of `godot/scenes/robots/AttackComponent.gd`:

```gdscript
extends Node

signal attack_damage_applied(target: Node2D, damage: int)
signal attack_started(target: Node2D)
signal windup_finished()

const ATTACK_RANGE_BUFFER = 1.3

var _weapon: Dictionary = {}
var _target: Node2D = null
var _attack_timer: Timer = null
var _windup_timer: Timer = null
var _is_winding_up: bool = false
var _buffered_action: Dictionary = {}
var _can_attack: bool = true

# Attack shake tween reference
var _attack_shake_tween: Tween = null

enum State { IDLE, WINDUP, RECOVERY }
var _state: int = State.IDLE

func setup(weapon: Dictionary, attack_timer: Timer) -> void:
	_weapon = weapon
	_attack_timer = attack_timer
	_attack_timer.wait_time = get_attack_speed()
	_attack_timer.one_shot = true
	_attack_timer.timeout.connect(_on_attack_cooldown_finished)

	_windup_timer = Timer.new()
	_windup_timer.one_shot = true
	_windup_timer.timeout.connect(_on_windup_complete)
	add_child(_windup_timer)

func get_weapon() -> Dictionary:
	return _weapon

func get_weapon_range() -> float:
	return float(_weapon.get("range", 50))

func get_buffered_range() -> float:
	return get_weapon_range() * ATTACK_RANGE_BUFFER

func get_weapon_damage() -> int:
	return int(_weapon.get("damage", 1))

func get_attack_speed() -> float:
	return float(_weapon.get("attack_speed", 1.0))

func is_winding_up() -> bool:
	return _is_winding_up

func get_target() -> Node2D:
	return _target

func has_target() -> bool:
	return _target != null and is_instance_valid(_target)

func start_attack(target: Node2D) -> void:
	if not _can_attack:
		return
	_target = target
	attack_started.emit(target)
	_begin_windup()

func stop_attack() -> void:
	_target = null
	_attack_timer.stop()
	_windup_timer.stop()
	_state = State.IDLE
	_is_winding_up = false
	_can_attack = true

func buffer_action(action: Dictionary) -> void:
	_buffered_action = action

func pop_buffered_action() -> Dictionary:
	var action = _buffered_action
	_buffered_action = {}
	return action

func _begin_windup() -> void:
	_state = State.WINDUP
	_is_winding_up = true
	_can_attack = false
	var windup_time = get_attack_speed() / 2.0
	_windup_timer.wait_time = windup_time
	_windup_timer.start()

func _on_windup_complete() -> void:
	_is_winding_up = false
	_state = State.RECOVERY

	# Check target validity at damage application moment
	if _target == null or not is_instance_valid(_target):
		_state = State.IDLE
		_can_attack = true
		windup_finished.emit()
		return

	if _target.has_method("is_alive") and not _target.is_alive():
		_target = null
		_state = State.IDLE
		_can_attack = true
		windup_finished.emit()
		return

	# Guaranteed hit -- damage applied regardless of current distance
	var damage = get_weapon_damage()
	attack_damage_applied.emit(_target, damage)

	windup_finished.emit()

	# Start cooldown for full attack_speed duration
	_attack_timer.wait_time = get_attack_speed()
	_attack_timer.start()

func _on_attack_cooldown_finished() -> void:
	_state = State.IDLE
	_can_attack = true

	# Auto-re-engage if target still in buffered range
	if has_target():
		var parent = get_parent()
		if parent:
			var dist = parent.global_position.distance_to(_target.global_position)
			if dist <= get_buffered_range():
				_begin_windup()
				return

	# Check for buffered action
	if not _buffered_action.is_empty():
		var action = pop_buffered_action()
		var parent = get_parent()
		if parent and parent.has_method("execute_action"):
			parent.execute_action(action)
```

- [ ] **Step 2: Update Robot.gd to respect windup movement lock**

In Robot.gd `_physics_process()`, gate movement on windup:
```gdscript
func _physics_process(delta: float) -> void:
	if not is_alive():
		return
	if not attack_component.is_winding_up():
		_execute_movement()
	_check_enemy_in_range()
	_auto_attack_if_idle()
	_update_stuck_detection(delta)
```

Update `execute_action()` to buffer actions during windup:
```gdscript
func execute_action(action: Dictionary) -> void:
	if _is_dead:
		return
	# Buffer action if winding up
	if attack_component.is_winding_up():
		attack_component.buffer_action(action)
		return
	_current_action = action
	thinking_label.visible = false
	GameRecorder.log_action_received(robot_id, action)
	attack_component.stop_attack()
	var action_name = action.get("action", "idle")
	if action_name == "build" or action_name == "deploy_turret":
		action_name = "move"
	match action_name:
		"move", "retreat":
			var destination_id = action.get("destination", "")
			if destination_id and _map:
				var target_pos = _map.get_strategic_position(destination_id)
				nav_agent.target_position = target_pos
		"attack", "snipe":
			_target_enemy = _find_enemy_by_id(action.get("target_id", -1))
			if _target_enemy:
				attack_component.start_attack(_target_enemy)
		"heal":
			_perform_heal(action)
		"idle":
			pass
	var reason = action.get("reason", "")
	if reason:
		var hud = get_tree().get_first_node_in_group("hud")
		if hud and hud.has_method("add_log_entry"):
			hud.add_log_entry(_config.get("name", robot_id) + ": " + reason)
```

Update `_auto_attack_if_idle()` to use buffered range for re-engagement check:
```gdscript
func _auto_attack_if_idle() -> void:
	if attack_component.is_winding_up():
		return
	if attack_component.has_target():
		return
	if _enemies_in_perception.is_empty():
		return
	var action_name = _current_action.get("action", "idle")
	if action_name in ["idle", "move", "retreat", "", "build", "deploy_turret"]:
		var nearest: Node2D = null
		var nearest_dist := 999999.0
		for e in _enemies_in_perception:
			if is_instance_valid(e):
				var d = global_position.distance_to(e.global_position)
				if d < nearest_dist:
					nearest_dist = d
					nearest = e
		if nearest:
			var weapon_range = attack_component.get_weapon_range()
			if nearest_dist <= weapon_range:
				attack_component.start_attack(nearest)
```

- [ ] **Step 3: Run E2E to verify consistent damage from all ARIAs**

Run: `bash run_e2e.sh`
Then: `python analyze_recording.py`

Expected: E2E log shows ATTACK events from all 4 ARIAs at their weapon-specific intervals (Rex ~1.5s, Aurora ~2.0s, Hana ~0.3s, Lily ~0.8s). No damage gaps. Verify:
```bash
grep "ATTACK" e2e_recording.log | head -30
```

- [ ] **Step 4: Commit**

```bash
git add godot/scenes/robots/AttackComponent.gd godot/scenes/robots/Robot.gd
git commit -m "feat: attack lock state machine with windup/recovery, guaranteed hits, action buffering"
```

---

## Task 6: Body Blocking + Collision Layers

**Files:**
- Modify: `godot/scenes/robots/Robot.tscn`
- Modify: `godot/scenes/enemies/Zombie.tscn`
- Modify: `godot/scenes/map/Map.tscn`
- Modify: `godot/scenes/map/Map.gd` (minor: no script changes needed but base node type changes)

- [ ] **Step 1: Add BODY_BLOCKING_ENABLED constant to Robot.gd**

At the top of Robot.gd, add:
```gdscript
const BODY_BLOCKING_ENABLED = true
```

This is a toggle for playtesting. Not used in code logic yet (collision layers handle it), but serves as documentation and can be wired up to disable collision masks at runtime if needed.

- [ ] **Step 2: Update Robot.tscn collision shape and layers**

Replace the CapsuleShape2D with CircleShape2D for the body:
```
[sub_resource type="CircleShape2D" id="CircleShape2D_body"]
radius = 20.0
```

Update the Robot node collision properties:
```
[node name="Robot" type="CharacterBody2D"]
collision_layer = 1
collision_mask = 7
```

`collision_mask = 7` means layers 1+2+3 (bitmask: bit1=1 + bit2=2 + bit3=4 = 7): collides with ARIAs (layer 1), enemies (layer 2), and structures (layer 3).

- [ ] **Step 3: Update Zombie.tscn collision shape and layers**

Replace CapsuleShape2D with CircleShape2D:
```
[sub_resource type="CircleShape2D" id="CircleShape2D_body"]
radius = 16.0
```

Update Zombie node:
```
[node name="Zombie" type="CharacterBody2D" groups=["enemies"]]
collision_layer = 2
collision_mask = 7
```

`collision_mask = 7` = layers 1+2+3 (bitmask 1+2+4=7): collides with ARIAs, other zombies, and structures.

- [ ] **Step 4: Update Map.tscn Base to be a StaticBody2D with collision layer 3**

The Base node is currently a plain Node2D with an Area2D child (BaseHitbox). For body blocking, the base needs a physics body. Convert the BaseHitbox Area2D to a StaticBody2D:

Replace the Base section in Map.tscn:
```
[node name="Base" type="Node2D" parent="."]
position = Vector2(960, 900)

[node name="Sprite2D" type="Sprite2D" parent="Base"]
scale = Vector2(0.8, 0.8)
texture = ExtResource("2")

[node name="BaseBody" type="StaticBody2D" parent="Base"]
collision_layer = 4
collision_mask = 3

[node name="CollisionShape2D" type="CollisionShape2D" parent="Base/BaseBody"]
shape = SubResource("CircleShape2D_base")
```

`collision_layer = 4` = layer 3 (bit 3 = value 4).
`collision_mask = 3` = layers 1+2 (bits 1+2 = value 3): blocks robots and zombies.

Keep the old Area2D BaseHitbox for damage detection (zombies use `take_base_damage` through the Map node, not through collision). Actually -- the zombie attacks the base via `_base_target.take_base_damage()` where `_base_target` is the Map node, not the Base node. So the StaticBody2D just needs to physically block movement. The damage path is unchanged.

- [ ] **Step 5: Run E2E to verify body blocking works**

Run: `bash run_e2e.sh`
Then: `python analyze_recording.py`

Expected: Zombies should no longer stack on the base. Rex standing in a path should physically block zombies. Look for:
- Base takes less damage early (zombies blocked by Rex)
- No script errors about collision shapes

- [ ] **Step 6: Commit**

```bash
git add godot/scenes/robots/Robot.tscn godot/scenes/enemies/Zombie.tscn godot/scenes/map/Map.tscn godot/scenes/robots/Robot.gd
git commit -m "feat: body blocking with collision layers, circle collision shapes"
```

---

## Task 7: MOVEMENT_BLOCKED Event + Stuck Detection

**Files:**
- Modify: `godot/scenes/robots/Robot.gd`

- [ ] **Step 1: Add stuck detection variables to Robot.gd**

Add to the variable declarations:
```gdscript
var _last_move_position: Vector2 = Vector2.ZERO
var _stuck_timer: float = 0.0
const STUCK_THRESHOLD_PX = 5.0
const STUCK_TIMEOUT_SEC = 2.0
```

- [ ] **Step 2: Implement _update_stuck_detection() in Robot.gd**

Add this function:
```gdscript
func _update_stuck_detection(delta: float) -> void:
	var action_name = _current_action.get("action", "idle")
	if action_name not in ["move", "retreat", "attack", "snipe"]:
		_stuck_timer = 0.0
		_last_move_position = global_position
		return
	if nav_agent.is_navigation_finished():
		_stuck_timer = 0.0
		_last_move_position = global_position
		return
	var moved = global_position.distance_to(_last_move_position)
	if moved > STUCK_THRESHOLD_PX:
		_stuck_timer = 0.0
		_last_move_position = global_position
		return
	_stuck_timer += delta
	if _stuck_timer >= STUCK_TIMEOUT_SEC:
		_stuck_timer = 0.0
		_last_move_position = global_position
		_fire_event("MOVEMENT_BLOCKED",
			"stuck moving to " + str(nav_agent.target_position))
```

This is already called from `_physics_process()` (added in Task 5 Step 2).

- [ ] **Step 3: Run E2E to verify MOVEMENT_BLOCKED fires when appropriate**

Run: `bash run_e2e.sh`
Then:
```bash
grep "MOVEMENT_BLOCKED" e2e_recording.log
```

Expected: MOVEMENT_BLOCKED events should appear when robots get stuck behind other units due to body blocking. If no events appear, that's acceptable too (means no robots got stuck during the test run).

- [ ] **Step 4: Commit**

```bash
git add godot/scenes/robots/Robot.gd
git commit -m "feat: MOVEMENT_BLOCKED event with stuck detection for body blocking feedback"
```

---

## Task 8: Backend Test Fixes + Final Integration Test

**Files:**
- Modify: `backend/tests/test_integration.py`
- Modify: `backend/tests/test_robot_state.py`
- Modify: `backend/tests/test_mock_llm.py`

- [ ] **Step 1: Update test_integration.py for new WebSocket message format**

The register_robot message no longer sends `ammo`, it sends `weapon_state`. Update the test fixtures accordingly. Find all `"ammo": ...` in register messages and replace with `"weapon_state": {"clip": X, "max_clip": X, "is_reloading": false}`.

- [ ] **Step 2: Update test_robot_state.py for weapon_state field**

Replace `ammo` parameter with `weapon_state` in all `register()` calls. Update assertions to check `weapon_state` instead of `ammo`.

- [ ] **Step 3: Run full backend test suite**

Run: `cd backend && python -m pytest -v`
Expected: ALL PASS

- [ ] **Step 4: Run full E2E pipeline**

```bash
bash run_e2e.sh
python analyze_recording.py
```

Expected: No [BUG] flags. Verify:
- All 4 ARIAs deal damage at their weapon-specific rates
- Zombies consistently damage the same target until it dies
- Base takes less early damage (body blocking)
- No stalemate timeout (kill rate sufficient)

- [ ] **Step 5: Commit**

```bash
git add backend/tests/
git commit -m "test: update backend tests for weapon_state migration"
```

---

## Task 9: Update Combat Refactor Spec with Review Fixes

**Files:**
- Modify: `docs/superpowers/specs/2026-04-01-combat-refactor-design.md`

- [ ] **Step 1: Update the callsite audit in the spec**

Add the missing callsites identified in the review:
- `prompt_builder.py:30` -- `stats["ammo"]` (removed, replaced by weapon_state)
- `robot_state.py:11` -- `ammo` field (replaced by weapon_state dict)
- `main.py:62` -- `runtime_stats["ammo"]` (replaced by weapon_state)
- `main.py:104` -- `register_robot` sends `ammo` (replaced by weapon_state)
- `main.py:120` -- `state_update` reads `ammo` (replaced by weapon_state)
- `WebSocketClient.gd:52-58` -- `register_robot` sends ammo (replaced)
- `WebSocketClient.gd:61-68` -- `send_state_update` sends ammo (replaced)
- `models.py:7-19` -- add WEAPON_RELOADING, MOVEMENT_BLOCKED to EventType

- [ ] **Step 2: Note that zombie attack_rate is now wired up from config**

Add a note in Section 5 that `attack_timer.wait_time` is now set from `stats["attack_rate"]` in `setup()`, fixing the previously dead data.

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/specs/2026-04-01-combat-refactor-design.md
git commit -m "docs: update combat refactor spec with review findings and callsite audit fixes"
```

---

## Summary

| Task | Description | E2E Gate |
|------|-------------|----------|
| 1 | Weapon data files + ConfigLoader.get_weapon() | Unit tests |
| 2 | Robot config migration + backend prompt/state updates | Backend tests |
| 3 | AttackComponent extraction (behavior unchanged) | Game runs identically |
| 4 | Zombie persistent target tracking | Consistent zombie damage in logs |
| 5 | Attack lock state machine (windup/recovery) | All ARIAs deal consistent damage |
| 6 | Body blocking (collision layers/shapes) | Zombies can't pass Rex in chokepoint |
| 7 | MOVEMENT_BLOCKED stuck detection | Event fires when stuck |
| 8 | Backend test fixes + final integration | All tests pass, clean E2E |
| 9 | Spec update with review fixes | Doc only |
