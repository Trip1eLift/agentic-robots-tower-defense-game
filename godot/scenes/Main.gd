extends Control

@onready var briefing: Control = $PreCombatBriefing
@onready var intro: Control = $Intro

var _show_intro: bool = true

func _ready() -> void:
	if CampaignManager.is_party_wiped():
		CampaignManager.reset_campaign()

	# Only show intro on first mission (or after campaign reset)
	_show_intro = not CampaignManager.has_meta("intro_seen")

	var missions = ["ch01_mission_01", "ch01_mission_02", "ch01_mission_03"]
	var current = ""
	for m in missions:
		if not CampaignManager.is_mission_completed(m):
			current = m
			break
	if current.is_empty():
		current = missions[-1]
	CampaignManager.set_current_mission(current)

	if _show_intro:
		briefing.visible = false
		intro.visible = true
		intro.intro_finished.connect(_on_intro_finished)
	else:
		intro.visible = false
		briefing.visible = true
		_setup_briefing(current)

func _on_intro_finished() -> void:
	CampaignManager.set_meta("intro_seen", true)
	intro.visible = false
	briefing.visible = true
	_setup_briefing(CampaignManager.get_current_mission())

func _setup_briefing(mission_id: String) -> void:
	briefing.setup(mission_id)
	briefing.briefing_confirmed.connect(_on_briefing_confirmed)

func _on_briefing_confirmed(_player_instructions: Dictionary) -> void:
	CampaignManager.set_meta("player_instructions", _player_instructions)
	get_tree().change_scene_to_file("res://scenes/Game.tscn")
