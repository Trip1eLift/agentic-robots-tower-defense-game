extends GutTest

func test_load_all_robots():
	var robots = ConfigLoader.get_all_robots()
	assert_eq(robots.size(), 4, "Should load 4 robot archetypes")

func test_load_robot_by_id():
	var robot = ConfigLoader.get_robot("architect_common_hana")
	assert_eq(robot["name"], "Hana")
	assert_eq(robot["class"], "architect")

func test_robot_has_required_fields():
	var robot = ConfigLoader.get_robot("vanguard_common_rex")
	assert_true(robot.has("base_stats"), "Robot should have base_stats")
	assert_true(robot.has("personality_prompt"), "Robot should have personality_prompt")
	assert_true(robot["base_stats"].has("attack_range"), "Stats should have attack_range")
	assert_true(robot["base_stats"].has("attack_rate"), "Stats should have attack_rate")

func test_load_all_robot_classes():
	var robots = ConfigLoader.get_all_robots()
	var classes = []
	for r in robots:
		classes.append(r["class"])
	assert_true(classes.has("architect"))
	assert_true(classes.has("vanguard"))
	assert_true(classes.has("striker"))
	assert_true(classes.has("medic"))

func test_load_map():
	var map_cfg = ConfigLoader.get_map("ch01_collapsed_road")
	assert_eq(map_cfg["name"], "Collapsed Road")
	assert_eq(map_cfg["strategic_positions"].size(), 4)

func test_load_enemy():
	var enemy = ConfigLoader.get_enemy("zombie")
	assert_eq(enemy["name"], "Zombie")
	assert_eq(enemy["stats"]["health"], 50)

func test_load_mission():
	var mission = ConfigLoader.get_mission("ch01_mission_01")
	assert_eq(mission["title"], "First Contact")
	assert_eq(mission["waves"].size(), 3)

func test_mission_has_wave_timing():
	var mission = ConfigLoader.get_mission("ch01_mission_01")
	var wave = mission["waves"][0]
	assert_true(wave.has("delay_before_wave_sec"), "Wave should have delay")
	var enemies = wave["enemies"][0]
	assert_true(enemies.has("spawn_point"), "Enemy group should have spawn_point")
	assert_true(enemies.has("spawn_interval_sec"), "Enemy group should have spawn_interval_sec")

func test_missing_robot_returns_empty():
	var robot = ConfigLoader.get_robot("nonexistent")
	assert_eq(robot, {})

func test_mission_has_base_health():
	var mission = ConfigLoader.get_mission("ch01_mission_01")
	assert_true(mission.has("base_health"), "Mission should have base_health")
	assert_eq(mission["base_health"], 500)
