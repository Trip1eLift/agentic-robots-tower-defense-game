extends Node

# Autoplay mode: skips lore, auto-fills default instructions, starts mission.
# Enable via command line: --autoplay
# Runs missions 1-3 sequentially, prints recording summary after each.

var _enabled: bool = false

func _ready() -> void:
	_enabled = OS.get_cmdline_args().has("--autoplay")
	if _enabled:
		print("AutoPlay: ENABLED -- skipping lore, auto-starting missions")

func is_enabled() -> bool:
	return _enabled
