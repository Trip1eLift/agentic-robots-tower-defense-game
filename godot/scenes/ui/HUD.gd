extends CanvasLayer

@onready var wave_label: Label = $LeftPanel/VBoxContainer/WaveLabel
@onready var base_health_label: Label = $LeftPanel/VBoxContainer/StatsGrid/BaseHealthLabel
@onready var kill_label: Label = $LeftPanel/VBoxContainer/StatsGrid/KillLabel
@onready var robot_stats_container: VBoxContainer = $LeftPanel/VBoxContainer/RobotStats
@onready var btn_fall_back: Button = $BottomPanel/HBox/BtnFallBack
@onready var btn_prioritize_base: Button = $BottomPanel/HBox/BtnPrioritizeBase
@onready var btn_focus_fire: Button = $BottomPanel/HBox/BtnFocusFire
@onready var event_log: ItemList = $RightPanel/VBox/EventLog

const MAX_LOG_ENTRIES = 25
var _robot_labels: Dictionary = {}
var _tracked_robots: Dictionary = {}

func _ready() -> void:
	add_to_group("hud")
	btn_fall_back.pressed.connect(func(): _broadcast("Fall back to base immediately!"))
	btn_prioritize_base.pressed.connect(func(): _broadcast("Prioritize defending the base above all else!"))
	btn_focus_fire.pressed.connect(func(): _broadcast("Focus all fire on the nearest enemy to the base!"))

var _map_ref: Node = null

func set_map(map: Node) -> void:
	_map_ref = map

func _process(_delta: float) -> void:
	_update_robot_stats()
	if _map_ref and is_instance_valid(_map_ref):
		var hp = _map_ref.get_base_health()
		base_health_label.text = str(hp) + " / 500"
		if hp < 150:
			base_health_label.add_theme_color_override("font_color", Color(1, 0.3, 0.3, 1))
		elif hp < 300:
			base_health_label.add_theme_color_override("font_color", Color(1, 0.65, 0.3, 1))
		else:
			base_health_label.add_theme_color_override("font_color", Color(0.3, 0.9, 0.5, 1))

var _mission_title: String = ""

func reset() -> void:
	for rid in _robot_labels:
		var data = _robot_labels[rid]
		if data is Dictionary and data.has("card"):
			data["card"].queue_free()
	_robot_labels.clear()
	_tracked_robots.clear()
	event_log.clear()
	var mission_id = CampaignManager.get_current_mission()
	var mission = ConfigLoader.get_mission(mission_id)
	_mission_title = mission.get("title", "") if not mission.is_empty() else ""
	wave_label.text = _mission_title + "  //  Wave 1"
	base_health_label.text = "500 / 500"
	kill_label.text = "0"

func register_robot(robot: Node) -> void:
	var rid = robot.robot_id
	if rid in _robot_labels:
		return

	# Create a styled card per ARIA unit
	var card = PanelContainer.new()
	var style = StyleBoxFlat.new()
	var cls = robot._config.get("class", "")
	style.bg_color = Color(0.04, 0.06, 0.1, 0.4)
	style.border_color = _get_class_color(cls) * Color(1, 1, 1, 0.4)
	style.border_width_left = 2
	style.set_corner_radius_all(3)
	style.set_content_margin_all(6)
	style.content_margin_left = 10.0
	card.add_theme_stylebox_override("panel", style)
	robot_stats_container.add_child(card)

	var vbox = VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 2)
	card.add_child(vbox)

	# Row 1: Name [Class] + action
	var header_row = HBoxContainer.new()
	vbox.add_child(header_row)
	var name_label = Label.new()
	name_label.add_theme_font_size_override("font_size", 14)
	name_label.add_theme_color_override("font_color", _get_class_color(cls))
	name_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header_row.add_child(name_label)
	var action_label = Label.new()
	action_label.add_theme_font_size_override("font_size", 11)
	action_label.add_theme_color_override("font_color", Color(0.5, 0.6, 0.55, 0.8))
	action_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	header_row.add_child(action_label)

	# Row 2: HP bar
	var hp_row = HBoxContainer.new()
	hp_row.add_theme_constant_override("separation", 6)
	vbox.add_child(hp_row)
	var hp_tag = Label.new()
	hp_tag.text = "HP"
	hp_tag.add_theme_font_size_override("font_size", 10)
	hp_tag.add_theme_color_override("font_color", Color(0.4, 0.5, 0.55, 0.7))
	hp_row.add_child(hp_tag)
	var hp_bar = ProgressBar.new()
	hp_bar.custom_minimum_size = Vector2(120, 8)
	hp_bar.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hp_bar.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	hp_bar.max_value = robot._max_health
	hp_bar.value = robot.get_health()
	hp_bar.show_percentage = false
	var bar_bg = StyleBoxFlat.new()
	bar_bg.bg_color = Color(0.08, 0.1, 0.14, 0.6)
	bar_bg.set_corner_radius_all(2)
	bar_bg.set_content_margin_all(0)
	hp_bar.add_theme_stylebox_override("background", bar_bg)
	var bar_fill = StyleBoxFlat.new()
	bar_fill.bg_color = _get_class_color(cls) * Color(1, 1, 1, 0.8)
	bar_fill.set_corner_radius_all(2)
	bar_fill.set_content_margin_all(0)
	hp_bar.add_theme_stylebox_override("fill", bar_fill)
	hp_row.add_child(hp_bar)
	var hp_val = Label.new()
	hp_val.add_theme_font_size_override("font_size", 11)
	hp_val.add_theme_color_override("font_color", Color(0.7, 0.75, 0.7, 0.9))
	hp_row.add_child(hp_val)

	# Row 3: Ammo
	var ammo_label = Label.new()
	ammo_label.add_theme_font_size_override("font_size", 11)
	ammo_label.add_theme_color_override("font_color", Color(0.55, 0.6, 0.65, 0.8))
	vbox.add_child(ammo_label)

	_robot_labels[rid] = {
		"card": card, "name": name_label, "action": action_label,
		"hp_bar": hp_bar, "hp_val": hp_val, "hp_fill": bar_fill,
		"ammo": ammo_label
	}
	_tracked_robots[rid] = robot

func _get_class_color(cls: String) -> Color:
	match cls.to_lower():
		"vanguard": return Color(0.9, 0.35, 0.35)
		"architect": return Color(0.35, 0.7, 0.9)
		"striker": return Color(0.9, 0.7, 0.25)
		"medic": return Color(0.35, 0.9, 0.45)
		_: return Color(0.6, 0.6, 0.6)

func _update_robot_stats() -> void:
	for rid in _tracked_robots:
		var robot = _tracked_robots[rid]
		var d = _robot_labels[rid]
		var name_lbl: Label = d["name"]
		var action_lbl: Label = d["action"]
		var hp_bar: ProgressBar = d["hp_bar"]
		var hp_val: Label = d["hp_val"]
		var hp_fill: StyleBoxFlat = d["hp_fill"]
		var ammo_lbl: Label = d["ammo"]

		if not is_instance_valid(robot):
			name_lbl.text = rid
			action_lbl.text = "SIGNAL LOST"
			hp_bar.value = 0
			hp_val.text = "---"
			ammo_lbl.text = ""
			name_lbl.modulate = Color(0.3, 0.3, 0.3)
			continue

		var config = robot._config
		var name_str = config.get("name", rid)
		var cls = config.get("class", "?").capitalize()
		var hp = robot.get_health()
		var max_hp = robot._max_health
		var ammo = robot.get_ammo()
		var action = robot._current_action.get("action", "idle")

		name_lbl.text = name_str + "  [" + cls + "]"

		if robot._is_dead:
			action_lbl.text = "DESTROYED"
			action_lbl.add_theme_color_override("font_color", Color(0.6, 0.2, 0.2, 0.8))
			hp_bar.value = 0
			hp_val.text = "0"
			hp_val.add_theme_color_override("font_color", Color(0.5, 0.2, 0.2))
			ammo_lbl.text = ""
			name_lbl.modulate = Color(0.35, 0.35, 0.35)
			hp_fill.bg_color = Color(0.3, 0.1, 0.1, 0.5)
		else:
			action_lbl.text = "> " + action.to_upper()
			action_lbl.add_theme_color_override("font_color", Color(0.5, 0.6, 0.55, 0.8))
			hp_bar.max_value = max_hp
			hp_bar.value = hp
			hp_val.text = str(hp) + "/" + str(max_hp)
			ammo_lbl.text = "AMMO " + str(ammo)
			name_lbl.modulate = Color(1, 1, 1)

			# Color the bar based on HP percentage
			var hp_pct = float(hp) / max_hp if max_hp > 0 else 0
			if hp_pct < 0.3:
				hp_fill.bg_color = Color(0.9, 0.25, 0.2, 0.85)
				hp_val.add_theme_color_override("font_color", Color(1, 0.4, 0.4))
			elif hp_pct < 0.6:
				hp_fill.bg_color = Color(0.9, 0.6, 0.2, 0.85)
				hp_val.add_theme_color_override("font_color", Color(1, 0.7, 0.3))
			else:
				hp_fill.bg_color = _get_class_color(config.get("class", "")) * Color(1, 1, 1, 0.8)
				hp_val.add_theme_color_override("font_color", Color(0.7, 0.8, 0.7))

func update_wave(wave_number: int) -> void:
	wave_label.text = _mission_title + "  //  Wave " + str(wave_number)

func update_base_health(current: int, maximum: int) -> void:
	base_health_label.text = str(current) + " / " + str(maximum)

func update_kill_count(count: int) -> void:
	kill_label.text = str(count)

func add_log_entry(text: String) -> void:
	event_log.add_item(text)
	while event_log.item_count > MAX_LOG_ENTRIES:
		event_log.remove_item(0)
	event_log.ensure_current_is_visible()

func _broadcast(text: String) -> void:
	GameManager.set_commander_broadcast(text)
