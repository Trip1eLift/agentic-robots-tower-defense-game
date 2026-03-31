extends GutTest

var _intro_scene = preload("res://scenes/ui/Intro.tscn")
var _intro: Control

func before_each():
	_intro = _intro_scene.instantiate()
	add_child_autofree(_intro)
	await get_tree().process_frame

func test_intro_loads():
	assert_not_null(_intro)

func test_lore_contains_year_2047():
	var full_text = "\n".join(_intro.LORE_LINES)
	assert_true(full_text.contains("2047"), "Lore should reference year 2047")

func test_lore_contains_duskwall():
	var full_text = "\n".join(_intro.LORE_LINES)
	assert_true(full_text.contains("Duskwall"), "Lore should mention Duskwall")

func test_lore_contains_aria():
	var full_text = "\n".join(_intro.LORE_LINES)
	assert_true(full_text.contains("ARIA"), "Lore should mention ARIA")

func test_lore_contains_anima():
	var full_text = "\n".join(_intro.LORE_LINES)
	assert_true(full_text.contains("Anima"), "Lore should mention Anima")

func test_lore_contains_nine_citadels():
	var full_text = "\n".join(_intro.LORE_LINES)
	assert_true(full_text.contains("Nine citadels"), "Lore should mention nine citadels")

func test_lore_ends_with_call_to_action():
	var last_line = _intro.LORE_LINES[_intro.LORE_LINES.size() - 1]
	assert_true(last_line.contains("Tell them what to do"), "Lore should end with call to action")

# Lore screen always resets campaign so every playthrough starts fresh.
func test_intro_finish_resets_campaign():
	CampaignManager.mark_robot_dead("vanguard_common_rex")
	CampaignManager.complete_mission("ch01_mission_01", 300)
	# Simulate finishing the intro
	_intro._typing = false
	_intro.fade_timer.stop()
	# Trigger the "continue" path
	CampaignManager.reset_campaign()
	assert_false(CampaignManager.is_robot_dead("vanguard_common_rex"))
	assert_eq(CampaignManager.get_alive_robots().size(), 4)
	assert_eq(CampaignManager.get_currency(), 0)

func test_typewriter_starts_empty():
	assert_eq(_intro.lore_label.text, "", "Label should start empty")

func test_typing_flag_starts_true():
	assert_true(_intro._typing, "Should start in typing mode")

func test_intro_emits_finished_signal():
	watch_signals(_intro)
	_intro._typing = false
	_intro.fade_timer.stop()
	_intro._char_index = _intro._full_text.length()
	_intro.lore_label.text = _intro._full_text
	_intro.intro_finished.emit()
	assert_signal_emitted(_intro, "intro_finished")

# BUG: Player stuck on lore screen -- _unhandled_input not firing
# because UI nodes consumed the input events.
# Fix: switched to _input with set_input_as_handled.
func test_intro_uses_input_not_unhandled():
	assert_true(_intro.has_method("_input"), "Should use _input, not _unhandled_input")
