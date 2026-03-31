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
