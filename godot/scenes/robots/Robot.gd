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
var _map: Node = null
var _ammo_low_fired: bool = false
var _is_dead: bool = false
var _event_cooldowns: Dictionary = {}
var _health_bar: ProgressBar = null
var _name_label_node: Label = null

const MAX_RECENT_EVENTS = 5
const EVENT_COOLDOWN_MS = 2000

func setup(config: Dictionary, map: Node) -> void:
	_config = config
	_map = map
	var stats = config["base_stats"]
	_health = stats["health"]
	_max_health = stats["health"]
	_ammo = stats["ammo"]
	_speed = stats["speed"] * 20.0
	robot_id = config["id"]
	add_to_group("robots")
	speech_label.visible = false
	speech_timer.wait_time = 3.0
	speech_timer.one_shot = true
	attack_timer.wait_time = 1.0
	attack_timer.one_shot = false
	attack_timer.timeout.connect(_on_attack_timer)
	thinking_label.text = "..."
	thinking_label.visible = false
	perception_area.body_entered.connect(_on_body_entered_perception)
	perception_area.body_exited.connect(_on_body_exited_perception)
	WebSocketClient.action_received.connect(_on_action_received)
	WebSocketClient.register_robot(robot_id, _health, _ammo, global_position)
	_setup_health_bar()
	_execute_default_spawn_action()

func _setup_health_bar() -> void:
	_name_label_node = Label.new()
	_name_label_node.text = _config.get("name", robot_id)
	_name_label_node.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_name_label_node.position = Vector2(-30, -35)
	_name_label_node.add_theme_font_size_override("font_size", 10)
	add_child(_name_label_node)
	_health_bar = ProgressBar.new()
	_health_bar.max_value = _max_health
	_health_bar.value = _health
	_health_bar.custom_minimum_size = Vector2(50, 3)
	_health_bar.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	_health_bar.position = Vector2(-25, -22)
	_health_bar.show_percentage = false
	# Force the height by overriding theme styles
	var bg = StyleBoxFlat.new()
	bg.bg_color = Color(0.2, 0.2, 0.2)
	bg.set_content_margin_all(0)
	var fill = StyleBoxFlat.new()
	fill.bg_color = Color(0.2, 0.8, 0.2)
	fill.set_content_margin_all(0)
	_health_bar.add_theme_stylebox_override("background", bg)
	_health_bar.add_theme_stylebox_override("fill", fill)
	add_child(_health_bar)

func set_player_instructions(text: String) -> void:
	var max_chars = _config["base_stats"]["intelligence"] * 100
	_player_instructions = text.left(max_chars)

func _execute_default_spawn_action() -> void:
	var robot_class = _config.get("class", "striker")
	match robot_class:
		"architect":
			if _map:
				var positions = _map.get_all_strategic_positions()
				if not positions.is_empty():
					var pos_id = positions[0].get("id", "base_entrance")
					nav_agent.target_position = _map.get_strategic_position(pos_id)
		"vanguard":
			if _map:
				var positions = _map.get_all_strategic_positions()
				if not positions.is_empty():
					var pos_id = positions[0].get("id", "north_chokepoint")
					nav_agent.target_position = _map.get_strategic_position(pos_id)
		"striker":
			pass
		"medic":
			if _map:
				nav_agent.target_position = _map.get_strategic_position("rear_support")

func _can_fire_event(event_type: String) -> bool:
	var now = Time.get_ticks_msec()
	var last_fired = _event_cooldowns.get(event_type, 0)
	if now - last_fired < EVENT_COOLDOWN_MS:
		return false
	_event_cooldowns[event_type] = now
	return true

func resupply_ammo() -> void:
	_ammo = _config["base_stats"]["ammo"]
	_ammo_low_fired = false

func _physics_process(delta: float) -> void:
	if not is_alive():
		return
	_execute_movement()
	_check_enemy_in_range()

func _execute_movement() -> void:
	if nav_agent.is_navigation_finished():
		return
	var next_pos = nav_agent.get_next_path_position()
	var direction = (next_pos - global_position).normalized()
	velocity = direction * _speed
	move_and_slide()

func _check_enemy_in_range() -> void:
	var attack_range = _config.get("base_stats", {}).get("attack_range", 120.0)
	for enemy in _enemies_in_perception:
		if is_instance_valid(enemy):
			var dist = global_position.distance_to(enemy.global_position)
			if dist <= attack_range:
				_fire_event("ENEMY_IN_RANGE",
					str(GameManager.get_enemy_id(enemy)) + " at distance " + str(int(dist)))
				return

func execute_action(action: Dictionary) -> void:
	if _is_dead:
		return
	_current_action = action
	thinking_label.visible = false
	GameRecorder.log_action_received(robot_id, action)
	attack_timer.stop()
	var action_name = action.get("action", "idle")
	# Build not implemented yet -- move to destination instead of idling
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
				_perform_attack()
				attack_timer.start()
		"heal":
			_perform_heal(action)
		"idle":
			pass
	var reason = action.get("reason", "")
	if reason:
		var hud = get_tree().get_first_node_in_group("hud")
		if hud and hud.has_method("add_log_entry"):
			hud.add_log_entry(_config.get("name", robot_id) + ": " + reason)

func _on_attack_timer() -> void:
	var action_name = _current_action.get("action", "idle")
	if not ["attack", "snipe"].has(action_name):
		attack_timer.stop()
		return
	if _target_enemy == null or not is_instance_valid(_target_enemy):
		_target_enemy = _find_enemy_by_id(_current_action.get("target_id", -1))
	if _target_enemy == null or not is_instance_valid(_target_enemy):
		attack_timer.stop()
		_fire_event("ENEMY_ELIMINATED", "current target lost, requesting new orders")
		return
	_perform_attack()

func _perform_attack() -> void:
	if _target_enemy == null or not is_instance_valid(_target_enemy):
		return
	var damage = _config["base_stats"]["damage"] * 5
	GameRecorder.log_attack(robot_id, GameManager.get_enemy_id(_target_enemy), damage)
	if _target_enemy.has_method("take_damage"):
		_target_enemy.take_damage(damage)
	_ammo = max(0, _ammo - 1)
	_push_recent_event("ENEMY_ATTACKED: " + str(_target_enemy.name))
	if not _ammo_low_fired and (_ammo == 0 or (_ammo / float(_config["base_stats"]["ammo"])) < 0.2):
		_ammo_low_fired = true
		_fire_event("AMMO_LOW", "ammo at " + str(_ammo))
	WebSocketClient.send_state_update(robot_id, _health, _ammo, global_position)

func _perform_heal(action: Dictionary) -> void:
	var target_id = action.get("target_id", null)
	if target_id == null:
		return
	# Find ally robot by matching robot_id or sequential index
	for r in get_tree().get_nodes_in_group("robots"):
		if is_instance_valid(r) and r != self and r.is_alive():
			if r.robot_id == str(target_id) or r.robot_id.ends_with(str(target_id)):
				var heal_amount = _config["base_stats"].get("intelligence", 5) * 5
				r._health = min(r._max_health, r._health + heal_amount)
				if r._health_bar:
					r._health_bar.value = r._health
				GameRecorder.log_heal(robot_id, r.robot_id, heal_amount)
				_push_recent_event("HEALED: " + r.robot_id + " for " + str(heal_amount))
				WebSocketClient.send_state_update(r.robot_id, r._health, r._ammo, r.global_position)
				return
	_push_recent_event("HEAL_FAILED: target " + str(target_id) + " not found")

func take_damage(amount: int) -> void:
	_health = max(0, _health - amount)
	if _health_bar:
		_health_bar.value = _health
	GameRecorder.log_damage_taken(robot_id, amount, _health)
	_push_recent_event("TOOK_DAMAGE: " + str(amount))
	_fire_event("TAKING_DAMAGE", "health now " + str(_health) + "/" + str(_max_health))
	WebSocketClient.send_state_update(robot_id, _health, _ammo, global_position)
	if _health == 0:
		_die()

func is_alive() -> bool:
	return _health > 0 and not _is_dead

func _die() -> void:
	_push_recent_event("ROBOT_DIED")
	_is_dead = true
	CampaignManager.mark_robot_dead(robot_id)
	GameRecorder.log_robot_died(robot_id)
	set_physics_process(false)
	set_process(false)
	remove_from_group("robots")
	collision_layer = 0
	collision_mask = 0
	perception_area.monitoring = false
	attack_timer.stop()
	# Disconnect from backend so no more actions arrive for this robot
	if WebSocketClient.action_received.is_connected(_on_action_received):
		WebSocketClient.action_received.disconnect(_on_action_received)
	hide()

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
	if _is_dead:
		return
	if not _can_fire_event(event_type):
		return
	var local_context = _build_local_context()
	var commander_broadcast = null
	if has_node("/root/GameManager"):
		commander_broadcast = GameManager.get_commander_broadcast()
	GameRecorder.log_event_sent(robot_id, event_type, event_detail)
	WebSocketClient.send_event(robot_id, event_type, event_detail, local_context,
			_player_instructions, commander_broadcast)

func _build_local_context() -> Dictionary:
	var enemies = []
	for e in _enemies_in_perception:
		if is_instance_valid(e):
			var e_health: int = 50
			if e.has_method("get_health"):
				e_health = e.get_health()
			enemies.append({"id": GameManager.get_enemy_id(e), "type": "zombie",
				"position": [e.global_position.x, e.global_position.y],
				"health": e_health})
	var allies = []
	for r in get_tree().get_nodes_in_group("robots"):
		if is_instance_valid(r) and r != self and r.has_method("is_alive") and r.is_alive():
			var dist = global_position.distance_to(r.global_position)
			if dist < 300:
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

func _find_enemy_by_id(enemy_id: int) -> Node2D:
	var enemy = GameManager.get_enemy_by_id(enemy_id)
	if enemy and is_instance_valid(enemy):
		return enemy
	# Fallback: attack any enemy in perception if target not found
	for e in _enemies_in_perception:
		if is_instance_valid(e):
			return e
	return null

func _show_speech(text: String) -> void:
	speech_label.text = text
	speech_timer.start()

func get_health() -> int:
	return _health

func get_ammo() -> int:
	return _ammo
