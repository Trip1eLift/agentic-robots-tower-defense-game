extends Node

# Autoplay mode: skips lore, auto-fills default instructions, starts mission.
# Enable via command line: --autoplay
# Speed up via: --speed=3 (default 1.0)

var _enabled: bool = false
var _speed: float = 1.0

func _ready() -> void:
	var all_args = OS.get_cmdline_args() + OS.get_cmdline_user_args()
	_enabled = all_args.has("--autoplay")
	for arg in all_args:
		if arg.begins_with("--speed="):
			_speed = float(arg.split("=")[1])
	if _enabled:
		print("AutoPlay: ENABLED -- speed=", _speed, "x")
		Engine.time_scale = _speed
	else:
		print("AutoPlay: disabled (args: ", all_args, ")")

func is_enabled() -> bool:
	return _enabled

func get_speed() -> float:
	return _speed
