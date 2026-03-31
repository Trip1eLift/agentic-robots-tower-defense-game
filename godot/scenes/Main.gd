extends Control

@onready var briefing: Control = $PreCombatBriefing

func _ready() -> void:
	# Check for total party kill
	if CampaignManager.is_party_wiped():
		CampaignManager.reset_campaign()

	# Advance to next mission if current one is completed
	var missions = ["ch01_mission_01", "ch01_mission_02", "ch01_mission_03"]
	var current = ""
	for m in missions:
		if not CampaignManager.is_mission_completed(m):
			current = m
			break
	if current.is_empty():
		current = missions[-1]
	CampaignManager.set_current_mission(current)
	briefing.setup(current)
	briefing.briefing_confirmed.connect(_on_briefing_confirmed)

func _on_briefing_confirmed(_player_instructions: Dictionary) -> void:
	CampaignManager.set_meta("player_instructions", _player_instructions)
	get_tree().change_scene_to_file("res://scenes/Game.tscn")
