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
var _is_spawning: bool = false
var _next_enemy_id: int = 1
var _enemy_id_map: Dictionary = {}
var _id_enemy_map: Dictionary = {}

func setup_mission(mission_id: String, map: Node) -> void:
	_map = map
	_current_mission = ConfigLoader.get_mission(mission_id)
	_current_wave = 0
	_kill_count = 0
	_commander_broadcast = ""
	_is_wave_active = false
	_is_spawning = false
	# Clean up old robots/enemies from previous mission
	for r in _robots:
		if is_instance_valid(r):
			r.queue_free()
	for e in _enemies:
		if is_instance_valid(e):
			e.queue_free()
	_robots.clear()
	_enemies.clear()
	_next_enemy_id = 1
	_enemy_id_map.clear()
	_id_enemy_map.clear()
	# Disconnect any lingering signals from previous game
	_disconnect_all()

func spawn_robots(robot_configs: Array, player_instructions: Dictionary) -> void:
	print("GameManager: spawn_robots called, count=", robot_configs.size(), " existing=", _robots.size())
	if not _robots.is_empty():
		push_warning("GameManager: robots already spawned, skipping")
		return
	for i in range(robot_configs.size()):
		var config = robot_configs[i]
		var robot = ROBOT_SCENE.instantiate()
		_map.add_child(robot)
		robot.global_position = _map.get_robot_spawn_position(i)
		robot.setup(config, _map)
		var instructions = player_instructions.get(config["id"], "")
		robot.set_player_instructions(instructions)
		_robots.append(robot)
		GameRecorder.log_robot_spawned(config["id"], config.get("class", ""), [robot.global_position.x, robot.global_position.y])
		# Register with HUD for status tracking
		var hud = robot.get_tree().get_first_node_in_group("hud")
		if hud and hud.has_method("register_robot"):
			hud.register_robot(robot)

func start_next_wave() -> void:
	var waves = _current_mission.get("waves", [])
	print("GameManager: start_next_wave called, wave=", _current_wave + 1, "/", waves.size(), " robots=", _robots.size())
	if _current_wave >= waves.size():
		mission_won.emit()
		return
	_is_wave_active = true
	var wave_data = waves[_current_wave]
	GameRecorder.log_wave_started(_current_wave + 1)
	wave_started.emit(_current_wave + 1)
	await _spawn_wave_enemies(wave_data)

func _spawn_wave_enemies(wave_data: Dictionary) -> void:
	_is_spawning = true
	for enemy_group in wave_data.get("enemies", []):
		var enemy_config = ConfigLoader.get_enemy(enemy_group["type"])
		var spawn_point_id = enemy_group.get("spawn_point", "")
		var spawn_pos = Vector2(512, 50)
		if spawn_point_id and _map:
			spawn_pos = _map.get_spawn_point(spawn_point_id)
		var interval = enemy_group.get("spawn_interval_sec", 1.0)
		for i in range(enemy_group["count"]):
			var zombie = ZOMBIE_SCENE.instantiate()
			_map.add_child(zombie)
			zombie.global_position = spawn_pos + Vector2(randf_range(-30, 30), randf_range(-30, 30))
			zombie.setup(enemy_config, _map.base_node)
			zombie.died.connect(_on_enemy_died)
			_enemies.append(zombie)
			var eid = _next_enemy_id
			_next_enemy_id += 1
			_enemy_id_map[zombie] = eid
			_id_enemy_map[eid] = zombie
			GameRecorder.log_enemy_spawned(eid, enemy_group["type"], [zombie.global_position.x, zombie.global_position.y])
			await get_tree().create_timer(interval).timeout
	_is_spawning = false
	# Check if all enemies already died during spawning
	if _enemies.is_empty() and _is_wave_active:
		_is_wave_active = false
		_current_wave += 1
		wave_completed.emit(_current_wave)

func _on_enemy_died(enemy: Node2D) -> void:
	var eid = _enemy_id_map.get(enemy, -1)
	_enemy_id_map.erase(enemy)
	if eid != -1:
		_id_enemy_map.erase(eid)
	_enemies.erase(enemy)
	_kill_count += 1
	GameRecorder.log_enemy_killed(eid)
	kill_count_changed.emit(_kill_count)
	_notify_robots_of_kill(enemy, eid)
	if _enemies.is_empty() and _is_wave_active and not _is_spawning:
		_is_wave_active = false
		_current_wave += 1
		GameRecorder.log_wave_completed(_current_wave)
		wave_completed.emit(_current_wave)

func _notify_robots_of_kill(enemy: Node2D, enemy_id: int) -> void:
	for robot in _robots:
		if is_instance_valid(robot) and robot.has_method("is_alive") and robot.is_alive():
			var dist = robot.global_position.distance_to(enemy.global_position)
			if dist < 300:
				robot._fire_event("ENEMY_ELIMINATED",
					"enemy " + str(enemy_id) + " killed at " + str(enemy.global_position))

func get_enemy_id(enemy: Node2D) -> int:
	return _enemy_id_map.get(enemy, -1)

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
	for robot in _robots:
		if is_instance_valid(robot) and robot.has_method("is_alive") and robot.is_alive():
			robot._fire_event("COMMANDER_BROADCAST", text)

func is_wave_active() -> bool:
	return _is_wave_active

func get_kill_count() -> int:
	return _kill_count

func _disconnect_all() -> void:
	for sig in [wave_started, wave_completed, mission_won, mission_lost, kill_count_changed]:
		for conn in sig.get_connections():
			sig.disconnect(conn["callable"])
