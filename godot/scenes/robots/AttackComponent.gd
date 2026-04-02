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
