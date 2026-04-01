extends Control

signal briefing_confirmed(player_instructions: Dictionary)

@onready var mission_title: Label = $Panel/MainMargin/MainVBox/HeaderSection/MissionTitle
@onready var mission_desc: Label = $Panel/MainMargin/MainVBox/HeaderSection/MissionDesc
@onready var robot_grid: GridContainer = $Panel/MainMargin/MainVBox/ContentHBox/LeftPanel/RobotScroll/RobotGrid
@onready var positions_list: VBoxContainer = $Panel/MainMargin/MainVBox/ContentHBox/RightPanel/InfoScroll/InfoVBox/PositionsSection/PositionsList
@onready var start_button: Button = $Panel/MainMargin/MainVBox/FooterSection/StartButton

var _robot_configs: Array = []
var _instruction_inputs: Dictionary = {}
var _max_chars: Dictionary = {}
var _updating: bool = false
var _char_labels: Dictionary = {}

func setup(mission_id: String) -> void:
	var mission = ConfigLoader.get_mission(mission_id)
	mission_title.text = mission.get("title", "Mission")

	var waves = mission.get("waves", [])
	var total_enemies = 0
	for w in waves:
		for eg in w.get("enemies", []):
			total_enemies += eg.get("count", 0)
	mission_desc.text = str(waves.size()) + " waves | " + str(total_enemies) + " enemies | Base HP: " + str(mission.get("base_health", 500))

	_robot_configs = CampaignManager.get_alive_robots()

	# Load map strategic positions
	var map_id = mission.get("map_id", "ch01_collapsed_road")
	var map_config = ConfigLoader.get_map(map_id)
	_build_positions_panel(map_config)
	_build_robot_cards()

	start_button.pressed.connect(_on_start_pressed)

func _build_positions_panel(map_config: Dictionary) -> void:
	for child in positions_list.get_children():
		child.queue_free()
	var positions = map_config.get("strategic_positions", [])
	for pos in positions:
		var pos_box = VBoxContainer.new()
		positions_list.add_child(pos_box)

		var name_label = Label.new()
		name_label.text = pos.get("id", "unknown").replace("_", " ").capitalize()
		name_label.add_theme_font_size_override("font_size", 22)
		name_label.add_theme_color_override("font_color", Color(0.4, 0.85, 1.0))
		pos_box.add_child(name_label)

		var desc_label = Label.new()
		desc_label.text = pos.get("description", "")
		desc_label.add_theme_font_size_override("font_size", 18)
		desc_label.add_theme_color_override("font_color", Color(0.7, 0.7, 0.7))
		desc_label.autowrap_mode = TextServer.AUTOWRAP_WORD
		pos_box.add_child(desc_label)

		var suitable = pos.get("suitable_for", [])
		if not suitable.is_empty():
			var suit_label = Label.new()
			suit_label.text = "Best for: " + ", ".join(suitable)
			suit_label.add_theme_font_size_override("font_size", 16)
			suit_label.add_theme_color_override("font_color", Color(0.5, 0.5, 0.5))
			pos_box.add_child(suit_label)

		var spacer = Control.new()
		spacer.custom_minimum_size = Vector2(0, 4)
		positions_list.add_child(spacer)

func _build_robot_cards() -> void:
	for child in robot_grid.get_children():
		child.queue_free()

	for config in _robot_configs:
		var card = PanelContainer.new()
		card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		card.size_flags_vertical = Control.SIZE_EXPAND_FILL
		var card_style = StyleBoxFlat.new()
		card_style.bg_color = Color(0.1, 0.12, 0.16)
		card_style.border_color = _get_class_color(config.get("class", ""))
		card_style.border_width_top = 3
		card_style.border_width_left = 1
		card_style.border_width_right = 1
		card_style.border_width_bottom = 1
		card_style.set_corner_radius_all(6)
		card_style.set_content_margin_all(14)
		card.add_theme_stylebox_override("panel", card_style)
		robot_grid.add_child(card)

		var vbox = VBoxContainer.new()
		vbox.add_theme_constant_override("separation", 6)
		card.add_child(vbox)

		# Header: name + class
		var header = HBoxContainer.new()
		vbox.add_child(header)

		var name_label = Label.new()
		name_label.text = config["name"]
		name_label.add_theme_font_size_override("font_size", 26)
		name_label.add_theme_color_override("font_color", _get_class_color(config.get("class", "")))
		header.add_child(name_label)

		var class_label = Label.new()
		class_label.text = "  [" + config["class"].capitalize() + "]"
		class_label.add_theme_font_size_override("font_size", 20)
		class_label.add_theme_color_override("font_color", Color(0.6, 0.6, 0.6))
		header.add_child(class_label)

		# Description
		var desc_label = Label.new()
		desc_label.text = config.get("description", "")
		desc_label.add_theme_font_size_override("font_size", 17)
		desc_label.add_theme_color_override("font_color", Color(0.55, 0.55, 0.55))
		desc_label.autowrap_mode = TextServer.AUTOWRAP_WORD
		vbox.add_child(desc_label)

		# Stats bar
		var stats = config.get("base_stats", {})
		var stats_label = Label.new()
		var hp = stats.get("health", 0)
		var dmg = stats.get("damage", 0)
		var armor = stats.get("armor", 0)
		var ammo = stats.get("ammo", 0)
		var rng = stats.get("attack_range", 0)
		# Show current HP if carrying over from previous mission
		var current_hp = CampaignManager.get_robot_health(config["id"], hp)
		var current_ammo = CampaignManager.get_robot_ammo(config["id"], ammo)
		if current_hp > 0 and current_hp < hp:
			stats_label.text = "HP:" + str(current_hp) + "/" + str(hp) + "  DMG:" + str(dmg) + "  ARM:" + str(armor) + "  Ammo:" + str(current_ammo) + "/" + str(ammo) + "  RNG:" + str(rng)
		else:
			stats_label.text = "HP:" + str(hp) + "  DMG:" + str(dmg) + "  ARM:" + str(armor) + "  Ammo:" + str(ammo) + "  RNG:" + str(rng)
		stats_label.add_theme_font_size_override("font_size", 18)
		stats_label.add_theme_color_override("font_color", Color(0.8, 0.8, 0.6))
		vbox.add_child(stats_label)

		# Role hint
		var role_label = Label.new()
		role_label.text = _get_role_hint(config.get("class", ""))
		role_label.add_theme_font_size_override("font_size", 16)
		role_label.add_theme_color_override("font_color", Color(0.5, 0.7, 0.5))
		role_label.autowrap_mode = TextServer.AUTOWRAP_WORD
		vbox.add_child(role_label)

		# Separator
		var sep = HSeparator.new()
		sep.add_theme_stylebox_override("separator", StyleBoxLine.new())
		vbox.add_child(sep)

		# Instructions label
		var instr_header = HBoxContainer.new()
		vbox.add_child(instr_header)

		var instr_label = Label.new()
		instr_label.text = "Orders:"
		instr_label.add_theme_font_size_override("font_size", 18)
		instr_label.add_theme_color_override("font_color", Color(0.7, 0.7, 0.7))
		instr_header.add_child(instr_label)

		var intelligence = stats.get("intelligence", 3)
		var max_chars = intelligence * 100
		_max_chars[config["id"]] = max_chars

		var char_label = Label.new()
		char_label.name = "CharLabel"
		char_label.add_theme_font_size_override("font_size", 16)
		char_label.add_theme_color_override("font_color", Color(0.5, 0.5, 0.5))
		char_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		char_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		instr_header.add_child(char_label)
		_char_labels[config["id"]] = char_label

		# Text input
		var input = TextEdit.new()
		input.custom_minimum_size = Vector2(0, 120)
		input.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		input.size_flags_vertical = Control.SIZE_EXPAND_FILL
		var input_style = StyleBoxFlat.new()
		input_style.bg_color = Color(0.06, 0.07, 0.1)
		input_style.border_color = Color(0.2, 0.22, 0.28)
		input_style.set_border_width_all(1)
		input_style.set_corner_radius_all(4)
		input_style.set_content_margin_all(8)
		input.add_theme_stylebox_override("normal", input_style)
		var focus_style = StyleBoxFlat.new()
		focus_style.bg_color = Color(0.07, 0.08, 0.12)
		focus_style.border_color = _get_class_color(config.get("class", "")) * Color(1, 1, 1, 0.6)
		focus_style.set_border_width_all(1)
		focus_style.set_corner_radius_all(4)
		focus_style.set_content_margin_all(8)
		input.add_theme_stylebox_override("focus", focus_style)
		input.add_theme_font_size_override("font_size", 18)
		input.add_theme_color_override("font_color", Color(0.9, 0.9, 0.9))
		input.text = _get_default_instructions(config.get("class", ""))
		input.wrap_mode = TextEdit.LINE_WRAPPING_BOUNDARY
		input.text_changed.connect(_on_text_changed.bind(config["id"]))
		vbox.add_child(input)
		_instruction_inputs[config["id"]] = input

		# Update char count for pre-filled text
		char_label.text = str(input.text.length()) + " / " + str(max_chars)

func _get_class_color(robot_class: String) -> Color:
	match robot_class:
		"vanguard": return Color(0.9, 0.3, 0.3)   # Red
		"architect": return Color(0.3, 0.7, 0.9)   # Blue
		"striker": return Color(0.9, 0.7, 0.2)     # Gold
		"medic": return Color(0.3, 0.9, 0.4)       # Green
		_: return Color(0.7, 0.7, 0.7)

func _get_role_hint(robot_class: String) -> String:
	match robot_class:
		"vanguard":
			return "Actions: attack, move, retreat | Tank -- holds chokepoints"
		"architect":
			return "Actions: build, move, attack | Builder -- creates fortifications"
		"striker":
			return "Actions: snipe, move, retreat | DPS -- long range damage"
		"medic":
			return "Actions: heal, move, attack | Support -- keeps team alive"
		_:
			return ""

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

func _on_text_changed(robot_id: String) -> void:
	if _updating:
		return
	_updating = true
	var input: TextEdit = _instruction_inputs[robot_id]
	var max_chars: int = _max_chars[robot_id]
	var char_label: Label = _char_labels[robot_id]
	var current_len = input.text.length()
	char_label.text = str(current_len) + " / " + str(max_chars)
	if current_len > max_chars:
		char_label.add_theme_color_override("font_color", Color(1.0, 0.3, 0.3))
		input.text = input.text.left(max_chars)
		input.set_caret_column(max_chars)
		char_label.text = str(max_chars) + " / " + str(max_chars)
	else:
		char_label.add_theme_color_override("font_color", Color(0.5, 0.5, 0.5))
	_updating = false

func _on_start_pressed() -> void:
	var instructions: Dictionary = {}
	for robot_id in _instruction_inputs:
		instructions[robot_id] = _instruction_inputs[robot_id].text
	briefing_confirmed.emit(instructions)
