extends Control

@onready var briefing: Control = $PreCombatBriefing
@onready var intro: Control = $Intro

func _ready() -> void:
	if AutoPlay.is_enabled():
		CampaignManager.reset_campaign()
		var current = _get_next_mission()
		CampaignManager.set_current_mission(current)
		print("AutoPlay: starting mission ", current)
		var instructions = {}
		for r in ConfigLoader.get_all_robots():
			instructions[r["id"]] = _get_default_instructions(r.get("class", ""))
		CampaignManager.set_meta("player_instructions", instructions)
		# Wait for WebSocket to connect before changing scene
		if not WebSocketClient._is_connected:
			await WebSocketClient.connected
		get_tree().change_scene_to_file.call_deferred("res://scenes/Game.tscn")
		return

	# Normal flow: show intro
	briefing.visible = false
	intro.visible = true
	intro.intro_finished.connect(_on_intro_finished)

func _on_intro_finished() -> void:
	intro.visible = false
	briefing.visible = true
	var current = _get_next_mission()
	CampaignManager.set_current_mission(current)
	_setup_briefing(current)

func _get_next_mission() -> String:
	var missions = ["ch01_mission_01", "ch01_mission_02", "ch01_mission_03"]
	for m in missions:
		if not CampaignManager.is_mission_completed(m):
			return m
	return missions[0]

func _setup_briefing(mission_id: String) -> void:
	briefing.setup(mission_id)
	briefing.briefing_confirmed.connect(_on_briefing_confirmed)

func _on_briefing_confirmed(_player_instructions: Dictionary) -> void:
	CampaignManager.set_meta("player_instructions", _player_instructions)
	get_tree().change_scene_to_file("res://scenes/Game.tscn")

func _get_default_instructions(robot_class: String) -> String:
	match robot_class:
		"architect":
			return "Move to north_chokepoint and build a wall there. If enemies break through, fall back to base_entrance."
		"vanguard":
			return "Move to north_chokepoint and hold the line. Attack any zombie that gets close. Protect the base."
		"striker":
			return "Position at west_flank. Snipe enemies heading toward the base. Retreat to rear_support if overwhelmed."
		"medic":
			return "Stay at rear_support. Heal any ally below 50% health. Only attack if no one needs healing."
		_:
			return ""
