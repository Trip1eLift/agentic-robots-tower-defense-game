extends GutTest

func before_each():
	CampaignManager._currency = 0
	CampaignManager._completed_missions.clear()
	CampaignManager._dead_robots.clear()
	CampaignManager._robot_health.clear()
	CampaignManager._robot_ammo.clear()
	CampaignManager._current_mission_id = ""

func test_initial_state():
	assert_eq(CampaignManager.get_currency(), 0)
	assert_false(CampaignManager.is_mission_completed("ch01_mission_01"))

func test_complete_mission():
	CampaignManager.complete_mission("ch01_mission_01", 300)
	assert_true(CampaignManager.is_mission_completed("ch01_mission_01"))
	assert_eq(CampaignManager.get_currency(), 300)

func test_complete_mission_twice_no_double_count():
	CampaignManager.complete_mission("ch01_mission_01", 300)
	CampaignManager.complete_mission("ch01_mission_01", 300)
	assert_eq(CampaignManager.get_currency(), 600)
	# Mission only appears once in completed list
	var count = 0
	for m in CampaignManager._completed_missions:
		if m == "ch01_mission_01":
			count += 1
	assert_eq(count, 1)

func test_mark_robot_dead():
	CampaignManager.mark_robot_dead("vanguard_common_rex")
	assert_true(CampaignManager.is_robot_dead("vanguard_common_rex"))
	assert_false(CampaignManager.is_robot_dead("architect_common_hana"))

func test_get_alive_robots_excludes_dead():
	CampaignManager.mark_robot_dead("vanguard_common_rex")
	var alive = CampaignManager.get_alive_robots()
	var alive_ids = []
	for r in alive:
		alive_ids.append(r["id"])
	assert_false(alive_ids.has("vanguard_common_rex"))
	assert_true(alive_ids.has("architect_common_hana"))

func test_party_wipe_detection():
	assert_false(CampaignManager.is_party_wiped())
	for r in ConfigLoader.get_all_robots():
		CampaignManager.mark_robot_dead(r["id"])
	assert_true(CampaignManager.is_party_wiped())

func test_reset_campaign():
	CampaignManager.complete_mission("ch01_mission_01", 300)
	CampaignManager.mark_robot_dead("vanguard_common_rex")
	CampaignManager.save_robot_state("architect_common_hana", 50, 20)
	CampaignManager.reset_campaign()
	assert_eq(CampaignManager.get_currency(), 0)
	assert_false(CampaignManager.is_mission_completed("ch01_mission_01"))
	assert_false(CampaignManager.is_robot_dead("vanguard_common_rex"))
	assert_eq(CampaignManager.get_alive_robots().size(), 4)

func test_save_and_restore_robot_state():
	CampaignManager.save_robot_state("architect_common_hana", 75, 30)
	assert_eq(CampaignManager.get_robot_health("architect_common_hana", 100), 75)
	assert_eq(CampaignManager.get_robot_ammo("architect_common_hana", 40), 30)

func test_robot_state_default_when_not_saved():
	assert_eq(CampaignManager.get_robot_health("architect_common_hana", 100), 100)
	assert_eq(CampaignManager.get_robot_ammo("architect_common_hana", 40), 40)

func test_set_current_mission():
	CampaignManager.set_current_mission("ch01_mission_02")
	assert_eq(CampaignManager.get_current_mission(), "ch01_mission_02")
