extends Node2D

@onready var map: Node2D = $Map
@onready var hud: CanvasLayer = $HUD

func _ready() -> void:
	var mission_id = CampaignManager.get_current_mission()
	hud.reset()
	GameRecorder.start_recording(mission_id)
	GameManager.setup_mission(mission_id, map)
	map.base_destroyed.connect(_on_base_destroyed)
	map.base_health_changed.connect(hud.update_base_health)
	GameManager.wave_started.connect(hud.update_wave)
	GameManager.wave_completed.connect(_on_wave_completed)
	GameManager.mission_won.connect(_on_mission_won)
	GameManager.mission_lost.connect(_on_mission_lost)
	GameManager.kill_count_changed.connect(hud.update_kill_count)

	# Get player instructions from briefing (stored in CampaignManager meta)
	var player_instructions: Dictionary = {}
	if CampaignManager.has_meta("player_instructions"):
		player_instructions = CampaignManager.get_meta("player_instructions")

	# Wait for WebSocket connection before spawning
	if not WebSocketClient._is_connected:
		await WebSocketClient.connected

	# Only spawn robots that survived previous missions
	var robot_configs = CampaignManager.get_alive_robots()
	GameManager.spawn_robots(robot_configs, player_instructions)

	# Restore health/ammo from previous mission
	for robot in get_tree().get_nodes_in_group("robots"):
		if is_instance_valid(robot):
			var rid = robot.robot_id
			var saved_hp = CampaignManager.get_robot_health(rid, robot._max_health)
			var saved_ammo = CampaignManager.get_robot_ammo(rid, robot._ammo)
			robot._health = saved_hp
			robot._ammo = saved_ammo
			if robot._health_bar:
				robot._health_bar.value = saved_hp

	await get_tree().create_timer(0.5).timeout
	GameManager.start_next_wave()

func _on_base_destroyed() -> void:
	GameManager.on_base_destroyed()

func _on_wave_completed(wave_number: int) -> void:
	hud.update_base_health(map.get_base_health(), 500)
	await get_tree().create_timer(3.0).timeout
	GameManager.start_next_wave()

func _on_mission_won() -> void:
	GameRecorder.stop_recording("WIN")
	_print_recording_summary()
	_save_robot_states()
	var mission = ConfigLoader.get_mission(CampaignManager.get_current_mission())
	CampaignManager.complete_mission(mission["id"], mission.get("reward_currency", 0))
	await _show_result_overlay("MISSION COMPLETE\n+" + str(mission.get("reward_currency", 0)) + " credits")
	_cleanup_and_exit()

func _on_mission_lost() -> void:
	GameRecorder.stop_recording("LOSS")
	_print_recording_summary()
	_save_robot_states()
	await _show_result_overlay("MISSION FAILED")
	_cleanup_and_exit()

func _show_result_overlay(text: String) -> void:
	var overlay = ColorRect.new()
	overlay.color = Color(0, 0, 0, 0.7)
	overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	var label = Label.new()
	label.text = text
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	label.set_anchors_preset(Control.PRESET_FULL_RECT)
	label.add_theme_font_size_override("font_size", 36)
	overlay.add_child(label)
	# Add to HUD's CanvasLayer so it renders on top
	hud.add_child(overlay)
	await get_tree().create_timer(3.0).timeout

func _save_robot_states() -> void:
	for robot in GameManager._robots:
		if is_instance_valid(robot):
			CampaignManager.save_robot_state(robot.robot_id, robot.get_health(), robot.get_ammo())

func _print_recording_summary() -> void:
	var s = GameRecorder.get_summary()
	print("=== MISSION RECORDING SUMMARY ===")
	print("Mission: ", s.get("mission_id", "?"))
	print("Attacks: ", s.get("attacks", 0))
	print("Kills: ", s.get("kills", 0))
	print("Robot deaths: ", s.get("robot_deaths", 0))
	print("LLM actions: ", s.get("actions", 0))
	print("Events sent: ", s.get("events_sent", 0))
	print("Heals: ", s.get("heals", 0))
	print("Total events: ", s.get("total_events", 0))
	print("=================================")

func _cleanup_and_exit() -> void:
	GameManager._disconnect_all()
	get_tree().change_scene_to_file("res://scenes/Main.tscn")
