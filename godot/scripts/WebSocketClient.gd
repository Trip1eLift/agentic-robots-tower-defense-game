extends Node

signal action_received(robot_id: String, action: Dictionary)
signal connected()
signal disconnected()

const SERVER_URL = "ws://localhost:8765/ws"

var _socket := WebSocketPeer.new()
var _is_connected := false
var _reconnect_timer: Timer = null

func _ready() -> void:
	_reconnect_timer = Timer.new()
	_reconnect_timer.wait_time = 2.0
	_reconnect_timer.one_shot = true
	_reconnect_timer.timeout.connect(_connect_to_server)
	add_child(_reconnect_timer)
	_connect_to_server()

func _connect_to_server() -> void:
	var err = _socket.connect_to_url(SERVER_URL)
	if err != OK:
		push_error("WebSocketClient: failed to initiate connection: " + str(err))

func _process(_delta: float) -> void:
	_socket.poll()
	var state = _socket.get_ready_state()

	if state == WebSocketPeer.STATE_OPEN:
		if not _is_connected:
			_is_connected = true
			connected.emit()
		while _socket.get_available_packet_count() > 0:
			var raw = _socket.get_packet().get_string_from_utf8()
			_handle_message(raw)

	elif state == WebSocketPeer.STATE_CLOSED and _is_connected:
		_is_connected = false
		disconnected.emit()
		if _reconnect_timer.is_stopped():
			_reconnect_timer.start()

func _handle_message(raw: String) -> void:
	var data = JSON.parse_string(raw)
	if data == null:
		push_error("WebSocketClient: invalid JSON received: " + raw)
		return
	if data.has("robot_id") and data.has("action"):
		action_received.emit(data["robot_id"], data["action"])

func register_robot(robot_id: String, health: int, ammo: int, position: Vector2) -> void:
	_send({
		"type": "register_robot",
		"robot_id": robot_id,
		"health": health,
		"ammo": ammo,
		"position": [position.x, position.y]
	})

func send_state_update(robot_id: String, health: int, ammo: int, position: Vector2) -> void:
	_send({
		"type": "state_update",
		"robot_id": robot_id,
		"health": health,
		"ammo": ammo,
		"position": [position.x, position.y]
	})

func send_event(robot_id: String, event_type: String, event_detail: String,
		local_context: Dictionary, player_instructions: String,
		commander_broadcast: Variant) -> void:
	_send({
		"type": "robot_event",
		"robot_id": robot_id,
		"event_type": event_type,
		"event_detail": event_detail,
		"local_context": local_context,
		"player_instructions": player_instructions,
		"commander_broadcast": commander_broadcast
	})

func _send(data: Dictionary) -> void:
	if _socket.get_ready_state() != WebSocketPeer.STATE_OPEN:
		push_warning("WebSocketClient: not connected, dropping message")
		return
	var text = JSON.stringify(data)
	_socket.send_text(text)
