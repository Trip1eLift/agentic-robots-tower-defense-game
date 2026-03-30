# Phase 1 — Godot Game Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Godot 4 game frontend for Phase 1 MVP — map, 4 robots, zombie enemies, wave spawning, event-driven AI integration, pre-combat briefing screen, preset commander broadcast, win/lose, and mission rewards.

**Architecture:** Godot handles all rendering, physics, pathfinding, and game logic. The WebSocket client connects to the Python backend and sends state-change events; it receives typed robot actions and passes them to the appropriate Robot node. The GameManager orchestrates waves, event detection, and mission flow.

**Prerequisite:** The Python backend (`feat/phase1-python-backend`) must be running at `ws://localhost:8765/ws` before testing Godot.

**Tech Stack:** Godot 4.x, GDScript, NavigationAgent2D (pathfinding), WebSocketPeer (built-in)

---

## Prerequisites: Godot Setup

1. **Download Godot 4.3+** from [godotengine.org](https://godotengine.org/download). It is a single portable executable — no installer needed. Extract it anywhere and run it directly.
2. **Creating a scene:** In the Godot editor, click `Scene > New Scene`. Choose a root node type (e.g., `Node2D`, `Control`, `CharacterBody2D`). Add child nodes via the "+" button in the Scene panel. Save with `Ctrl+S`.
3. **Adding nodes:** Right-click a node in the Scene panel > "Add Child Node". Search for the node type (e.g., `CollisionShape2D`, `Label`, `Timer`). Rename nodes by double-clicking their name in the Scene panel.
4. **Setting properties in the Inspector:** Select any node in the Scene panel. The Inspector panel (right side) shows all properties. Click a property to edit it. For example: select a `CollisionShape2D`, then in Inspector set `Shape` to a new `CircleShape2D` and set its `Radius`.
5. **Running scenes:** Press `F5` to run the main scene, or `F6` to run the currently open scene. The Output panel at the bottom shows print statements and errors.

---

## Branch

```bash
git checkout -b feat/phase1-godot-game
```

---

## Godot Concepts (New to Godot)

- **Scene (.tscn):** A reusable tree of nodes. Like a prefab in Unity.
- **Node:** The basic building block. Each has a type (CharacterBody2D, Label, etc.) and scripts.
- **GDScript (.gd):** Python-like scripting language. `_ready()` = constructor. `_physics_process(delta)` = update loop.
- **Signal:** Godot's event system. `signal enemy_died(enemy_id)` → `enemy.enemy_died.connect(_on_enemy_died)`.
- **CharacterBody2D:** A physics body for characters. Use `move_and_slide()` for movement.
- **NavigationAgent2D:** Add to a CharacterBody2D to enable pathfinding. Requires a NavigationRegion2D on the map.
- **Area2D:** A detection zone (no physics). Use for perception radius.
- **@export:** Exposes a variable in the Godot editor.
- **autoload:** A singleton script loaded at game start (`Project > Project Settings > Autoload`).

---

## File Structure

```
godot/
├── project.godot
├── export_presets.cfg
├── scripts/
│   ├── WebSocketClient.gd      # WebSocket connection to Python backend
│   ├── ConfigLoader.gd         # Load JSON data files
│   ├── GameManager.gd          # Wave spawning, event detection, mission flow
│   └── CampaignManager.gd      # Campaign progress, currency, mission unlocks
├── scenes/
│   ├── Main.tscn               # Entry point (campaign map screen)
│   ├── Game.tscn               # In-game scene (map + HUD)
│   ├── robots/
│   │   ├── Robot.tscn          # Robot scene (all classes share this)
│   │   └── Robot.gd
│   ├── enemies/
│   │   ├── Zombie.tscn
│   │   └── Zombie.gd
│   ├── map/
│   │   └── Map.tscn            # Tilemap + NavigationRegion2D + base node
│   └── ui/
│       ├── PreCombatBriefing.tscn
│       ├── PreCombatBriefing.gd
│       ├── HUD.tscn
│       ├── HUD.gd
│       ├── MissionSelect.tscn
│       └── MissionSelect.gd
└── assets/
    └── placeholder/            # Placeholder sprites during development
```

---

## Task 1: Godot Project Setup

**Files:**
- Create: `godot/` directory with Godot project

- [ ] **Step 1: Create branch**

```bash
git checkout -b feat/phase1-godot-game
```

- [ ] **Step 2: Create a new Godot 4 project**

Open Godot 4. Click "New Project". Set:
- Project Name: `agentic-robots-tower-defense`
- Project Path: `<repo>/godot/`
- Renderer: Forward+ (default)

Click "Create & Edit".

- [ ] **Step 3: Configure autoloads**

In Godot editor: `Project > Project Settings > Autoload`

Add these autoload singletons (create empty .gd files first):

| Name | Path |
|---|---|
| `WebSocketClient` | `res://scripts/WebSocketClient.gd` |
| `ConfigLoader` | `res://scripts/ConfigLoader.gd` |
| `CampaignManager` | `res://scripts/CampaignManager.gd` |

- [ ] **Step 4: Set main scene**

`Project > Project Settings > Application > Run > Main Scene` → set to `res://scenes/Main.tscn`

- [ ] **Step 5: Copy data directory into Godot project**

The `data/` directory lives at the repo root, but Godot's `res://` cannot use `..` path traversal. Copy (or symlink) it so Godot can access the JSON files:

```bash
# Option A: Symlink (recommended for development — changes stay in sync)
# On Linux/Mac:
ln -s ../../data godot/data
# On Windows (requires admin or Developer Mode):
mklink /D godot\data ..\..\data

# Option B: Copy (simpler, but must re-copy after data changes)
cp -r data/ godot/data/
```

Add `godot/data/` to `.gitignore` if using a symlink so the duplicate isn't committed:
```
# .gitignore
godot/data/
```

- [ ] **Step 6: Create placeholder sprite assets**

Scenes that use `preload` or `Sprite2D` will fail if the referenced image files don't exist. Create simple colored rectangles in `godot/assets/placeholder/`:

In the Godot editor:
1. Create the directory `res://assets/placeholder/`
2. For each placeholder, create a new `Image` resource via script or use **Editor > Tools > Create Placeholder Sprites** (if available). Alternatively, create them manually:

Open Godot's script editor and run this one-time tool script (`@tool` script or paste into the debugger console):

```gdscript
# Run once from Godot's script editor to generate placeholder sprites
func _create_placeholder(filename: String, color: Color, size: Vector2i = Vector2i(32, 32)) -> void:
	var img = Image.create(size.x, size.y, false, Image.FORMAT_RGBA8)
	img.fill(color)
	img.save_png("res://assets/placeholder/" + filename)

func _ready():
	DirAccess.make_dir_recursive_absolute("res://assets/placeholder")
	_create_placeholder("robot_architect.png", Color(0.2, 0.6, 1.0))  # blue
	_create_placeholder("robot_vanguard.png", Color(1.0, 0.3, 0.3))   # red
	_create_placeholder("robot_striker.png", Color(1.0, 0.8, 0.2))    # yellow
	_create_placeholder("robot_medic.png", Color(0.3, 1.0, 0.4))      # green
	_create_placeholder("zombie.png", Color(0.5, 0.0, 0.5))           # purple
	_create_placeholder("base.png", Color(0.8, 0.8, 0.8), Vector2i(64, 64))  # gray, larger
	print("Placeholder sprites created in res://assets/placeholder/")
```

After running, verify that `godot/assets/placeholder/` contains 6 `.png` files. Then assign these sprites in the scenes:
- `Robot.tscn` > `Sprite2D` > Texture: `res://assets/placeholder/robot_architect.png` (the robot script can swap the texture at runtime based on class)
- `Zombie.tscn` > `Sprite2D` > Texture: `res://assets/placeholder/zombie.png`
- `Map.tscn` > `Base` > `Sprite2D` > Texture: `res://assets/placeholder/base.png`

- [ ] **Step 7: Commit**

```bash
git add godot/
git commit -m "feat: initialize godot 4 project"
```

---

## Task 2: Config Loader (GDScript)

**Files:**
- Create: `godot/scripts/ConfigLoader.gd`

- [ ] **Step 1: Create `godot/scripts/ConfigLoader.gd`**

```gdscript
extends Node

var _robots: Dictionary = {}
var _maps: Dictionary = {}
var _missions: Dictionary = {}
var _enemies: Dictionary = {}

func _ready() -> void:
	_load_robots()
	_load_maps()
	_load_enemies()
	_load_missions()

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

func _load_maps() -> void:
	var dir = DirAccess.open("res://data/maps")
	if dir == null:
		return
	dir.list_dir_begin()
	var file_name = dir.get_next()
	while file_name != "":
		if file_name.ends_with(".json"):
			var cfg = _load_json("res://data/maps/" + file_name)
			if cfg:
				_maps[cfg["id"]] = cfg
		file_name = dir.get_next()

func _load_enemies() -> void:
	var dir = DirAccess.open("res://data/enemies")
	if dir == null:
		return
	dir.list_dir_begin()
	var file_name = dir.get_next()
	while file_name != "":
		if file_name.ends_with(".json"):
			var cfg = _load_json("res://data/enemies/" + file_name)
			if cfg:
				_enemies[cfg["id"]] = cfg
		file_name = dir.get_next()

func _load_missions() -> void:
	_load_missions_from_dir("res://data/campaign/chapter_01")

func _load_missions_from_dir(path: String) -> void:
	var dir = DirAccess.open(path)
	if dir == null:
		return
	dir.list_dir_begin()
	var file_name = dir.get_next()
	while file_name != "":
		if file_name.begins_with("mission_") and file_name.ends_with(".json"):
			var cfg = _load_json(path + "/" + file_name)
			if cfg:
				_missions[cfg["id"]] = cfg
		file_name = dir.get_next()

func _load_json(path: String) -> Dictionary:
	var file = FileAccess.open(path, FileAccess.READ)
	if file == null:
		push_error("ConfigLoader: cannot open " + path)
		return {}
	var text = file.get_as_text()
	file.close()
	var result = JSON.parse_string(text)
	if result == null:
		push_error("ConfigLoader: invalid JSON in " + path)
		return {}
	return result

func get_robot(robot_id: String) -> Dictionary:
	return _robots.get(robot_id, {})

func get_all_robots() -> Array:
	return _robots.values()

func get_map(map_id: String) -> Dictionary:
	return _maps.get(map_id, {})

func get_mission(mission_id: String) -> Dictionary:
	return _missions.get(mission_id, {})

func get_enemy(enemy_id: String) -> Dictionary:
	return _enemies.get(enemy_id, {})
```

- [ ] **Step 2: Manual test**

Run the Godot project. In the Godot debugger output, verify no errors appear about missing files. Add a temporary test in `Main.tscn`'s script:

```gdscript
func _ready():
	var robot = ConfigLoader.get_robot("architect_common_hana")
	print("Loaded robot: ", robot.get("name", "NOT FOUND"))
	# Expected output: "Loaded robot: Hana"
```

Remove the test code after verifying.

- [ ] **Step 3: Commit**

```bash
git add godot/scripts/ConfigLoader.gd
git commit -m "feat: add gdscript config loader for json data files"
```

---

## Task 3: WebSocket Client

**Files:**
- Create: `godot/scripts/WebSocketClient.gd`

- [ ] **Step 1: Create `godot/scripts/WebSocketClient.gd`**

```gdscript
extends Node

signal action_received(robot_id: String, action: Dictionary)
signal connected()
signal disconnected()

const SERVER_URL = "ws://localhost:8765/ws"

var _socket := WebSocketPeer.new()
var _is_connected := false
var _reconnect_timer: Timer = null

func _ready() -> void:
	# Create a one-shot reconnect timer (avoids await in _process)
	_reconnect_timer = Timer.new()
	_reconnect_timer.wait_time = 2.0
	_reconnect_timer.one_shot = true
	_reconnect_timer.timeout.connect(_connect_to_server)
	add_child(_reconnect_timer)
	_connect_to_server()

func _connect_to_server() -> void:
	var err = _socket.connect_to_url(SERVER_URL)
	if err != OK:
		push_error("WebSocketClient: failed to initiate connection: " + str(err))

func _process(_delta: float) -> void:
	_socket.poll()
	var state = _socket.get_ready_state()

	if state == WebSocketPeer.STATE_OPEN:
		if not _is_connected:
			_is_connected = true
			connected.emit()
		while _socket.get_available_packet_count() > 0:
			var raw = _socket.get_packet().get_string_from_utf8()
			_handle_message(raw)

	elif state == WebSocketPeer.STATE_CLOSED and _is_connected:
		_is_connected = false
		disconnected.emit()
		# Schedule reconnect via Timer instead of await (safe in _process)
		if _reconnect_timer.is_stopped():
			_reconnect_timer.start()

func _handle_message(raw: String) -> void:
	var data = JSON.parse_string(raw)
	if data == null:
		push_error("WebSocketClient: invalid JSON received: " + raw)
		return
	if data.has("robot_id") and data.has("action"):
		action_received.emit(data["robot_id"], data["action"])

func register_robot(robot_id: String, health: int, ammo: int, position: Vector2) -> void:
	_send({
		"type": "register_robot",
		"robot_id": robot_id,
		"health": health,
		"ammo": ammo,
		"position": [position.x, position.y]
	})

func send_state_update(robot_id: String, health: int, ammo: int, position: Vector2) -> void:
	_send({
		"type": "state_update",
		"robot_id": robot_id,
		"health": health,
		"ammo": ammo,
		"position": [position.x, position.y]
	})

func send_event(robot_id: String, event_type: String, event_detail: String,
		local_context: Dictionary, player_instructions: String,
		commander_broadcast: Variant) -> void:
	_send({
		"type": "robot_event",
		"robot_id": robot_id,
		"event_type": event_type,
		"event_detail": event_detail,
		"local_context": local_context,
		"player_instructions": player_instructions,
		"commander_broadcast": commander_broadcast
	})

func _send(data: Dictionary) -> void:
	if _socket.get_ready_state() != WebSocketPeer.STATE_OPEN:
		push_warning("WebSocketClient: not connected, dropping message")
		return
	var text = JSON.stringify(data)
	_socket.send_text(text)
```

- [ ] **Step 2: Manual test**

Start the Python backend:
```bash
cd backend && uvicorn backend.main:app --port 8765
```

Run the Godot project. In Godot Output panel, verify:
```
(no connection errors)
```

Add temporary test in Main scene:
```gdscript
func _ready():
	WebSocketClient.connected.connect(func(): print("WS connected!"))
# Expected output after 1-2 seconds: "WS connected!"
```

Remove test code after verifying.

- [ ] **Step 3: Commit**

```bash
git add godot/scripts/WebSocketClient.gd
git commit -m "feat: add websocket client with auto-reconnect"
```

<!-- PLAYTEST GATE: After Task 3, verify WebSocket round-trip.
Start the Python backend (uvicorn backend.main:app --port 8765).
Run the Godot project. Check the Output panel for "WS connected!" (from the temporary test).
If connection fails, verify the backend URL and that no firewall blocks localhost:8765.
Do NOT proceed until WebSocket connection is confirmed working. -->

---

## Task 4: Map Scene

**Files:**
- Create: `godot/scenes/map/Map.tscn` and `godot/scenes/map/Map.gd`

- [ ] **Step 1: Create Map scene in Godot editor**

In Godot editor, create a new scene:
- Root node: `Node2D`, rename to `Map`
- Add child: `TileMapLayer` (for visual tiles) — rename to `Ground`
- Add child: `NavigationRegion2D` — rename to `NavRegion`
  - Inside NavRegion, add a `NavigationPolygon` resource
  - Draw the walkable area polygon covering the map (avoid base area)
- Add child: `Node2D` — rename to `Base`
  - Add `Sprite2D` child for base visual (use placeholder)
  - Add `Area2D` child named `BaseHitbox` with `CollisionShape2D`
- Add child: `Node2D` — rename to `EnemySpawnPoints`
  - Add `Marker2D` children named `spawn_north`, `spawn_west`
- Add child: `Node2D` — rename to `RobotSpawnZone`
- Add child: `Node2D` — rename to `StrategicPositions`
  - Add `Marker2D` children for each position: `north_chokepoint`, `west_flank`, `base_entrance`, `rear_support`

Save as `res://scenes/map/Map.tscn`.

- [ ] **Step 2: Create `godot/scenes/map/Map.gd`**

```gdscript
extends Node2D

signal base_destroyed()

@export var map_id: String = "ch01_mission_01_map"

@onready var base_node: Node2D = $Base
@onready var enemy_spawn_points: Node2D = $EnemySpawnPoints
@onready var robot_spawn_zone: Node2D = $RobotSpawnZone
@onready var strategic_positions_node: Node2D = $StrategicPositions

var _base_health: int = 500
var _base_max_health: int = 500
var _map_config: Dictionary = {}
var _strategic_positions: Dictionary = {}  # id -> Vector2

func _ready() -> void:
	_map_config = ConfigLoader.get_map(map_id)
	_load_strategic_positions()

func _load_strategic_positions() -> void:
	for pos_data in _map_config.get("strategic_positions", []):
		var marker = strategic_positions_node.find_child(pos_data["id"])
		if marker:
			_strategic_positions[pos_data["id"]] = marker.global_position
		else:
			# Fall back to config position if marker not placed
			_strategic_positions[pos_data["id"]] = Vector2(
				pos_data["position"][0], pos_data["position"][1]
			)

func get_strategic_position(position_id: String) -> Vector2:
	return _strategic_positions.get(position_id, base_node.global_position)

func get_all_strategic_positions() -> Array:
	return _map_config.get("strategic_positions", [])

func get_spawn_point(spawn_id: String) -> Vector2:
	var marker = enemy_spawn_points.find_child(spawn_id)
	if marker:
		return marker.global_position
	return Vector2.ZERO

func get_all_spawn_points() -> Array[Vector2]:
	var points: Array[Vector2] = []
	for child in enemy_spawn_points.get_children():
		points.append(child.global_position)
	return points

func get_robot_spawn_position(index: int) -> Vector2:
	var cfg = _map_config.get("robot_spawn_zones", [])
	if cfg.is_empty():
		return base_node.global_position + Vector2(0, -80)
	var zone = cfg[0]["rect"]
	var x = zone[0] + (zone[2] / 4.0) * (index % 4)
	var y = zone[1] + zone[3] / 2.0
	return Vector2(x, y)

func get_base_position() -> Vector2:
	return base_node.global_position

func take_base_damage(amount: int) -> void:
	_base_health = max(0, _base_health - amount)
	if _base_health == 0:
		base_destroyed.emit()

func get_base_health() -> int:
	return _base_health

func get_base_health_percent() -> float:
	return float(_base_health) / float(_base_max_health)
```

- [ ] **Step 3: Manual test**

Run the Godot scene (`Map.tscn` directly). Verify it opens without errors in the Output panel.

- [ ] **Step 4: Commit**

```bash
git add godot/scenes/map/
git commit -m "feat: add map scene with navigation region and strategic positions"
```

---

## Task 5: Robot Scene

**Files:**
- Create: `godot/scenes/robots/Robot.tscn`
- Create: `godot/scenes/robots/Robot.gd`

- [ ] **Step 1: Create Robot scene in Godot editor**

Create new scene:
- Root: `CharacterBody2D`, rename to `Robot`
- Children:
  - `Sprite2D` (placeholder robot sprite)
  - `CollisionShape2D` (capsule, height 40, radius 16)
  - `NavigationAgent2D` — rename `NavAgent`
  - `Area2D` rename `PerceptionArea`
    - `CollisionShape2D` (circle, radius 200)
  - `Label` rename `SpeechLabel` (shows robot's `reason` text)
  - `Label` rename `ThinkingLabel` (shows "..." while waiting for LLM response; initially hidden)
  - `Timer` rename `SpeechTimer` (hides speech after 3s)
  - `Timer` rename `AttackTimer` (wait_time=1.0, one_shot=false — fires repeated attacks while action is "attack"/"snipe")

**Collision layer configuration** (select node in Scene panel, then Inspector > Collision > Layer/Mask):
- `Robot` (the root CharacterBody2D): Layer = 1, Mask = 2 (robots are on layer 1, collide with enemies on layer 2)
- `PerceptionArea` (the Area2D): Monitoring = true, Monitorable = false, Layer = (none), Mask = 2 (detect enemies only)

Save as `res://scenes/robots/Robot.tscn`.

- [ ] **Step 2: Create `godot/scenes/robots/Robot.gd`**

```gdscript
extends CharacterBody2D

signal event_detected(robot_id: String, event_type: String, event_detail: String)

@export var robot_id: String = ""

@onready var nav_agent: NavigationAgent2D = $NavAgent
@onready var perception_area: Area2D = $PerceptionArea
@onready var speech_label: Label = $SpeechLabel
@onready var thinking_label: Label = $ThinkingLabel
@onready var speech_timer: Timer = $SpeechTimer
@onready var attack_timer: Timer = $AttackTimer

var _config: Dictionary = {}
var _health: int = 0
var _max_health: int = 0
var _ammo: int = 0
var _speed: float = 100.0
var _current_action: Dictionary = {}
var _target_enemy: Node2D = null
var _player_instructions: String = ""
var _enemies_in_perception: Array[Node2D] = []
var _recent_events: Array[String] = []
var _map: Node = null  # set by GameManager
var _ammo_low_fired: bool = false  # only fire AMMO_LOW event once per resupply cycle
var _event_cooldowns: Dictionary = {}  # event_type -> last fire time (msec)

const MAX_RECENT_EVENTS = 5
const EVENT_COOLDOWN_MS = 2000  # minimum 2 seconds between same event type

func setup(config: Dictionary, map: Node) -> void:
	_config = config
	_map = map
	var stats = config["base_stats"]
	_health = stats["health"]
	_max_health = stats["health"]
	_ammo = stats["ammo"]
	_speed = stats["speed"] * 20.0  # convert stat to pixels/sec
	robot_id = config["id"]
	add_to_group("robots")  # GD-7: register in robots group for ally detection
	speech_label.text = ""
	speech_timer.wait_time = 3.0
	speech_timer.one_shot = true
	speech_timer.timeout.connect(func(): speech_label.text = "")
	# GD-6: AttackTimer for continuous auto-attack while action is "attack"/"snipe"
	attack_timer.wait_time = 1.0
	attack_timer.one_shot = false
	attack_timer.timeout.connect(_on_attack_timer)
	thinking_label.text = "..."
	thinking_label.visible = false
	perception_area.body_entered.connect(_on_body_entered_perception)
	perception_area.body_exited.connect(_on_body_exited_perception)
	WebSocketClient.action_received.connect(_on_action_received)
	WebSocketClient.register_robot(robot_id, _health, _ammo, global_position)
	# Default spawn action based on class (before any LLM decisions arrive)
	_execute_default_spawn_action()

func set_player_instructions(text: String) -> void:
	var max_chars = _config["base_stats"]["intelligence"] * 100
	_player_instructions = text.left(max_chars)

## Execute a default action on spawn based on robot class (before LLM responds)
func _execute_default_spawn_action() -> void:
	var robot_class = _config.get("class", "striker")
	match robot_class:
		"architect":
			# Move to nearest strategic position
			if _map:
				var positions = _map.get_all_strategic_positions()
				if not positions.is_empty():
					var pos_id = positions[0].get("id", "base_entrance")
					nav_agent.target_position = _map.get_strategic_position(pos_id)
		"vanguard":
			# Move to nearest strategic position
			if _map:
				var positions = _map.get_all_strategic_positions()
				if not positions.is_empty():
					var pos_id = positions[0].get("id", "north_chokepoint")
					nav_agent.target_position = _map.get_strategic_position(pos_id)
		"striker":
			pass  # hold position (idle)
		"medic":
			# Move to rear support
			if _map:
				nav_agent.target_position = _map.get_strategic_position("rear_support")

## Check if enough time has passed to fire this event type again (2s cooldown)
func _can_fire_event(event_type: String) -> bool:
	var now = Time.get_ticks_msec()
	var last_fired = _event_cooldowns.get(event_type, 0)
	if now - last_fired < EVENT_COOLDOWN_MS:
		return false
	_event_cooldowns[event_type] = now
	return true

## Called by GameManager between waves to reset ammo
func resupply_ammo() -> void:
	_ammo = _config["base_stats"]["ammo"]
	_ammo_low_fired = false  # reset the AMMO_LOW guard

func _physics_process(delta: float) -> void:
	if not is_alive():
		return
	_execute_movement()
	_check_enemy_in_range()  # GD-8: fire ENEMY_IN_RANGE event

func _execute_movement() -> void:
	if nav_agent.is_navigation_finished():
		return
	var next_pos = nav_agent.get_next_path_position()
	var direction = (next_pos - global_position).normalized()
	velocity = direction * _speed
	move_and_slide()

## GD-8: Check if any enemy is within attack range (shorter than perception range)
## and fire ENEMY_IN_RANGE event so the backend can decide to engage.
func _check_enemy_in_range() -> void:
	var attack_range = _config.get("base_stats", {}).get("attack_range", 120.0)
	for enemy in _enemies_in_perception:
		if is_instance_valid(enemy):
			var dist = global_position.distance_to(enemy.global_position)
			if dist <= attack_range:
				_fire_event("ENEMY_IN_RANGE",
					str(GameManager.get_enemy_id(enemy)) + " at distance " + str(int(dist)))
				return  # fire once per physics frame at most

func execute_action(action: Dictionary) -> void:
	_current_action = action
	# Hide thinking indicator — we received an LLM response
	thinking_label.visible = false
	# Stop attack timer by default; only restart if action is attack/snipe
	attack_timer.stop()
	var action_name = action.get("action", "idle")
	# Phase 1: build/deploy_turret not supported — treat as idle
	if action_name == "build" or action_name == "deploy_turret":
		action_name = "idle"
	match action_name:
		"move", "retreat":
			var destination_id = action.get("destination", "")
			if destination_id and _map:
				var target_pos = _map.get_strategic_position(destination_id)
				nav_agent.target_position = target_pos
		"attack", "snipe":
			# GD-6: LLM sets STRATEGY; robot auto-attacks on a timer
			_target_enemy = _find_enemy_by_id(action.get("target_id", -1))
			if _target_enemy:
				_perform_attack()         # fire immediately
				attack_timer.start()      # then keep firing on timer
		"heal":
			_perform_heal(action)
		"idle":
			pass
	var reason = action.get("reason", "")
	if reason:
		_show_speech(reason)
		# Log action reason to HUD event log
		var hud = get_tree().get_first_node_in_group("hud")
		if hud and hud.has_method("add_log_entry"):
			hud.add_log_entry(_config.get("name", robot_id) + ": " + reason)

## GD-6: Called repeatedly by AttackTimer while action is "attack"/"snipe"
func _on_attack_timer() -> void:
	var action_name = _current_action.get("action", "idle")
	if not ["attack", "snipe"].has(action_name):
		attack_timer.stop()
		return
	# Re-acquire target if it died
	if _target_enemy == null or not is_instance_valid(_target_enemy):
		_target_enemy = _find_enemy_by_id(_current_action.get("target_id", -1))
	if _target_enemy == null or not is_instance_valid(_target_enemy):
		attack_timer.stop()
		# Target is dead/invalid — fire ENEMY_ELIMINATED to get a new decision
		_fire_event("ENEMY_ELIMINATED", "current target lost, requesting new orders")
		return
	_perform_attack()

func _perform_attack() -> void:
	if _target_enemy == null or not is_instance_valid(_target_enemy):
		return
	var damage = _config["base_stats"]["damage"] * 5
	if _target_enemy.has_method("take_damage"):
		_target_enemy.take_damage(damage)
	_ammo = max(0, _ammo - 1)
	_push_recent_event("ENEMY_ATTACKED: " + str(_target_enemy.name))
	if not _ammo_low_fired and (_ammo == 0 or (_ammo / float(_config["base_stats"]["ammo"])) < 0.2):
		_ammo_low_fired = true
		_fire_event("AMMO_LOW", "ammo at " + str(_ammo))
	WebSocketClient.send_state_update(robot_id, _health, _ammo, global_position)

func _perform_heal(action: Dictionary) -> void:
	_push_recent_event("HEALING: ally " + str(action.get("target_id", "unknown")))

func take_damage(amount: int) -> void:
	_health = max(0, _health - amount)
	_push_recent_event("TOOK_DAMAGE: " + str(amount))
	_fire_event("TAKING_DAMAGE", "health now " + str(_health) + "/" + str(_max_health))
	WebSocketClient.send_state_update(robot_id, _health, _ammo, global_position)
	if _health == 0:
		_die()

func is_alive() -> bool:
	return _health > 0

func _die() -> void:
	_push_recent_event("ROBOT_DIED")
	set_physics_process(false)
	hide()
	# Phase 1: No permadeath. Robot is dead for THIS mission only.
	# GameManager resets robots to full health on next mission start.

## Called by GameManager to revive robot for next mission
func revive() -> void:
	_health = _max_health
	_ammo = _config["base_stats"]["ammo"]
	_ammo_low_fired = false
	_event_cooldowns.clear()
	set_physics_process(true)
	show()

func _on_body_entered_perception(body: Node2D) -> void:
	if body.is_in_group("enemies"):
		if not _enemies_in_perception.has(body):
			_enemies_in_perception.append(body)
		_fire_event("ENEMY_SPOTTED", body.name + " at " + str(body.global_position))

func _on_body_exited_perception(body: Node2D) -> void:
	_enemies_in_perception.erase(body)

func _on_action_received(received_robot_id: String, action: Dictionary) -> void:
	if received_robot_id == robot_id:
		execute_action(action)

func _fire_event(event_type: String, event_detail: String) -> void:
	if not _can_fire_event(event_type):
		return  # cooldown not elapsed, skip
	var local_context = _build_local_context()
	var commander_broadcast = null
	if has_node("/root/GameManager"):
		commander_broadcast = GameManager.get_commander_broadcast()
	WebSocketClient.send_event(robot_id, event_type, event_detail, local_context,
			_player_instructions, commander_broadcast)
	# Show thinking indicator while waiting for LLM response
	thinking_label.visible = true

func _build_local_context() -> Dictionary:
	var enemies = []
	for e in _enemies_in_perception:
		if is_instance_valid(e):
			# INT-1: Use sequential integer IDs instead of Godot instance IDs
			var e_health: int = 50
			if e.has_method("get_health"):
				e_health = e.get_health()
			enemies.append({"id": GameManager.get_enemy_id(e), "type": "zombie",
				"position": [e.global_position.x, e.global_position.y],
				"health": e_health})
	# GD-7: Populate nearby_allies from "robots" group
	var allies = []
	for r in get_tree().get_nodes_in_group("robots"):
		if is_instance_valid(r) and r != self and r.has_method("is_alive") and r.is_alive():
			var dist = global_position.distance_to(r.global_position)
			if dist < 300:  # only report allies within a useful range
				allies.append({"id": r.robot_id, "class": r._config.get("class", "unknown"),
					"position": [r.global_position.x, r.global_position.y],
					"health": r.get_health()})
	var positions: Array = []
	if _map:
		positions = _map.get_all_strategic_positions()
	return {
		"nearby_enemies": enemies,
		"nearby_allies": allies,
		"structures": [],
		"recent_events": _recent_events.duplicate(),
		"strategic_positions": positions
	}

func _push_recent_event(event_str: String) -> void:
	_recent_events.append(event_str)
	if _recent_events.size() > MAX_RECENT_EVENTS:
		_recent_events.pop_front()

## INT-1: Look up enemy by sequential integer ID (via GameManager mapping)
func _find_enemy_by_id(enemy_id: int) -> Node2D:
	var enemy = GameManager.get_enemy_by_id(enemy_id)
	if enemy and is_instance_valid(enemy) and enemy in _enemies_in_perception:
		return enemy
	return null

func _show_speech(text: String) -> void:
	speech_label.text = text
	speech_timer.start()

func get_health() -> int:
	return _health

func get_ammo() -> int:
	return _ammo
```

- [ ] **Step 3: Manual test**

Open `Robot.tscn` in Godot editor. Click "Run Scene" (F6). Verify no script errors in Output. The robot should appear on screen (placeholder sprite) and not crash.

- [ ] **Step 4: Commit**

```bash
git add godot/scenes/robots/
git commit -m "feat: add robot scene with navigation, perception, and ws action handling"
```

---

## Task 6: Zombie Enemy Scene

**Files:**
- Create: `godot/scenes/enemies/Zombie.tscn`
- Create: `godot/scenes/enemies/Zombie.gd`

- [ ] **Step 1: Create Zombie scene in Godot editor**

Create new scene:
- Root: `CharacterBody2D`, rename `Zombie`
- Add to group: `enemies`
- Children:
  - `Sprite2D` (placeholder zombie sprite)
  - `CollisionShape2D` (capsule, height 40, radius 16)
  - `NavigationAgent2D` rename `NavAgent`
  - `Timer` rename `AttackTimer` (wait_time=1.0, autostart=true)

**Collision layer configuration** (select node in Scene panel, then Inspector > Collision > Layer/Mask):
- `Zombie` (the root CharacterBody2D): Layer = 2, Mask = 1 (enemies are on layer 2, collide with robots on layer 1)

Save as `res://scenes/enemies/Zombie.tscn`.

- [ ] **Step 2: Create `godot/scenes/enemies/Zombie.gd`**

```gdscript
extends CharacterBody2D

signal died(zombie: Node2D)

@onready var nav_agent: NavigationAgent2D = $NavAgent
@onready var attack_timer: Timer = $AttackTimer

var _health: int = 50
var _speed: float = 60.0
var _damage: int = 8
var _attack_range: float = 40.0
var _base_target: Node2D = null  # the base node (always the fallback)
var _current_target: Node2D = null  # current attack target (robot or base)

func setup(config: Dictionary, target: Node2D) -> void:
	var stats = config["stats"]
	_health = stats["health"]
	_speed = stats["speed"] * 20.0
	_damage = stats["damage"]
	_attack_range = stats["attack_range"]
	_base_target = target
	_current_target = target
	nav_agent.target_position = _base_target.global_position
	attack_timer.timeout.connect(_on_attack_timer)

func _physics_process(_delta: float) -> void:
	# Check for robots in melee range — attack them instead of walking past
	_current_target = _find_nearby_robot()
	if _current_target == null:
		_current_target = _base_target

	if _current_target == null or not is_instance_valid(_current_target):
		return

	var dist = global_position.distance_to(_current_target.global_position)
	if dist <= _attack_range:
		velocity = Vector2.ZERO
		return

	# Navigate toward current target (robot or base)
	nav_agent.target_position = _current_target.global_position
	if not nav_agent.is_navigation_finished():
		var next_pos = nav_agent.get_next_path_position()
		velocity = (next_pos - global_position).normalized() * _speed
	move_and_slide()

## Find the closest alive robot within attack range (melee).
## Returns null if no robot is close enough to hit.
func _find_nearby_robot() -> Node2D:
	var closest: Node2D = null
	var closest_dist := _attack_range  # only consider robots within melee range
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
	if _current_target == null or not is_instance_valid(_current_target):
		return
	var dist = global_position.distance_to(_current_target.global_position)
	if dist <= _attack_range:
		if _current_target.has_method("take_base_damage"):
			_current_target.take_base_damage(_damage)
		elif _current_target.has_method("take_damage"):
			_current_target.take_damage(_damage)

func take_damage(amount: int) -> void:
	_health = max(0, _health - amount)
	if _health == 0:
		died.emit(self)
		queue_free()

func get_health() -> int:
	return _health
```

- [ ] **Step 3: Manual test**

Open `Zombie.tscn`. Run scene (F6). Verify no script errors.

- [ ] **Step 4: Commit**

```bash
git add godot/scenes/enemies/
git commit -m "feat: add zombie enemy scene with navigation to base"
```

<!-- PLAYTEST GATE: After Task 6, verify pathfinding works.
Open Map.tscn, instance a Robot and a Zombie manually, run the scene (F6).
Verify: the robot's NavigationAgent2D finds a path, the zombie walks toward the base.
If pathfinding fails, check that NavigationRegion2D has a baked NavigationPolygon covering the walkable area.
Do NOT proceed until pathfinding is confirmed working. -->

---

## Task 7: Game Manager

**Files:**
- Create: `godot/scripts/GameManager.gd`

- [ ] **Step 1: Create `godot/scripts/GameManager.gd`**

```gdscript
extends Node

signal wave_started(wave_number: int)
signal wave_completed(wave_number: int)
signal mission_won()
signal mission_lost()
signal kill_count_changed(count: int)

const ROBOT_SCENE = preload("res://scenes/robots/Robot.tscn")
const ZOMBIE_SCENE = preload("res://scenes/enemies/Zombie.tscn")

var _map: Node = null
var _current_mission: Dictionary = {}
var _robots: Array[Node] = []
var _enemies: Array[Node] = []
var _current_wave: int = 0
var _kill_count: int = 0
var _commander_broadcast: String = ""
var _is_wave_active: bool = false
# INT-1: Sequential enemy ID system (small integers for LLM readability)
var _next_enemy_id: int = 1
var _enemy_id_map: Dictionary = {}   # Node -> int
var _id_enemy_map: Dictionary = {}   # int -> Node

func setup_mission(mission_id: String, map: Node) -> void:
	_map = map
	_current_mission = ConfigLoader.get_mission(mission_id)
	_current_wave = 0
	_kill_count = 0
	_robots.clear()
	_enemies.clear()
	# INT-1: Reset enemy ID tracking
	_next_enemy_id = 1
	_enemy_id_map.clear()
	_id_enemy_map.clear()

func spawn_robots(robot_configs: Array, player_instructions: Dictionary) -> void:
	for i in range(robot_configs.size()):
		var config = robot_configs[i]
		var robot = ROBOT_SCENE.instantiate()
		_map.add_child(robot)
		robot.global_position = _map.get_robot_spawn_position(i)
		robot.setup(config, _map)
		var instructions = player_instructions.get(config["id"], "")
		robot.set_player_instructions(instructions)
		_robots.append(robot)

func start_next_wave() -> void:
	var waves = _current_mission.get("waves", [])
	if _current_wave >= waves.size():
		mission_won.emit()
		return
	_is_wave_active = true
	var wave_data = waves[_current_wave]
	wave_started.emit(_current_wave + 1)
	await _spawn_wave_enemies(wave_data)

func _spawn_wave_enemies(wave_data: Dictionary) -> void:
	var spawn_points = _map.get_all_spawn_points()
	var spawn_index = 0
	for enemy_group in wave_data.get("enemies", []):
		var enemy_config = ConfigLoader.get_enemy(enemy_group["type"])
		for i in range(enemy_group["count"]):
			var zombie = ZOMBIE_SCENE.instantiate()
			_map.add_child(zombie)
			var spawn_pos = spawn_points[spawn_index % spawn_points.size()]
			zombie.global_position = spawn_pos + Vector2(randf_range(-30, 30), randf_range(-30, 30))
			zombie.setup(enemy_config, _map.base_node)
			zombie.died.connect(_on_enemy_died)
			_enemies.append(zombie)
			# INT-1: Assign sequential integer ID
			var eid = _next_enemy_id
			_next_enemy_id += 1
			_enemy_id_map[zombie] = eid
			_id_enemy_map[eid] = zombie
			spawn_index += 1
			await get_tree().create_timer(0.2).timeout  # stagger spawning

func _on_enemy_died(enemy: Node2D) -> void:
	# INT-1: Clean up ID mapping
	var eid = _enemy_id_map.get(enemy, -1)
	_enemy_id_map.erase(enemy)
	if eid != -1:
		_id_enemy_map.erase(eid)
	_enemies.erase(enemy)
	_kill_count += 1
	kill_count_changed.emit(_kill_count)
	_notify_robots_of_kill(enemy, eid)
	if _enemies.is_empty() and _is_wave_active:
		_is_wave_active = false
		_current_wave += 1
		wave_completed.emit(_current_wave)

func _notify_robots_of_kill(enemy: Node2D, enemy_id: int) -> void:
	for robot in _robots:
		if is_instance_valid(robot) and robot.has_method("is_alive") and robot.is_alive():
			var dist = robot.global_position.distance_to(enemy.global_position)
			if dist < 300:
				# GD-11: Fire ENEMY_ELIMINATED event instead of state_update
				# GD-10: Use get_ammo() instead of accessing robot._ammo directly
				robot._fire_event("ENEMY_ELIMINATED",
					"enemy " + str(enemy_id) + " killed at " + str(enemy.global_position))

## INT-1: Get the sequential integer ID for an enemy node
func get_enemy_id(enemy: Node2D) -> int:
	return _enemy_id_map.get(enemy, -1)

## INT-1: Get the enemy node for a sequential integer ID
func get_enemy_by_id(enemy_id: int) -> Node2D:
	return _id_enemy_map.get(enemy_id, null)

func on_base_destroyed() -> void:
	_is_wave_active = false
	mission_lost.emit()

func get_commander_broadcast() -> Variant:
	if _commander_broadcast.is_empty():
		return null
	return _commander_broadcast

func set_commander_broadcast(text: String) -> void:
	_commander_broadcast = text
	# Trigger a think for all alive robots
	for robot in _robots:
		if is_instance_valid(robot) and robot.has_method("is_alive") and robot.is_alive():
			robot._fire_event("COMMANDER_BROADCAST", text)

func is_wave_active() -> bool:
	return _is_wave_active

func get_kill_count() -> int:
	return _kill_count
```

- [ ] **Step 2: Add GameManager to autoloads**

In Godot: `Project > Project Settings > Autoload`
Add: Name=`GameManager`, Path=`res://scripts/GameManager.gd`

- [ ] **Step 3: Commit**

```bash
git add godot/scripts/GameManager.gd
git commit -m "feat: add game manager for wave spawning and mission flow"
```

---

## Task 8: Pre-Combat Briefing UI

**Files:**
- Create: `godot/scenes/ui/PreCombatBriefing.tscn`
- Create: `godot/scenes/ui/PreCombatBriefing.gd`

- [ ] **Step 1: Create PreCombatBriefing scene in Godot editor**

Create new scene:
- Root: `Control`, rename `PreCombatBriefing`, set anchors to Full Rect
- Children:
  - `VBoxContainer` (fills screen)
    - `Label` text="Pre-Combat Briefing", font size 24
    - `Label` name=`MissionTitle`
    - `HBoxContainer` name=`RobotCards` (holds 4 robot cards)
    - `Button` name=`StartButton`, text="Start Mission"

For each robot card (repeat 4 times inside RobotCards):
- `VBoxContainer` name=`RobotCard_N`
  - `Label` name=`RobotName`
  - `Label` name=`RobotClass`
  - `Label` name=`IntelligenceLabel` (shows "Instructions: X/Y chars")
  - `TextEdit` name=`InstructionsInput` (multiline text input)

Save as `res://scenes/ui/PreCombatBriefing.tscn`.

- [ ] **Step 2: Create `godot/scenes/ui/PreCombatBriefing.gd`**

```gdscript
extends Control

signal briefing_confirmed(player_instructions: Dictionary)

@onready var mission_title: Label = $VBoxContainer/MissionTitle
@onready var robot_cards: HBoxContainer = $VBoxContainer/RobotCards
@onready var start_button: Button = $VBoxContainer/StartButton

var _robot_configs: Array = []
var _instruction_inputs: Dictionary = {}  # robot_id -> TextEdit
var _max_chars: Dictionary = {}           # robot_id -> int
var _updating: bool = false               # re-entrancy guard for _on_text_changed

func setup(mission_id: String) -> void:
	var mission = ConfigLoader.get_mission(mission_id)
	mission_title.text = mission.get("title", "Mission")
	_robot_configs = ConfigLoader.get_all_robots()
	_build_robot_cards()
	start_button.pressed.connect(_on_start_pressed)
	# Show available strategic positions from the map config
	var map_id = mission.get("map_id", "ch01_mission_01_map")
	var map_config = ConfigLoader.get_map(map_id)
	var positions = map_config.get("strategic_positions", [])
	var pos_names: Array[String] = []
	for pos in positions:
		pos_names.append(pos.get("id", "unknown"))
	var positions_label = Label.new()
	positions_label.text = "Available positions: " + ", ".join(pos_names)
	$VBoxContainer.add_child(positions_label)
	$VBoxContainer.move_child(positions_label, 2)  # after MissionTitle

func _build_robot_cards() -> void:
	for child in robot_cards.get_children():
		child.queue_free()

	for config in _robot_configs:
		var card = VBoxContainer.new()
		robot_cards.add_child(card)

		var name_label = Label.new()
		name_label.text = config["name"] + " (" + config["class"].capitalize() + ")"
		card.add_child(name_label)

		var intelligence = config["base_stats"]["intelligence"]
		var max_chars = intelligence * 100
		_max_chars[config["id"]] = max_chars

		var char_label = Label.new()
		char_label.name = "CharLabel"
		char_label.text = "0 / " + str(max_chars) + " chars"
		card.add_child(char_label)

		var input = TextEdit.new()
		input.custom_minimum_size = Vector2(200, 120)
		input.placeholder_text = _get_example_prompt(config.get("class", ""))
		input.text_changed.connect(_on_text_changed.bind(config["id"], input, char_label, max_chars))
		card.add_child(input)
		_instruction_inputs[config["id"]] = input

func _get_example_prompt(robot_class: String) -> String:
	match robot_class:
		"architect":
			return "Position at the north chokepoint and hold. If enemies approach from the west, reposition to cover that flank."
		"vanguard":
			return "Hold the north chokepoint. Engage any enemy that gets close. Protect the base at all costs."
		"striker":
			return "Stay at west_flank for range advantage. Pick off enemies heading toward the base. Conserve ammo."
		"medic":
			return "Stay behind the front line at rear_support. Heal any ally below 50% health. Move toward injured allies."
		_:
			return "Write instructions..."

func _on_text_changed(robot_id: String, input: TextEdit, char_label: Label, max_chars: int) -> void:
	if _updating:
		return
	_updating = true
	var current_len = input.text.length()
	char_label.text = str(current_len) + " / " + str(max_chars) + " chars"
	if current_len > max_chars:
		input.text = input.text.left(max_chars)
		input.set_caret_column(max_chars)
	_updating = false

func _on_start_pressed() -> void:
	var instructions: Dictionary = {}
	for robot_id in _instruction_inputs:
		instructions[robot_id] = _instruction_inputs[robot_id].text
	briefing_confirmed.emit(instructions)
```

- [ ] **Step 3: Manual test**

Run `PreCombatBriefing.tscn`. Verify:
- 4 robot cards appear with names (Hana, Rex, Aurora, Lily)
- Each has a text input
- Typing beyond the character limit stops accepting input
- "Start Mission" button is visible

- [ ] **Step 4: Commit**

```bash
git add godot/scenes/ui/
git commit -m "feat: add pre-combat briefing ui with per-robot instruction inputs"
```

---

## Task 9: HUD and Commander Broadcast

**Files:**
- Create: `godot/scenes/ui/HUD.tscn`
- Create: `godot/scenes/ui/HUD.gd`

- [ ] **Step 1: Create HUD scene in Godot editor**

Create new scene:
- Root: `CanvasLayer`, rename `HUD`
- Children:
  - `VBoxContainer` anchored to top-left:
    - `Label` name=`WaveLabel` text="Wave 1"
    - `Label` name=`BaseHealthLabel` text="Base: 500/500"
    - `Label` name=`KillLabel` text="Kills: 0"
  - `VBoxContainer` anchored to bottom-left:
    - `Label` text="Commander Broadcast:"
    - `HBoxContainer`:
      - `Button` name=`BtnFallBack` text="Fall Back!"
      - `Button` name=`BtnPrioritizeBase` text="Prioritize Base!"
      - `Button` name=`BtnFocusFire` text="Focus Fire!"
  - `ItemList` name=`EventLog` anchored to right side (Anchor preset: Right Wide or custom right-side anchors). max_visible_items=10. Displays recent robot action log entries.

Add the HUD node to group `hud` so robots can find it: select the root `HUD` node, Node panel > Groups > add `hud`.

Save as `res://scenes/ui/HUD.tscn`.

- [ ] **Step 2: Create `godot/scenes/ui/HUD.gd`**

```gdscript
extends CanvasLayer

@onready var wave_label: Label = $VBoxContainer/WaveLabel
@onready var base_health_label: Label = $VBoxContainer/BaseHealthLabel
@onready var kill_label: Label = $VBoxContainer/KillLabel
@onready var btn_fall_back: Button = $VBoxContainer2/HBoxContainer/BtnFallBack
@onready var btn_prioritize_base: Button = $VBoxContainer2/HBoxContainer/BtnPrioritizeBase
@onready var btn_focus_fire: Button = $VBoxContainer2/HBoxContainer/BtnFocusFire
@onready var event_log: ItemList = $EventLog

const MAX_LOG_ENTRIES = 10

func _ready() -> void:
	add_to_group("hud")  # so robots can find the HUD via get_first_node_in_group("hud")
	btn_fall_back.pressed.connect(func(): _broadcast("Fall back to base immediately!"))
	btn_prioritize_base.pressed.connect(func(): _broadcast("Prioritize defending the base above all else!"))
	btn_focus_fire.pressed.connect(func(): _broadcast("Focus all fire on the nearest enemy to the base!"))

func update_wave(wave_number: int) -> void:
	wave_label.text = "Wave " + str(wave_number)

func update_base_health(current: int, maximum: int) -> void:
	base_health_label.text = "Base: " + str(current) + "/" + str(maximum)

func update_kill_count(count: int) -> void:
	kill_label.text = "Kills: " + str(count)

func add_log_entry(text: String) -> void:
	event_log.add_item(text)
	while event_log.item_count > MAX_LOG_ENTRIES:
		event_log.remove_item(0)
	# Auto-scroll to latest entry
	event_log.ensure_current_is_visible()

func _broadcast(text: String) -> void:
	GameManager.set_commander_broadcast(text)
```

- [ ] **Step 3: Manual test**

Run `HUD.tscn`. Verify 3 broadcast buttons appear and labels are visible.

- [ ] **Step 4: Commit**

```bash
git add godot/scenes/ui/HUD.tscn godot/scenes/ui/HUD.gd
git commit -m "feat: add hud with wave info and preset commander broadcast buttons"
```

---

## Task 10: Campaign Manager

**Files:**
- Create: `godot/scripts/CampaignManager.gd`

- [ ] **Step 1: Create `godot/scripts/CampaignManager.gd`**

```gdscript
extends Node

signal mission_unlocked(mission_id: String)

const SAVE_PATH = "user://campaign_save.json"

var _currency: int = 0
var _completed_missions: Array[String] = []
var _current_mission_id: String = ""

func _ready() -> void:
	_load_save()

func get_currency() -> int:
	return _currency

func add_currency(amount: int) -> void:
	_currency += amount
	_save()

func complete_mission(mission_id: String, currency_reward: int) -> void:
	if not _completed_missions.has(mission_id):
		_completed_missions.append(mission_id)
	add_currency(currency_reward)
	_save()

func is_mission_completed(mission_id: String) -> bool:
	return mission_id in _completed_missions

func set_current_mission(mission_id: String) -> void:
	_current_mission_id = mission_id

func get_current_mission() -> String:
	return _current_mission_id

func _save() -> void:
	var data = {
		"currency": _currency,
		"completed_missions": _completed_missions
	}
	var file = FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(data))
		file.close()

func _load_save() -> void:
	if not FileAccess.file_exists(SAVE_PATH):
		return
	var file = FileAccess.open(SAVE_PATH, FileAccess.READ)
	if file == null:
		return
	var data = JSON.parse_string(file.get_as_text())
	file.close()
	if data == null:
		return
	_currency = data.get("currency", 0)
	# GD-9: JSON parse returns untyped Array; convert each element to String
	var raw_missions = data.get("completed_missions", [])
	_completed_missions.clear()
	for m in raw_missions:
		_completed_missions.append(str(m))
```

- [ ] **Step 2: Add CampaignManager to autoloads**

In Godot: `Project > Project Settings > Autoload`
Add: Name=`CampaignManager`, Path=`res://scripts/CampaignManager.gd`

(Already added in Task 1 if following in order — skip if already present.)

- [ ] **Step 3: Commit**

```bash
git add godot/scripts/CampaignManager.gd
git commit -m "feat: add campaign manager with save/load and currency tracking"
```

---

## Task 11: Game Scene (Wire Everything Together)

**Files:**
- Create: `godot/scenes/Game.tscn`
- Create: `godot/scenes/Main.tscn` and `godot/scenes/Main.gd`

- [ ] **Step 1: Create Game.tscn**

Create new scene:
- Root: `Node2D`, rename `Game`
- Instance `Map.tscn` as child (rename `Map`)
- Instance `HUD.tscn` as child
- Add script `Game.gd`

Save as `res://scenes/Game.tscn`.

- [ ] **Step 2: Create `godot/scenes/Game.gd`**

```gdscript
extends Node2D

@onready var map: Node2D = $Map
@onready var hud: CanvasLayer = $HUD

func _ready() -> void:
	var mission_id = CampaignManager.get_current_mission()

	GameManager.setup_mission(mission_id, map)
	map.base_destroyed.connect(_on_base_destroyed)
	GameManager.wave_started.connect(hud.update_wave)
	GameManager.wave_completed.connect(_on_wave_completed)
	GameManager.mission_won.connect(_on_mission_won)
	GameManager.mission_lost.connect(_on_mission_lost)
	GameManager.kill_count_changed.connect(hud.update_kill_count)

func start_with_instructions(player_instructions: Dictionary) -> void:
	var robot_configs = ConfigLoader.get_all_robots()
	GameManager.spawn_robots(robot_configs, player_instructions)
	await get_tree().create_timer(0.5).timeout
	GameManager.start_next_wave()

func _on_base_destroyed() -> void:
	GameManager.on_base_destroyed()

func _on_wave_completed(wave_number: int) -> void:
	hud.update_base_health(map.get_base_health(), 500)
	# Resupply ammo for all robots between waves
	for robot in get_tree().get_nodes_in_group("robots"):
		if is_instance_valid(robot) and robot.has_method("resupply_ammo"):
			robot.resupply_ammo()
	await get_tree().create_timer(3.0).timeout
	GameManager.start_next_wave()

func _on_mission_won() -> void:
	var mission = ConfigLoader.get_mission(CampaignManager.get_current_mission())
	CampaignManager.complete_mission(mission["id"], mission.get("reward_currency", 0))
	get_tree().change_scene_to_file("res://scenes/Main.tscn")

func _on_mission_lost() -> void:
	get_tree().change_scene_to_file("res://scenes/Main.tscn")
```

- [ ] **Step 3: Create Main.tscn and Main.gd**

Create new scene:
- Root: `Control`, rename `Main`, full rect
- Instance `PreCombatBriefing.tscn` as child
- Add script

```gdscript
# Main.gd
extends Control

@onready var briefing: Control = $PreCombatBriefing

const GAME_SCENE = preload("res://scenes/Game.tscn")

func _ready() -> void:
	CampaignManager.set_current_mission("ch01_mission_01")
	briefing.setup("ch01_mission_01")
	briefing.briefing_confirmed.connect(_on_briefing_confirmed)

func _on_briefing_confirmed(player_instructions: Dictionary) -> void:
	var game = GAME_SCENE.instantiate()
	get_tree().root.add_child(game)
	game.start_with_instructions(player_instructions)
	queue_free()
```

Save both as `res://scenes/Main.tscn`.

- [ ] **Step 4: Commit**

```bash
git add godot/scenes/Game.tscn godot/scenes/Game.gd godot/scenes/Main.tscn godot/scenes/Main.gd
git commit -m "feat: wire game scene and main scene for full mission flow"
```

<!-- PLAYTEST GATE: After Task 11, verify the full game loop.
Start the Python backend. Run Godot (F5). Go through the briefing, start a mission.
Verify: robots spawn, zombies spawn, events fire to backend, LLM responses come back, robots act.
Check for: missing node errors, null references, WebSocket disconnects.
If robots never act, check the backend logs for LLM errors.
Do NOT proceed to the integration test task until a basic loop is confirmed working. -->

---

## Task 12: End-to-End Integration Test

- [ ] **Step 1: Start the Python backend**

In terminal 1:
```bash
cd backend
uvicorn backend.main:app --host 0.0.0.0 --port 8765
```

Expected: `Uvicorn running on http://0.0.0.0:8765`

- [ ] **Step 2: Run the Godot game**

Press F5 in Godot editor (or run `Main.tscn`).

- [ ] **Step 3: Verify pre-combat briefing**

Expected:
- 4 robot cards appear (Hana, Rex, Aurora, Lily)
- Each has a text input with character counter
- Typing works and is bounded by intelligence * 100

- [ ] **Step 4: Enter instructions and start**

Type short instructions for each robot (e.g. "Defend the north chokepoint.") then click "Start Mission".

- [ ] **Step 5: Verify game runs**

Expected:
- Map appears with base
- 4 robots spawn near the base
- After a few seconds, zombie wave spawns from spawn points
- Zombies walk toward the base
- In backend terminal: LLM queries appear (Ollama is called)
- In Godot: robots start moving or attacking based on LLM decisions
- Robot speech labels show decision reasons
- HUD shows wave number and kill count

- [ ] **Step 6: Verify win condition**

Let all 3 waves complete. Expected: scene returns to Main (briefing screen).

- [ ] **Step 7: Verify lose condition**

Start a new game, enter no instructions, let zombies destroy the base. Expected: scene returns to Main.

---

## Task 13: Push and Open PR

- [ ] **Step 1: Push branch**

```bash
git push -u origin feat/phase1-godot-game
```

- [ ] **Step 2: Open PR**

```bash
gh pr create \
  --title "Phase 1: Godot Game MVP" \
  --body "$(cat <<'EOF'
## Summary
- Godot 4 project with Map, Robot, Zombie, HUD, PreCombatBriefing, Game, and Main scenes
- WebSocket client connects to Python backend, sends events, receives typed actions
- 4 robots (Architect, Vanguard, Striker, Medic) spawn from JSON configs
- Zombie enemies navigate to base and attack
- Event-driven robot AI: perception area, damage, ammo-low events fire to backend
- Pre-combat briefing screen with per-robot instruction inputs bounded by intelligence stat
- Preset commander broadcast buttons (Fall Back, Prioritize Base, Focus Fire)
- Campaign manager with save/load and currency tracking
- Win (all waves cleared) and lose (base destroyed) conditions

## Test plan
- [ ] Python backend running at ws://localhost:8765/ws
- [ ] Godot project opens without errors
- [ ] Pre-combat briefing shows 4 robot cards with instruction inputs
- [ ] Mission starts, robots and zombies spawn
- [ ] Robots receive and execute LLM decisions (move, attack, idle visible)
- [ ] Robot speech bubbles show decision reasons
- [ ] Wave completes when all enemies die
- [ ] Next wave starts after 3 second delay
- [ ] Win condition returns to briefing screen
- [ ] Lose condition returns to briefing screen
- [ ] Currency is saved after mission win

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```
