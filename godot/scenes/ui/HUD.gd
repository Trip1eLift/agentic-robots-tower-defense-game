extends CanvasLayer

@onready var wave_label: Label = $VBoxContainer/WaveLabel
@onready var base_health_label: Label = $VBoxContainer/BaseHealthLabel
@onready var kill_label: Label = $VBoxContainer/KillLabel
@onready var robot_stats_container: VBoxContainer = $VBoxContainer/RobotStats
@onready var btn_fall_back: Button = $VBoxContainer2/HBoxContainer/BtnFallBack
@onready var btn_prioritize_base: Button = $VBoxContainer2/HBoxContainer/BtnPrioritizeBase
@onready var btn_focus_fire: Button = $VBoxContainer2/HBoxContainer/BtnFocusFire
@onready var event_log: ItemList = $EventLog

const MAX_LOG_ENTRIES = 10
var _robot_labels: Dictionary = {}    # robot_id -> Label
var _tracked_robots: Dictionary = {}  # robot_id -> Node

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
		base_health_label.text = "Base: " + str(_map_ref.get_base_health()) + "/" + str(500)

func reset() -> void:
	for label in _robot_labels.values():
		label.queue_free()
	_robot_labels.clear()
	_tracked_robots.clear()
	event_log.clear()
	wave_label.text = "Wave 1"
	base_health_label.text = "Base: 500/500"
	kill_label.text = "Kills: 0"

func register_robot(robot: Node) -> void:
	var rid = robot.robot_id
	if rid in _robot_labels:
		return
	var label = Label.new()
	label.add_theme_font_size_override("font_size", 12)
	robot_stats_container.add_child(label)
	_robot_labels[rid] = label
	_tracked_robots[rid] = robot

func _update_robot_stats() -> void:
	for rid in _tracked_robots:
		var robot = _tracked_robots[rid]
		var label: Label = _robot_labels[rid]
		if not is_instance_valid(robot):
			label.text = rid + " -- DESTROYED"
			label.modulate = Color(0.5, 0.5, 0.5)
			continue
		var config = robot._config
		var name_str = config.get("name", rid)
		var cls = config.get("class", "?").capitalize()
		var hp = robot.get_health()
		var max_hp = robot._max_health
		var ammo = robot.get_ammo()
		var action = robot._current_action.get("action", "idle")
		if robot._is_dead:
			label.text = "%s [%s] HP:0/%d -- DEAD" % [name_str, cls, max_hp]
			label.modulate = Color(1, 0.3, 0.3)
		else:
			label.text = "%s [%s] HP:%d/%d Ammo:%d (%s)" % [name_str, cls, hp, max_hp, ammo, action]
			label.modulate = Color(1, 1, 1)

func update_wave(wave_number: int) -> void:
	wave_label.text = "Wave " + str(wave_number)

func update_base_health(current: int, maximum: int) -> void:
	base_health_label.text = "Base: " + str(current) + "/" + str(maximum)

func update_kill_count(count: int) -> void:
	kill_label.text = "Kills: " + str(count)

func add_log_entry(text: String) -> void:
	event_log.add_item(text)
	while event_log.item_count > MAX_LOG_ENTRIES:
		event_log.remove_item(0)
	event_log.ensure_current_is_visible()

func _broadcast(text: String) -> void:
	GameManager.set_commander_broadcast(text)
