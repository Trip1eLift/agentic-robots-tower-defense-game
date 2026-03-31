extends Control

@onready var lore_label: RichTextLabel = $Panel/MarginContainer/VBoxContainer/LoreText
@onready var skip_label: Label = $Panel/MarginContainer/VBoxContainer/SkipLabel
@onready var fade_timer: Timer = $FadeTimer

signal intro_finished()

const LORE_LINES = [
	"[center][b]YEAR 2047[/b][/center]",
	"",
	"[center]The sun betrayed us.[/center]",
	"",
	"[center]A solar storm of unprecedented magnitude struck without warning.[/center]",
	"[center]Not a flare -- a sustained bombardment that lasted eleven days.[/center]",
	"[center]The magnetosphere collapsed on day three.[/center]",
	"[center]By day seven, the surface was an irradiated wasteland.[/center]",
	"",
	"[center]Eight billion reduced to thousands.[/center]",
	"",
	"[center]But the dying wasn't over.[/center]",
	"[center]The radiation seeped into the soil, the water, the blood of every living thing.[/center]",
	"[center]Animals didn't die -- they [i]changed[/i].[/center]",
	"[center]Bones lengthened. Eyes multiplied.[/center]",
	"[center]Hunger became the only instinct that survived the rewriting of their DNA.[/center]",
	"",
	"[center]They came for what was left of us.[/center]",
	"",
	"[center]Nine citadels were built. Eight fell.[/center]",
	"[center]The last one earned a name: [b]Duskwall[/b].[/center]",
	"",
	"[center]Flesh couldn't hold the perimeter.[/center]",
	"[center]Too few. Too fragile. Too slow.[/center]",
	"[center]So we built machines in our image and gave them[/center]",
	"[center]something we couldn't afford to lose ourselves:[/center]",
	"[center]the will to fight.[/center]",
	"",
	"[center]We called them [b]ARIA[/b] --[/center]",
	"[center]Autonomous Robotic Infantry Agents.[/center]",
	"",
	"[center]But a machine without purpose is just metal.[/center]",
	"[center]So we developed the [b]Anima[/b] system --[/center]",
	"[center]a synthetic consciousness derived from human neural patterns.[/center]",
	"[center]Not truly alive. Not truly dead.[/center]",
	"[center]Something in between that could think, adapt,[/center]",
	"[center]and choose to stand between us and extinction.[/center]",
	"",
	"[center]Four Anima units remain operational.[/center]",
	"[center]Four minds holding the line.[/center]",
	"",
	"[center]You are their [b]Commander[/b].[/center]",
	"[center]You don't control them -- you instruct them.[/center]",
	"[center]They interpret your orders through their own judgment.[/center]",
	"[center]Their own instincts.[/center]",
	"",
	"[center]The wall is cracking. The next wave is coming.[/center]",
	"",
	"[center][b]Tell them what to do.[/b][/center]",
]

var _current_line: int = 0
var _full_text: String = ""
var _char_index: int = 0
var _typing: bool = true

func _ready() -> void:
	lore_label.text = ""
	lore_label.bbcode_enabled = true
	skip_label.text = "Press any key to skip..."
	skip_label.modulate.a = 0.5
	fade_timer.wait_time = 0.03
	fade_timer.timeout.connect(_on_type_tick)
	_full_text = "\n".join(LORE_LINES)
	fade_timer.start()

func _on_type_tick() -> void:
	if _char_index < _full_text.length():
		_char_index += 1
		lore_label.text = _full_text.substr(0, _char_index)
	else:
		_typing = false
		fade_timer.stop()
		skip_label.text = "Press any key to continue..."
		skip_label.modulate.a = 1.0

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		if _typing:
			# Skip typing, show full text
			_typing = false
			fade_timer.stop()
			_char_index = _full_text.length()
			lore_label.text = _full_text
			skip_label.text = "Press any key to continue..."
			skip_label.modulate.a = 1.0
		else:
			intro_finished.emit()
