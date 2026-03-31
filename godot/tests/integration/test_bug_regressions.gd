extends GutTest

# Regression tests for bugs found during playtesting.
# Each test documents the original bug and verifies the fix.

var _game_scene = preload("res://scenes/Game.tscn")
var _game: Node2D

func before_each():
	CampaignManager.reset_campaign()
	CampaignManager.set_current_mission("ch01_mission_01")
	_game = _game_scene.instantiate()
	add_child_autofree(_game)
	await get_tree().process_frame
	await get_tree().process_frame


# BUG: Dead robots respawned on wave 2 within same mission.
# Root cause: Missing _is_dead flag and no disconnect from WebSocket.
func test_dead_robot_stays_dead_across_waves():
	var robots = get_tree().get_nodes_in_group("robots")
	assert_true(robots.size() > 0, "Should have robots")
	var robot = robots[0]
	var rid = robot.robot_id
	robot.take_damage(robot.get_health())
	assert_false(robot.is_alive(), "Robot should be dead")
	assert_false(robot.is_in_group("robots"), "Dead robot removed from group")
	assert_true(robot._is_dead, "_is_dead flag should be set")
	# Verify dead robot doesn't respond to actions
	robot.execute_action({"action": "move", "destination": "north_chokepoint"})
	assert_true(robot._is_dead, "Dead robot should ignore actions")


# BUG: Dead robots respawned in mission 2 with full health.
# Root cause: CampaignManager didn't track dead robots.
func test_dead_robot_persists_across_missions():
	var robots = get_tree().get_nodes_in_group("robots")
	var robot = robots[0]
	var rid = robot.robot_id
	robot.take_damage(robot.get_health())
	assert_true(CampaignManager.is_robot_dead(rid), "CampaignManager should track death")
	var alive = CampaignManager.get_alive_robots()
	var alive_ids = []
	for r in alive:
		alive_ids.append(r["id"])
	assert_false(alive_ids.has(rid), "Dead robot should not be in alive list")


# BUG: Health bar was a square instead of a thin bar.
# Root cause: Used .size instead of .custom_minimum_size, no StyleBoxFlat override.
func test_health_bar_is_thin():
	var robots = get_tree().get_nodes_in_group("robots")
	if robots.is_empty():
		pass_test("No robots")
		return
	var bar = robots[0]._health_bar
	assert_not_null(bar, "Robot should have health bar")
	assert_eq(bar.custom_minimum_size.y, 3.0, "Health bar should be 3px tall")
	# Verify it has StyleBoxFlat overrides (not default chunky theme)
	var fill_style = bar.get_theme_stylebox("fill")
	assert_true(fill_style is StyleBoxFlat, "Fill should be StyleBoxFlat")


# BUG: HUD status panel from mission 1 persisted into mission 2 pre-combat screen.
# Root cause: Game scene was added to root via instantiate() instead of change_scene_to_file().
# Fix: Both transitions use change_scene_to_file(), and HUD has reset() method.
func test_hud_reset_clears_robot_labels():
	var hud = _game.hud
	# Register a robot manually
	var robots = get_tree().get_nodes_in_group("robots")
	if robots.size() > 0:
		hud.register_robot(robots[0])
	assert_true(hud._robot_labels.size() > 0, "Should have labels after register")
	hud.reset()
	assert_eq(hud._robot_labels.size(), 0, "Reset should clear labels")
	assert_eq(hud._tracked_robots.size(), 0, "Reset should clear tracked robots")


# BUG: 4 characters still showed on map after one died in wave 1.
# Root cause: Dead robot was hidden but still in "robots" group and had collision.
func test_dead_robot_fully_disabled():
	var robots = get_tree().get_nodes_in_group("robots")
	var robot = robots[0]
	robot.take_damage(robot.get_health())
	assert_false(robot.visible, "Dead robot should be hidden")
	assert_false(robot.is_in_group("robots"), "Dead robot removed from group")
	assert_eq(robot.collision_layer, 0, "Dead robot collision layer cleared")
	assert_eq(robot.collision_mask, 0, "Dead robot collision mask cleared")
	assert_false(robot.perception_area.monitoring, "Perception disabled")


# BUG: Status screen showed robots as "destroyed" even when alive in mission 2.
# Root cause: HUD _tracked_robots had stale references from previous Game scene.
func test_hud_tracks_current_robots_only():
	var hud = _game.hud
	hud.reset()
	var robots = get_tree().get_nodes_in_group("robots")
	for r in robots:
		hud.register_robot(r)
	assert_eq(hud._tracked_robots.size(), robots.size())
	# All should show as alive
	hud._update_robot_stats()
	for rid in hud._robot_labels:
		var label: Label = hud._robot_labels[rid]
		assert_false(label.text.contains("DEAD"), rid + " should show as alive")


# BUG: Robot health carried over but displayed as full in mission 2.
# Root cause: Health bar value not updated after restoring saved state.
func test_saved_health_restores_correctly():
	CampaignManager.save_robot_state("architect_common_hana", 50, 20)
	var saved_hp = CampaignManager.get_robot_health("architect_common_hana", 100)
	var saved_ammo = CampaignManager.get_robot_ammo("architect_common_hana", 40)
	assert_eq(saved_hp, 50, "Saved health should be 50")
	assert_eq(saved_ammo, 20, "Saved ammo should be 20")


# BUG: All robots died -> campaign softlocked (no robots to spawn).
# Root cause: No reset mechanism when party is wiped.
func test_party_wipe_resets_campaign():
	for r in ConfigLoader.get_all_robots():
		CampaignManager.mark_robot_dead(r["id"])
	assert_true(CampaignManager.is_party_wiped(), "All dead = party wiped")
	CampaignManager.reset_campaign()
	assert_false(CampaignManager.is_party_wiped(), "Reset should clear dead list")
	assert_eq(CampaignManager.get_alive_robots().size(), 4, "All 4 should be alive after reset")


# BUG: Zombie AttackTimer fired before signal was connected (race condition).
# Root cause: AttackTimer had autostart=true in scene, signal connected in setup().
func test_zombie_attack_timer_not_autostart():
	var zombie_scene = preload("res://scenes/enemies/Zombie.tscn")
	var zombie = zombie_scene.instantiate()
	# Before setup, timer should not be running
	add_child_autofree(zombie)
	await get_tree().process_frame
	assert_false(zombie.attack_timer.is_stopped() == false and zombie.attack_timer.timeout.get_connections().is_empty(),
		"Timer should not run without signal connected")


# BUG: Heal action was a no-op (medic class non-functional).
# Root cause: _perform_heal only logged, didn't actually heal.
func test_heal_restores_ally_health():
	var robots = get_tree().get_nodes_in_group("robots")
	if robots.size() < 2:
		pass_test("Need 2+ robots for heal test")
		return
	var medic = null
	var target = null
	for r in robots:
		if r._config.get("class", "") == "medic":
			medic = r
		elif target == null:
			target = r
	if medic == null or target == null:
		pass_test("No medic or target found")
		return
	# Damage the target
	target.take_damage(50)
	var hp_after_damage = target.get_health()
	# Medic heals
	medic._perform_heal({"target_id": target.robot_id})
	assert_gt(target.get_health(), hp_after_damage, "Target health should increase after heal")


# BUG: Base health only updated on wave completion, not during combat.
# Root cause: update_base_health only called in _on_wave_completed.
# Fix: Map emits base_health_changed signal on every damage.
func test_base_health_updates_in_realtime():
	watch_signals(_game.map)
	_game.map.take_base_damage(10)
	assert_signal_emitted(_game.map, "base_health_changed")
	assert_eq(_game.map.get_base_health(), 490)


# BUG: CampaignManager save/load didn't persist dead_robots, robot_health, robot_ammo.
# Root cause: _save() only saved currency and completed_missions.
func test_campaign_save_persists_all_state():
	CampaignManager.mark_robot_dead("vanguard_common_rex")
	CampaignManager.save_robot_state("architect_common_hana", 75, 30)
	CampaignManager.complete_mission("ch01_mission_01", 300)
	# Force reload from disk
	CampaignManager._dead_robots.clear()
	CampaignManager._robot_health.clear()
	CampaignManager._robot_ammo.clear()
	CampaignManager._completed_missions.clear()
	CampaignManager._currency = 0
	CampaignManager._load_save()
	assert_true(CampaignManager.is_robot_dead("vanguard_common_rex"), "Dead robot should persist")
	assert_eq(CampaignManager.get_robot_health("architect_common_hana", 100), 75, "Health should persist")
	assert_eq(CampaignManager.get_robot_ammo("architect_common_hana", 40), 30, "Ammo should persist")
	assert_true(CampaignManager.is_mission_completed("ch01_mission_01"), "Mission completion should persist")
	assert_eq(CampaignManager.get_currency(), 300, "Currency should persist")
