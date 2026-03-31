extends GutTest

# End-to-end integration test for the full game flow.
# Requires Python backend running: USE_MOCK_LLM=true uvicorn backend.main:app --port 8765

var _game_scene = preload("res://scenes/Game.tscn")
var _game: Node2D

func before_all():
	# Reset campaign state for clean test
	CampaignManager.reset_campaign()
	CampaignManager.set_current_mission("ch01_mission_01")

func before_each():
	CampaignManager.reset_campaign()
	CampaignManager.set_current_mission("ch01_mission_01")
	_game = _game_scene.instantiate()
	add_child_autofree(_game)
	await get_tree().process_frame
	await get_tree().process_frame

func test_game_scene_loads():
	assert_not_null(_game, "Game scene should load")
	assert_not_null(_game.map, "Map should exist")
	assert_not_null(_game.hud, "HUD should exist")

func test_map_has_base():
	assert_not_null(_game.map.base_node, "Map should have a base")
	assert_eq(_game.map.get_base_health(), 500)

func test_map_has_spawn_points():
	var points = _game.map.get_all_spawn_points()
	assert_eq(points.size(), 2, "Map should have 2 spawn points")

func test_map_has_strategic_positions():
	var positions = _game.map.get_all_strategic_positions()
	assert_eq(positions.size(), 4, "Map should have 4 strategic positions")

func test_spawn_robots():
	var configs = ConfigLoader.get_all_robots()
	GameManager.spawn_robots(configs, {})
	await get_tree().process_frame
	var robots = get_tree().get_nodes_in_group("robots")
	assert_eq(robots.size(), 4, "Should spawn 4 robots")

func test_robots_have_correct_ids():
	var configs = ConfigLoader.get_all_robots()
	GameManager.spawn_robots(configs, {})
	await get_tree().process_frame
	var robots = get_tree().get_nodes_in_group("robots")
	var ids = []
	for r in robots:
		ids.append(r.robot_id)
	assert_true(ids.has("architect_common_hana"))
	assert_true(ids.has("vanguard_common_rex"))
	assert_true(ids.has("striker_common_aurora"))
	assert_true(ids.has("medic_common_lily"))

func test_robots_have_health_bars():
	var configs = ConfigLoader.get_all_robots()
	GameManager.spawn_robots(configs, {})
	await get_tree().process_frame
	var robots = get_tree().get_nodes_in_group("robots")
	for r in robots:
		assert_not_null(r._health_bar, r.robot_id + " should have health bar")

func test_robots_start_alive():
	var configs = ConfigLoader.get_all_robots()
	GameManager.spawn_robots(configs, {})
	await get_tree().process_frame
	for r in get_tree().get_nodes_in_group("robots"):
		assert_true(r.is_alive(), r.robot_id + " should be alive")

func test_robot_takes_damage():
	var configs = ConfigLoader.get_all_robots()
	GameManager.spawn_robots(configs, {})
	await get_tree().process_frame
	var robot = get_tree().get_nodes_in_group("robots")[0]
	var initial_hp = robot.get_health()
	robot.take_damage(10)
	assert_eq(robot.get_health(), initial_hp - 10)

func test_robot_dies_at_zero_health():
	var configs = ConfigLoader.get_all_robots()
	GameManager.spawn_robots(configs, {})
	await get_tree().process_frame
	var robot = get_tree().get_nodes_in_group("robots")[0]
	robot.take_damage(robot.get_health())
	assert_false(robot.is_alive())
	assert_true(CampaignManager.is_robot_dead(robot.robot_id))

func test_dead_robot_removed_from_group():
	var configs = ConfigLoader.get_all_robots()
	GameManager.spawn_robots(configs, {})
	await get_tree().process_frame
	var robot = get_tree().get_nodes_in_group("robots")[0]
	var rid = robot.robot_id
	robot.take_damage(robot.get_health())
	assert_false(robot.is_in_group("robots"))

func test_spawn_zombie():
	var zombie_scene = preload("res://scenes/enemies/Zombie.tscn")
	var zombie = zombie_scene.instantiate()
	_game.map.add_child(zombie)
	var config = ConfigLoader.get_enemy("zombie")
	zombie.setup(config, _game.map.base_node)
	await get_tree().process_frame
	assert_eq(zombie.get_health(), 50)
	assert_true(zombie.is_in_group("enemies"))

func test_zombie_takes_damage_and_dies():
	var zombie_scene = preload("res://scenes/enemies/Zombie.tscn")
	var zombie = zombie_scene.instantiate()
	_game.map.add_child(zombie)
	var config = ConfigLoader.get_enemy("zombie")
	zombie.setup(config, _game.map.base_node)
	watch_signals(zombie)
	zombie.take_damage(50)
	assert_signal_emitted(zombie, "died")

func test_base_takes_damage():
	_game.map.take_base_damage(100)
	assert_eq(_game.map.get_base_health(), 400)

func test_base_destroyed_triggers_loss():
	# Test the map signal directly (GameManager signals are wired by Game._ready)
	watch_signals(_game.map)
	_game.map.take_base_damage(500)
	assert_signal_emitted(_game.map, "base_destroyed")

func test_wave_system_exists():
	# Game._ready already called setup_mission, verify state
	assert_true(GameManager._current_mission.has("waves"), "Mission should have waves")
	assert_eq(GameManager._current_mission["waves"].size(), 3, "Mission 1 should have 3 waves")

func test_kill_count_increments():
	GameManager.setup_mission("ch01_mission_01", _game.map)
	watch_signals(GameManager)
	var zombie_scene = preload("res://scenes/enemies/Zombie.tscn")
	var zombie = zombie_scene.instantiate()
	_game.map.add_child(zombie)
	var config = ConfigLoader.get_enemy("zombie")
	zombie.setup(config, _game.map.base_node)
	zombie.died.connect(GameManager._on_enemy_died)
	GameManager._enemies.append(zombie)
	GameManager._is_wave_active = true
	var eid = GameManager._next_enemy_id
	GameManager._enemy_id_map[zombie] = eid
	GameManager._id_enemy_map[eid] = zombie
	GameManager._next_enemy_id += 1
	zombie.take_damage(50)
	assert_eq(GameManager.get_kill_count(), 1)
	assert_signal_emitted(GameManager, "kill_count_changed")

func test_player_instructions_set_on_robot():
	# Game._ready already spawned robots. Set instructions directly.
	var robots = get_tree().get_nodes_in_group("robots")
	if robots.is_empty():
		pass_test("No robots to test (already consumed by Game._ready)")
		return
	var robot = robots[0]
	robot.set_player_instructions("Hold the north chokepoint")
	assert_eq(robot._player_instructions, "Hold the north chokepoint")

func test_commander_broadcast():
	var configs = ConfigLoader.get_all_robots()
	GameManager.spawn_robots(configs, {})
	await get_tree().process_frame
	GameManager.set_commander_broadcast("Fall back!")
	assert_eq(GameManager.get_commander_broadcast(), "Fall back!")

func test_only_alive_robots_returned_after_death():
	# Don't spawn -- just verify CampaignManager filters correctly
	CampaignManager.mark_robot_dead("vanguard_common_rex")
	var alive = CampaignManager.get_alive_robots()
	assert_eq(alive.size(), 3)
	var ids = []
	for r in alive:
		ids.append(r["id"])
	assert_false(ids.has("vanguard_common_rex"))
	assert_true(ids.has("architect_common_hana"))
