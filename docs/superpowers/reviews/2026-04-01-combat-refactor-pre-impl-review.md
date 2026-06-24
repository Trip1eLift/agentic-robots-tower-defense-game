# Pre-Implementation Review: Combat Refactor

**Date:** 2026-04-01
**Scope:** Full codebase + combat refactor spec review before implementation
**Reviewers:** code-reviewer, silent-failure-hunter, pr-test-analyzer, comment-analyzer (all Opus)

---

## Critical Issues (7)

| # | Agent | Issue | Location |
|---|-------|-------|----------|
| 1 | errors | Processor task death is unrecoverable -- any unhandled exception permanently kills a robot's AI for the rest of the session | `backend/main.py:76-79` |
| 2 | errors | WebSocket messages silently dropped when disconnected -- register_robot can be lost, leaving a robot without AI forever | `WebSocketClient.gd:83-86` |
| 3 | errors | OllamaClient returns fake JSON on timeout/error -- indistinguishable from a real "idle" decision, masks total LLM failure | `ollama_client.py:28-34` |
| 4 | errors | Silent target fallback -- LLM orders attack on enemy 3, enemy dies, robot silently attacks enemy 7 instead with no logging | `Robot.gd:368-376` |
| 5 | code | EventType enum missing new events -- spec introduces WEAPON_RELOADING and MOVEMENT_BLOCKED but does not list `models.py` in file changes | `backend/models.py` + spec Section 7 |
| 6 | code | MockLLM will break after config migration -- `prompt_builder.py:30` KeyErrors on `stats["ammo"]` not listed in callsite audit | `backend/prompt_builder.py:30` |
| 7 | comments | Incomplete callsite audit for ammo removal -- backend pipeline (robot_state.py, main.py WS registration, prompt_builder fallback) not mentioned in migration notes | Spec Section 1, lines 96-122 |

### Details

**1. Processor task death (main.py:76-79)**
If a robot's processor task dies from an unexpected exception, it logs the error and the task is gone forever. That robot will never receive another LLM action for the rest of the game session. No restart, no notification to the client.

**2. WebSocket message drops (WebSocketClient.gd:83-86)**
When the WebSocket is not connected, all outgoing messages are silently dropped with only a `push_warning`. No queuing, no retry. `register_robot` messages can be dropped during initial connection race, meaning a robot never gets registered with the backend.

**3. OllamaClient fake JSON (ollama_client.py:28-34)**
Both timeout and connection errors return a hardcoded JSON string that looks like a valid LLM response. The caller parses it as a legitimate "idle" action. Persistent Ollama failures make ALL robots permanently idle with no user-visible indication.

**4. Silent target fallback (Robot.gd:368-376)**
When the LLM orders an attack on a specific enemy ID and that enemy is not found, the code silently falls back to attacking ANY enemy in perception range. No logging, no event fired. The E2E analyzer cannot detect misdirected attacks.

**5-7. Spec callsite gaps**
The combat refactor spec's callsite audit missed several backend references that will break during the config migration: `prompt_builder.py:30` (`stats["ammo"]`), `robot_state.py` (ammo field), `main.py:62,104,120` (ammo in runtime_stats and WS messages), `models.py` (new EventTypes needed).

---

## Important Issues (10)

| # | Agent | Issue | Location |
|---|-------|-------|----------|
| 1 | comments | Zombie `attack_rate` is dead data -- JSON field exists but Zombie.gd never reads it; timer uses .tscn default | `Zombie.gd` + `zombie.json` |
| 2 | code | ConfigLoader missing `list_dir_end()` -- directory handles leaked in 4 loading functions | `ConfigLoader.gd:19,32,47,62` |
| 3 | code | Robot._perform_heal() accesses private members of other robots -- needs public `heal()` method | `Robot.gd:264-266` |
| 4 | code | Zombie._current_target set to map node in setup() -- spec says "initially null" | `Zombie.gd:27` vs spec Section 5 |
| 5 | code | Body blocking may cause zombie traffic jams in chokepoints, triggering stalemate timer | Spec Section 4 |
| 6 | errors | Robot.gd:37-41 no config key validation -- missing JSON keys crash with unhelpful errors | `Robot.gd:37-41` |
| 7 | errors | GameManager:96 missing enemy config crashes wave spawning silently | `GameManager.gd:96` |
| 8 | errors | Unknown WebSocket message types silently ignored -- server errors never reach client | `WebSocketClient.gd:44-50` |
| 9 | errors | Spec weapon fallback hides config errors -- robot dealing 1 damage is nearly invisible | Spec Section 1, line 113 |
| 10 | comments | mock_llm.py comment claims target_id "must be int" when schema accepts `Union[int, str]` | `mock_llm.py:74-77` |

---

## Test Coverage Gaps (Priority Order)

| Priority | Gap | Criticality |
|----------|-----|-------------|
| 1 | No tests for Robot attack behavior (dealing damage) | 9/10 |
| 2 | No tests for Zombie targeting logic | 9/10 |
| 3 | Weapon data system tests needed for refactor | 9/10 |
| 4 | AttackComponent state machine tests needed | 9/10 |
| 5 | Reload system tests needed (PR 2) | 7/10 |
| 6 | Collision layer verification tests needed | 7/10 |
| 7 | Prompt builder weapon context tests | 6/10 |
| 8 | `test_dead_robot_fully_disabled` asserts `visible=false` but Robot._die() never sets it | Bug in test |

---

## Spec Reference Accuracy

The comment-analyzer verified all line references in the combat refactor spec:

| Reference | Claimed | Actual | Status |
|-----------|---------|--------|--------|
| Robot.gd:244 `damage * 3` | Line 244 | Line 244 | Correct |
| prompt_builder.py:34 `stats['damage']` | Line 34 | Line 34 | Correct |
| Robot.gd:140 `resupply_ammo()` | Line 140 | Line 140 | Correct |
| Robot.gd line count | 386 | 387 | Off by one |
| Rex damage 6*3=18 | 18 | 18 | Correct |
| Zombie attack_range 45px | 45 | 45 (in JSON) | Correct |
| Zombie aggro 135px | 135 | 135 (45*3) | Correct |

---

## Strengths

- Backend Python test coverage is comprehensive (models, parsing, events, WebSocket integration)
- Regression test suite in GUT documents 12 specific bugs with root causes
- Event queue coalescing is well-designed and well-tested
- Combat refactor spec line references are mostly accurate
- Damage math checks out correctly
- E2E recording system provides good observability for verifying combat changes

---

## Resolution

All critical and important issues from this review are addressed in the implementation plan at `docs/superpowers/plans/2026-04-01-pr1-core-combat-fix-plan.md`. Items 1-3 (processor death, WS drops, Ollama fake JSON) are out of scope for the combat refactor PR but should be addressed in a follow-up hardening PR.
