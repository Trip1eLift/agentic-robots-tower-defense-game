extends Node

# Records all game events to a text log file for debugging and E2E testing.
# Each line is a tab-separated event: timestamp_ms \t event_type \t json_data
# Appends continuously -- no buffering, no data loss on crash.

var _recording: bool = false
var _mission_id: String = ""
var _start_time_ms: int = 0
var _file: FileAccess = null
var _event_count: int = 0
var _summary: Dictionary = {}

const LOG_FILE = "e2e_recording.log"

func start_recording(mission_id: String) -> void:
	_mission_id = mission_id
	_recording = true
	_start_time_ms = Time.get_ticks_msec()
	_event_count = 0
	_summary = {"attacks": 0, "kills": 0, "robot_deaths": 0, "actions": 0, "events_sent": 0, "heals": 0}
	# Write to project root (parent of godot/)
	var project_root = ProjectSettings.globalize_path("res://").get_base_dir()
	var path = project_root.path_join(LOG_FILE)
	# Always append
	if FileAccess.file_exists(path):
		_file = FileAccess.open(path, FileAccess.READ_WRITE)
		if _file:
			_file.seek_end(0)
	if _file == null:
		_file = FileAccess.open(path, FileAccess.WRITE)
	if _file == null:
		push_error("GameRecorder: cannot open " + path)
		_recording = false
		return
	_log("RECORDING_START", {"mission_id": mission_id})
	print("GameRecorder: recording to ", path)

func stop_recording(result: String) -> void:
	_log("RECORDING_END", {"mission_id": _mission_id, "result": result, "total_events": _event_count, "summary": _summary})
	_recording = false
	if _file:
		_file.close()
		_file = null
	print("GameRecorder: stopped recording, ", _event_count, " events")

func log_robot_spawned(robot_id: String, robot_class: String, position: Array) -> void:
	_log("ROBOT_SPAWNED", {"robot_id": robot_id, "class": robot_class, "position": position})

func log_enemy_spawned(enemy_id: int, enemy_type: String, position: Array) -> void:
	_log("ENEMY_SPAWNED", {"enemy_id": enemy_id, "type": enemy_type, "position": position})

func log_event_sent(robot_id: String, event_type: String, event_detail: String) -> void:
	_log("EVENT_SENT", {"robot_id": robot_id, "event_type": event_type, "detail": event_detail})
	_summary["events_sent"] += 1

func log_action_received(robot_id: String, action: Dictionary) -> void:
	_log("ACTION_RECEIVED", {"robot_id": robot_id, "action": action})
	_summary["actions"] += 1

func log_attack(attacker_id: String, target_id: int, damage: int) -> void:
	_log("ATTACK", {"attacker_id": attacker_id, "target_id": target_id, "damage": damage})
	_summary["attacks"] += 1

func log_damage_taken(entity_id: String, amount: int, health_remaining: int) -> void:
	_log("DAMAGE_TAKEN", {"entity_id": entity_id, "amount": amount, "health_remaining": health_remaining})

func log_enemy_killed(enemy_id: int) -> void:
	_log("ENEMY_KILLED", {"enemy_id": enemy_id})
	_summary["kills"] += 1

func log_robot_died(robot_id: String) -> void:
	_log("ROBOT_DIED", {"robot_id": robot_id})
	_summary["robot_deaths"] += 1

func log_wave_started(wave_number: int) -> void:
	_log("WAVE_STARTED", {"wave_number": wave_number})

func log_wave_completed(wave_number: int) -> void:
	_log("WAVE_COMPLETED", {"wave_number": wave_number})

func log_base_damage(amount: int, health_remaining: int) -> void:
	_log("BASE_DAMAGE", {"amount": amount, "health_remaining": health_remaining})

func log_heal(healer_id: String, target_id: String, amount: int) -> void:
	_log("HEAL", {"healer_id": healer_id, "target_id": target_id, "amount": amount})
	_summary["heals"] += 1

func _log(event_type: String, data: Dictionary) -> void:
	if not _recording or _file == null:
		return
	var elapsed_ms = Time.get_ticks_msec() - _start_time_ms
	var line = str(elapsed_ms) + "\t" + event_type + "\t" + JSON.stringify(data)
	_file.store_line(line)
	_file.flush()
	_event_count += 1

func get_summary() -> Dictionary:
	var s = _summary.duplicate()
	s["mission_id"] = _mission_id
	s["total_events"] = _event_count
	return s
