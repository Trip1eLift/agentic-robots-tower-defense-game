extends Node

signal mission_unlocked(mission_id: String)

const SAVE_PATH = "res://campaign_save.json"

var _currency: int = 0
var _completed_missions: Array[String] = []
var _current_mission_id: String = ""
var _dead_robots: Array[String] = []       # robot IDs that died (persist across missions)
var _robot_health: Dictionary = {}          # robot_id -> current health (persist across missions)
var _robot_ammo: Dictionary = {}            # robot_id -> current ammo (persist across missions)

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

func mark_robot_dead(robot_id: String) -> void:
	if robot_id not in _dead_robots:
		_dead_robots.append(robot_id)
		_save()

func is_robot_dead(robot_id: String) -> bool:
	return robot_id in _dead_robots

func get_alive_robots() -> Array:
	var all_robots = ConfigLoader.get_all_robots()
	return all_robots.filter(func(r): return r["id"] not in _dead_robots)

func save_robot_state(robot_id: String, health: int, ammo: int) -> void:
	_robot_health[robot_id] = health
	_robot_ammo[robot_id] = ammo
	_save()

func get_robot_health(robot_id: String, default: int) -> int:
	return _robot_health.get(robot_id, default)

func get_robot_ammo(robot_id: String, default: int) -> int:
	return _robot_ammo.get(robot_id, default)

func reset_campaign() -> void:
	_currency = 0
	_completed_missions.clear()
	_dead_robots.clear()
	_robot_health.clear()
	_robot_ammo.clear()
	_current_mission_id = ""
	_save()

func is_party_wiped() -> bool:
	return get_alive_robots().is_empty()

func _save() -> void:
	var data = {
		"currency": _currency,
		"completed_missions": _completed_missions,
		"dead_robots": _dead_robots,
		"robot_health": _robot_health,
		"robot_ammo": _robot_ammo
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
	var raw_missions = data.get("completed_missions", [])
	_completed_missions.clear()
	for m in raw_missions:
		_completed_missions.append(str(m))
	var raw_dead = data.get("dead_robots", [])
	_dead_robots.clear()
	for r in raw_dead:
		_dead_robots.append(str(r))
	_robot_health = data.get("robot_health", {})
	_robot_ammo = data.get("robot_ammo", {})
