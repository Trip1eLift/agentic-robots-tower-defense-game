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
