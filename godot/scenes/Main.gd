extends Control

@onready var briefing: Control = $PreCombatBriefing
@onready var intro: Control = $Intro

func _ready() -> void:
	# Always show intro -- it resets the campaign on continue
	briefing.visible = false
	intro.visible = true
	intro.intro_finished.connect(_on_intro_finished)

func _on_intro_finished() -> void:
	intro.visible = false
	briefing.visible = true
	# Set mission AFTER reset (intro calls reset_campaign)
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
