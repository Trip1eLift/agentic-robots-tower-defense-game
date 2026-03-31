extends Control

signal briefing_confirmed(player_instructions: Dictionary)

@onready var mission_title: Label = $VBoxContainer/MissionTitle
@onready var robot_cards: HBoxContainer = $VBoxContainer/RobotCards
@onready var start_button: Button = $VBoxContainer/StartButton

var _robot_configs: Array = []
var _instruction_inputs: Dictionary = {}
var _max_chars: Dictionary = {}
var _updating: bool = false

func setup(mission_id: String) -> void:
	var mission = ConfigLoader.get_mission(mission_id)
	mission_title.text = mission.get("title", "Mission")
	_robot_configs = CampaignManager.get_alive_robots()
	_build_robot_cards()
	start_button.pressed.connect(_on_start_pressed)
	var map_id = mission.get("map_id", "ch01_collapsed_road")
	var map_config = ConfigLoader.get_map(map_id)
	var positions = map_config.get("strategic_positions", [])
	var pos_names: Array[String] = []
	for pos in positions:
		pos_names.append(pos.get("id", "unknown"))
	var positions_label = Label.new()
	positions_label.text = "Available positions: " + ", ".join(pos_names)
	$VBoxContainer.add_child(positions_label)
	$VBoxContainer.move_child(positions_label, 2)

func _build_robot_cards() -> void:
	for child in robot_cards.get_children():
		child.queue_free()

	for config in _robot_configs:
		var card = VBoxContainer.new()
		robot_cards.add_child(card)

		var name_label = Label.new()
		name_label.text = config["name"] + " (" + config["class"].capitalize() + ")"
		card.add_child(name_label)

		var intelligence = config["base_stats"]["intelligence"]
		var max_chars = intelligence * 100
		_max_chars[config["id"]] = max_chars

		var char_label = Label.new()
		char_label.name = "CharLabel"
		char_label.text = "0 / " + str(max_chars) + " chars"
		card.add_child(char_label)

		var input = TextEdit.new()
		input.custom_minimum_size = Vector2(200, 120)
		input.text = _get_default_instructions(config.get("class", ""))
		input.text_changed.connect(_on_text_changed.bind(config["id"], input, char_label, max_chars))
		card.add_child(input)
		_instruction_inputs[config["id"]] = input
		# Update char count for pre-filled text
		char_label.text = str(input.text.length()) + " / " + str(max_chars) + " chars"

func _get_default_instructions(robot_class: String) -> String:
	match robot_class:
		"architect":
			return "Move to north_chokepoint and build a wall there. If enemies break through, fall back to base_entrance and build barricades. Stay behind Rex."
		"vanguard":
			return "Move to north_chokepoint and hold the line. Attack any zombie that gets close. If your health drops below 50, retreat to base_entrance. Protect the base at all costs."
		"striker":
			return "Position at west_flank where you have range advantage. Snipe enemies heading toward the base. If enemies get too close, retreat to rear_support. Conserve ammo when possible."
		"medic":
			return "Stay at rear_support behind the front line. Heal any ally whose health drops below 50%. If Rex is taking heavy damage, move closer to heal him. Only attack if no one needs healing."
		_:
			return ""

func _on_text_changed(robot_id: String, input: TextEdit, char_label: Label, max_chars: int) -> void:
	if _updating:
		return
	_updating = true
	var current_len = input.text.length()
	char_label.text = str(current_len) + " / " + str(max_chars) + " chars"
	if current_len > max_chars:
		input.text = input.text.left(max_chars)
		input.set_caret_column(max_chars)
	_updating = false

func _on_start_pressed() -> void:
	var instructions: Dictionary = {}
	for robot_id in _instruction_inputs:
		instructions[robot_id] = _instruction_inputs[robot_id].text
	briefing_confirmed.emit(instructions)
