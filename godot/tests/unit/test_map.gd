extends GutTest

var _map_scene = preload("res://scenes/map/Map.tscn")
var _map: Node2D

func before_each():
	_map = _map_scene.instantiate()
	add_child_autofree(_map)
	await get_tree().process_frame

func test_base_position():
	var pos = _map.get_base_position()
	assert_eq(pos, Vector2(512, 500))

func test_base_initial_health():
	assert_eq(_map.get_base_health(), 500)

func test_take_base_damage():
	_map.take_base_damage(100)
	assert_eq(_map.get_base_health(), 400)

func test_base_health_clamps_to_zero():
	_map.take_base_damage(999)
	assert_eq(_map.get_base_health(), 0)

func test_base_destroyed_signal():
	watch_signals(_map)
	_map.take_base_damage(500)
	assert_signal_emitted(_map, "base_destroyed")

func test_base_health_changed_signal():
	watch_signals(_map)
	_map.take_base_damage(50)
	assert_signal_emitted(_map, "base_health_changed")

func test_strategic_positions_loaded():
	var positions = _map.get_all_strategic_positions()
	assert_eq(positions.size(), 4)

func test_get_strategic_position():
	var pos = _map.get_strategic_position("north_chokepoint")
	assert_eq(pos, Vector2(512, 200))

func test_get_spawn_point():
	var pos = _map.get_spawn_point("spawn_north")
	assert_eq(pos, Vector2(512, 50))

func test_robot_spawn_positions():
	var pos0 = _map.get_robot_spawn_position(0)
	var pos1 = _map.get_robot_spawn_position(1)
	assert_ne(pos0, pos1, "Different robots should spawn at different positions")

func test_base_health_percent():
	_map.take_base_damage(250)
	assert_almost_eq(_map.get_base_health_percent(), 0.5, 0.01)
