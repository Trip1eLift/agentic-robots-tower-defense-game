extends Node2D

signal base_destroyed()

@export var map_id: String = "ch01_collapsed_road"

@onready var base_node: Node2D = $Base
@onready var enemy_spawn_points: Node2D = $EnemySpawnPoints
@onready var robot_spawn_zone: Node2D = $RobotSpawnZone
@onready var strategic_positions_node: Node2D = $StrategicPositions

var _base_health: int = 500
var _base_max_health: int = 500
var _map_config: Dictionary = {}
var _strategic_positions: Dictionary = {}

func _ready() -> void:
	_map_config = ConfigLoader.get_map(map_id)
	_load_strategic_positions()

func _load_strategic_positions() -> void:
	for pos_data in _map_config.get("strategic_positions", []):
		var marker = strategic_positions_node.find_child(pos_data["id"])
		if marker:
			_strategic_positions[pos_data["id"]] = marker.global_position
		else:
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

signal base_health_changed(current: int, maximum: int)

func take_base_damage(amount: int) -> void:
	_base_health = max(0, _base_health - amount)
	GameRecorder.log_base_damage(amount, _base_health)
	base_health_changed.emit(_base_health, _base_max_health)
	if _base_health == 0:
		base_destroyed.emit()

func get_base_health() -> int:
	return _base_health

func get_base_health_percent() -> float:
	return float(_base_health) / float(_base_max_health)
