extends Node

# Records all game events to a JSON file for replay, debugging, and E2E testing.
# Enable via autoload. Events are flushed to disk on mission end or game exit.

var _events: Array = []
var _recording: bool = false
var _mission_id: String = ""
var _start_time_ms: int = 0

var RECORD_PATH: String = ProjectSettings.globalize_path("res://").get_base_dir().path_join("e2e_recording.json")
const FLUSH_INTERVAL_SEC = 5.0
var _flush_timer: float = 0.0

func _process(delta: float) -> void:
	if _recording:
		_flush_timer += delta
		if _flush_timer >= FLUSH_INTERVAL_SEC:
			_flush_timer = 0.0
			_save()

func start_recording(mission_id: String) -> void:
	_mission_id = mission_id
	_recording = true
	_start_time_ms = Time.get_ticks_msec()
	_flush_timer = 0.0
	_events.clear()
	_log("RECORDING_START", {"mission_id": mission_id})
	_save()
	print("GameRecorder: started recording for ", mission_id)

func stop_recording(result: String) -> void:
	_log("RECORDING_END", {"mission_id": _mission_id, "result": result, "total_events": _events.size()})
	_recording = false
	_save()

func log_robot_spawned(robot_id: String, robot_class: String, position: Array) -> void:
	_log("ROBOT_SPAWNED", {"robot_id": robot_id, "class": robot_class, "position": position})

func log_enemy_spawned(enemy_id: int, enemy_type: String, position: Array) -> void:
	_log("ENEMY_SPAWNED", {"enemy_id": enemy_id, "type": enemy_type, "position": position})

func log_event_sent(robot_id: String, event_type: String, event_detail: String) -> void:
	_log("EVENT_SENT", {"robot_id": robot_id, "event_type": event_type, "detail": event_detail})

func log_action_received(robot_id: String, action: Dictionary) -> void:
	_log("ACTION_RECEIVED", {"robot_id": robot_id, "action": action})

func log_attack(attacker_id: String, target_id: int, damage: int) -> void:
	_log("ATTACK", {"attacker_id": attacker_id, "target_id": target_id, "damage": damage})

func log_damage_taken(entity_id: String, amount: int, health_remaining: int) -> void:
	_log("DAMAGE_TAKEN", {"entity_id": entity_id, "amount": amount, "health_remaining": health_remaining})

func log_enemy_killed(enemy_id: int) -> void:
	_log("ENEMY_KILLED", {"enemy_id": enemy_id})

func log_robot_died(robot_id: String) -> void:
	_log("ROBOT_DIED", {"robot_id": robot_id})

func log_wave_started(wave_number: int) -> void:
	_log("WAVE_STARTED", {"wave_number": wave_number})

func log_wave_completed(wave_number: int) -> void:
	_log("WAVE_COMPLETED", {"wave_number": wave_number})

func log_base_damage(amount: int, health_remaining: int) -> void:
	_log("BASE_DAMAGE", {"amount": amount, "health_remaining": health_remaining})

func log_heal(healer_id: String, target_id: String, amount: int) -> void:
	_log("HEAL", {"healer_id": healer_id, "target_id": target_id, "amount": amount})

func _log(event_type: String, data: Dictionary) -> void:
	if not _recording:
		return
	var elapsed_ms = Time.get_ticks_msec() - _start_time_ms
	_events.append({
		"t": elapsed_ms,
		"type": event_type,
		"data": data
	})

func _save() -> void:
	var output = {
		"mission_id": _mission_id,
		"event_count": _events.size(),
		"events": _events
	}
	var file = FileAccess.open(RECORD_PATH, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(output, "\t"))
		file.close()
		print("GameRecorder: saved ", _events.size(), " events to ", RECORD_PATH)

func get_events() -> Array:
	return _events

func get_summary() -> Dictionary:
	var summary = {
		"mission_id": _mission_id,
		"total_events": _events.size(),
		"robots_spawned": 0,
		"enemies_spawned": 0,
		"events_sent": 0,
		"actions_received": 0,
		"attacks": 0,
		"enemies_killed": 0,
		"robots_died": 0,
		"heals": 0,
		"waves_completed": 0,
		"action_types": {},
	}
	for e in _events:
		match e["type"]:
			"ROBOT_SPAWNED": summary["robots_spawned"] += 1
			"ENEMY_SPAWNED": summary["enemies_spawned"] += 1
			"EVENT_SENT": summary["events_sent"] += 1
			"ACTION_RECEIVED":
				summary["actions_received"] += 1
				var act = e["data"].get("action", {}).get("action", "unknown")
				summary["action_types"][act] = summary["action_types"].get(act, 0) + 1
			"ATTACK": summary["attacks"] += 1
			"ENEMY_KILLED": summary["enemies_killed"] += 1
			"ROBOT_DIED": summary["robots_died"] += 1
			"HEAL": summary["heals"] += 1
			"WAVE_COMPLETED": summary["waves_completed"] += 1
	return summary
