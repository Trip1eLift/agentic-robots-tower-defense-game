extends CharacterBody2D

signal died(zombie: Node2D)

@onready var nav_agent: NavigationAgent2D = $NavAgent
@onready var attack_timer: Timer = $AttackTimer

var _health: int = 50
var _max_health: int = 50
var _speed: float = 60.0
var _damage: int = 8
var _attack_range: float = 40.0
var _base_target: Node2D = null
var _current_target: Node2D = null
var _health_bar: ProgressBar = null

func setup(config: Dictionary, target: Node2D) -> void:
	var stats = config["stats"]
	_health = stats["health"]
	_max_health = stats["health"]
	_speed = stats["speed"] * 20.0
	_damage = stats["damage"]
	_attack_range = stats["attack_range"]
	_base_target = target
	_current_target = target
	nav_agent.target_position = _base_target.global_position
	attack_timer.timeout.connect(_on_attack_timer)
	attack_timer.start()
	_health_bar = ProgressBar.new()
	_health_bar.max_value = _max_health
	_health_bar.value = _health
	_health_bar.custom_minimum_size = Vector2(30, 3)
	_health_bar.position = Vector2(-15, -25)
	_health_bar.show_percentage = false
	var bg = StyleBoxFlat.new()
	bg.bg_color = Color(0.2, 0.2, 0.2)
	bg.set_content_margin_all(0)
	var fill = StyleBoxFlat.new()
	fill.bg_color = Color(0.8, 0.2, 0.2)
	fill.set_content_margin_all(0)
	_health_bar.add_theme_stylebox_override("background", bg)
	_health_bar.add_theme_stylebox_override("fill", fill)
	add_child(_health_bar)

func _physics_process(_delta: float) -> void:
	_current_target = _find_nearby_robot()
	if _current_target == null:
		_current_target = _base_target

	if _current_target == null or not is_instance_valid(_current_target):
		return

	var dist = global_position.distance_to(_current_target.global_position)
	if dist <= _attack_range:
		velocity = Vector2.ZERO
		return

	nav_agent.target_position = _current_target.global_position
	if not nav_agent.is_navigation_finished():
		var next_pos = nav_agent.get_next_path_position()
		velocity = (next_pos - global_position).normalized() * _speed
	move_and_slide()

func _find_nearby_robot() -> Node2D:
	var closest: Node2D = null
	var closest_dist := _attack_range
	for robot in get_tree().get_nodes_in_group("robots"):
		if not is_instance_valid(robot):
			continue
		if robot.has_method("is_alive") and not robot.is_alive():
			continue
		var dist = global_position.distance_to(robot.global_position)
		if dist < closest_dist:
			closest_dist = dist
			closest = robot
	return closest

func _on_attack_timer() -> void:
	if _current_target == null or not is_instance_valid(_current_target):
		return
	var dist = global_position.distance_to(_current_target.global_position)
	if dist <= _attack_range:
		if _current_target.has_method("take_base_damage"):
			_current_target.take_base_damage(_damage)
		elif _current_target.has_method("take_damage"):
			_current_target.take_damage(_damage)

func take_damage(amount: int) -> void:
	_health = max(0, _health - amount)
	if _health_bar:
		_health_bar.value = _health
	if _health == 0:
		died.emit(self)
		queue_free()

func get_health() -> int:
	return _health
